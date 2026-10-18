# Graph model

Anchor stores a fixed synthetic manufacturing scenario in FalkorDB's `anchor_demo` graph. The application uses the stable `id` property for lookups; all query values are parameters and labels/relationship types come from fixed internal templates.

## Nodes

The seed contains `Supplier`, `Facility`, `Product`, `Inventory`, `Order`, `Customer`, `Location`, `Contract`, `RouteLeg`, `Incident`, `Evidence`, `RecoveryPlan`, `Action`, `ExecutionReceipt`, `Scenario`, `Policy`, and `Organization` labels. Operational facts include scenario IDs, source/provenance, availability, quantity/capacity, unit, lead days, price in integer USD minor units, contract status, or UTC timestamps as applicable. Commercial entities and relationships are synthetic. The coordinates are reference locations only.

## Relationships used by the demo

- `(:Supplier)-[:DEPENDS_ON]->(:Supplier)` models shared upstream exposure.
- `(:Supplier)-[:OPERATES]->(:Facility)` and `(:Facility)-[:LOCATED_AT]->(:Location)` connect capability to site and geography.
- `(:Supplier)-[:SUPPLIES]->(:Product)` stores supply capacity, unit, price, currency, lead time, availability, provenance, and verification flag.
- `(:Inventory)-[:STORES]->(:Product)` and `(:Inventory)-[:HELD_AT]->(:Facility)` model inventory.
- `(:Order)-[:REQUIRES]->(:Product)` and `(:Order)-[:DELIVERED_TO]->(:Customer)` connect demand to products and customers.
- `(:Contract)-[:APPROVES]->(:Supplier)` records qualification.
- Route legs connect to start/end locations. Incidents connect to affected entities and evidence; plans connect to incidents/actions; actions connect to execution receipts.

The synthetic demonstration models a 1,000-unit MCU order, 350 inventory units, and independent suppliers with 650 and 250 units. Primary and two apparent backups have `DEPENDS_ON` paths to the affected Taiwan foundry. The optimizer does not key on supplier names.

## Graph version

Each material simulation mutation increments `Scenario.version`. Plans capture that version. Execution compares the captured value to the current graph version and rejects stale plans. This is a local demo guard, not a distributed locking protocol.

The current planner focuses on one target order and its product for a compact, auditable demonstration. Other synthetic orders and products populate the wider network view; multi-order competition and full bill-of-materials production propagation remain limitations.
