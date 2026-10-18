# Anchor: participant explanation and judge preparation

This guide describes the intended system. Before presenting, participants must compare each statement with the code and a fresh run, and remove or qualify anything that is not implemented.

## The one-minute explanation

Anchor is a local simulation agent for supply-chain disruptions. When a fictional supplier fails, it uses FalkorDB to follow dependencies across supplier tiers and orders. That matters because two apparent replacements can share the same failed upstream source. A deterministic optimizer finds a feasible allocation. Anchor then tests that candidate against a bounded set of additional failures derived from the graph. If it finds a failure path that defeats the candidate, it shows the path and replans. It applies only synthetic changes to a local mock ERP and reads the state back before reporting success.

## Why FalkorDB is central

The important question is not simply “which supplier lists this product?” It is “which alternatives are connected through upstream dependencies to the failed source, and which downstream orders depend on them?” Those are paths and shared neighborhoods in a graph. Anchor's impact assessment, alternative qualification, shared-dependency counterexamples, evidence paths, and persistent incident history depend on graph queries. If FalkorDB is down, those features should fail explicitly. The system must not carry a second hidden in-memory copy of the supply graph.

## Nodes, edges, and paths

Nodes represent entities such as suppliers, facilities, products, inventory, orders, contracts, incidents, and plans. Directed edges represent relationships such as `SUPPLIES`, `PRODUCES`, `REQUIRES_INPUT`, `DEPENDS_ON`, `STORES`, `REQUIRES`, `AFFECTS`, and `CONTAINS`. A multi-hop path can connect an upstream source to a backup supplier, product, facility, and customer order. Each reported reason should expose the path/evidence IDs and the fact provenance instead of relying on an LLM's unsupported explanation.

## What the current impact calculation does

The current deterministic calculator takes graph-resolved source availability/capacity, one target product, one target order, lead days, and discrete units. It solves the shortfall and allocation arithmetic for those inputs. It does not yet propagate full bills of materials through multiple facilities or compete across all 60 seeded orders. Its cascade exposure ratio is weighted unmet units divided by weighted demand and is not the academic ESRI metric.

## Why an optimizer is used

Supplier choice is a constrained allocation problem. The solver decides integer quantities by source and order while respecting demand balance, capacities, approved contracts, product compatibility, availability, and modeled delivery constraints. Hard restrictions cannot be traded away for lower cost. The objective prioritizes service and follow-on failure performance before cost according to documented weights or lexicographic stages. The LLM can help interpret the operator's request, but it does not invent or select quantities.

## Hidden dependency and counterexample

In the demo, the graph links two cheaper backup suppliers to the same affected upstream factory. A direct supplier list can make them look independent; traversing `DEPENDS_ON` paths exposes their shared exposure and excludes those suppliers from the eligible source list. The current bounded evaluator tests individual supplier failures and selected supplier pairs connected through a shared upstream node. It does not inject facility or route failures. Its report covers only the enumerated scenarios and is not a proof that other disruptions cannot cause failure.

## How the action is verified

The MCP action invokes a simulation-only operation. The local mock ERP actually changes its persistent state and returns a receipt. Anchor independently reads back the allocations and compares them with the plan and order completion. A test-only injector can reject one supplier reservation. Anchor records the rejection, returns a failed first attempt and its partial read-back, then solves and executes at most one replacement plan. General timeout/backoff handling, partial workflow compensation, and automatic synchronization after an external production constraint change are out of scope.

## MCP and session history

MCP exposes typed domain tools to the coding agent; it is the interface, not the decision engine. Tool results should include concise summaries and structured IDs, quantities, statuses, paths, assumptions, and errors. Plans, actions, and outcomes are persisted in FalkorDB so an operator can ask about a previous run after reopening the client. The agent's conversation history is not the authoritative operational record.

## Limitations to state plainly

- The supply network is synthetic; real supplier/customer relationships and operational capacity are not present.
- Simulation modes and solver objectives simplify real manufacturing, substitution, logistics, labor, contractual, and time uncertainty.
- Follow-on failures are bounded and selected by explicit rules; they do not cover every combination or provide calibrated event probabilities.
- “Robust” means tested against the declared finite set, not universally resilient.
- Mock ERP writes are not real procurement actions and do not establish production readiness.
- Any performance, cost, recovery, or success-rate number must be measured with an explained fixture, machine, and method before inclusion.

## Likely judge questions

**What would happen if FalkorDB were removed?**
Impact traversal, shared-upstream checks, graph-derived stress scenarios, graph-backed explanations, and graph history should return a clear dependency error. No recommendations should be fabricated from a duplicate local topology.

**How do you know the backup suppliers share a dependency?**
Show the actual FalkorDB query result and the path IDs/nodes linking each supplier to the affected source. Explain the assumptions about whether that dependency constrains usable capacity.

**Is this a formal resilience guarantee?**
No. The report gives outcomes for a declared bounded scenario set under synthetic data and model assumptions. It is an evidence report, not formal verification.

**What makes the optimizer choose this allocation?**
Show solver inputs and hard constraints, then the lexicographic objective values and allocation quantities. The solver—not supplier-name conditionals or generated prose—selects quantities.

**What if no plan is feasible?**
Anchor should report the unmet quantities and binding constraints. It must not manufacture an alternative or claim recovery.

**What does “verified execution” mean?**
Only that the synthetic allocation request has a receipt and that its allocation source/order/quantity is present in current mock ERP state when verification is requested. This does not establish a real procurement action. A later replan can replace those allocations, in which case verification of the old run correctly fails against current state.

**How was AI used?**
See `docs/ai-disclosure.md`. The team owns review and verification and must be able to explain the code. Do not attribute machine-generated artifacts to human authorship without review.

## Team readiness check

Before demo/submission, each participant should be able to explain the graph schema; walk through one Cypher traversal; reproduce the changed allocation after a capacity edit; describe the stress bounds and one counterexample; show a verified mock ERP state change; and state the difference between a finite simulation result and a guarantee. A rehearsed answer is not a substitute for understanding.
