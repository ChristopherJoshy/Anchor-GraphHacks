# Anchor service contract

The browser and MCP server call the same `AnchorService`; the browser does not maintain an independent operational graph.

## Local HTTP

- `GET /api/health`: graph, ERP, mode, and dataset readiness.
- `GET /api/network`: bounded entities, relationships, and scenario locations for display.
- `GET /api/history`: persisted incidents, plans, actions, and verification records.
- `POST /api/demo/reset`: restore deterministic synthetic graph and ERP state.
- `POST /api/incidents`: `{scenario_id, entity_id, incident_type, severity, mode}`.
- `POST /api/incidents/{incident_id}/assess`: `{max_depth, include_paths}`.
- `POST /api/incidents/{incident_id}/plans`: `{max_plans}`.
- `POST /api/plans/{plan_id}/execute`: `{mode, idempotency_key}`.
- `GET /api/runs/{run_id}/verify`: independently read back ERP state.
- `POST /api/simulation/modify`: allowlisted capacity, inventory, route, or order-priority change.

Responses are JSON, include stable IDs and explicit status, and return an error object `{code, message}` on failure. Services bind to loopback by default. Graph-dependent routes fail when FalkorDB is unavailable.
