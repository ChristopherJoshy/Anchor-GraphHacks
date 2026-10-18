# Product decision: Anchor — counterexample-driven recovery under attack

**Decision date:** 18 October 2026
**Status:** Direction selected; the core local recovery flow, stress checks, changed-capacity replan, and MCP execution were exercised. Public demo video and participant review remain outstanding.

## Decision

Retain the supply-chain recovery concept and name it **Anchor**. Center the product on **bounded counterexample-driven follow-on failure testing**: a feasible recovery plan is challenged with additional failures derived from shared dependencies in FalkorDB; when a tested failure breaks the candidate, Anchor exposes the path and asks the optimizer to account for it. Execute only inside the synthetic mock ERP and independently read back outcomes.

The report is evidence about a finite declared scenario set. It is not a proof, an all-hazards guarantee, or a prediction of actual supplier reliability.

## Why this direction

Research confirms strong prior art for global supply-chain risk analysis (RiskWise), visualized autonomous logistics routing (CHRONOS entrant-reported award), procurement agents (Swerve), graph-backed recovery and verification (Blackbox in data operations; Interdict in security), and dependency investigation (BatchZero and other public Graph Hacks entries). A final-day scan also found FlowSherlock's workflow repair and Blast Radius's on-call actions, plus GraphDispatch's graph-driven dispatch and self-reported ablation. Therefore “AI supply-chain risk,” a globe, route changes, incident diagnosis, or detect/fix/verify by themselves are weak differentiation.

The product thesis is more testable than a generic risk dashboard: **a shared dependency discovered in FalkorDB changes which suppliers are eligible; a constrained optimizer produces a feasible allocation, stress-tests bounded follow-on failures, and records a verified simulated action.** A separate optimizer test shows how a path-bearing counterexample can change an allocation across priority orders. Prior work on supply-chain network rewiring establishes the relevance of topology-sensitive resilience questions, while its metrics and findings cannot be imported as Anchor results.

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
| Anchor counterexample-driven recovery | Keeps the useful existing concept but adds graph-sensitive eligibility, constrained supplier allocation, bounded follow-on recourse, and independently checked synthetic execution. A deterministic optimizer test supplies a failure scenario with an evidence path and confirms the counterexample can change a priority allocation. The flagship run separately demonstrates shared-dependency rejection, a capacity-driven replan, and a stress pass over its declared scenarios; it does not claim that this single-order run found a counterexample. Novelty remains a hypothesis against the incomplete public field. | Select. |

## Final-day public entrant check

The 18 Oct scan found self-described Track 01 entries for FlowSherlock (workflow contract diagnosis and remembered fixes) and Blast Radius (on-call root cause, paging, issue creation, and incident memory), alongside GraphDispatch's graph-based emergency routing and evaluation. Their published descriptions are meaningful adjacent competition, but are not official winner/finalist evidence and were not independently executed. This evidence makes generic diagnosis and action less distinctive; it does not justify a last-minute domain pivot. The reviewed public set still leaves Anchor's strongest demonstrable distinction at the intersection of shared-supplier graph paths, integer allocation, bounded recourse, and read-back-verified simulation. This conclusion is bounded to the pages reviewed; private and unindexed projects remain unknown.

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
