# Anchor

**Graph-backed recovery under attack.** Anchor helps answer: *Will this recovery still work if another connected part of the network fails?*

## Product thesis

Anchor investigates a disruption in a synthetic manufacturing supply network, traces affected orders and shared upstream dependencies through FalkorDB, computes feasible recovery allocations, then stress-tests a candidate against a bounded set of graph-derived follow-on failures. If it finds a counterexample, it reports the failure path and revises the allocation. It can execute approved actions only inside a persistent local mock ERP, read back the resulting state, and write evidence-linked history to FalkorDB.

The core loop is:

**DETECT → TRACE → SIMULATE → ALLOCATE → STRESS-TEST → REPLAN → EXECUTE IN SIMULATION → VERIFY → EXPLAIN**

## The differentiating demo

In **The Silicon Cascade**, a fictional 1,000-unit microcontroller order is exposed to a failed upstream factory. Two apparently separate backup suppliers share that dependency. Inventory and independent suppliers offer alternatives. Anchor must use the graph to uncover the shared exposure and use deterministic constrained optimization to allocate stock and capacity.

Then the operator reduces the primary independent source's capacity. The feasible allocation should change because the actual graph-backed constraints changed. Anchor evaluates the proposed recovery against explicitly modeled single failures and correlated pairs linked by shared dependencies. A discovered counterexample becomes visible evidence and may change the plan. The operator can inject an execution fault; Anchor must detect it from read-back, bound its retry/replan behavior, and report any unresolved shortage honestly.

## What Anchor is and is not

- **Is:** an inspectable decision-and-action prototype for a synthetic supply network, centered on graph relationships and testable constrained decisions.
- **Is:** an evidence report about the particular modeled failures evaluated.
- **Is not:** a formal proof, a guarantee against every future event, live global supply-chain intelligence, or a production procurement agent.
- **Is not:** merely a globe, risk dashboard, general chatbot, or LLM-generated supplier recommender.

## Audience and value

The demo is for hackathon judges and engineers evaluating graph-backed agent behavior. The practical user is an operations planner who needs to understand why apparent alternatives are correlated, what a feasible recovery costs, which tested failure can break it, and whether a permitted change actually took effect.

## Success evidence

The idea is substantiated only if a reproducible run shows: a real multi-hop FalkorDB path changing an eligibility or stress-test result; solver-derived feasible allocations; a changed decision after a material capacity edit; bounded failure testing with a counterexample or explicit pass over the declared test set; persistent mock ERP mutation plus independent read-back; and persisted evidence that can be retrieved after restart. No metric or success is presumed before it is measured.
