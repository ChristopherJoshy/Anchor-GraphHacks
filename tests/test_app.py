import asyncio

from fastapi.testclient import TestClient

from anchor.app import app, mcp, service
from anchor.graph import GraphUnavailableError


def test_mcp_exposes_the_domain_tools_and_http_app():
    tools = asyncio.run(mcp.get_tools())
    assert set(tools) == {
        "anchor_health",
        "anchor_network_summary",
        "anchor_trigger_incident",
        "anchor_assess_cascade",
        "anchor_find_recovery_plans",
        "anchor_execute_recovery",
        "anchor_verify_recovery",
        "anchor_explain_decision",
        "anchor_modify_simulation",
        "anchor_reset_demo",
    }
    assert any(getattr(route, "path", "").startswith("/mcp") for route in app.routes)


def test_health_reports_graph_dependency_failure(monkeypatch):
    def fail():
        raise GraphUnavailableError("offline")

    monkeypatch.setattr(service.graph, "ping", fail)
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json()["ready"] is False
    assert response.json()["graph"] == "unavailable"
