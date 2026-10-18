# MCP tool reference

Transport: Streamable HTTP at `http://127.0.0.1:8765/mcp`; loopback binding by default. FastMCP validates tool schemas. Tools share the same `AnchorService` as the REST API.

| Tool | Inputs | Effect / output |
|---|---|---|
| `anchor_health` | none | Graph connection, mode, dataset, mock ERP readiness. |
| `anchor_network_summary` | none | Bounded graph counts, geography, node/edge records, provenance, recent incidents. |
| `anchor_trigger_incident` | scenario ID, entity ID, incident type, severity 1–5, mode | Adds synthetic incident and graph evidence link. Only `SIMULATION` is accepted. |
| `anchor_assess_cascade` | incident ID, depth 1–12 | FalkorDB downstream paths, dependent orders, upstream supplier evidence. |
| `anchor_find_recovery_plans` | incident ID, iteration bound 0–16 | CP-SAT plan, allocations, objective values, tested scenarios, residual demand. |
| `anchor_execute_recovery` | plan ID, mode, optional idempotency key | Applies local simulated allocations, stores receipts, validates read-back. Rejects stale graph versions. |
| `anchor_verify_recovery` | run ID | Reads the current mock ERP state. (Run-specific historical verification is a known limitation.) |
| `anchor_explain_decision` | plan ID | Plan objective and current graph cascade evidence. |
| `anchor_modify_simulation` | entity ID, nonnegative capacity, kind | Changes supplier capacity only; unsupported kinds fail. |
| `anchor_reset_demo` | none | Destructively reseeds only the named demo graph and local mock ERP. |

Inputs and outputs are structured; graph-dependent operations do not fall back to an in-memory topology. All execution is synthetic. No client compatibility is claimed until tool discovery is exercised in that client.
