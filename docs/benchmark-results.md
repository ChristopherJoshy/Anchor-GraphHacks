# Local benchmark results

Measured on 18 Oct 2026 at 09:23 UTC with `scripts/benchmark.py`. This is one local run over Anchor's synthetic Silicon Cascade; it is not a production benchmark or an estimate of business impact.

## Environment and dataset

- Lenovo 83D4 laptop, Intel Core Ultra 9 185H, 31.6 GiB reported memory.
- Windows 11 build 26200, Python 3.13.14, Docker Desktop 4.95.0, Docker Engine 29.8.2.
- FalkorDB image `falkordb/falkordb:v4.20.4`, running locally on loopback.
- Seed graph: 285 nodes, 384 relationships, 40 suppliers, and 60 orders. All supplier, contract, capacity, inventory, price, and disruption facts are synthetic.
- The benchmark creates a uniquely named FalkorDB graph and a temporary SQLite ERP, then deletes them. It does not reset the user's `anchor_demo` graph or ERP.

## Method

The measurement helper performs one warm-up before graph traversal, impact simulation, planning, and missing-incident handling. It records 30 samples for traversal, impact simulation, and missing-incident handling, and 5 for planning. End-to-end has 5 timed runs after the preceding queries have warmed the local graph and solver; there is no hidden or excluded end-to-end sample. P95 is the nearest-rank sample. Timings use `time.perf_counter_ns()` and include local client and process overhead.

`GraphStore.assess` measures the graph traversal and its affected-order/upstream evidence queries. Impact simulation measures the deterministic OR-Tools allocation calculation after eligible sources have been resolved from FalkorDB. Planning includes graph candidate/scenario retrieval, CP-SAT optimization, and graph persistence. End-to-end timing runs from incident creation through cascade assessment, planning, mock ERP mutation, receipt persistence, and ERP read-back verification; it excludes graph seeding and reset.

| Operation | Samples | Median | P95 |
|---|---:|---:|---:|
| Graph cascade traversal | 30 | 8.446 ms | 12.428 ms |
| Source/order impact simulation | 30 | 10.102 ms | 17.320 ms |
| Graph-backed planning and persistence | 5 | 110.024 ms | 122.578 ms |
| Incident trigger through verified recovery | 5 | 174.620 ms | 178.005 ms |
| Missing incident rejected explicitly | 30 | 1.264 ms | 2.190 ms |

These values describe this machine, software, graph, and run only. The sample is intentionally small and no latency target is claimed.

## Scenario comparison

Prices are synthetic USD minor units (100 minor units = USD 1.00). “Naive cheapest” allocates using nominal supplier availability and price while ignoring dependency edges; its proposal is then checked against the source eligibility FalkorDB derives for the foundry incident.

| Case | Proposed / available allocation | Unmet units after incident | Incremental cost |
|---|---|---:|---:|
| No supplier intervention | 350 inventory units | 650 | USD 0.00 |
| Naive cheapest, dependency-blind | 350 inventory + 600 backup B + 50 backup C; only the 350 inventory units remain graph-eligible | 650 realized | USD 2,220.00 nominal |
| Graph-optimized recovery | 350 inventory + 650 independent D | 0 | USD 5,850.00 |
| D reduced to 450 capacity | 350 inventory + 450 D + 200 independent E | 0 | USD 6,550.00 |
| Deliberately infeasible capacity | 350 inventory; D, E, and F set to zero | 650, reported as unmet | USD 0.00 |

The base plan passed its 9 graph-derived, deterministic stress scenarios. This means only that the enumerated test set had no unmet demand in that run. It is not a probability estimate or a guarantee against unmodeled disruptions. Both feasible capacity settings recovered fully (2/2); the deliberately infeasible setting was reported with its remaining 650 units rather than counted as a successful recovery.

The full automated suite passed 25 tests in this environment; Ruff passed, and the frontend production build completed. The suite emitted three dependency deprecation warnings, and Vite emitted a large optional globe-chunk warning.

## Reproduction

Start FalkorDB, then run:

```powershell
uv run python scripts/benchmark.py
```

The script fails clearly when FalkorDB is unavailable. It asserts the expected allocation changes and verifies every timed end-to-end run by reading the mock ERP state back.
