# Silicon Cascade live demo (3–4 minutes)

## Setup before recording

Start Docker Compose, install the project, run `uv run anchor reset`, and start `uv run anchor serve`. Register Anchor in Codex using `codex mcp add anchor --url http://127.0.0.1:8765/mcp`. Run `codex mcp list` and `uv run anchor doctor`. Only record if FalkorDB is connected and the named tools are discoverable. The MCP reset tool deletes only the demo graph/ERP state.

## Live sequence

1. **Problem (20 sec):** “This fictional MCU order needs 1,000 units. The cheap backups share a failed foundry, so choosing by supplier price alone is unsafe.” State that the dataset is synthetic.
2. **Trigger and trace (40 sec):** Ask Codex to trigger the synthetic Taiwan foundry outage, assess the cascade, and show returned paths. Point to the path list and affected orders from FalkorDB.
3. **Plan and challenge (50 sec):** Ask for a constrained recovery and bounded follow-on failure test. Show allocation quantities, remaining demand, tested scenario count, counterexample paths, and objective values. Clarify the finite stress set is not a guarantee.
4. **Execute and verify (40 sec):** Execute in simulation. Show receipt IDs and call verification to read back SQLite ERP state. Do not describe it as a real-world order.
5. **Change conditions (40 sec):** Reduce `SUP-INDEPENDENT-D` to 450 capacity using `anchor_modify_simulation`, replan and execute. Explain the new plan based on solver output, not a predetermined supplier choice.
6. **Graph dependence and history (30 sec):** Ask why the cheap backups were excluded, then ask “Show the latest Anchor recovery history.” Show the shared upstream path and the graph-backed incident, plan, action, and receipt records.
7. **Honest limit (15 sec):** Ask what happens if FalkorDB is down. Demonstrate/describe the explicit graph-unavailable response. If the database isn't actually down during recording, don't fake this operation.

The dashboard is optional. Record genuine tool calls and current backend output; don't use fabricated terminal output or present an unexecuted action as complete. If Docker or graph integration has not been verified, record no success claim.
