# Security and action boundary

- Anchor runs in `SIMULATION` only. The ERP adapter is local SQLite and refuses other modes; no procurement, payment, production, or logistics write connector is present.
- HTTP and MCP bind to loopback by default. Do not expose the server to the Internet or another network. Remote authentication and deployment are not implemented.
- MCP accepts bounded typed domain arguments. It does not offer arbitrary Cypher, shell commands, SQL, or file access.
- Synthetic graph mutations are limited to capacity changes in the current tool implementation; unknown entities and negative/non-integer values are rejected.
- Prices and quantities are integer-valued; graph queries parameterize values. Stable labels and relation query fragments are internal constants.
- The local demo reset deletes only the named `anchor_demo` graph and replaces the mock ERP seed state. The `anchor_reset_demo` MCP tool is destructive to this demo data and should be used intentionally.
- The mock ERP enforces capacity, order quantity, product match, availability, and idempotency in SQLite transactions. Execution read-back is separate from the solver's predicted result.

Imported messages and alerts are not used as instructions to the policy or executor. The demo facts are synthetic. A graph/database failure fails graph-dependent actions clearly; the app does not keep an in-memory mirror.
