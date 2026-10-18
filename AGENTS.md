# Anchor — contributor and agent instructions

## Mission

Build Anchor, a FalkorDB-centered agent for synthetic supply-chain recovery under disruption. Its distinguishing workflow is to find a feasible recovery, search for bounded follow-on failure counterexamples in the connected dependency graph, revise the candidate when the modeled test exposes a weakness, and verify simulated actions by reading back the operational state.

The product goal is a clear, defensible Track 01 submission. Do not optimize for feature count or claim a win is assured.

## Governance

- Read `Idea.md`, `rules.txt`, `docs/product-decision.md`, and `docs/architecture.md` before substantive product or architecture changes.
- Treat `docs/research.md` as a dated evidence log. Recheck changeable APIs, event status, and competition requirements against their primary sources before relying on them.
- Preserve scope and decision history in the existing documents. When a decision materially changes, update `docs/product-decision.md` and the affected explanation instead of silently creating a conflicting story.
- Only state features, test results, integration coverage, benchmark numbers, or deployment status that have actually been implemented and verified. Label plans and synthetic examples as such.
- Maintain the canonical repository at `https://github.com/ChristopherJoshy/Anchor-GraphHacks.git`. Keep one working branch only (the repository's existing default branch); do not create or switch to additional branches. Worktrees are allowed only when they use that same branch safely and do not create competing branch histories.
- Commit each completed, reviewable change promptly. Use concise professional Conventional Commit messages (for example, `feat: add graph-backed recovery assessment` or `docs: document installation and verification`). Never commit secrets, generated local state, or unreviewed changes. Before committing, inspect the exact staged diff and run the relevant checks; report commit IDs truthfully.
- Push tested commits regularly, including after a small or major change, once the relevant checks pass. This instruction explicitly authorizes pushing Anchor project commits to its configured canonical repository. Never push untested changes, force push, or push unrelated files. If a push fails, retain the local commit and report the cause; do not rewrite or discard history to work around it.
- Do not publish the project or submit it to the competition except by pushing the authorized project commits to the canonical repository; competition submission, deployments, and unrelated external publishing still require separate explicit authorization.
- Do not claim formal proof, universal resilience, real-time global visibility, real supplier relationships, or measured improvement without evidence. A passed bounded stress suite means only that the tested modeled cases passed.

## Data and safety

- Use synthetic, public, or team-owned data with rights to use it. The supply network and all commercial relationships in the demo are synthetic. Never add private, personal, paywalled, login-protected, or otherwise restricted data.
- Keep execution confined to the local synthetic simulation. Do not connect procurement, payment, logistics, or production systems for writes. Do not spend money or place real orders.
- Keep operational facts distinct from assumptions, inferred outcomes, and simulated receipts. Preserve provenance and disclose uncertainty.
- No arbitrary user-supplied Cypher, shell, SQL, or unrestricted file access through agent tools. Use parameterized queries and typed, allowlisted inputs.
- Keep local services loopback-bound by default and do not commit secrets.

## Engineering expectations

- FalkorDB is the primary dependency graph and evidence/history store. Graph-dependent impact assessment, shared-dependency discovery, stress-case generation, and explanations must fail clearly when it is unavailable; do not replace it with a parallel in-memory graph.
- Keep optimization deterministic and constraint based. Hard safety, contract, compatibility, and authorization rules are not objective penalties.
- Stress testing is bounded and its scenario set, limits, and stopping reason must be visible. Report infeasibility rather than manufacturing a success.
- Verify action outcomes against the mock ERP's persisted state; a success-shaped response alone is not verification.
- Add a focused test or assert-based check for each new non-trivial branch, algorithm, or trust-boundary rule. Run relevant checks after changes; never report tests that were not run.
- Prefer the smallest complete change consistent with the current package structure. Avoid adding dependencies, abstraction layers, domains, or UI work without a clear demo or correctness benefit.

## Hackathon integrity and communication

- Track 01 is “Agents That Act on Connected Data.” Follow the [official rules](https://www.wemakedevs.org/hackathons/falkordb/rules); they control if this file conflicts with them.
- The main implementation must be new work from the event window. Properly licensed tools and general templates are permitted; do not copy another submission's code or distinctive implementation.
- AI coding assistance is permitted but must be disclosed. Team members must review, verify, and be able to explain the submitted graph model, Cypher, architecture, and technical choices. See `docs/ai-disclosure.md` and `docs/participant-explanation.md`.
- Do not publish, deploy externally, or submit to the competition without the team's explicit authorization. Prepare and review materials locally first.
- Keep updates factual: completed work, actual verification, blockers, and remaining gaps.
