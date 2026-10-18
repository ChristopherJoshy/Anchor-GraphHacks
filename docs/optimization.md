# Optimization and bounded resilience testing

The planner uses OR-Tools CP-SAT with integer allocation variables. Hard eligibility excludes unavailable sources, unapproved suppliers, incompatible products, failed sources, and sources whose lead time exceeds an order's deadline. Per-source capacity and exact demand/unmet equations prevent over-allocation. Inventory is modeled as a zero-price source.

The implementation solves sequential lexicographic objectives, fixing each optimum before optimizing the next:

1. Minimize current weighted unmet demand (`priority × units`).
2. Minimize worst weighted unmet demand across enumerated single-source/failure scenarios.
3. Minimize worst weighted unmet demand across enumerated correlated supplier pairs.
4. Minimize total allocation cost in integer minor currency units.
5. Minimize newly activated supplier count.

The solver uses one worker, a fixed random seed, and a 20-second limit per lexicographic solve. It requires an `OPTIMAL` result; otherwise it raises rather than claiming a proven optimum. The graph layer creates a bounded set of single-source scenarios and shared-upstream pairs. The stress evaluator permits recourse only from surviving unused capacities and does not assign probabilities.

`cascade_exposure_score` in the deterministic simulator is weighted unmet demand divided by weighted demand. It is Anchor's simplified scenario metric; it is not the academic ESRI metric described by Diem et al. A richer multi-order production-network simulator is not implemented yet.

References: [OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver), [minimum-cost flow](https://developers.google.com/optimization/flow/mincostflow). The project uses CP-SAT because scenario recourse and lexicographic discrete objectives exceed a plain single-commodity min-cost-flow formulation.
