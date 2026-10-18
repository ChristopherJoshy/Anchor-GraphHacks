# Limitations

- Only the synthetic Silicon Cascade order is optimized end to end. The wider network is for graph traversal and visualization, not complete global operational visibility.
- Commercial entities, capacities, contracts, prices, route facts, and incidents are synthetic. Real coordinates do not imply real supplier or transport relationships.
- Current cascade arithmetic is a deterministic source/order allocation model. It does not yet propagate full bills of materials across multiple production facilities or time buckets.
- The optimizer tests a finite bounded scenario set, uses no estimated event probabilities, and cannot prove universal resilience.
- No independent end-to-end FalkorDB container run has been completed in the present environment. The code-level tests do not validate the Cypher against a running server.
- Execution failures, timeouts, retry/backoff, partial workflow compensation, and multi-process concurrency have not been fully integrated into the orchestrator.
- HTTP/MCP is local and unauthenticated; remote exposure is unsupported. Codex tool registration, Claude Code, and OpenCode have not been exercised here.
- Benchmarks and performance claims are not published because no full graph-backed workload has been measured on the development machine.
