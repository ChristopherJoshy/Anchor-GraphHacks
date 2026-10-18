# Limitations

- Only the synthetic Silicon Cascade order is optimized end to end. The wider network is for graph traversal and visualization, not complete global operational visibility.
- Commercial entities, capacities, contracts, prices, route facts, and incidents are synthetic. Real coordinates do not imply real supplier or transport relationships.
- Current cascade arithmetic is a deterministic source/order allocation model. It does not yet propagate full bills of materials across multiple production facilities or time buckets.
- The optimizer tests a finite bounded scenario set, uses no estimated event probabilities, and cannot prove universal resilience.
- A local Docker/FalkorDB end-to-end test validates the Silicon Cascade Cypher, graph-backed replan, persistent history, and mock ERP read-back. The wider synthetic graph is not a real-world supplier network.
- The simulation supports one injected supplier-reservation rejection and at most one solver replan. General timeout/backoff handling, partial workflow compensation, and multi-process concurrency are not implemented.
- HTTP/MCP is local and unauthenticated; remote exposure is unsupported. Codex CLI registration and tool calls were exercised; Claude Code and OpenCode have not been exercised.
- Benchmarks and performance claims are not published because no full graph-backed workload has been measured on the development machine.
