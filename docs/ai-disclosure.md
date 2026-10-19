# AI assistance disclosure

Updated 19 Oct 2026 with the creator's attribution and README media references.

## Creator attribution and build context

Christopher describes his contribution as designing the graph schema and building the MCP layer, with Codex building the web view under his direction. He reports approximately eight hours of build time fitted around exam commitments. This is participant-provided context, not an instrumented development-time measurement. Human design/ownership and AI coding assistance can coexist; the assistance record below remains applicable.

## AI tools and contributions

- **OpenAI Codex coding agent.** The runtime identifies this assistant as GPT-6; its exact build identifier is not exposed. It assisted with public-source research, product and architecture decisions, Python backend and MCP implementation, graph queries, optimization and simulation code, synthetic seed generation, tests, benchmark tooling, and project documentation. The user supplied the project brief, named the product Anchor, set the goals and constraints, and steered the product direction.
- **OpenAI Codex CLI 0.163.0.** A fresh CLI execution reported model `gpt-6-luna` and was used as an actual MCP client. It selected and called Anchor tools for health, dependency validation, history, and the recovery demonstration. The exact hosted model build is not exposed by the CLI.
- **Web interface and demo media.** Codex helped implement the web interface under Christopher's direction and assisted with the demo's script, editing, graphics, and documentation. The narrated recording uses local Kokoro AI speech; [demo production notes](../artifacts/demo/README.md) contain model, music, font, and asset credits. The README uses actual recording excerpts and screenshots, plus explanatory SVG diagrams; [README media provenance](media/README.md) identifies their sources and limits. Any additional AI tools, models, generated media, or collaborator usage must be added by Team Nexus before submission.

## What the running product uses

Anchor's backend does not call an LLM API. Its graph traversals, source qualification, impact calculation, CP-SAT allocation, mock ERP mutations, and verification are performed by application code and FalkorDB. A connected coding-agent client supplies natural-language interpretation and MCP tool selection; it does not supply operational facts or the computed allocation.

The demo network is synthetic. Real-world company relationships, supplier capacities, contracts, prices, inventory, routes, and disruptions are not represented as real data.

## Verification and participant responsibility

During this work session, the coding agent ran the automated test suite, Ruff, the frontend production build, a reproducible local benchmark, Docker/FalkorDB health checks, and fresh Codex CLI MCP calls. Those results are recorded in the repository; they are not a claim that a human independently reviewed every line or ran every command.

The participant provided the requirements, product direction, constraints, and review steering. Before submission, Team Nexus must personally inspect the implementation, reproduce the demo, understand the graph model and queries, explain the optimizer and action checks, and update this disclosure with any AI use by other team members. The [official rules](https://www.wemakedevs.org/hackathons/falkordb/rules) require meaningful participant understanding and verification; this disclosure does not replace that work.
