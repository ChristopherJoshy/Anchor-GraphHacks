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


def test_mcp_streamable_http_initializes_lists_tools_and_rejects_bad_host():
    headers = {
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2025-06-18",
    }
    with TestClient(app, base_url="http://127.0.0.1:8765") as client:
        initialized = client.post(
            "/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "anchor-test", "version": "1.0"},
                },
            },
        )
        assert initialized.status_code == 200
        session_id = initialized.headers["mcp-session-id"]

        listed = client.post(
            "/mcp",
            headers={**headers, "Mcp-Session-Id": session_id},
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        )
        assert listed.status_code == 200
        assert '"name":"anchor_health"' in listed.text
        assert '"name":"anchor_reset_demo"' in listed.text

        rejected = client.post(
            "/mcp",
            headers={**headers, "Host": "attacker.example"},
            json={"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
        )
        assert rejected.status_code == 421


def test_health_reports_graph_dependency_failure(monkeypatch):
    def fail():
        raise GraphUnavailableError("offline")

    monkeypatch.setattr(service.graph, "ping", fail)
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json()["ready"] is False
    assert response.json()["graph"] == "unavailable"
