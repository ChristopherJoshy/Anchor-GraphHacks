"""FalkorDB persistence and bounded graph reasoning for Anchor."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, ClassVar
from uuid import uuid4

from falkordb import FalkorDB
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from anchor.models import FailureScenario, RecoveryPlan
from anchor.seed import INCIDENT_ENTITY_ID, SCENARIO_ID, build_seed_records


class GraphUnavailableError(RuntimeError):
    """Raised when the configured FalkorDB graph cannot be reached or queried."""


class GraphStore:
    LABELS = (
        "Supplier",
        "Facility",
        "Product",
        "Inventory",
        "Order",
        "Customer",
        "Location",
        "Contract",
        "RouteLeg",
        "Incident",
        "Evidence",
        "RecoveryPlan",
        "Action",
        "ExecutionReceipt",
        "Scenario",
        "Policy",
        "Organization",
    )
    # Labels and relationship types are fixed internal constants; all record values are parameters.
    NODE_QUERIES: ClassVar[dict[str, str]] = {
        label: f"UNWIND $rows AS row MERGE (n:{label} {{id: row.id}}) SET n += row"
        for label in LABELS
    }
    RELATIONSHIP_QUERIES: ClassVar[dict[str, str]] = {
        "DEPENDS_ON": "MATCH (a {id: row.from}), (b {id: row.to}) MERGE (a)-[r:DEPENDS_ON]->(b) SET r.source = row.source",
        "OPERATES": "MATCH (a:Supplier {id: row.from}), (b:Facility {id: row.to}) MERGE (a)-[r:OPERATES]->(b) SET r.source = row.source",
        "SUPPLIES": "MATCH (a:Supplier {id: row.from}), (b:Product {id: row.to}) MERGE (a)-[r:SUPPLIES]->(b) SET r.capacity = row.capacity, r.unit = row.unit, r.unit_price_minor = row.unit_price_minor, r.currency = row.currency, r.lead_days = row.lead_days, r.available = row.available, r.source = row.source, r.verified = row.verified",
        "PRODUCES": "MATCH (a:Facility {id: row.from}), (b:Product {id: row.to}) MERGE (a)-[r:PRODUCES]->(b) SET r.capacity = row.capacity, r.unit = row.unit, r.source = row.source, r.verified = row.verified",
        "REQUIRES_INPUT": "MATCH (a:Facility {id: row.from}), (b:Product {id: row.to}) MERGE (a)-[r:REQUIRES_INPUT]->(b) SET r.quantity_per_output = row.quantity_per_output, r.unit = row.unit, r.source = row.source, r.verified = row.verified",
        "LOCATED_AT": "MATCH (a:Facility {id: row.from}), (b:Location {id: row.to}) MERGE (a)-[r:LOCATED_AT]->(b) SET r.source = row.source",
        "STORES": "MATCH (a:Inventory {id: row.from}), (b:Product {id: row.to}) MERGE (a)-[r:STORES]->(b) SET r.unit = row.unit, r.source = row.source",
        "HELD_AT": "MATCH (a:Inventory {id: row.from}), (b:Facility {id: row.to}) MERGE (a)-[r:HELD_AT]->(b) SET r.source = row.source",
        "REQUIRES": "MATCH (a:Order {id: row.from}), (b:Product {id: row.to}) MERGE (a)-[r:REQUIRES]->(b) SET r.source = row.source",
        "DELIVERED_TO": "MATCH (a:Order {id: row.from}), (b:Customer {id: row.to}) MERGE (a)-[r:DELIVERED_TO]->(b) SET r.source = row.source",
        "APPROVES": "MATCH (a:Contract {id: row.from}), (b:Supplier {id: row.to}) MERGE (a)-[r:APPROVES]->(b) SET r.status = row.status, r.source = row.source, r.verified = row.verified",
        "STARTS_AT": "MATCH (a:RouteLeg {id: row.from}), (b:Location {id: row.to}) MERGE (a)-[r:STARTS_AT]->(b) SET r.source = row.source",
        "ENDS_AT": "MATCH (a:RouteLeg {id: row.from}), (b:Location {id: row.to}) MERGE (a)-[r:ENDS_AT]->(b) SET r.source = row.source",
        "AFFECTS": "MATCH (a:Incident {id: row.from}), (b {id: row.to}) MERGE (a)-[r:AFFECTS]->(b) SET r.source = row.source",
        "SUPPORTED_BY": "MATCH (a:Incident {id: row.from}), (b:Evidence {id: row.to}) MERGE (a)-[r:SUPPORTED_BY]->(b) SET r.source = row.source",
        "MITIGATES": "MATCH (a:RecoveryPlan {id: row.from}), (b:Incident {id: row.to}) MERGE (a)-[r:MITIGATES]->(b) SET r.source = row.source",
        "CONTAINS": "MATCH (a:RecoveryPlan {id: row.from}), (b:Action {id: row.to}) MERGE (a)-[r:CONTAINS]->(b) SET r.source = row.source",
        "JUSTIFIED_BY": "MATCH (a:Action {id: row.from}), (b:Evidence {id: row.to}) MERGE (a)-[r:JUSTIFIED_BY]->(b) SET r.source = row.source",
        "PRODUCED": "MATCH (a:Action {id: row.from}), (b:ExecutionReceipt {id: row.to}) MERGE (a)-[r:PRODUCED]->(b) SET r.source = row.source",
        "IN_SCENARIO": "MATCH (a {id: row.from}), (b:Scenario {id: row.to}) MERGE (a)-[r:IN_SCENARIO]->(b) SET r.source = row.source",
    }
    DOWNSTREAM_CYPHER = (
        "MATCH (root {id: $entity_id}) "
        "MATCH p=(n)-[:DEPENDS_ON*1..12]->(root) WHERE length(p) <= $max_depth "
        "RETURN DISTINCT n.id AS id, labels(n) AS labels, n.name AS name, "
        "length(p) AS depth, [x IN nodes(p) | x.id] AS path LIMIT $limit"
    )
    SHARED_UPSTREAM_CYPHER = (
        "MATCH p1=(a:Supplier)-[:DEPENDS_ON*1..6]->(u:Supplier) "
        "MATCH p2=(b:Supplier)-[:DEPENDS_ON*1..6]->(u) "
        "WHERE a.id < b.id "
        "RETURN a.id AS left_id, b.id AS right_id, u.id AS shared_id, "
        "[x IN nodes(p1) | x.id] AS left_path, [x IN nodes(p2) | x.id] AS right_path "
        "LIMIT $limit"
    )

    def __init__(self, host: str = "127.0.0.1", port: int = 6379, graph_name: str = "anchor_demo"):
        self._host = host
        self._port = port
        self._graph_name = graph_name
        self._db = None
        self._graph = None

    def _connect(self) -> None:
        if self._db is not None:
            return
        try:
            self._db = FalkorDB(host=self._host, port=self._port)
            self._graph = self._db.select_graph(self._graph_name)
        except Exception as exc:
            self._db = None
            self._graph = None
            raise GraphUnavailableError(
                f"FalkorDB is unavailable at {self._host}:{self._port}: {exc}"
            ) from exc

    def _query(self, cypher: str, params: dict[str, Any] | None = None) -> list[list[Any]]:
        try:
            self._connect()
            result = self._graph.query(cypher, params=params or {})
            return result.result_set
        except (RedisConnectionError, RedisTimeoutError, OSError) as exc:
            raise GraphUnavailableError(
                f"FalkorDB graph '{self._graph_name}' query failed: {exc}"
            ) from exc

    @staticmethod
    def _props(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        props = getattr(value, "properties", None)
        return dict(props) if props is not None else {}

    def ping(self) -> bool:
        try:
            self._connect()
            return self._db.connection.ping()
        except Exception as exc:
            raise GraphUnavailableError(
                f"FalkorDB is unavailable at the configured endpoint: {exc}"
            ) from exc

    def version(self) -> int:
        rows = self._query(
            "MATCH (s:Scenario {id: $scenario_id}) RETURN s.version AS version LIMIT 1",
            {"scenario_id": SCENARIO_ID},
        )
        if not rows:
            return 0
        return int(rows[0][0] or 0)

    def _bump_version(self) -> int:
        rows = self._query(
            "MATCH (s:Scenario {id: $scenario_id}) SET s.version = coalesce(s.version, 0) + 1 "
            "RETURN s.version",
            {"scenario_id": SCENARIO_ID},
        )
        return int(rows[0][0]) if rows else 0

    def reset_and_seed(self) -> dict[str, Any]:
        """Delete and recreate only the explicitly selected demo graph."""
        try:
            self._connect()
            if self._graph_name in self._db.list_graphs():
                self._graph.delete()
            self._graph = self._db.select_graph(self._graph_name)
        except Exception as exc:
            raise GraphUnavailableError(
                f"Could not reset graph '{self._graph_name}': {exc}"
            ) from exc
        records = build_seed_records()
        for label in self.LABELS:
            rows = records.get(label, [])
            if rows:
                self._query(self.NODE_QUERIES[label], {"rows": rows})
        by_id = {row["id"]: row for label in self.LABELS for row in records.get(label, [])}
        relationship_rows: dict[str, list[dict[str, Any]]] = {}
        for relation in records["relationships"]:
            source = by_id.get(relation["from"], {})
            rel = dict(relation)
            rel.update(
                source=source.get("source", "synthetic-fixed-seed-v1"),
                capacity=source.get("capacity", 0),
                unit="unit",
                unit_price_minor=source.get("unit_price_minor", 0),
                currency="USD",
                minor_units_per_major=100,
                lead_days=source.get("lead_days", 0),
                available=source.get("available", True),
                verified=source.get("verified", True),
                status=source.get("status", "APPROVED"),
                quantity_per_output=1,
            )
            relationship_rows.setdefault(relation["type"], []).append(rel)
        for kind, rows in relationship_rows.items():
            self._query(f"UNWIND $rows AS row {self.RELATIONSHIP_QUERIES[kind]}", {"rows": rows})
        for query in (
            "CREATE INDEX FOR (n:Supplier) ON (n.id)",
            "CREATE INDEX FOR (n:Incident) ON (n.id)",
            "CREATE INDEX FOR (n:Order) ON (n.id)",
            "CREATE INDEX FOR (n:Scenario) ON (n.id)",
        ):
            try:
                self._query(query)
            except GraphUnavailableError:
                # Index syntax/support varies by FalkorDB version; indexed identifiers are an optimization.
                pass
        counts = self._query("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count LIMIT 100")
        return {
            "graph_name": self._graph_name,
            "scenario_id": SCENARIO_ID,
            "version": self.version(),
            "counts": {str(row[0]): int(row[1]) for row in counts},
            "synthetic": True,
        }

    def set_capacity(self, entity_id: str, capacity: int) -> int:
        if (
            not entity_id
            or isinstance(capacity, bool)
            or not isinstance(capacity, int)
            or capacity < 0
        ):
            raise ValueError("entity_id must be set and capacity must be a non-negative integer")
        rows = self._query(
            "MATCH (n {id: $entity_id}) WHERE n:Supplier OR n:Facility "
            "SET n.capacity = $capacity RETURN n.id",
            {"entity_id": entity_id, "capacity": int(capacity)},
        )
        if not rows:
            raise ValueError(f"No supplier or facility found with id '{entity_id}'")
        self._query(
            "MATCH (n:Supplier {id: $entity_id})-[r:SUPPLIES]->() SET r.capacity = $capacity",
            {"entity_id": entity_id, "capacity": capacity},
        )
        return self._bump_version()

    def set_dependency(self, supplier_id: str, upstream_id: str, connected: bool) -> int:
        """Change one synthetic supplier edge, rejecting cycles and unknown entities."""
        if not supplier_id or not upstream_id or supplier_id == upstream_id:
            raise ValueError("distinct supplier and upstream IDs are required")
        if not isinstance(connected, bool):
            raise TypeError("connected must be a boolean")
        endpoints = self._query(
            "MATCH (s:Supplier {id: $supplier_id}), (u:Supplier {id: $upstream_id}) "
            "RETURN s.id, u.id LIMIT 1",
            {"supplier_id": supplier_id, "upstream_id": upstream_id},
        )
        if not endpoints:
            raise ValueError("both dependency endpoints must be synthetic Supplier nodes")
        if connected:
            cycle = self._query(
                "MATCH p=(u:Supplier {id: $upstream_id})-[:DEPENDS_ON*1..40]->"
                "(s:Supplier {id: $supplier_id}) RETURN p LIMIT 1",
                {"supplier_id": supplier_id, "upstream_id": upstream_id},
            )
            if cycle:
                raise ValueError("dependency would create a cycle")
            self._query(
                "MATCH (s:Supplier {id: $supplier_id}), (u:Supplier {id: $upstream_id}) "
                "MERGE (s)-[r:DEPENDS_ON]->(u) SET r.source = 'synthetic-simulation'",
                {"supplier_id": supplier_id, "upstream_id": upstream_id},
            )
        else:
            edge = self._query(
                "MATCH (s:Supplier {id: $supplier_id})-[r:DEPENDS_ON]->"
                "(u:Supplier {id: $upstream_id}) RETURN r LIMIT 1",
                {"supplier_id": supplier_id, "upstream_id": upstream_id},
            )
            if not edge:
                raise ValueError("dependency edge does not exist")
            self._query(
                "MATCH (s:Supplier {id: $supplier_id})-[r:DEPENDS_ON]->"
                "(u:Supplier {id: $upstream_id}) DELETE r",
                {"supplier_id": supplier_id, "upstream_id": upstream_id},
            )
        return self._bump_version()

    def trigger_incident(
        self, scenario_id: str, entity_id: str, incident_type: str, severity: int
    ) -> dict[str, Any]:
        if not 1 <= severity <= 5:
            raise ValueError("severity must be between 1 and 5")
        if not all((scenario_id, entity_id, incident_type)):
            raise ValueError("scenario_id, entity_id and incident_type are required")
        incident_type = incident_type.upper()
        outage_labels = {"SUPPLIER_OUTAGE": "Supplier", "FACILITY_OUTAGE": "Facility"}
        expected_label = outage_labels.get(incident_type)
        match = (
            f"MATCH (s:Scenario {{id: $scenario_id}}), (n:{expected_label} {{id: $entity_id}}) "
            "RETURN s.id, n.id LIMIT 1"
            if expected_label
            else "MATCH (s:Scenario {id: $scenario_id}), (n {id: $entity_id}) "
            "RETURN s.id, n.id LIMIT 1"
        )
        exists = self._query(match, {"scenario_id": scenario_id, "entity_id": entity_id})
        if not exists:
            if expected_label:
                raise ValueError(f"{incident_type} requires an existing {expected_label} entity")
            raise ValueError("scenario or affected entity does not exist")
        incident_id = f"INC-{uuid4().hex[:12].upper()}"
        created = datetime.now(UTC).isoformat()
        evidence_id = "EVIDENCE-SILICON-SYNTHETIC"
        params = {
            "id": incident_id,
            "scenario_id": scenario_id,
            "entity_id": entity_id,
            "incident_type": incident_type,
            "severity": severity,
            "status": "DETECTED",
            "mode": "SIMULATION",
            "created_at": created,
            "source": "synthetic-simulation",
            "evidence_id": evidence_id,
        }
        self._query(
            "CREATE (i:Incident {id: $id, scenario_id: $scenario_id, entity_id: $entity_id, "
            "incident_type: $incident_type, severity: $severity, status: $status, mode: $mode, "
            "created_at: $created_at, source: $source}) "
            "WITH i MATCH (n {id: $entity_id}), (e:Evidence {id: $evidence_id}) "
            "CREATE (i)-[:AFFECTS]->(n), (i)-[:SUPPORTED_BY]->(e)",
            params,
        )
        if expected_label:
            self._query(
                f"MATCH (n:{expected_label} {{id: $entity_id}}) "
                "SET n.available = false, n.capacity = 0",
                {"entity_id": entity_id},
            )
            relationship = "SUPPLIES" if expected_label == "Supplier" else "PRODUCES"
            self._query(
                f"MATCH (n:{expected_label} {{id: $entity_id}})-[r:{relationship}]->() "
                "SET r.available = false, r.capacity = 0",
                {"entity_id": entity_id},
            )
        graph_version = self._bump_version()
        self._query(
            "MATCH (i:Incident {id: $id}) SET i.graph_version = $version",
            {"id": incident_id, "version": graph_version},
        )
        return self.get_incident(incident_id)

    def get_incident(self, incident_id: str) -> dict[str, Any] | None:
        rows = self._query(
            "MATCH (i:Incident {id: $id}) RETURN properties(i) LIMIT 1", {"id": incident_id}
        )
        return self._props(rows[0][0]) if rows else None

    def get_plan(self, plan_id: str) -> dict[str, Any] | None:
        rows = self._query(
            "MATCH (p:RecoveryPlan {id: $id}) RETURN properties(p) LIMIT 1", {"id": plan_id}
        )
        if not rows:
            return None
        plan = self._props(rows[0][0])
        for field in (
            "allocations",
            "unmet_by_order",
            "objective",
            "tested_scenarios",
            "evidence_ids",
            "assumptions",
            "worst_counterexample",
            "excluded_sources",
        ):
            value = plan.get(field)
            if isinstance(value, str):
                try:
                    plan[field] = json.loads(value)
                except json.JSONDecodeError:
                    pass
        return plan

    def record_run_outcome(self, plan_id: str, incident_id: str, status: str) -> None:
        if status not in {
            "RECOVERED",
            "PARTIALLY_RECOVERED",
            "EXECUTION_FAILED",
            "NEEDS_HUMAN_REVIEW",
        }:
            raise ValueError("unsupported recovery outcome status")
        self._query(
            "MATCH (p:RecoveryPlan {id: $plan_id})-[:CONTAINS]->(a:Action) "
            "SET a.status = $status, a.updated_at = $updated_at WITH p "
            "MATCH (i:Incident {id: $incident_id}) "
            "SET i.status = $status, i.updated_at = $updated_at",
            {
                "plan_id": plan_id,
                "incident_id": incident_id,
                "status": status,
                "updated_at": datetime.now(UTC).isoformat(),
            },
        )

    def run_receipts(self, run_id: str) -> list[dict[str, Any]]:
        rows = self._query(
            "MATCH (r:ExecutionReceipt {run_id: $run_id}) "
            "RETURN properties(r) AS receipt ORDER BY r.created_at LIMIT 100",
            {"run_id": run_id},
        )
        return [self._props(row[0]) for row in rows]

    def read_scenario_state(self, scenario_id: str = SCENARIO_ID) -> dict[str, Any]:
        rows = self._query(
            "MATCH (s:Scenario {id: $id}) RETURN properties(s) LIMIT 1", {"id": scenario_id}
        )
        if not rows:
            raise ValueError(f"Scenario '{scenario_id}' not found")
        scenario = self._props(rows[0][0])
        entities = self._query(
            "MATCH (n) WHERE n.scenario_id = $id OR n.id IN $ids "
            "RETURN labels(n)[0] AS label, properties(n) AS props LIMIT $limit",
            {
                "id": scenario_id,
                "ids": [
                    INCIDENT_ENTITY_ID,
                    "SUP-INDEPENDENT-D",
                    "SUP-INDEPENDENT-E",
                    "INV-MCU-350",
                    "ORDER-SILICON-1000",
                ],
                "limit": 200,
            },
        )
        state: dict[str, Any] = {"scenario": scenario, "version": self.version(), "entities": {}}
        for label, props in entities:
            state["entities"].setdefault(str(label), []).append(props)
        return state

    def network_summary(self) -> dict[str, Any]:
        detail = self._query(
            "MATCH (n) OPTIONAL MATCH (n)-[r]->(m) "
            "RETURN properties(n) AS node, type(r) AS relation, properties(r) AS edge, "
            "properties(m) AS target LIMIT 400"
        )
        rows = self._query(
            "MATCH (n) OPTIONAL MATCH (n)-[r]->() "
            "RETURN labels(n)[0] AS label, count(DISTINCT n) AS nodes, "
            "count(r) AS outgoing_edges LIMIT 100"
        )
        incidents = self._query(
            "MATCH (i:Incident) RETURN properties(i) AS incident ORDER BY i.created_at DESC LIMIT 20"
        )
        countries = self._query(
            "MATCH (l:Location) RETURN DISTINCT l.country AS country ORDER BY country LIMIT 100"
        )
        nodes: dict[str, dict[str, Any]] = {}
        relationships: list[dict[str, Any]] = []
        for node, relation, edge, target in detail:
            node_props = self._props(node)
            if node_props.get("id"):
                nodes[str(node_props["id"])] = node_props
            target_props = self._props(target)
            if target_props.get("id"):
                nodes[str(target_props["id"])] = target_props
            if relation and node_props.get("id") and target_props.get("id"):
                relationships.append(
                    {
                        "from": node_props["id"],
                        "to": target_props["id"],
                        "type": relation,
                        **self._props(edge),
                    }
                )
        return {
            "graph_name": self._graph_name,
            "version": self.version(),
            "entities": {str(row[0]): int(row[1]) for row in rows},
            "entity_count": sum(int(row[1]) for row in rows),
            "relationships": sum(int(row[2]) for row in rows),
            "relationship_count": sum(int(row[2]) for row in rows),
            "entity_records": list(nodes.values())[:200],
            "relationship_records": relationships[:400],
            "locations": [node for node in nodes.values() if "lat" in node and "lon" in node],
            "countries": [row[0] for row in countries],
            "incidents": [self._props(row[0]) for row in incidents],
            "provenance": "Synthetic demonstration data; supplier relationships are fictional.",
        }

    def assess(self, incident_id: str, max_depth: int = 6) -> dict[str, Any]:
        if not 1 <= max_depth <= 12:
            raise ValueError("max_depth must be between 1 and 12")
        incident = self.get_incident(incident_id)
        if incident is None:
            raise ValueError(f"Incident '{incident_id}' not found")
        rows = self._query(
            self.DOWNSTREAM_CYPHER,
            {"entity_id": incident["entity_id"], "max_depth": max_depth, "limit": 500},
        )
        affected = [
            {"id": row[0], "labels": row[1], "name": row[2], "depth": row[3], "path": row[4]}
            for row in rows
        ]
        orders = self._query(
            "MATCH (i:Incident {id: $id})-[:AFFECTS]->(root) "
            "MATCH (root)<-[:DEPENDS_ON*0..12]-(s:Supplier)-[:SUPPLIES]->(p:Product)<-[:REQUIRES]-(o:Order) "
            "RETURN DISTINCT properties(o) AS order, p.id AS product_id LIMIT 500",
            {"id": incident_id},
        )
        upstream = self._query(
            "MATCH (i:Incident {id: $id})-[:AFFECTS]->(root) "
            "MATCH p=(s:Supplier)-[:DEPENDS_ON*1..12]->(root) "
            "RETURN s.id, [x IN nodes(p) | x.id] AS path LIMIT 500",
            {"id": incident_id},
        )
        return {
            "incident": incident,
            "graph_version": self.version(),
            "affected_entities": affected,
            "affected_orders": [
                {"order": self._props(row[0]), "product_id": row[1]} for row in orders
            ],
            "shared_dependency_paths": [
                {"supplier_id": row[0], "path": row[1]} for row in upstream
            ],
            "assumptions": ["All seed-network operational records are synthetic."],
        }

    def source_candidates(self, incident_id: str) -> list[dict[str, Any]]:
        incident = self.get_incident(incident_id)
        if incident is None:
            raise ValueError(f"Incident '{incident_id}' not found")
        rows = self._query(
            "MATCH (i:Incident {id: $id})-[:AFFECTS]->(failed) "
            "MATCH (o:Order)-[:REQUIRES]->(p:Product) "
            "WHERE o.scenario_id = i.scenario_id "
            "MATCH (s:Supplier)-[sp:SUPPLIES]->(p) "
            "OPTIONAL MATCH (c:Contract)-[:APPROVES]->(s) "
            "WITH i, failed, o, p, s, sp, c "
            "OPTIONAL MATCH path=(s)-[:DEPENDS_ON*1..12]->(failed) "
            "WITH o, p, s, sp, c, path "
            "WHERE s.available = true AND (path IS NULL) "
            "AND c.status = 'APPROVED' "
            "RETURN DISTINCT properties(s) AS supplier, properties(sp) AS supply, "
            "properties(o) AS order, p.id AS product_id, c.status AS contract_status LIMIT 1000",
            {"id": incident_id},
        )
        inventory = self._query(
            "MATCH (i:Incident {id: $id}), (o:Order)-[:REQUIRES]->(p:Product), "
            "(v:Inventory)-[:STORES]->(p) "
            "WHERE o.scenario_id = i.scenario_id AND v.quantity > coalesce(v.reserved, 0) "
            "RETURN properties(v) AS inventory, properties(o) AS order, p.id AS product_id LIMIT 1000",
            {"id": incident_id},
        )
        results = []
        for supplier, supply, order, product_id, contract_status in rows:
            s, edge, o = self._props(supplier), self._props(supply), self._props(order)
            results.append(
                {
                    "id": s["id"],
                    "name": s.get("name"),
                    "kind": "supplier",
                    "product_id": product_id,
                    "capacity": int(edge.get("capacity", s.get("capacity", 0))),
                    "unit_price_minor": int(
                        edge.get("unit_price_minor", s.get("unit_price_minor", 0))
                    ),
                    "currency": edge.get("currency", "USD"),
                    "minor_units_per_major": int(edge.get("minor_units_per_major", 100)),
                    "lead_days": int(edge.get("lead_days", s.get("lead_days", 0))),
                    "available": bool(edge.get("available", s.get("available", False))),
                    "contract_approved": contract_status == "APPROVED",
                    "order_id": o["id"],
                    "evidence_ids": ["EVIDENCE-SILICON-SYNTHETIC"],
                }
            )
        for inventory_row, order, product_id in inventory:
            v, o = self._props(inventory_row), self._props(order)
            qty = max(0, int(v.get("quantity", 0)) - int(v.get("reserved", 0)))
            results.append(
                {
                    "id": v["id"],
                    "name": v["id"],
                    "kind": "inventory",
                    "product_id": product_id,
                    "capacity": qty,
                    "unit_price_minor": 0,
                    "currency": "USD",
                    "minor_units_per_major": 100,
                    "lead_days": 0,
                    "available": qty > 0,
                    "contract_approved": True,
                    "order_id": o["id"],
                    "evidence_ids": ["EVIDENCE-SILICON-SYNTHETIC"],
                }
            )
        return results

    def dependency_exclusions(self, incident_id: str) -> list[dict[str, Any]]:
        """Return order-compatible suppliers with a path to the incident-affected entity."""
        rows = self._query(
            "MATCH (i:Incident {id: $id})-[:AFFECTS]->(failed) "
            "MATCH (o:Order)-[:REQUIRES]->(p:Product) "
            "WHERE o.scenario_id = i.scenario_id "
            "MATCH (s:Supplier)-[sp:SUPPLIES]->(p) "
            "MATCH path=(s)-[:DEPENDS_ON*1..12]->(failed) "
            "OPTIONAL MATCH (c:Contract)-[:APPROVES]->(s) "
            "RETURN DISTINCT s.id, s.name, p.id, s.capacity, s.available, "
            "sp.capacity, sp.available, c.status, [x IN nodes(path) | x.id] AS path LIMIT 500",
            {"id": incident_id},
        )
        return [
            {
                "supplier_id": row[0],
                "supplier_name": row[1],
                "product_id": row[2],
                "supplier_capacity": int(row[3] or 0),
                "supplier_available": bool(row[4]),
                "supply_capacity": int(row[5] or 0),
                "supply_available": bool(row[6]),
                "contract_status": row[7],
                "reasons": ["SHARED_UPSTREAM_PATH_TO_INCIDENT_ENTITY"],
                "dependency_path": list(row[8] or []),
                "evidence_ids": ["EVIDENCE-SILICON-SYNTHETIC"],
            }
            for row in rows
        ]

    def failure_scenarios(self, incident_id: str) -> list[dict[str, Any]]:
        candidates = self.source_candidates(incident_id)
        incident = self.get_incident(incident_id)
        assert incident is not None
        relevant = sorted({item["id"] for item in candidates if item["kind"] == "supplier"})
        products = self._query(
            "MATCH (i:Incident {id: $id}), (o:Order)-[:REQUIRES]->(p:Product) "
            "WHERE o.scenario_id = i.scenario_id RETURN DISTINCT p.id LIMIT 100",
            {"id": incident_id},
        )
        if products:
            possible = self._query(
                "MATCH (s:Supplier)-[:SUPPLIES]->(p:Product) "
                "WHERE p.id IN $product_ids AND s.available = true "
                "RETURN DISTINCT s.id LIMIT 500",
                {"product_ids": [row[0] for row in products]},
            )
            relevant = sorted(set(relevant + [row[0] for row in possible]))
        affected = self._query(
            "MATCH (i:Incident {id: $id})-[:AFFECTS]->(n) RETURN n.id LIMIT 100",
            {"id": incident_id},
        )
        node_ids = sorted(set(relevant + [row[0] for row in affected]))
        scenarios: list[dict[str, Any]] = []
        for entity_id in node_ids:
            scenarios.append(
                FailureScenario(
                    id=f"FAIL-{entity_id}",
                    failed_entity_ids=[entity_id],
                    paths=[[entity_id]],
                    label=f"Single-node failure: {entity_id}",
                ).model_dump(mode="json")
            )
        shared = self._query(self.SHARED_UPSTREAM_CYPHER, {"limit": 500})
        for left, right, shared_id, path_left, path_right in shared:
            if left not in relevant and right not in relevant:
                continue
            scenarios.append(
                FailureScenario(
                    id=f"FAIL-PAIR-{left}-{right}",
                    failed_entity_ids=[left, right],
                    paths=[path_left, path_right],
                    label=f"Correlated supplier failure via shared upstream {shared_id}",
                ).model_dump(mode="json")
            )
        return scenarios

    def persist_plan(self, plan: RecoveryPlan | dict[str, Any]) -> dict[str, Any]:
        payload = plan.model_dump(mode="json") if isinstance(plan, RecoveryPlan) else dict(plan)
        if not payload.get("id") or not payload.get("incident_id"):
            raise ValueError("plan must include id and incident_id")
        payload.setdefault("created_at", datetime.now(UTC).isoformat())
        payload["allocations_json"] = json.dumps(payload.get("allocations", []), sort_keys=True)
        payload["objective_json"] = json.dumps(payload.get("objective", {}), sort_keys=True)
        payload["evidence_ids_json"] = json.dumps(payload.get("evidence_ids", []), sort_keys=True)
        payload["tested_scenarios_json"] = json.dumps(
            payload.get("tested_scenarios", []), sort_keys=True
        )
        graph_payload = {
            key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value
            for key, value in payload.items()
        }
        self._query(
            "MERGE (p:RecoveryPlan {id: $id}) SET p += $props "
            "WITH p MATCH (i:Incident {id: $incident_id}) MERGE (p)-[:MITIGATES]->(i)",
            {"id": payload["id"], "incident_id": payload["incident_id"], "props": graph_payload},
        )
        for index, allocation in enumerate(payload.get("allocations", [])):
            action = {
                "id": f"{payload['id']}-ACTION-{index + 1:03d}",
                "plan_id": payload["id"],
                "incident_id": payload["incident_id"],
                "status": "PLANNED",
                "created_at": payload["created_at"],
                "allocation_json": json.dumps(allocation, sort_keys=True),
                "source_id": allocation.get("source_id"),
                "order_id": allocation.get("order_id"),
                "quantity": int(allocation.get("quantity", 0)),
            }
            self._query(
                "MERGE (a:Action {id: $id}) SET a += $props "
                "WITH a MATCH (p:RecoveryPlan {id: $plan_id}) MERGE (p)-[:CONTAINS]->(a)",
                {"id": action["id"], "plan_id": payload["id"], "props": action},
            )
        return payload

    def persist_receipt(self, run_id: str, receipt: dict[str, Any]) -> dict[str, Any]:
        if not run_id:
            raise ValueError("run_id is required")
        receipt_id = str(receipt.get("id") or f"RECEIPT-{uuid4().hex[:12].upper()}")
        payload = dict(receipt, id=receipt_id, run_id=run_id)
        payload.setdefault("created_at", datetime.now(UTC).isoformat())
        graph_payload = {
            key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value
            for key, value in payload.items()
        }
        action_id = payload.get("action_id")
        if action_id:
            self._query(
                "MERGE (r:ExecutionReceipt {id: $id}) SET r += $props "
                "WITH r MATCH (a:Action {id: $action_id}) MERGE (a)-[:PRODUCED]->(r)",
                {"id": receipt_id, "props": graph_payload, "action_id": action_id},
            )
        else:
            self._query(
                "MERGE (r:ExecutionReceipt {id: $id}) SET r += $props",
                {"id": receipt_id, "props": graph_payload},
            )
        return payload

    def history(self, limit: int = 10) -> list[dict[str, Any]]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        rows = self._query(
            "MATCH (n) WHERE n:Incident OR n:RecoveryPlan OR n:Action OR n:ExecutionReceipt "
            "RETURN labels(n)[0] AS kind, properties(n) AS props "
            "ORDER BY coalesce(n.updated_at, n.created_at) DESC LIMIT $limit",
            {"limit": limit},
        )
        return [{"kind": row[0], **self._props(row[1])} for row in rows]
