"""Loopback FastAPI and domain-specific MCP entry point."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from mcp.server.transport_security import TransportSecurityMiddleware, TransportSecuritySettings
from pydantic import BaseModel, Field
from starlette.middleware import Middleware
from starlette.requests import Request

from anchor.service import AnchorService

service = AnchorService()
mcp = FastMCP("Anchor graph-native recovery")


class LoopbackMCPGuard:
    def __init__(self, app):
        self.app = app
        self.security = TransportSecurityMiddleware(
            TransportSecuritySettings(
                enable_dns_rebinding_protection=True,
                allowed_hosts=["127.0.0.1:8765", "localhost:8765"],
                allowed_origins=["http://127.0.0.1:8765", "http://localhost:8765"],
            )
        )

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            response = await self.security.validate_request(Request(scope))
            if response is not None:
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


@mcp.tool
def anchor_health() -> dict:
    """Report FalkorDB and local simulation readiness."""
    return service.health()


@mcp.tool
def anchor_history(limit: int = Field(default=20, ge=1, le=100)) -> dict:
    """Retrieve recent incidents, recovery plans, actions, and receipts from FalkorDB."""
    items = service.history(limit)
    return {
        "summary": f"Retrieved {len(items)} graph-backed records.",
        "count": len(items),
        "items": items,
    }


@mcp.tool
def anchor_network_summary() -> dict:
    """Summarize the synthetic connected supply network and incidents."""
    return service.network()


@mcp.tool
def anchor_trigger_incident(
    scenario_id: str,
    entity_id: str,
    incident_type: str = "SUPPLIER_OUTAGE",
    severity: int = Field(default=5, ge=1, le=5),
    mode: str = "SIMULATION",
) -> dict:
    """Create a synthetic incident; the only accepted mode is SIMULATION."""
    return service.trigger(scenario_id, entity_id, incident_type, severity, mode)


@mcp.tool
def anchor_assess_cascade(incident_id: str, max_depth: int = Field(default=6, ge=1, le=12)) -> dict:
    """Trace graph-backed consequences and dependency paths."""
    return service.assess(incident_id, max_depth)


@mcp.tool
def anchor_find_recovery_plans(
    incident_id: str, max_iterations: int = Field(default=8, ge=0, le=16)
) -> dict:
    """Solve a deterministic constrained allocation and bounded resilience tests."""
    return service.plan(incident_id, max_iterations).model_dump(mode="json")


@mcp.tool
def anchor_execute_recovery(
    plan_id: str, mode: str = "SIMULATION", idempotency_key: str | None = None
) -> dict:
    """Execute an authorized plan in the local simulation and read back its results."""
    return service.execute(plan_id, mode, idempotency_key)


@mcp.tool
def anchor_verify_recovery(run_id: str) -> dict:
    """Read the persistent mock ERP state for a recovery run."""
    return service.verify(run_id)


@mcp.tool
def anchor_explain_decision(plan_id: str) -> dict:
    """Return the persisted plan, graph paths, optimization objective, and evidence."""
    plan = service._plans.get(plan_id)
    if plan is None:
        for item in service.history():
            if item.get("kind") == "RecoveryPlan" and item.get("id") == plan_id:
                return item
        raise ValueError(f"Plan {plan_id} is not in graph history")
    return {**plan.model_dump(mode="json"), "cascade": service.assess(plan.incident_id)}


@mcp.tool
def anchor_modify_simulation(
    entity_id: str, value: int = Field(..., ge=0), kind: str = "supplier_capacity"
) -> dict:
    """Modify an allowlisted synthetic capacity field; no production data is writable."""
    if kind != "supplier_capacity":
        raise ValueError("Only supplier_capacity is currently supported")
    version = service.graph.set_capacity(entity_id, value)
    service.erp.set_capacity(entity_id, value)
    return {
        "entity_id": entity_id,
        "capacity": value,
        "graph_version": version,
        "mode": "SIMULATION",
    }


@mcp.tool
def anchor_reset_demo() -> dict:
    """Destructively reset only Anchor's named synthetic demo graph and local ERP."""
    return service.reset()


mcp_app = mcp.http_app(
    path="/",
    middleware=[Middleware(LoopbackMCPGuard)],
)
app = FastAPI(title="Anchor", version="0.1.0", lifespan=mcp_app.lifespan)


class TriggerBody(BaseModel):
    scenario_id: str
    entity_id: str
    incident_type: str = "SUPPLIER_OUTAGE"
    severity: int = Field(default=5, ge=1, le=5)
    mode: str = "SIMULATION"


class PlanBody(BaseModel):
    max_iterations: int = Field(default=8, ge=0, le=16)


class ExecuteBody(BaseModel):
    mode: str = "SIMULATION"
    idempotency_key: str | None = None


class ModificationBody(BaseModel):
    entity_id: str
    capacity: int = Field(ge=0)


def _call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        raise HTTPException(
            status_code=409, detail={"code": type(exc).__name__, "message": str(exc)}
        ) from exc


@app.get("/api/health")
def health():
    return _call(service.health)


@app.get("/api/network")
def network():
    return _call(service.network)


@app.get("/api/history")
def history():
    return _call(service.history)


@app.post("/api/demo/reset")
def reset():
    return _call(service.reset)


@app.post("/api/incidents")
def trigger(body: TriggerBody):
    return _call(service.trigger, **body.model_dump())


@app.post("/api/incidents/{incident_id}/assess")
def assess(incident_id: str, max_depth: int = 6):
    return _call(service.assess, incident_id, max_depth)


@app.post("/api/incidents/{incident_id}/plans")
def plans(incident_id: str, body: PlanBody):
    return _call(lambda: service.plan(incident_id, body.max_iterations).model_dump(mode="json"))


@app.post("/api/plans/{plan_id}/execute")
def execute(plan_id: str, body: ExecuteBody):
    return _call(service.execute, plan_id, body.mode, body.idempotency_key)


@app.get("/api/runs/{run_id}/verify")
def verify(run_id: str):
    return _call(service.verify, run_id)


@app.post("/api/simulation/modify")
def modify(body: ModificationBody):
    version = _call(service.graph.set_capacity, body.entity_id, body.capacity)
    _call(service.erp.set_capacity, body.entity_id, body.capacity)
    return {"entity_id": body.entity_id, "capacity": body.capacity, "graph_version": version}


@app.get("/api/mcp-health")
def mcp_health():
    return {"endpoint": "/mcp", "transport": "streamable-http"}


app.mount("/mcp", mcp_app)
