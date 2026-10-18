# AI assistance disclosure

Updated 18 Oct 2026 for the Graph Hacks submission.

## AI tools and contributions

- **OpenAI Codex coding agent.** The runtime identifies this assistant as GPT-6; its exact build identifier is not exposed. It assisted with public-source research, product and architecture decisions, Python backend and MCP implementation, graph queries, optimization and simulation code, synthetic seed generation, tests, benchmark tooling, and project documentation. The user supplied the project brief, named the product Anchor, set the goals and constraints, and steered the product direction.
- **OpenAI Codex CLI 0.163.0.** A fresh CLI execution reported model `gpt-6-luna` and was used as an actual MCP client. It selected and called Anchor tools for health, dependency validation, history, and the recovery demonstration. The exact hosted model build is not exposed by the CLI.
- AI assistance also contributed to the dashboard and its presentation during project implementation. Any additional AI tools, models, generated media, or collaborator usage must be added by Team Nexus before submission.

## What the running product uses

Anchor's backend does not call an LLM API. Its graph traversals, source qualification, impact calculation, CP-SAT allocation, mock ERP mutations, and verification are performed by application code and FalkorDB. A connected coding-agent client supplies natural-language interpretation and MCP tool selection; it does not supply operational facts or the computed allocation.

The demo network is synthetic. Real-world company relationships, supplier capacities, contracts, prices, inventory, routes, and disruptions are not represented as real data.

## Verification and participant responsibility

During this work session, the coding agent ran the automated test suite, Ruff, the frontend production build, a reproducible local benchmark, Docker/FalkorDB health checks, and fresh Codex CLI MCP calls. Those results are recorded in the repository; they are not a claim that a human independently reviewed every line or ran every command.

The participant provided the requirements, product direction, constraints, and review steering. Before submission, Team Nexus must personally inspect the implementation, reproduce the demo, understand the graph model and queries, explain the optimizer and action checks, and update this disclosure with any AI use by other team members. The [official rules](https://www.wemakedevs.org/hackathons/falkordb/rules) require meaningful participant understanding and verification; this disclosure does not replace that work.
