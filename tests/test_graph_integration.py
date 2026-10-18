import pytest

from anchor.erp import ERP
from anchor.graph import GraphStore, GraphUnavailableError
from anchor.seed import INCIDENT_ENTITY_ID, SCENARIO_ID
from anchor.service import AnchorService


def test_falkordb_backed_silicon_recovery_and_replan(tmp_path):
    graph = GraphStore(graph_name="anchor_integration_test")
    try:
        graph.ping()
    except GraphUnavailableError as exc:
        pytest.skip(f"FalkorDB integration service unavailable: {exc}")

    erp_path = tmp_path / "erp.sqlite3"
    service = AnchorService(graph=graph, erp=ERP(erp_path))
    service.reset()

    incident = service.trigger(SCENARIO_ID, INCIDENT_ENTITY_ID)
    impact = service.assess(incident["id"])
    shared_paths = {tuple(item["path"]) for item in impact["shared_dependency_paths"]}
    assert ("SUP-BACKUP-B", "SUP-TAIWAN-FOUNDRY") in shared_paths
    assert ("SUP-BACKUP-C", "SUP-TAIWAN-FOUNDRY") in shared_paths
    assert any(item["order"]["id"] == "ORDER-SILICON-1000" for item in impact["affected_orders"])

    first_plan = service.plan(incident["id"])
    assert {item.source_id: item.quantity for item in first_plan.allocations} == {
        "INV-MCU-350": 350,
        "SUP-INDEPENDENT-D": 650,
    }
    assert first_plan.objective.worst_single_failure_shortfall == 0
    assert first_plan.stress_passed

    restarted_service = AnchorService(
        graph=GraphStore(graph_name="anchor_integration_test"), erp=ERP(erp_path)
    )
    first_run = restarted_service.execute(first_plan.id, idempotency_key="integration-run-1")
    assert first_run["verified"] is True
    assert restarted_service.verify(first_run["run_id"])["verified"] is True

    graph.set_capacity("SUP-INDEPENDENT-D", 450)
    service.erp.set_capacity("SUP-INDEPENDENT-D", 450)
    second_plan = service.plan(incident["id"])
    assert {item.source_id: item.quantity for item in second_plan.allocations} == {
        "INV-MCU-350": 350,
        "SUP-INDEPENDENT-D": 450,
        "SUP-INDEPENDENT-E": 200,
    }
    assert second_plan.objective.worst_single_failure_shortfall == 0
    assert second_plan.stress_passed
    second_run = service.execute(second_plan.id, idempotency_key="integration-run-2")
    assert second_run["status"] == "RECOVERED"
    assert second_run["remaining_shortfall"] == 0
    assert service.verify(second_run["run_id"])["verified"] is True
    assert any(
        record.get("run_id") == second_run["run_id"]
        for record in graph.run_receipts(second_run["run_id"])
    )
    history = graph.history(100)
    timestamps = [record.get("updated_at") or record.get("created_at") for record in history]
    assert all(timestamps)
    assert timestamps == sorted(timestamps, reverse=True)
    assert any(
        record["kind"] == "ExecutionReceipt" and record.get("run_id") == second_run["run_id"]
        for record in history
    )

    graph._graph.delete()
