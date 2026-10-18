"""Orchestration shared by the HTTP API and MCP tools."""

from __future__ import annotations

from uuid import uuid4

from anchor.config import settings
from anchor.erp import ERP
from anchor.graph import GraphStore, GraphUnavailableError
from anchor.models import FailureScenario, OrderDemand, RecoveryPlan, Source
from anchor.optimizer import optimize_recovery
from anchor.seed import (
    INCIDENT_ENTITY_ID,
    SCENARIO_ID,
    TARGET_ORDER_ID,
    build_seed_records,
)


class AnchorService:
    def __init__(self, graph: GraphStore | None = None, erp: ERP | None = None):
        self.graph = graph or GraphStore(
            settings.graph_host, settings.graph_port, settings.graph_name
        )
        self.erp = erp or ERP()
        self._plans: dict[str, RecoveryPlan] = {}

    def health(self) -> dict:
        try:
            graph_ready = self.graph.ping()
            graph_error = None
        except GraphUnavailableError as exc:
            graph_ready = False
            graph_error = str(exc)
        return {
            "ready": graph_ready,
            "graph": "connected" if graph_ready else "unavailable",
            "graph_error": graph_error,
            "mode": "SIMULATION",
            "dataset_id": SCENARIO_ID,
            "erp": "ready",
        }

    def reset(self) -> dict:
        result = self.graph.reset_and_seed()
        records = build_seed_records()
        sources = []
        for supplier in records["Supplier"]:
            products = [
                r["to"]
                for r in records["relationships"]
                if r["from"] == supplier["id"] and r["type"] == "SUPPLIES"
            ]
            for product_id in products:
                sources.append(
                    {
                        "id": supplier["id"],
                        "kind": "supplier",
                        "product_id": product_id,
                        "capacity": supplier["capacity"],
                        "available": supplier["available"],
                        "unit_price_minor": supplier["unit_price_minor"],
                        "lead_days": supplier["lead_days"],
                    }
                )
        for inv in records["Inventory"]:
            sources.append(
                {
                    "id": inv["id"],
                    "kind": "inventory",
                    "product_id": inv["product_id"],
                    "capacity": inv["quantity"] - inv["reserved"],
                    "available": True,
                    "unit_price_minor": 0,
                    "lead_days": 0,
                }
            )
        self.erp.reset({"sources": sources, "orders": records["Order"]})
        self._plans.clear()
        return result

    def trigger(
        self,
        scenario_id: str = SCENARIO_ID,
        entity_id: str = INCIDENT_ENTITY_ID,
        incident_type: str = "SUPPLIER_OUTAGE",
        severity: int = 5,
        mode: str = "SIMULATION",
    ) -> dict:
        if mode != "SIMULATION":
            raise ValueError("This build supports simulation mode only")
        return self.graph.trigger_incident(scenario_id, entity_id, incident_type, severity)

    def assess(self, incident_id: str, max_depth: int = 6) -> dict:
        return self.graph.assess(incident_id, max_depth)

    def plan(self, incident_id: str, max_iterations: int | None = None) -> RecoveryPlan:
        incident = self.graph.get_incident(incident_id)
        if incident is None:
            raise ValueError(f"Incident '{incident_id}' not found")
        candidates = self.graph.source_candidates(incident_id)
        source_by_id: dict[str, Source] = {}
        for item in candidates:
            source_by_id[item["id"]] = Source(
                id=item["id"],
                label=item.get("name") or item["id"],
                kind=item["kind"],
                product_id=item["product_id"],
                capacity=item["capacity"],
                unit_price_minor=item["unit_price_minor"],
                currency=item["currency"],
                lead_days=item["lead_days"],
                available=item["available"],
                contract_approved=item["contract_approved"],
                evidence_ids=item["evidence_ids"],
            )
        order_nodes = self.graph._query(
            "MATCH (o:Order {id: $id})-[:REQUIRES]->(p:Product) "
            "RETURN o.id, p.id, o.quantity, o.priority, o.due_days LIMIT 1",
            {"id": TARGET_ORDER_ID},
        )
        if not order_nodes:
            raise ValueError("The target order is missing from FalkorDB")
        order = OrderDemand(
            id=order_nodes[0][0],
            product_id=order_nodes[0][1],
            quantity=int(order_nodes[0][2]),
            priority=int(order_nodes[0][3]),
            due_days=int(order_nodes[0][4]),
        )
        relevant = [s for s in source_by_id.values() if s.product_id == order.product_id]
        scenarios = [
            FailureScenario.model_validate(row)
            for row in self.graph.failure_scenarios(incident_id)
            if set(row["failed_entity_ids"]).issubset({s.id for s in relevant})
        ]
        plan = optimize_recovery(
            incident_id,
            int(self.graph.version()),
            relevant,
            [order],
            correlated_scenarios=scenarios,
            max_iterations=max_iterations
            if max_iterations is not None
            else settings.max_stress_iterations,
        )
        self.graph.persist_plan(plan)
        self._plans[plan.id] = plan
        return plan

    def execute(
        self, plan_id: str, mode: str = "SIMULATION", idempotency_key: str | None = None
    ) -> dict:
        if mode != "SIMULATION":
            raise ValueError("Only simulation execution is enabled")
        plan = self._plans.get(plan_id)
        if plan is None:
            saved = self.graph.get_plan(plan_id)
            if saved is None:
                raise ValueError(f"Plan '{plan_id}' not found in FalkorDB")
            plan = RecoveryPlan.model_validate(saved)
            self._plans[plan_id] = plan
        if plan.graph_version != self.graph.version():
            raise ValueError("STALE_PLAN: graph changed after planning; replan before execution")
        run_id = f"RUN-{uuid4().hex[:12].upper()}"
        receipts = []
        expected = {(a.source_id, a.order_id): a for a in plan.allocations}
        # A changed plan replaces its prior reservations in the synthetic ERP.
        try:
            for index, current in enumerate(self.erp.read_allocations()):
                desired = expected.get((current.source_id, current.order_id))
                if desired is None or desired != current:
                    released = self.erp.release_allocation(
                        current.source_id, current.order_id, f"{run_id}:release:{index}"
                    )
                    receipts.append(released.model_dump(mode="json"))
            for index, allocation in enumerate(plan.allocations):
                key = f"{idempotency_key}:{index}" if idempotency_key else f"{run_id}:{index}"
                receipt = self.erp.apply_allocation(allocation, key)
                receipt_record = receipt.model_dump(mode="json")
                receipt_record["action_id"] = f"{plan.id}-ACTION-{index + 1:03d}"
                receipts.append(receipt_record)
                self.graph.persist_receipt(
                    run_id,
                    {
                        **receipt_record,
                        "id": f"{run_id}-ACTION-{index + 1:03d}",
                        "erp_receipt_id": receipt.id,
                    },
                )
            verified = self.erp.verify(plan.allocations)
            shortfall = sum(plan.unmet_by_order.values())
            status = "RECOVERED" if verified and not shortfall else "PARTIALLY_RECOVERED"
            self.graph.record_run_outcome(plan.id, plan.incident_id, status)
            state = self.erp.current_state()
            return {
                "run_id": run_id,
                "incident_id": plan.incident_id,
                "status": status,
                "verified": verified,
                "receipts": receipts,
                "verified_allocations": [
                    a.model_dump(mode="json") for a in self.erp.read_allocations()
                ],
                "remaining_shortfall": shortfall,
                "erp_orders": state["orders"],
                "graph_version": self.graph.version(),
            }
        except Exception:
            self.graph.record_run_outcome(plan.id, plan.incident_id, "EXECUTION_FAILED")
            raise

    def verify(self, run_id: str) -> dict:
        receipts = self.graph.run_receipts(run_id)
        actual = {(a.source_id, a.order_id, a.quantity) for a in self.erp.read_allocations()}
        expected = {
            (r.get("source_id"), r.get("order_id"), int(r.get("quantity", 0)))
            for r in receipts
            if r.get("status") in {"APPLIED", "DUPLICATE"}
        }
        verified = bool(expected) and expected.issubset(actual)
        return {
            "run_id": run_id,
            "verified": verified,
            "receipts": receipts,
            "verified_allocations": [
                a.model_dump(mode="json") for a in self.erp.read_allocations()
            ],
            "state": self.erp.current_state(),
        }

    def network(self) -> dict:
        return self.graph.network_summary()

    def history(self, limit: int = 20) -> list[dict]:
        return self.graph.history(limit)
