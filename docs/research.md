# Research and competitive assessment

**Research checked:** 18 October 2026 (IST). Web pages and repositories can change after this snapshot. Publication dates below are taken from the source where stated; where a page does not expose a date in the accessible view, it is marked “date not stated.”

## Executive finding

Keep Anchor, but distinguish it through **counterexample-driven, bounded follow-on failure testing that changes the chosen recovery**, with simulation-only execution and read-back verification. Supply-chain risk analysis and agentic recovery already have strong precedents. A graph, a globe, or “detect → repair → verify” alone is not a defensible novelty claim. Anchor's claim should be narrower: a shared-dependency-aware recovery is stress-tested against declared additional failures; discovered counterexamples are exposed as graph paths and feed re-optimization; then only simulated actions are executed and independently read back.

This is a product positioning decision based on public material, not an estimate of win probability. Private submissions and unpublished implementations cannot be compared.

## Official Graph Hacks requirements

The [official rules](https://www.wemakedevs.org/hackathons/falkordb/rules) and [event/track page](https://www.wemakedevs.org/hackathons/falkordb) were checked on 18 Oct 2026. They say FalkorDB must be the primary graph database and do central work; the project must use permitted public, synthetic, or team-owned data; the main coding/design work must start after the event begins; and submissions require a public repository, README with setup and graph model, key Cypher/graph algorithms, demo video, deployment or complete local setup, and track designation. AI assistance is allowed but must be disclosed, and participants must understand and explain the work. The official Track 01 focus includes multi-hop reasoning, graph queries/algorithms as agent tools, MCP tool selection, actions based on graph evidence, and explainability.

The schedule on the event page gives Oct 15, 12:01 AM through Oct 18, 11:59 PM IST. The page is live and may be updated; verify before submission. This document does not assert that Anchor has been submitted.

## Winner and adjacent-project review

### RiskWise — Microsoft AI Agents Hackathon 2025

Microsoft's [official winners page](https://microsoft.github.io/AI_Agents_Hackathon/winners/) names RiskWise “Best Overall Winner” and describes a supply-chain risk analysis system; it reports 570 submissions and lists Python, React/Next.js, Azure AI Agent Service, Semantic Kernel, and SQL. Page text does not supply a clearly visible original publication date in the fetched copy; checked 18 Oct 2026. This verifies the award and broad theme, not every inferred implementation detail on the page. The same area is already competitive, so Anchor must not sell ordinary supply-chain risk analysis as novel.

### Project Blackbox — DataHub Agent Hackathon 2026

DataHub's [winner announcement](https://datahub.com/blog/meet-the-winners-of-build-with-datahub-the-agent-hackathon/) prints the date `09.10.26`; the page does not clarify whether that means 9 October or 10 September. It names Project Blackbox Grand Prize. The account describes lineage-based incident investigation, evidence gates, code repair, invariant tests, a human-reviewed pull request, writeback, evaluation including failures, and an ablation with DataHub disabled. It is a different data platform/domain, but a useful standard for evidence-gated action and testing graph/context contribution. It establishes that autonomous repair plus verification is not by itself a unique product promise.

### Memory Meets Motion — FalkorDB, Atrium, and Hopper

FalkorDB's recap, [“Memory Meets Motion: The FalkorDB Standouts”](https://www.falkordb.com/blog/memory-meets-motion-the-falkordb-standouts/), was published and updated 18 Aug 2026; the event was held 3 Aug 2026. The sponsor recap calls Atrium first place overall and explains its graph-native distinction: representing individual misconceptions as nodes, so interventions follow the underlying misconception rather than an aggregate score. It also describes Hopper: Adaptive Distribution Network, a separate supply-chain simulator with agents negotiating cost versus urgency and writing decisions to FalkorDB. Because the evidence is the sponsor's own recap, use it as a published event/winner account, not as an independent evaluation of its claims. Lesson: a relationship must alter the intervention, and history should be made queryable.

### Neo4j Aura Agent Hackathon 2026

The Neo4j community manager's [winner announcement](https://community.neo4j.com/t/aura-agent-hackathon-winners-announced/79568) is dated 23 Jun 2026 and reports 40 submissions. It names ConspiracyGraph Agent first, RegulatoryRisk GraphAgent second, and Korca Triage Agent third. The winner post highlights a graph connecting claims, narratives, entities, sources, and evidence to uncover otherwise hidden links. This supports a demo where the graph reveals a consequential relationship, rather than merely displaying stored nodes.

### Hack the Video Agent Context Graph

Neo4j's [event recap](https://neo4j.com/blog/developer/one-starter-repo-three-winners-neo4j-at-the-hack-the-video-agent-context-graph/) (published 2 Aug 2026 according to Neo4j community listing) describes MealPrep Video Context Graph in first place, Rehearsal second, and ZooVision third. It emphasizes task-specific graph relationships and an on-stage, actual-use demonstration. The recap says Rehearsal's weaknesses link to timestamped example clips; that is a useful demo lesson: make evidence and action visible in the moment. It is a Neo4j-hosted recap, not an independent judging audit.

### Other relevant public winners/projects

- [CHRONOS, Devpost](https://devpost.com/software/chronos-i5kwq9), page checked 18 Oct 2026 (page's project update says started 11 May 2026; exact award date not stated in the retrieved page), self-reports winning “Best Use of Gemini” at Code With Gemini. It describes autonomous logistics routing, a planner/critic loop, and a globe. Treat the award as a Devpost entrant claim unless independently confirmed. A globe and replanning alone are not Anchor's differentiator.
- [Swerve, Devpost](https://devpost.com/software/swerve-gqmenk), page checked 18 Oct 2026, identifies itself as submitted to Caltech Hacktech 2025 and lists the Dryft Challenge Prize; the project describes a procurement assistant. It does not establish that procurement agents are novel or that its award was the event's overall win.
- The user-listed **Interdict**, **GraphDispatch**, **BatchZero**, **Bedrock**, **Trace**, and **Hearsay** were inspected as public project pages/repositories or a public project write-up on 18 Oct 2026. Their pages identify themselves with Graph Hacks 2026 or describe that event. Public visibility and self-identification do **not** establish official finalist or winner status. At the research snapshot, no official Graph Hacks winner announcement had been found; therefore none is called a winner here.

| Public entry checked | What its public materials describe | Research status and relevance |
|---|---|---|
| [Interdict](https://github.com/YashSoni998265/interdict) | FalkorDB-backed security attack-path analysis, constrained least-disruptive containment, independent path checking, simulation certificate and counterexample-style replanning. | Public, substantial active-looking repository (27 commits visible at check), self-identifies as Graph Hacks 2026 Track 01. No winner status known. Closest execution/evidence competitor; Anchor must be distinctive through supply-chain recourse and resilience stress tests, not generic “verify a fix.” |
| [GraphDispatch](https://github.com/aggarmoksh/GraphDispatch) | FalkorDB road/unit/hospital dispatch with address memory, graph-derived routing and decisions; its README reports a synthetic evaluation against alternatives. | Public repository (17 commits visible), self-identifies as built for Graph Hacks. No winner status known. Direct action and clear live decision are strong demo lessons. Its reported measurements are the entrant's claims, not independently audited here. |
| [BatchZero](https://github.com/ionfwsrijan/BatchZero) | Four role-scoped MCP agents trace a foodborne outbreak through supply-chain paths and attach evidence to hypotheses. | Public repository (12 commits visible), described as an outbreak source-investigation agent. No winner status known. Strong overlap in supply-chain traversal/evidence; Anchor must foreground computed resilience interventions, not just tracing. |
| [Bedrock](https://github.com/ibnweb3/bedrock) and [author's public write-up](https://dev.to/ibnweb3/the-retraction-two-citations-back-building-a-citation-path-audit-on-falkordb-3cjk) | Citation paths from user-supplied papers to retracted research; public write-up dated 17 Oct 2026 says it uses FalkorDB and proposes, but does not apply, edits. | The repository URL is linked from the write-up; its page was not readable in this research tool, so code/activity could not be independently inspected. The dated public write-up verifies a public Graph Hacks self-description, not winner status. |
| [Trace](https://github.com/swarnnim/trace) | FalkorDB graph memory for research, multi-hop answers, session persistence and a shared agent blackboard. | Public repository (22 commits visible), explicitly self-identifies as a Graph Hacks submission. No winner status known; primarily Track 02/03 by its own account, with Track 01 also claimed. |
| [Hearsay](https://github.com/Yashgurav002/hearsay) | Playable NPC memory/gossip experience with explanations of who told whom. | Public repository (18 commits visible), explicitly identifies Graph Hacks and tracks 02/01. No winner status known. Strong lesson in immediate comprehensibility and interaction. |

“Active-looking” above refers only to public repository content/commit history visible at the check; it is not a claim about the entrant's current work, completeness, judging status, or performance. GitHub rendered commit dates inconsistently in the accessible view, so commit counts are included only as a snapshot signal, not as verified recent activity dates. No private projects are represented.

### Competition implication

Anchor should not claim novelty for supply-chain risk, graph visualization, rerouting, automated recovery, verification, or a generic resilience score. The differentiated testable proposition is: **a material graph relationship generates a follow-on failure counterexample; that counterexample is evidence-linked and changes the optimizer's recovery; simulated action is then independently read back.** The product must demonstrate this end to end to earn the claim.

## Scientific and optimization foundations

### Production networks and systemic risk

Diem, Borsos, Reisch, Kertész, and Thurner, [“Quantifying firm-level economic systemic risk from nation-wide supply networks”](https://www.nature.com/articles/s41598-022-11522-z), *Scientific Reports* 12, 7719, published 11 May 2022 (DOI 10.1038/s41598-022-11522-z). The paper models firm-level production networks and evaluates systemic effects of disruptions using its own data and assumptions. It motivates graph-aware propagation, but Anchor's simplified synthetic shortfall ratio is not the paper's Economic Systemic Risk Index and must not be labeled as ESRI.

Zelbi, Ialongo, and Thurner, [“Systemic risk mitigation in supply chains through network rewiring”](https://www.nature.com/articles/s41598-026-42549-1), *Scientific Reports* 16, 12334, published 5 Mar 2026; version of record 14 Apr 2026 (DOI 10.1038/s41598-026-42549-1). The paper analyzes six Ecuadorian and Hungarian supply-network subnetworks and reports modeled risk reductions of 16–50% under its production constraints and rewiring method. These results are specific to those data and assumptions; Anchor must not reuse them as its own results or imply it implements the paper's model. It supports investigating topology-sensitive interventions and comparing pre/post stress scenarios.

### OR-Tools

Google's [Minimum Cost Flow documentation](https://developers.google.com/optimization/flow/mincostflow) is the primary reference for capacitated allocation where the model fits a flow network. Anchor's supplier activation, hard eligibility rules, multiple failure scenarios, and recourse may require CP-SAT rather than a plain min-cost flow. Solver choice must follow the actual formulation; OR-Tools documentation is a technical reference, not evidence of Anchor's correctness.

### FalkorDB client and Cypher

The [official FalkorDB Python client repository](https://github.com/FalkorDB/falkordb-py) documents `pip install FalkorDB`, graph selection, and `graph.query(...)`. The project dependency currently declares a broad `falkordb>=1.0,<2`; validate its lockfile and actual server/client compatibility before describing a tested setup. Use only Cypher features and procedures demonstrated on the selected server image; don't assume algorithm procedure availability from documentation for another release.

### FastMCP and Codex MCP

FastMCP's current [HTTP deployment documentation](https://gofastmcp.com/deployment/http) describes Streamable HTTP. Its official [HTTP source documentation](https://github.com/PrefectHQ/fastmcp/blob/main/docs/deployment/http.mdx) explicitly notes that `host_origin_protection=False` disables Host/Origin validation and DNS-rebinding protection. Anchor's local MCP listener should explicitly enable protection, bind loopback, and have no public unauthenticated exposure.

OpenAI's [Codex MCP setup reference](https://developers.openai.com/learn/docs-mcp) documents `codex mcp add <name> --url <url>` for a Streamable HTTP MCP server and `codex mcp list`; the page itself focuses on the OpenAI documentation MCP, so verify current Codex CLI behavior against the installed version before claiming Anchor registration worked. The [Codex MCP connections guide](https://developers.openai.com/api/docs/guides/agents-api/tools/mcp) is an API connection reference, not necessarily a local Codex CLI installation guide.

## Source and date ledger

All sources below were checked 18 Oct 2026. Dates are source publication/event dates when shown, otherwise stated explicitly as not exposed.

| Source | Date | Use |
|---|---|---|
| [Graph Hacks rules](https://www.wemakedevs.org/hackathons/falkordb/rules) and [track page](https://www.wemakedevs.org/hackathons/falkordb) | Event 15–18 Oct 2026; page accessed 18 Oct | Binding technical, data, work-period, disclosure, and submission requirements |
| [Microsoft winners](https://microsoft.github.io/AI_Agents_Hackathon/winners/) | Hackathon Apr 8–30, 2025; page date not stated | RiskWise award and broad product precedent |
| [DataHub winners](https://datahub.com/blog/meet-the-winners-of-build-with-datahub-the-agent-hackathon/) | Page prints `09.10.26` (date order ambiguous); accessed 18 Oct | Blackbox Grand Prize and evidence-gated repair pattern |
| [FalkorDB Memory Meets Motion recap](https://www.falkordb.com/blog/memory-meets-motion-the-falkordb-standouts/) | Published/updated 18 Aug 2026; event 3 Aug | Atrium and Hopper product lessons |
| [Neo4j Aura Agent winners](https://community.neo4j.com/t/aura-agent-hackathon-winners-announced/79568) | 23 Jun 2026 | Official community manager's winner announcement |
| [Neo4j video-context recap](https://neo4j.com/blog/developer/one-starter-repo-three-winners-neo4j-at-the-hack-the-video-agent-context-graph/) | 2 Aug 2026 per Neo4j community listing | MealPrep, Rehearsal, ZooVision and demo lessons |
| [Diem et al.](https://www.nature.com/articles/s41598-022-11522-z) | 11 May 2022 | Firm-level production network systemic risk |
| [Zelbi et al.](https://www.nature.com/articles/s41598-026-42549-1) | 5 Mar 2026; version of record 14 Apr | Topology rewiring under stated model constraints |
| [OR-Tools min-cost flow](https://developers.google.com/optimization/flow/mincostflow) | Living documentation; accessed 18 Oct 2026 | Solver formulation reference |
| [FalkorDB Python client](https://github.com/FalkorDB/falkordb-py) | Living repository; accessed 18 Oct 2026 | Official Python client API reference |
| [FastMCP HTTP](https://gofastmcp.com/deployment/http) | Living documentation; accessed 18 Oct 2026 | Streamable HTTP and protection configuration |
| [Codex MCP setup](https://developers.openai.com/learn/docs-mcp) | Living documentation; accessed 18 Oct 2026 | Codex MCP registration syntax reference |
| [Graph Hacks public repository: Interdict](https://github.com/YashSoni998265/interdict), [GraphDispatch](https://github.com/aggarmoksh/GraphDispatch), [BatchZero](https://github.com/ionfwsrijan/BatchZero), [Bedrock write-up](https://dev.to/ibnweb3/the-retraction-two-citations-back-building-a-citation-path-audit-on-falkordb-3cjk), [Trace](https://github.com/swarnnim/trace), [Hearsay](https://github.com/Yashgurav002/hearsay) | Accessed 18 Oct 2026; some entrants publish dates, others do not | Public project descriptions only; not official winner evidence |

## Limitations of this research

This is a bounded public-web review, not a census of all registered Graph Hacks projects. The event was still in its submission window at the snapshot, so no outcome is inferred. Some winner/project descriptions come from organizers, sponsors, or entrants; source attribution is preserved above. We did not independently run competing projects, audit their code, or validate their measurements. API and package docs are mutable and must be rechecked at implementation/submission time.
