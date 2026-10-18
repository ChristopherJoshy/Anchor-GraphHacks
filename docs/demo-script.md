# Silicon Cascade live demo checklist

**Full pitch, time-coded recording flow, exact Codex prompts, and judge Q&A:** [pitch-and-recording-guide.md](pitch-and-recording-guide.md). Aim for a concise recording and check any duration limit on the submission form.

## Setup before recording

Start Docker Compose, install the project, run `uv run anchor reset`, and start `uv run anchor serve`. Register Anchor in Codex using `codex mcp add anchor --url http://127.0.0.1:8765/mcp`. Run `codex mcp list` and `uv run anchor doctor`. Only record if FalkorDB is connected and the named tools are discoverable. The MCP reset tool deletes only the demo graph/ERP state.

## Live sequence

1. **Problem (20 sec):** “This fictional MCU order needs 1,000 units. The cheap backups share a failed foundry, so choosing by supplier price alone is unsafe.” State that the dataset is synthetic.
2. **Trigger and trace (40 sec):** Ask Codex to trigger the synthetic Taiwan foundry outage, assess the cascade, and show returned paths. Point to the path list and affected orders from FalkorDB.
3. **Plan and challenge (50 sec):** Ask for a constrained recovery and bounded follow-on failure test. The checked-in fixture comparison is 650 units unmet for the dependency-blind cheap proposal versus 350 inventory + 650 D, zero unmet, and USD 5,850 for the graph-aware plan. Show the actual allocation, objective, and number/result of tested scenarios. If a counterexample is returned, show its graph path; if none is found, say the declared set passed. Do not imply the flagship single-order run found a counterexample. Clarify that the finite stress set is not a guarantee.
4. **Execute and verify (40 sec):** Inject one supplier reservation rejection with `anchor_inject_simulated_failure`, then execute the plan. Show the rejected receipt, failed read-back, one bounded replan, successful receipt IDs, and SQLite ERP read-back. Do not describe it as a real-world order.
5. **Change conditions (40 sec):** Reduce `SUP-INDEPENDENT-D` to 450 capacity using `anchor_modify_simulation`, replan and execute. The expected fixture result is 350 inventory + 450 D + 200 E, zero unmet, and USD 6,550. Show the tool's actual output and explain the new plan from solver constraints, not a predetermined supplier choice.
6. **Graph dependence and history (30 sec):** Ask why the cheap backups were excluded, then ask “Show the latest Anchor recovery history.” Show the shared upstream path and the graph-backed incident, plan, action, and receipt records.
7. **Honest limit (15 sec):** Ask what happens if FalkorDB is down. Demonstrate/describe the explicit graph-unavailable response. If the database isn't actually down during recording, don't fake this operation.

The dashboard is optional. Record genuine tool calls and current backend output; don't use fabricated terminal output or present an unexecuted action as complete. If Docker or graph integration has not been verified, record no success claim.
