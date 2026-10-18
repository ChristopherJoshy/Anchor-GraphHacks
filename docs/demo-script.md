# Silicon Cascade live demo checklist

**Full pitch, time-coded browser/CLI recording flow, exact Codex prompts, and judge Q&A:** [pitch-and-recording-guide.md](pitch-and-recording-guide.md). Target about three minutes; check any duration limit on the submission form.

## Setup before recording

Start Docker Desktop. From the repository root, run `docker compose up -d`, `uv sync --extra dev`, `npm --prefix web ci`, `uv run anchor reset`, and `uv run anchor doctor`. Confirm Node.js is 22.18 or newer. Start `uv run anchor serve` and `npm --prefix web run dev` in separate terminals. Check `codex mcp list`; if Anchor is absent, run `codex mcp add anchor --url http://127.0.0.1:8765/mcp` and restart Codex. Open `http://127.0.0.1:5173/` and launch Codex from the repository root. Only record if FalkorDB and the mock ERP are ready and Codex discovers Anchor's tools. Reset deletes the named synthetic graph and mock ERP state.

## Live sequence

1. **Hook, 0:00–0:12 — Recover orders:** “Two backups can be the same failure in disguise. Anchor follows the supply graph, changes the recovery plan, and checks whether the simulated operation actually took effect.” State that the data is synthetic.
2. **Agent action, 0:12–0:40 — Codex CLI:** Trigger the Taiwan foundry incident, assess impact, then request a recovery plan. Show the real MCP tool calls.
3. **Graph insight, 0:40–1:05 — Explore network:** Show the paths from backup B and C to the affected foundry and the affected order. Explain that this relationship changes supplier eligibility.
4. **Plan, 1:05–1:25 — Recover orders:** Show the computed allocation and bounded stress result. Fixture expectation: 350 inventory + 650 D, zero unmet, synthetic cost USD 5,850. Use live tool output if it differs.
5. **Execute, 1:25–1:55 — Codex, then Recover orders:** Inject one simulated reservation rejection and execute. Show the rejected receipt, one bounded replan, and ERP read-back verification.
6. **Adapt, 1:55–2:30 — Codex, then Recover orders:** Reduce D's capacity to 450, replan, execute, and verify. Fixture expectation: 350 inventory + 450 D + 200 E, zero unmet, synthetic cost USD 6,550. Show the actual result and new graph version.
7. **Proof and close, 2:30–2:55 — Activity & evidence:** Show persisted incident/action history and one supporting path. State that FalkorDB changes eligibility and all writes are confined to simulation. The graph-unavailable check is for judge Q&A; never fake a database outage in the video.

Use the web interface to make the operational story readable, and keep Codex visible for the real MCP interaction. Record genuine tool calls and current backend output; don't use fabricated terminal output or present an unexecuted action as complete. See the updated pitch guide for the recommended browser/CLI sequence and screen-recording setup. If Docker or graph integration has not been verified, record no success claim.
