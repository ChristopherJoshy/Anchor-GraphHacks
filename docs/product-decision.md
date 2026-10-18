# Product decision: Anchor — graph-witnessed recovery under follow-on failures

**Decision date:** 18 October 2026
**Status:** Direction selected; the core local recovery flow, stress checks, changed-capacity replan, and MCP execution were exercised. Public demo video and participant review remain outstanding.

## Reliability correction from the CLI rehearsal — 18 October 2026

The rehearsal exposed three product defects and one runbook hazard. The seeded Taiwan foundry started with zero capacity, so the baseline was already disrupted. Triggering an outage recorded an incident but did not mutate the supplier or its supply edge. Decision explanations depended on the current service process instead of reloading a persisted plan. Finally, the rehearsal reused incident and plan IDs from a different graph state after reset; those IDs correctly no longer resolved.

The corrected fixture starts the foundry at 1,000 units of capacity and models its upstream component relationship. A supplier or facility outage now marks the affected entity and its outgoing supply/production edges unavailable with zero capacity. Recovery plans persist exclusion paths and objective currency/scale, and explanations reload plans from FalkorDB after service restart. The MCP execution tool exposes `max_replans=0` to stop on the first failure or `1` for the existing single bounded replan. Use only incident and plan IDs returned by the current graph state. The service was restarted and graph reset before the rehearsal below; the full test suite passed after these corrections.

The post-fix rehearsal reset the graph, confirmed the foundry at 1,000 units/available, then triggered incident `INC-92F196856B7F`. FalkorDB returned paths from Primary, Backup B, and Backup C to the failed foundry. The baseline solver allocated 350 inventory + 650 from D (USD 5,850; zero unmet; seven bounded cases passed), and ERP read-back verified run `RUN-9CB493F5AE1E`. After D was reduced to 450, graph version 3 produced 350 inventory + 450 D + 200 E (USD 6,550; zero unmet; seven bounded cases passed); read-back verified run `RUN-D5B156BCFF87`. The second run reused the still-active 350-unit inventory reservation and returned an idempotent `DUPLICATE` receipt for that allocation; verification confirmed the final 1,000-unit state.

For this rehearsal, health, reset, incident, cascade, plan, explanation, and verification calls used MCP; execution used the local single-attempt REST endpoint. The current Codex session retained its older MCP tool schema without `max_replans`, even after the server process was restarted. The source and automated schema test include that parameter. Restart Codex before recording, confirm the updated tool schema is visible, and run the execution step through MCP; do not describe this rehearsal as a complete MCP-only execution.

## Decision

Retain the supply-chain recovery concept and name it **Anchor**. Position it as **a recovery that is challenged by graph-derived follow-on failures before simulated execution**. FalkorDB must change source eligibility and expose the path witness; OR-Tools must compute a feasible allocation; the bounded stress set must return its tested cases and any counterexample; the policy gate permits only synthetic actions; and independent ERP read-back determines whether the action is verified.

The report is evidence about a finite declared scenario set. It is not a proof, an all-hazards guarantee, or a prediction of actual supplier reliability.

## Why this direction

Research confirms strong prior art for global supply-chain risk analysis (RiskWise), logistics routing and globe visualization (CHRONOS's Devpost page lists a Code With Gemini win), supplier sourcing/production generation (Banana Couture), procurement agents (Swerve), and graph-backed repair and verification (Blackbox and Hindsight in data operations; Interdict in security). Atrium's FalkorDB-sponsored first-place project is a useful graph-specific precedent: a relationship representing a student's misconception selects the intervention. A final-day scan also found FlowSherlock's workflow repair and Blast Radius's on-call actions, plus GraphDispatch's graph-driven dispatch and self-reported ablation. Therefore “AI supply-chain risk,” a globe, route changes, incident diagnosis, or detect/fix/verify by themselves are weak differentiation.

The product thesis is more testable than a generic risk dashboard: **a shared dependency discovered in FalkorDB changes which suppliers are eligible; a constrained optimizer produces a feasible allocation; a bounded, graph-derived second-hit suite challenges it; and a simulated action is accepted as verified only after ERP read-back.** The integration test changes a predefined dependency edge and verifies the plan changes. A separate optimizer test shows a path-bearing counterexample changing a scarce-source allocation across priority orders. The flagship single-order demo does not claim that it finds a counterexample that changes its allocation. Prior work on supply-chain network rewiring establishes the relevance of topology-sensitive resilience questions, while its metrics and findings cannot be imported as Anchor results.

## Updated pitch after winner review

**Anchor answers a question a supplier list cannot: will this recovery still work when the next connected source fails?** It follows shared upstream paths in FalkorDB, allocates inventory and qualified capacity under hard operational constraints, and evaluates the candidate against an explicit finite set of additional failures. Each reported exclusion and counterexample has graph evidence; each simulated action has an independently checked postcondition. When a material graph or capacity change affects eligibility or feasibility, the plan must change or report infeasibility.

The competitive point is the decision chain, not a new dashboard category: **graph path → eligibility/constraint change → computed allocation → bounded failure result → verified state mutation**. The README now shows the actual synthetic cost/shortfall comparison and clearly separates the flagship end-to-end run from the unit-tested counterexample behavior.

## Alternatives considered

| Direction | Evidence and assessment | Decision |
|---|---|---|
| Original SHOCKWAVE: general graph-backed supply-chain risk and immediate recovery | Relevant and useful, but overlaps known winners and public projects; insufficient as a distinct pitch by itself. | Retain domain, reject broad positioning. |
| Pivot to cybersecurity containment | Interdict publicly describes an advanced graph-based attack-path remediation and independent verification system; a new security entry would face direct overlap and abandon the supply-chain fixture. | Do not pivot. |
| Workflow repair or on-call incident response | FlowSherlock describes graph-based n8n contract diagnosis and remembered fixes; Blast Radius describes graph-root-cause analysis, paging, issue creation, and incident memory. Both self-identify as Graph Hacks entries; no official winner status is inferred. | Strong adjacent Track 01 work; keep Anchor focused on constrained supply recovery. |
| Emergency dispatch | GraphDispatch is a public Graph Hacks entry with a legible graph-based action, path explanations, and published synthetic evaluation. | Do not pivot. |
| Foodborne outbreak tracing | BatchZero publicly describes multi-agent evidence-backed supply-chain investigation. Useful adjacent precedent, but primarily investigation, not resilience allocation. | Do not pivot. |
| Citation/retraction audit | Bedrock's public dated write-up describes crisp path-based evidence and human-approved changes. Strong but not a better fit for the existing product direction. | Do not pivot. |
| Persistent graph memory/research or NPC social memory | Trace and Hearsay publicly demonstrate these themes and align naturally with Track 02. | Do not pivot from Track 01. |
| Anchor graph-witnessed recovery under follow-on failures | Keeps the useful existing concept but makes the graph's role a falsifiable decision: paths alter eligibility, constraints alter allocation, bounded graph-derived failures challenge the plan, and simulated execution requires read-back. A deterministic optimizer test supplies a failure scenario with an evidence path and confirms the counterexample can change a priority allocation. The flagship run separately demonstrates shared-dependency rejection, capacity-driven replanning, and a pass over its declared scenarios; it does not claim that this single-order run found a counterexample. Novelty remains a hypothesis against the incomplete public field. | Select. |

## Final-day public entrant check

The 18 Oct scan found self-described Track 01 entries for FlowSherlock (workflow contract diagnosis and remembered fixes) and Blast Radius (on-call root cause, paging, issue creation, and incident memory), alongside GraphDispatch's graph-based emergency routing and evaluation. Their published descriptions are meaningful adjacent competition, but are not official winner/finalist evidence and were not independently executed. The winner review adds three practical standards: let one graph relation alter the intervention (Atrium); bind action claims to evidence and independent read-back (Blackbox/Hindsight); and keep failures visible in evaluation rather than showing only a happy path (Blackbox). This evidence makes generic diagnosis and action less distinctive; it does not justify a last-minute domain pivot. The reviewed public set still leaves Anchor's strongest demonstrable distinction at the intersection of shared-supplier graph paths, integer allocation, bounded follow-on testing, and read-back-verified simulation. This conclusion is bounded to the pages reviewed; private and unindexed projects remain unknown.

## Internal concept score

Subjective pre-implementation design score (1–5), using the weights in the original brief. It is not judge scoring, implementation quality, or a win probability.

| Criterion | Weight | Broad original pitch | Anchor decision |
|---|---:|---:|---:|
| FalkorDB indispensability and multi-hop reasoning | 25% | 5 | 5 |
| Autonomous action and successful execution | 20% | 4 | 4 |
| Originality relative to reviewed work | 15% | 2 | 3 |
| Reliability and testability | 15% | 2 | 3 |
| Live demo clarity | 15% | 4 | 5 |
| User value/extensibility | 10% | 4 | 4 |
| **Weighted total / 5** | **100%** | **3.55** | **4.05** |

Score improvement reflects narrower, falsifiable framing and a stronger demo design only. It does not claim a working feature or higher empirical performance.

## Demo thesis and proof obligations

In The Silicon Cascade, two cheaper suppliers share an affected upstream facility. FalkorDB must return the relevant paths; the optimizer must reject or limit their usable capacity for graph-derived reasons. A separate feasible allocation uses 350 inventory units and 650 independent units for the baseline. Reducing the independent supplier to 450 must produce a computed allocation involving at least 200 units from another eligible source if fixture constraints permit. No supplier-selection conditional may encode these answers.

The stress feature must identify a bounded set of additional failure cases from graph topology, score the candidate under them, return a concrete worst counterexample when one exists, and re-optimize. Tests must establish the decision changes when a relevant dependency edge or capacity changes. A passed result must name the tested set and search bound. If no feasible plan exists, report the shortage and binding constraints.

## Revisit triggers

Change this decision only if implementation tests show the counterexample loop cannot be made deterministic and inspectable within the event window, or a verifiable official Graph Hacks result/public entry demonstrates the same core behavior and materially changes differentiation. Any revision must record evidence and consequences here; no pivot is justified by speculative competitor claims alone.
