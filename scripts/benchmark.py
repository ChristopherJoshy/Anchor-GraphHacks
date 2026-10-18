"""Measure Anchor's seeded recovery path against a disposable FalkorDB graph."""

from __future__ import annotations

import gc
import json
import math
import platform
import statistics
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from anchor.erp import ERP
from anchor.graph import GraphStore, GraphUnavailableError
from anchor.models import OrderDemand, Source
from anchor.seed import (
    INCIDENT_ENTITY_ID,
    SCENARIO_ID,
    TARGET_ORDER_ID,
    TARGET_PRODUCT_ID,
    build_seed_records,
)
from anchor.service import AnchorService
from anchor.simulation import simulate_production_impact


def measure(function, samples: int) -> dict[str, float | int]:
    function()
    elapsed_ms = []
    for _ in range(samples):
        start = time.perf_counter_ns()
        function()
        elapsed_ms.append((time.perf_counter_ns() - start) / 1_000_000)
    ordered = sorted(elapsed_ms)
    return {
        "samples": samples,
        "median_ms": round(statistics.median(ordered), 3),
        "p95_ms": round(ordered[math.ceil(0.95 * samples) - 1], 3),
        "min_ms": round(ordered[0], 3),
    }


def as_source(row: dict) -> Source:
    return Source(
        id=row["id"],
        label=row.get("name") or row["id"],
        kind=row["kind"],
        product_id=row["product_id"],
        capacity=int(row["capacity"]),
        unit_price_minor=int(row["unit_price_minor"]),
        currency=row.get("currency", "USD"),
        lead_days=int(row["lead_days"]),
        available=bool(row["available"]),
        contract_approved=bool(row["contract_approved"]),
        evidence_ids=row.get("evidence_ids", []),
    )


def main() -> None:
    records = build_seed_records()
    seed_suppliers = {row["id"]: row for row in records["Supplier"]}
    seed_order = next(row for row in records["Order"] if row["id"] == TARGET_ORDER_ID)
    order = OrderDemand.model_validate(seed_order)
    graph = GraphStore(graph_name=f"anchor_bench_{uuid4().hex[:10]}")

    try:
        graph.ping()
    except GraphUnavailableError as exc:
        raise SystemExit(f"FalkorDB is required for this benchmark: {exc}") from exc

    with tempfile.TemporaryDirectory(prefix="anchor-benchmark-") as temp_dir:
        service = AnchorService(graph=graph, erp=ERP(Path(temp_dir) / "erp.sqlite3"))
        try:
            service.reset()
            incident = service.trigger(SCENARIO_ID, INCIDENT_ENTITY_ID)
            incident_id = incident["id"]
            candidates = [as_source(row) for row in graph.source_candidates(incident_id)]
            inventory = [source for source in candidates if source.kind == "inventory"]

            no_action = simulate_production_impact(inventory, [order])
            naive_ids = {
                relation["from"]
                for relation in records["relationships"]
                if relation["type"] == "SUPPLIES" and relation["to"] == TARGET_PRODUCT_ID
            }
            naive_sources = [
                as_source(
                    {
                        **seed_suppliers[supplier_id],
                        "kind": "supplier",
                        "product_id": TARGET_PRODUCT_ID,
                        "contract_approved": True,
                        "currency": "USD",
                        "evidence_ids": ["EVIDENCE-SILICON-SYNTHETIC"],
                    }
                )
                for supplier_id in sorted(naive_ids)
            ] + inventory
            naive_plan = simulate_production_impact(naive_sources, [order])
            naive_allocations = {
                item["source_id"]: int(item["quantity"])
                for item in naive_plan["allocations"]
            }
            if naive_allocations != {
                "INV-MCU-350": 350,
                "SUP-BACKUP-B": 600,
                "SUP-BACKUP-C": 50,
            }:
                raise AssertionError("dependency-blind baseline allocation changed")
            eligible_ids = {source.id for source in candidates}
            naive_realized = sum(
                int(allocation["quantity"])
                for allocation in naive_plan["allocations"]
                if allocation["source_id"] in eligible_ids
            )

            base_plan = service.plan(incident_id)
            if base_plan.unmet_by_order[TARGET_ORDER_ID] != 0:
                raise AssertionError("baseline graph-aware recovery should fulfill the order")

            traversal = measure(lambda: graph.assess(incident_id, 6), 30)
            impact = measure(lambda: simulate_production_impact(candidates, [order]), 30)
            planning = measure(lambda: service.plan(incident_id), 5)

            graph.set_capacity("SUP-INDEPENDENT-D", 450)
            reduced_plan = service.plan(incident_id)
            reduced_allocations = {
                item.source_id: item.quantity for item in reduced_plan.allocations
            }
            if reduced_plan.unmet_by_order[TARGET_ORDER_ID] != 0:
                raise AssertionError("reduced-capacity recovery should remain feasible")
            if reduced_allocations.get("SUP-INDEPENDENT-D") != 450:
                raise AssertionError("reduced-capacity plan should use all 450 D units")
            if reduced_allocations.get("SUP-INDEPENDENT-E") != 200:
                raise AssertionError("reduced-capacity plan should use 200 E units")

            for supplier_id in (
                "SUP-INDEPENDENT-D",
                "SUP-INDEPENDENT-E",
                "SUP-INDEPENDENT-F",
            ):
                graph.set_capacity(supplier_id, 0)
            infeasible_plan = service.plan(incident_id)
            if infeasible_plan.unmet_by_order[TARGET_ORDER_ID] != 650:
                raise AssertionError("infeasible case should report 650 units unmet")

            def missing_incident() -> None:
                try:
                    graph.assess("INCIDENT-MISSING-BENCHMARK", 6)
                except ValueError:
                    return
                raise AssertionError("missing incident must fail explicitly")

            missing = measure(missing_incident, 30)

            end_to_end_ms = []
            for _ in range(5):
                service.reset()
                start = time.perf_counter_ns()
                current_incident = service.trigger(SCENARIO_ID, INCIDENT_ENTITY_ID)
                service.assess(current_incident["id"])
                plan = service.plan(current_incident["id"])
                run = service.execute(plan.id)
                verification = service.verify(run["run_id"])
                elapsed = (time.perf_counter_ns() - start) / 1_000_000
                if not run["verified"] or not verification["verified"]:
                    raise AssertionError("end-to-end recovery did not verify")
                end_to_end_ms.append(elapsed)

            ordered = sorted(end_to_end_ms)
            dataset_counts = {
                "nodes": sum(
                    len(rows) for label, rows in records.items() if label != "relationships"
                ),
                "relationships": len(records["relationships"]),
                "suppliers": len(records["Supplier"]),
                "orders": len(records["Order"]),
            }
            result = {
                "measured_at_utc": datetime.now(UTC).isoformat(),
                "environment": {
                    "platform": platform.platform(),
                    "processor": platform.processor() or "not exposed by Python",
                    "python": sys.version.split()[0],
                    "graph_name": "temporary, uniquely named FalkorDB graph",
                },
                "method": {
                    "dataset": dataset_counts,
                    "warmups": 1,
                    "samples": {"traversal": 30, "impact": 30, "planning": 5, "end_to_end": 5},
                    "end_to_end_scope": "incident trigger through ERP read-back verification; excludes graph seed/reset",
                },
                "latency": {
                    "graph_cascade_traversal": traversal,
                    "source_order_impact_simulation": impact,
                    "graph_backed_planning_and_persistence": planning,
                    "end_to_end_trigger_to_verified_recovery": {
                        "samples": len(ordered),
                        "median_ms": round(statistics.median(ordered), 3),
                        "p95_ms": round(ordered[math.ceil(0.95 * len(ordered)) - 1], 3),
                        "min_ms": round(ordered[0], 3),
                    },
                    "missing_incident_fail_closed": missing,
                },
                "scenario_results": {
                    "no_intervention": {
                        "unmet_units": no_action["unmet_units"],
                        "incremental_cost_minor": 0,
                    },
                    "naive_nominal_cheapest_ignoring_dependencies": {
                        "allocations": naive_plan["allocations"],
                        "nominal_unmet_units": naive_plan["unmet_units"],
                        "nominal_cost_minor": sum(
                            int(item["quantity"]) * int(item["unit_price_minor"])
                            for item in naive_plan["allocations"]
                        ),
                        "realized_unmet_units_after_graph_eligibility": order.quantity
                        - naive_realized,
                    },
                    "graph_optimized_foundry_failure": {
                        "unmet_units": base_plan.unmet_by_order[TARGET_ORDER_ID],
                        "incremental_cost_minor": base_plan.objective.incremental_cost_minor,
                        "stress_passed": base_plan.stress_passed,
                        "stress_scenarios_tested": len(base_plan.tested_scenarios),
                        "allocations": [
                            item.model_dump(mode="json") for item in base_plan.allocations
                        ],
                    },
                    "independent_D_capacity_450": {
                        "unmet_units": reduced_plan.unmet_by_order[TARGET_ORDER_ID],
                        "incremental_cost_minor": reduced_plan.objective.incremental_cost_minor,
                        "allocations": [
                            item.model_dump(mode="json") for item in reduced_plan.allocations
                        ],
                    },
                    "infeasible_independent_capacity": {
                        "unmet_units": infeasible_plan.unmet_by_order[TARGET_ORDER_ID],
                        "reported_infeasible": infeasible_plan.unmet_by_order[TARGET_ORDER_ID] > 0,
                    },
                    "recovery_cases": {
                        "feasible_cases_fully_recovered": 2,
                        "feasible_cases_tested": 2,
                        "intentionally_infeasible_case_unmet_units": infeasible_plan.unmet_by_order[
                            TARGET_ORDER_ID
                        ],
                    },
                },
            }
            print(json.dumps(result, indent=2, sort_keys=True))
        finally:
            graph._graph.delete()
            service = None
            gc.collect()


if __name__ == "__main__":
    main()
