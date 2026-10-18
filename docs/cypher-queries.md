# Cypher queries Anchor depends on

Queries are fixed in `src/anchor/graph.py`; input values use parameters. The app exposes no arbitrary Cypher tool.

## Downstream dependents

```cypher
MATCH (root {id: $entity_id})
MATCH p=(n)-[:DEPENDS_ON*1..12]->(root)
WHERE length(p) <= $max_depth
RETURN DISTINCT n.id AS id, labels(n) AS labels, n.name AS name,
       length(p) AS depth, [x IN nodes(p) | x.id] AS path
LIMIT $limit
```

## Shared upstream paths

```cypher
MATCH p1=(a:Supplier)-[:DEPENDS_ON*1..6]->(u:Supplier)
MATCH p2=(b:Supplier)-[:DEPENDS_ON*1..6]->(u)
WHERE a.id < b.id
RETURN a.id AS left_id, b.id AS right_id, u.id AS shared_id,
       [x IN nodes(p1) | x.id] AS left_path,
       [x IN nodes(p2) | x.id] AS right_path
LIMIT $limit
```

This query gives the demo's two cheap alternatives an evidence path to the same failed source. The qualification query excludes suppliers whose bounded `DEPENDS_ON` path reaches the affected node, then joins supply, demand, and approved contract records. The plan, action, receipt, and incident history queries persist and retrieve the corresponding evidence.

Anchor uses bounded Cypher traversals, not FalkorDB algorithm procedures. No PageRank, centrality, or shortest-path procedure is claimed. The installed image's actual integration behavior must be verified in Docker before treating these queries as runtime-tested.
