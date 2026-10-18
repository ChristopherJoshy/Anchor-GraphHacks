import json

from anchor.graph import GraphStore


def test_get_plan_decodes_persisted_json_fields(monkeypatch):
    props = {
        "id": "plan-1",
        "unmet_by_order": json.dumps({"order-1": 0}),
        "allocations": json.dumps([]),
        "objective": json.dumps({"incremental_cost_minor": 0}),
    }
    graph = GraphStore()
    monkeypatch.setattr(graph, "_query", lambda *_args, **_kwargs: [[props]])

    assert graph.get_plan("plan-1") == {
        "id": "plan-1",
        "unmet_by_order": {"order-1": 0},
        "allocations": [],
        "objective": {"incremental_cost_minor": 0},
    }
