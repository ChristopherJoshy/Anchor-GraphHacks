# Anchor

**Find the shared failure. Recover. Test what breaks next.**

## Product thesis

An operational recovery can become the next failure if its replacement sources share the same upstream dependency. Anchor uses FalkorDB to find those common paths, computes a feasible allocation under capacity, contract, compatibility, and delivery constraints, and challenges the candidate against a bounded set of additional graph-derived failures. It executes only in a persistent synthetic ERP and calls the result verified only after reading the changed state back.

**The graph must change the decision, not just decorate its explanation.** A supplier that appears available in an isolated record can be excluded when its graph path reaches the failed factory. A predefined dependency edge or a capacity edit must be able to change the plan.

## What makes the idea distinctive

Anchor does not claim that supply-chain risk analysis, route planning, a globe, or “detect, fix, verify” is novel. Public winners already cover those broad ideas. The sharper product is **a graph-witnessed recovery that is tested against explicit follow-on failures before a simulated action is accepted**:

1. **Trace the common cause.** FalkorDB returns paths from an incident through shared upstream dependencies to apparently independent alternatives.
2. **Allocate scarce resources.** OR-Tools computes integer source-to-order quantities while respecting hard qualification rules and reporting unmet demand.
3. **Challenge the recovery.** A deterministic, bounded scenario set tests additional single and correlated failures. A counterexample includes its graph path; the optimizer can account for the supplied counterexample, or the system reports the remaining weakness/infeasibility.
4. **Act inside the safe boundary.** The policy gate allows only synthetic simulation actions. The mock ERP mutates persistent state and returns receipts.
5. **Verify independently.** Anchor reads the ERP state back, checks postconditions, and stores the incident, plan, evidence, action, and outcome in FalkorDB for later sessions.

The stress result is a report about the declared scenarios and search bound. It is not a formal proof, probability estimate, or guarantee against unmodeled failures.

## The Silicon Cascade demo

A fictional order needs 1,000 microcontrollers. It has 350 units of synthetic inventory. Two cheap backup suppliers share a failed foundry, while independent supplier D can provide 650 units. The graph should make the cheap backups ineligible for affected capacity, so the optimizer chooses the inventory and D. If D falls to 450 units, supplier E must supply the additional 200 units. The same code handles both conditions; names do not select the answer.

The benchmark reports these fixture results: the dependency-blind cheapest proposal leaves 650 units unmet after graph eligibility is applied; graph-aware recovery supplies all 1,000 at USD 5,850; reducing D's capacity to 450 produces a 350 + 450 + 200 allocation at USD 6,550. Costs and all commercial facts are synthetic. The base plan passes its nine declared graph-derived stress scenarios in the checked-in benchmark; that is only a result for that finite test set.

The demo's falsifiable proof points are:

- The failed facility and two backups appear on returned multi-hop graph paths.
- Changing a predefined dependency edge changes the selected strategy (integration-tested).
- A path-bearing counterexample changes scarce-source allocation between two priority orders (unit-tested; separate from the single-order flagship run).
- Reducing D's capacity changes the computed feasible allocation and cost.
- A rejected reservation is caught by read-back, then handled with bounded replanning.
- With FalkorDB unavailable, graph-dependent tools fail rather than inventing a recovery.

## Audience and user value

For an operations planner, Anchor answers: **Which of my apparent backups are exposed to the same failure? What allocation can still satisfy the critical orders? What modeled failure could break that recovery? Did the authorized change actually take effect?** The demo is an inspectable decision-and-action prototype, not an operational procurement service.

## Scope and limits

- The global-looking network is synthetic, with real city reference points clearly separated from synthetic firms, facilities, routes, contracts, capacities, and orders.
- Execution is confined to a local persistent mock ERP. There are no live supplier, payment, logistics, or production writes.
- Scenario generation is bounded and deterministic. “Passed” means only that the named cases passed within the stated limits.
- If evidence is missing, capacity is insufficient, the plan is stale, or verification fails, Anchor reports the failure and unresolved demand.
- The agent is a domain-specific Track 01 MCP tool set. The host coding agent provides natural-language reasoning; deterministic code owns graph access, feasibility, policy, and execution.

## Research basis

The product decision is informed by comparable winners: RiskWise and CHRONOS show that broad supply-chain risk and logistics planning are already proven hackathon themes; Atrium demonstrates that a graph relationship can select a different intervention; Project Blackbox and Hindsight emphasize evidence gates, context ablation, and independent write verification. Anchor applies those lessons to shared supplier dependencies and constrained recovery. Sources, dates, competitor limits, and the rejected alternatives are recorded in [`docs/research.md`](docs/research.md) and [`docs/product-decision.md`](docs/product-decision.md).
