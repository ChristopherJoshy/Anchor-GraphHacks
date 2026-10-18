# MCP tool reference

Transport: Streamable HTTP at `http://127.0.0.1:8765/mcp`; loopback binding by default. FastMCP validates tool schemas. Tools share the same `AnchorService` as the REST API.

| Tool | Inputs | Effect / output |
|---|---|---|
| `anchor_health` | none | Graph connection, mode, dataset, mock ERP readiness. |
| `anchor_history` | limit 1–100 (default 20) | Recent persisted incidents, plans, actions, and receipts, with a bounded count and summary. |
| `anchor_network_summary` | none | Bounded graph counts, geography, node/edge records, provenance, recent incidents. |
| `anchor_trigger_incident` | scenario ID, entity ID, incident type, severity 1–5, mode | Adds synthetic incident and graph evidence link. `SUPPLIER_OUTAGE` and `FACILITY_OUTAGE` set the target and its supply/production edge to unavailable with zero capacity. Only `SIMULATION` is accepted. |
| `anchor_assess_cascade` | incident ID, depth 1–12 | FalkorDB downstream paths, dependent orders, upstream supplier evidence. |
| `anchor_find_recovery_plans` | incident ID, iteration bound 0–16 | CP-SAT plan, allocations, graph-path exclusions, objective values with currency and minor-unit scale, tested scenarios, residual demand. Mixed currencies or scales fail clearly. |
| `anchor_inject_simulated_failure` | supplier ID | Rejects exactly one future reservation for that synthetic supplier; simulation fault-injection only. |
| `anchor_execute_recovery` | plan ID, mode, optional idempotency key, `max_replans` 0 or 1 (default 1) | Applies simulated allocations and reads state back. Set `max_replans=0` to stop after a failed action; the default permits one new graph-backed solve/execute attempt. Rejects stale graph versions. |
| `anchor_verify_recovery` | run ID | Reads the current mock ERP state. (Run-specific historical verification is a known limitation.) |
| `anchor_explain_decision` | plan ID | Persisted plan, explicit shared-dependency exclusion reasons and paths, cost currency/scale, and graph cascade evidence; works after backend restart while the graph record remains. |
| `anchor_modify_simulation` | entity ID, nonnegative capacity, kind | Changes supplier capacity only; unsupported kinds fail. |
| `anchor_modify_dependency` | supplier ID, upstream supplier ID, connected, mode | Connects or removes one synthetic supplier dependency in `SIMULATION`, rejects unknown endpoints and cycles, and bumps the graph version so existing plans become stale. |
| `anchor_reset_demo` | none | Destructively reseeds only the named demo graph and local mock ERP. |

Inputs and outputs are structured; graph-dependent operations do not fall back to an in-memory topology. All execution is synthetic. Codex CLI 0.163.0 was registered and exercised against this local Streamable HTTP server. Claude Code and OpenCode have not been tested.
