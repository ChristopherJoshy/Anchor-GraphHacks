# Anchor pitch and recording guide

**For:** Team Nexus · Graph Hacks 2026 · Track 01 — Agents That Act on Connected Data
**Checked:** 18 October 2026. The official rules require a video showing the working project and do not state a duration. Check the submission form once more before upload.

## The pitch

### One sentence

**Anchor finds when apparent backup suppliers share the same upstream failure, computes a feasible recovery from the connected graph, executes it in a local simulation, and verifies the result.**

### 30-second version

> A supplier outage is dangerous when the backups depend on the same failed source. Anchor is a graph-native recovery agent for supply networks: Codex asks it to investigate, FalkorDB traces the multi-hop dependencies, and a deterministic OR-Tools solver calculates a feasible allocation. Anchor can execute that allocation in a persistent mock ERP, verify the changed state, and replan after a simulated failure or capacity change. Our Silicon Cascade demo is synthetic, but the graph paths, constraints, receipts, and read-back checks are real parts of the running system.

### 60-second version

> A supplier can fail, and the replacement can fail for the same reason. A flat supplier list sees two backups; a dependency graph can reveal that both rely on the same upstream factory.
>
> Anchor gives a coding agent operational context and bounded tools to act on it. In our synthetic Silicon Cascade, a Taiwan foundry outage threatens a 1,000-unit microcontroller order. FalkorDB exposes the shared upstream paths for two apparently independent backups. The graph affects which supply is eligible; OR-Tools then solves the allocation under capacity and order constraints.
>
> Anchor executes only in simulation. It changes persistent mock ERP records, stores receipts, reads the state back, and can replan after an injected reservation rejection or a capacity change. It also evaluates a finite, declared set of follow-on failures. The result is an auditable recovery workflow, not a promise that every future disruption is covered.

### What the audience should remember

1. **The graph changes the decision:** backups B and C both reach the failed Taiwan foundry, so their nominal capacity is not treated as independent supply.
2. **The agent acts and checks:** the solver produces allocations; the local ERP changes; Anchor checks persisted state rather than trusting a success-shaped response.
3. **The claim is bounded:** synthetic fixture, simulation-only writes, finite stress cases, and no claim of universal resilience or live supply-chain visibility.

## The problem, user, and value

**Problem:** During a disruption, procurement or continuity teams must quickly determine what depends on the failed entity, which replacements are actually independent, how much can arrive before the deadline, and whether the proposed change took effect. Supplier names and isolated inventory rows do not reveal shared upstream exposure.

**Primary user:** A manufacturing procurement or operational-continuity planner deciding how to protect an order when a supplier, facility, or modeled dependency becomes unavailable.

**Demonstrated use case:** Recover the synthetic 1,000-unit microcontroller order after the Taiwan foundry incident. The fixture has 350 inventory units, independent supplier D at 650 units, and independent supplier E as a more expensive fallback. B and C share the failed upstream source.

**Why it is useful:** Anchor joins impact tracing to constrained allocation and verified action. It can distinguish a nominally cheap proposal from supply that remains feasible after graph relationships and capacities are considered. A human can inspect the paths, constraints, costs, receipts, and remaining shortfall.

**Other plausible applications (not implemented integrations):** multi-tier component sourcing, supplier-continuity planning, inventory contingency analysis, and other dependency networks such as cloud services or energy infrastructure. The current end-to-end implementation is the synthetic manufacturing scenario; do not describe these adjacent domains as supported products today.

## What is actually running

- **Codex CLI** supplies natural-language interaction and invokes Anchor's MCP tools.
- **FalkorDB** stores the synthetic topology, incidents, evidence, graph versions, plans, and action history. Cypher traversals expose the shared upstream paths and influence source eligibility. Graph-dependent operations do not silently switch to an in-memory network.
- **Python + OR-Tools CP-SAT** calculate integer allocations from graph-resolved sources, capacities, eligibility, and order demand. The LLM does not invent stock or choose the arithmetic result.
- **SQLite mock ERP** is the local simulation adapter. It persists reservations and order status, supports idempotency, and can inject one reservation rejection.
- **Read-back verification** compares the requested allocation with ERP state and the order state; receipts and outcomes are recorded against graph history.
- **Bounded stress evaluation** tests the plan against the fixture's declared graph-linked failure scenarios. A pass means only that those tested cases passed.

All suppliers, contracts, stock, prices, orders, and incidents in the demonstration are synthetic. Anchor does not contact real procurement, payment, production, or logistics services.

## Recommended format: a product-led recording, no PowerPoint

Record Anchor working, not a slide presentation. Use the **web interface as the visual guide** for a non-coder, and show **Codex CLI making the real MCP calls** so judges can see the agent act. Switch between the two full-size windows as the story advances; avoid a cramped split-screen. The browser reads the same backend state, so it makes the graph paths and verified outcome easier to follow after Codex changes them.

The current interface has three views. Use them intentionally:

- **Recover orders:** orient the viewer with the 1,000-unit order, what is at risk, the proposed or completed allocation, and whether ERP read-back verified it.
- **Explore network:** show the Taiwan foundry and the graph paths that expose the two apparent backups. Use the layers control and select a supplier/path when needed; say the business relationships and operational data are synthetic, while the locations are geographic references.
- **Activity & evidence:** close on the persisted incident, plan, actions, receipts, and evidence history.

The official rules require a working-project video, a public repository, graph-model/Cypher documentation, and either a live deployment or complete local setup instructions. They do **not** require a PowerPoint or specify a video duration. Devpost's recording guidance favors a quick story, a scripted demonstration of the working product, clear audio, and a concise close. Target **about 3 minutes**; allow up to **3:30** if real tool responses take longer and the submission form permits it. A short opening caption is fine; don't build a deck for the video. If a separate live presentation requires slides, use at most three: problem, graph path changing the plan, verified result and limits.

## Recording runbook

### Before recording

Start Docker Desktop and confirm its engine is running. From the repository root, prepare the services. Run `uv run anchor serve` in its own terminal and leave it running; start the web app and a fresh Codex session in separate windows.

~~~powershell
docker compose up -d
uv sync --extra dev
npm --prefix web ci
uv run anchor reset
uv run anchor doctor
~~~

In a separate terminal:

~~~powershell
uv run anchor serve
~~~

In another terminal:

~~~powershell
npm --prefix web run dev
~~~

The web app requires Node.js 22.18 or newer (`node --version`); the currently verified machine has Node 26.7.0. Open `http://127.0.0.1:5173/`, then open Codex from the repository root. Increase the terminal font until tool names and key returned fields are readable. Keep the browser at a size where the three named views and order-status labels are easy to read. If NASA or OpenStreetMap tiles are slow or unavailable, the app still has its bundled overview layer; don't hold the recording hostage to optional basemap detail.

The reset replaces only the named synthetic demo graph and local mock ERP state. It is destructive to the current demo session, so run it before rehearsal or a clean take, not midway through recording.

In another terminal, check the Codex registration:

~~~powershell
codex mcp list
~~~

Anchor has already been registered in the verified local setup. If **anchor** is absent, add it once, then restart Codex so its tool list refreshes:

~~~powershell
codex mcp add anchor --url http://127.0.0.1:8765/mcp
~~~

Start a fresh Codex CLI session from the repository. Confirm **anchor_health** reports **ready: true**, FalkorDB **connected**, **SIMULATION**, and ERP **ready**. Do not record if graph readiness fails or Codex cannot discover the Anchor tools. The Codex command follows current OpenAI documentation; local client setup is also in [installation.md](installation.md).

### Record this sequence

Use one real Codex session and the running web app against the same local services. Let Codex make the changes through MCP; use the browser to make the graph evidence and resulting order state legible. Switch windows only after a tool call completes. Do not paste fabricated output or edit a failed attempt into a success.

| Time | On screen | Say / do |
|---|---|---|
| 0:00–0:12 | **Recover orders**, clean opening state | **Say:** “Two backups can be the same failure in disguise. Anchor follows the supply graph, changes the recovery plan, and checks whether the simulated operation actually took effect.” Add: “This network is synthetic.” |
| 0:12–0:40 | Codex CLI | Send the trigger-and-trace prompt, then the solve-and-stress-check prompt. Let Anchor create the incident, assess the cascade, and calculate the plan. Keep MCP tool names/results visible long enough to establish that Codex is acting through Anchor. |
| 0:40–1:05 | **Explore network** | Point out the multi-hop paths from backup B and C to **SUP-TAIWAN-FOUNDRY**, then the affected order. Say: “The graph exposes that both cheaper backups share this failed upstream source.” |
| 1:05–1:25 | **Recover orders** | Show the live plan: 350 inventory + 650 D, 1,000 total, zero unmet, synthetic cost USD 5,850, and the bounded stress result. State that this is the fixture's computed output, not a real-world price or guarantee. |
| 1:25–1:55 | Codex CLI, then **Recover orders** | Inject one simulated reservation rejection and execute. Show the rejected receipt and one bounded replan in Codex; switch to Recover orders to show ERP read-back and the verified state. |
| 1:55–2:30 | Codex CLI, then **Recover orders** | Reduce D's capacity to 450, replan, execute, and verify. Show the recalculated 350 inventory + 450 D + 200 E allocation and USD 6,550 fixture cost, if the live result matches. The graph-version change makes clear this is a new plan. |
| 2:30–2:55 | **Activity & evidence**, then finish | Show the persisted incident/action history and one evidence path. Close: “FalkorDB supplies the relationships that change eligibility; the solver allocates; Anchor executes only in simulation and verifies by reading the ERP back.” |

If the live tool calls take the full 3:30, keep the spoken explanation calm and cut pauses between completed actions. Don't speed up the audio or remove a failure/outcome in a way that changes what happened.

### Copyable Codex prompts

**1. Trigger and trace**

~~~text
Use Anchor's SIMULATION tools only. Trigger a severity-5 SUPPLIER_OUTAGE for scenario SCENARIO-SILICON-CASCADE at SUP-TAIWAN-FOUNDRY. Then assess the cascade. Show the affected ORDER-SILICON-1000 and the exact shared-dependency paths for SUP-BACKUP-B and SUP-BACKUP-C. Separate returned graph facts from your explanation.
~~~

Expected tools: **anchor_trigger_incident**, then **anchor_assess_cascade**. Show the returned incident ID, path evidence, and affected order rather than narrating a guessed result.

**2. Solve and stress-check**

~~~text
Using that incident ID, find recovery plans. Show the actual source allocations, unmet quantity, objective cost, graph version, and the count and results of the bounded failure scenarios. Explain why SUP-BACKUP-B and SUP-BACKUP-C do or do not qualify, with their graph paths. Do not call the tested set a guarantee.
~~~

Expected tool: **anchor_find_recovery_plans**. The checked-in baseline computes 350 inventory + 650 from independent D, zero unmet, synthetic cost USD 5,850. The benchmark's dependency-blind proposal uses 350 inventory + 600 B + 50 C, but both suppliers are graph-exposed to the failed foundry; after eligibility is enforced that proposal leaves 650 units unmet. These are deterministic fixture outputs, not real-world prices or savings. Report what the live tool returns if it differs.

**3. Execute through a real simulated rejection**

~~~text
Inject one simulated reservation rejection for SUP-INDEPENDENT-D. Then execute the selected plan in SIMULATION. Show the failed attempt's returned verified=false, rejected receipt, and one bounded replan. Call anchor_verify_recovery for the successful run ID and confirm the persisted allocations and order status from the mock ERP.
~~~

Expected tools: **anchor_inject_simulated_failure**, **anchor_execute_recovery**, and **anchor_verify_recovery**. The integration fixture expects one rejected attempt followed by one successful replan. Show the actual receipt and verification response. This is a local simulation, not a purchase order.

**4. Change the constraint and adapt**

~~~text
Change SUP-INDEPENDENT-D's synthetic supplier capacity to 450 with anchor_modify_simulation. Recalculate a plan for the same incident, then execute and verify the new plan in SIMULATION. Show the graph version change and compare the actual before/after allocations and costs.
~~~

Expected tools: **anchor_modify_simulation**, **anchor_find_recovery_plans**, **anchor_execute_recovery**, and **anchor_verify_recovery**. The fixture computes 350 inventory + 450 D + 200 independent E, zero unmet, synthetic cost USD 6,550. The changed plan invalidates the old graph-version snapshot. Do not reset between this prompt and the previous one; the service handles replacing changed demo reservations when executing the replan.

**5. Explain and retrieve memory**

~~~text
Explain why the two cheaper backup suppliers were rejected using their stored graph evidence paths. Then retrieve the latest Anchor history and summarize the incident, plans, actions, receipts, and verified outcome. Label every result as simulated.
~~~

Expected tools: **anchor_explain_decision** and **anchor_history**. Point out that the decision history is in FalkorDB, not only in the current conversation.

### Spoken close

> The important result is not a map or a warning. The graph exposed a shared failure, that changed the feasible allocation, Anchor executed the simulated recovery, and the ERP read-back verified it. When we reduced D's capacity, the solver changed the plan. These are synthetic operations and a finite stress set, but the graph, optimizer, state changes, and verification are running code.

## What the baseline numbers mean

| Scenario | Allocation or proposal | Unmet units | Synthetic incremental cost |
|---|---|---:|---:|
| No supplier intervention | 350 inventory | 650 | USD 0 |
| Dependency-blind nominal proposal | 350 inventory + 600 B + 50 C; B and C share the failed foundry | 650 after graph qualification | USD 2,220 nominal |
| Graph-eligible baseline recovery | 350 inventory + 650 D | 0 | USD 5,850 |
| D reduced to 450 | 350 inventory + 450 D + 200 E | 0 | USD 6,550 |

These values are from the checked-in deterministic synthetic benchmark. The cost comparison is not a measured real-world benefit claim. Explain that graph-aware recovery costs more than the paper-cheap but infeasible proposal because B and C's exposure removes their capacity from eligible recovery. See [benchmark-results.md](benchmark-results.md) for assumptions and methodology.

## Recording and delivery checklist

- Use OBS if it is already available, or another screen recorder you already know. Capture the desktop at 1920×1080 if available and record your microphone. Keep the browser and Codex full-size in turns; don't shrink both into unreadable panels.
- Before recording, set browser zoom and terminal text large enough that a judge can read the order, allocations, tool names, receipt status, and verification status in the exported video.
- Use a clear microphone in a quiet room. Narrate the consequence and result, not every line of JSON. Avoid background music.
- Close notifications, unrelated windows, and anything that could expose credentials or personal data. Keep only the needed browser, terminals, and Codex session visible.
- Rehearse the transitions once, reset the named demo, and record the real sequence. Light trimming of pauses is fine; preserve the order and outcomes of actions. If a real action fails differently from the expected fixture, show that result or make a fresh clean run—never edit failure into success.
- Play the exported video from beginning to end. Check audio, readable output, duration, and that every claim matches the footage and current code.
- Upload to the platform accepted by the submission form. Set access so judges can open it without signing into your personal account; test the link in a private browser window.
- If the form accepts screenshots, add one genuine frame showing the shared-dependency evidence and one showing the verified post-action state. Do not create a slide deck in place of these screenshots or the demo.
- Keep a separate live-demo fallback: **uv run anchor doctor**, the **anchor_health** MCP call, and the baseline prompts. If a component fails, say so; never splice a successful run from another state into a failure run.

## Likely judge questions

**Why is FalkorDB essential?** The dependency paths from backup suppliers through shared upstream suppliers to the failed foundry are queried from FalkorDB. Those paths affect eligible capacity and the resulting plan. Graph-dependent operations fail when FalkorDB is unavailable; the application does not maintain a duplicate in-memory topology.

**What does the language model decide?** Codex interprets the request and selects MCP tools. The graph query returns connected facts, and deterministic application code plus OR-Tools calculates the allocation. The model is not the source of stock, prices, capacity, receipt status, or arithmetic.

**Does Anchor place real orders?** No. This build only changes a persistent local SQLite mock ERP in **SIMULATION** mode. There is no production procurement or payment connection.

**Does a passing stress test prove resilience?** No. It means the computed plan passed the finite, declared synthetic scenarios evaluated for that run. It cannot cover unmodeled failures or prove real-world performance.

**Is verification a historical snapshot for every retry?** No. The execution response includes each attempt's verification result, and the final run can be read back with anchor_verify_recovery. That tool reads current ERP state; do not present a later read as a time-frozen snapshot of an earlier failed run.

**Are these real suppliers and prices?** No. Supplier relationships, capacities, contracts, inventory, orders, and prices are synthetic. Geographic labels are for the demo network and do not assert real commercial relationships.

**What happens if FalkorDB is removed?** Anchor cannot produce graph-dependent cascade paths, source eligibility, stress scenarios, or evidence explanations; it reports the dependency failure instead of making a flat-table guess.

**What is the next real-world step?** A domain owner would connect a permissioned, validated supply graph and a read-only operational source first, then add an approval-gated adapter for a sandbox ERP. That integration is future work, not part of this demo.

## Submission and team guardrails

- Name **Track 01 — Agents That Act on Connected Data** in the submission.
- The official rules require a **public source-code repository**. The canonical GitHub repository is currently private by Team Nexus's choice. That privacy setting conflicts with the public-repository requirement; this guide does not change it. Resolve visibility deliberately before submission and do not submit until the required links are accessible.
- Include the README's graph model and the Cypher queries/algorithms on which Anchor depends. Disclose AI assistance and have the participant personally review and explain the work.
- No demo video has been recorded or uploaded by this document. Do not describe it as completed until the genuine recording and accessible link exist.
- The official deadline is **18 October 2026, 11:59 PM IST**. Reserve time for the repository-visibility decision, recording, playback check, upload, and submission-form review; Devpost's participant guidance recommends leaving the final two to three hours for recording and submission work.

## Research behind this format

This is a synthesis of official event requirements, winner artifacts, and published judge/participant guidance—not a claim that the same format guarantees a win.

| Evidence | What it suggests for Anchor |
|---|---|
| [Graph Hacks official rules](https://www.wemakedevs.org/hackathons/falkordb/rules) require FalkorDB to be central, a public repository, graph/Cypher documentation, a working-project video, and a live deployment or complete local setup. | Demonstrate the graph changing an action; explicitly state the Track 01 fit; make setup and evidence easy to review. |
| Microsoft's [2025 AI Agents Hackathon winners](https://microsoft.github.io/AI_Agents_Hackathon/winners/) name RiskWise Best Overall; the [official submission issue](https://github.com/microsoft/AI_Agents_Hackathon/issues/526) describes explainable risk analysis and links its project video. | Supply-chain analysis, maps, and risk reporting are already compelling. Anchor's short demo must make the distinct step—graph-constrained recovery plus verified simulated mutation—visible early. The video is linked in the entry; this guide does not claim a frame-by-frame review of that recording. |
| DataHub's [2026 winner announcement](https://datahub.com/blog/meet-the-winners-of-build-with-datahub-the-agent-hackathon/) and [Project Blackbox entry](https://devpost.com/software/project-blackbox) describe a grand-prize agent that starts from a concrete symptom, follows lineage, gates action on evidence, repairs, verifies, writes history back, and includes failure-oriented evaluation. | Use one concrete outage; show path evidence before selecting an action; show the failed reservation and verified replan; disclose the bounded stress envelope. |
| FalkorDB's [Memory Meets Motion winner write-up](https://www.falkordb.com/blog/memory-meets-motion-the-falkordb-standouts/) describes Atrium using a student's misconception node to choose a different teaching intervention. | Make a graph relationship visibly change what the system does; don't spend the core demo on a graph visualization alone. |
| Devpost's [demo-video guidance](https://info.devpost.com/blog/6-tips-for-making-a-hackathon-demo-video) recommends an early script, clear opening, app-in-use demo, concise technical detail, good audio, and checking video accessibility; it says many hackathon demos are around/under three minutes but urges entrants to follow their own event's limit. | Script the sequence, show the working product, target roughly three minutes, and verify the final video link. Graph Hacks has no duration cap on the rules page checked. |
| Devpost's [demo presentation advice](https://info.devpost.com/blog/how-to-present-a-successful-hackathon-demo) recommends a brief problem setup, working-project interaction, then a concise impact close. Its [judge interviews](https://info.devpost.com/blog/hackathon-judging-tips) say some judges watch the video for context before testing and that story, technical evidence, and criteria fit work together. | Put the graph insight and visible result before architecture detail; keep the walkthrough reproducible and the code/README aligned with the video. |
| OpenAI's [Codex MCP setup documentation](https://developers.openai.com/resources/docs-mcp) documents **codex mcp add <name> --url <url>** and **codex mcp list**. | Use the already-tested local Streamable HTTP registration, verify it, and restart Codex if tool discovery is stale. |

## Suggested Devpost project summary

**Anchor — Find the shared failure. Recover. Test what breaks next.**

Anchor is a FalkorDB-backed recovery agent for connected supply networks. When a supplier fails, Anchor follows multi-hop dependency paths to find apparently independent backups that share the same upstream exposure. A deterministic OR-Tools solver computes feasible allocations; a local simulation adapter applies them; and read-back verification checks the persisted outcome. Anchor then tests a bounded set of modeled follow-on failures and recalculates after network constraints change.

The Silicon Cascade demonstration uses a fully synthetic 1,000-unit microcontroller order. It shows shared-dependency evidence, recovery planning, an injected reservation rejection, bounded replanning, persistent simulated execution, and independent verification. FalkorDB is load-bearing: graph paths affect source eligibility and Anchor's graph-dependent operations fail clearly without it. All operational data and costs are synthetic; no real orders are placed, and finite stress results are not a guarantee.
