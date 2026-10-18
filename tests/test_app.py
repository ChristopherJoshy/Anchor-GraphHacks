import asyncio

from anchor.app import app, mcp


def test_mcp_exposes_the_domain_tools_and_http_app():
    tools = asyncio.run(mcp.get_tools())
    assert set(tools) == {
        "anchor_health", "anchor_network_summary", "anchor_trigger_incident",
        "anchor_assess_cascade", "anchor_find_recovery_plans", "anchor_execute_recovery",
        "anchor_verify_recovery", "anchor_explain_decision", "anchor_modify_simulation",
        "anchor_reset_demo",
    }
    assert any(getattr(route, "path", "").startswith("/mcp") for route in app.routes)
