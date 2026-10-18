"""Deterministic synthetic network used by Anchor's local demonstration."""

from __future__ import annotations

from typing import Any

SCENARIO_ID = "SCENARIO-SILICON-CASCADE"
INCIDENT_ENTITY_ID = "SUP-TAIWAN-FOUNDRY"
TARGET_PRODUCT_ID = "PROD-MCU-001"
TARGET_ORDER_ID = "ORDER-SILICON-1000"

COUNTRIES = [
    ("TW", "Taiwan", 25.0330, 121.5654),
    ("CN", "China", 31.2304, 121.4737),
    ("JP", "Japan", 35.6762, 139.6503),
    ("KR", "South Korea", 37.5665, 126.9780),
    ("IN", "India", 19.0760, 72.8777),
    ("SG", "Singapore", 1.3521, 103.8198),
    ("MY", "Malaysia", 3.1390, 101.6869),
    ("TH", "Thailand", 13.7563, 100.5018),
    ("VN", "Vietnam", 21.0278, 105.8342),
    ("DE", "Germany", 52.5200, 13.4050),
    ("NL", "Netherlands", 52.3676, 4.9041),
    ("US", "United States", 37.7749, -122.4194),
    ("MX", "Mexico", 19.4326, -99.1332),
    ("ZA", "South Africa", -33.9249, 18.4241),
    ("AE", "United Arab Emirates", 25.2048, 55.2708),
]


def build_seed_records() -> dict[str, list[dict[str, Any]]]:
    """Return stable records and typed relationship tuples for the demo graph."""
    locations = [
        {"id": f"LOC-{code}", "name": name, "country": code, "lat": lat, "lon": lon}
        for code, name, lat, lon in COUNTRIES
    ]
    suppliers: list[dict[str, Any]] = []
    for index in range(34):
        suppliers.append(
            {
                "id": f"SUP-{index + 1:03d}",
                "name": f"Synthetic Supplier {index + 1:02d}",
                "country": COUNTRIES[index % len(COUNTRIES)][0],
                "capacity": 250 + (index * 37 % 500),
                "available": True,
                "unit_price_minor": 100 + index * 7,
                "lead_days": 3 + index % 18,
                "source": "synthetic-fixed-seed-v1",
                "verified": True,
            }
        )
    overrides = {
        "SUP-TAIWAN-FOUNDRY": ("Taiwan Foundry (synthetic)", "TW", 0, 0, 2),
        "SUP-PRIMARY": ("Primary MCU Vendor (synthetic)", "TW", 1000, 520, 4),
        "SUP-BACKUP-B": ("Backup Vendor B (synthetic)", "JP", 600, 340, 6),
        "SUP-BACKUP-C": ("Backup Vendor C (synthetic)", "KR", 600, 360, 7),
        "SUP-INDEPENDENT-D": ("Independent Vendor D (synthetic)", "DE", 650, 900, 9),
        "SUP-INDEPENDENT-E": ("Independent Vendor E (synthetic)", "US", 250, 1250, 12),
    }
    for entity_id, (name, country, capacity, price, lead) in overrides.items():
        suppliers.append(
            {
                "id": entity_id,
                "name": name,
                "country": country,
                "capacity": capacity,
                "available": True,
                "unit_price_minor": price,
                "lead_days": lead,
                "source": "synthetic-silicon-cascade-v1",
                "verified": True,
            }
        )

    facilities = [
        {
            "id": f"FAC-{i:03d}",
            "name": f"Synthetic Facility {i:02d}",
            "country": COUNTRIES[(i - 1) % len(COUNTRIES)][0],
            "capacity": 500 + i * 25,
            "available": True,
            "unit": "units_per_bucket",
            "source": "synthetic-fixed-seed-v1",
        }
        for i in range(1, 21)
    ]
    facilities[0].update(id="FAC-TAIWAN-FOUNDRY", name="Taiwan Foundry Facility")
    facilities[1].update(id="FAC-MCU-ASSEMBLY", name="MCU Assembly Facility")

    products = [
        {
            "id": f"PROD-{i:03d}",
            "name": f"Synthetic Component {i:02d}",
            "unit": "unit",
            "compatible_products": [f"PROD-{i:03d}"],
            "source": "synthetic-fixed-seed-v1",
        }
        for i in range(1, 31)
    ]
    products[0].update(id=TARGET_PRODUCT_ID, name="Microcontroller MCU-001")

    customers = [
        {
            "id": f"CUS-{i:03d}",
            "name": f"Synthetic Customer {i:02d}",
            "country": COUNTRIES[(i * 3) % 15][0],
        }
        for i in range(1, 13)
    ]
    orders = [
        {
            "id": f"ORDER-{i:03d}",
            "product_id": f"PROD-{(i - 1) % 30 + 1:03d}",
            "quantity": 80 + (i * 29 % 180),
            "priority": 1 + i % 5,
            "due_days": 10 + i % 30,
            "status": "OPEN",
            "scenario_id": SCENARIO_ID,
            "source": "synthetic-fixed-seed-v1",
        }
        for i in range(1, 61)
    ]
    target_order = {
        "id": TARGET_ORDER_ID,
        "product_id": TARGET_PRODUCT_ID,
        "quantity": 1000,
        "priority": 5,
        "due_days": 20,
        "status": "OPEN",
        "scenario_id": SCENARIO_ID,
        "source": "synthetic-silicon-cascade-v1",
    }
    orders[0] = target_order

    inventories = [
        {
            "id": f"INV-{i:03d}",
            "facility_id": f"FAC-{(i - 1) % 20 + 1:03d}",
            "product_id": f"PROD-{(i - 1) % 30 + 1:03d}",
            "quantity": 40 + i * 3,
            "reserved": 0,
            "unit": "unit",
            "source": "synthetic-fixed-seed-v1",
            "verified": True,
        }
        for i in range(1, 21)
    ]
    inventories[0].update(
        id="INV-MCU-350", facility_id="FAC-MCU-ASSEMBLY", product_id=TARGET_PRODUCT_ID, quantity=350
    )

    contracts = [
        {
            "id": f"CON-{supplier['id']}",
            "supplier_id": supplier["id"],
            "status": "APPROVED",
            "effective": "2026-01-01T00:00:00Z",
            "expires": "2027-01-01T00:00:00Z",
            "source": "synthetic-fixed-seed-v1",
            "verified": True,
        }
        for supplier in suppliers
    ]
    route_legs = [
        {
            "id": f"ROUTE-{i:03d}",
            "start_location_id": locations[(i - 1) % 15]["id"],
            "end_location_id": locations[(i + 4) % 15]["id"],
            "available": True,
            "lead_days": 2 + i % 14,
            "capacity": 1000 + i * 50,
            "unit": "unit",
            "source": "synthetic-fixed-seed-v1",
        }
        for i in range(1, 31)
    ]

    # Relationship rows use stable IDs; these edges create the hidden common source.
    dependencies = [
        {"from": "SUP-PRIMARY", "to": "SUP-TAIWAN-FOUNDRY", "type": "DEPENDS_ON"},
        {"from": "SUP-BACKUP-B", "to": "SUP-TAIWAN-FOUNDRY", "type": "DEPENDS_ON"},
        {"from": "SUP-BACKUP-C", "to": "SUP-TAIWAN-FOUNDRY", "type": "DEPENDS_ON"},
        {"from": "SUP-TAIWAN-FOUNDRY", "to": "FAC-TAIWAN-FOUNDRY", "type": "OPERATES"},
        {"from": "SUP-PRIMARY", "to": "FAC-MCU-ASSEMBLY", "type": "OPERATES"},
        {"from": "SUP-BACKUP-B", "to": "FAC-003", "type": "OPERATES"},
        {"from": "SUP-BACKUP-C", "to": "FAC-004", "type": "OPERATES"},
        {"from": "SUP-INDEPENDENT-D", "to": "FAC-005", "type": "OPERATES"},
        {"from": "SUP-INDEPENDENT-E", "to": "FAC-006", "type": "OPERATES"},
    ]
    for i, supplier in enumerate(suppliers):
        if supplier["id"] not in {item["from"] for item in dependencies}:
            dependencies.append(
                {"from": supplier["id"], "to": facilities[i % 20]["id"], "type": "OPERATES"}
            )
        product_id = (
            TARGET_PRODUCT_ID if supplier["id"] in overrides else products[1 + i % 29]["id"]
        )
        dependencies.append({"from": supplier["id"], "to": product_id, "type": "SUPPLIES"})
    for facility in facilities:
        dependencies.append(
            {"from": facility["id"], "to": f"LOC-{facility['country']}", "type": "LOCATED_AT"}
        )
        product_id = (
            TARGET_PRODUCT_ID
            if facility["id"] == "FAC-MCU-ASSEMBLY"
            else products[1 + int(facility["id"][-3:]) % 29]["id"]
        )
        dependencies.append({"from": facility["id"], "to": product_id, "type": "PRODUCES"})
    dependencies.append({"from": "FAC-MCU-ASSEMBLY", "to": "PROD-002", "type": "REQUIRES_INPUT"})
    for inventory in inventories:
        dependencies.extend(
            [
                {"from": inventory["id"], "to": inventory["product_id"], "type": "STORES"},
                {"from": inventory["id"], "to": inventory["facility_id"], "type": "HELD_AT"},
            ]
        )
    for order in orders:
        dependencies.extend(
            [
                {"from": order["id"], "to": order["product_id"], "type": "REQUIRES"},
                {
                    "from": order["id"],
                    "to": customers[(int(order["id"][-3:]) - 1) % 12]["id"],
                    "type": "DELIVERED_TO",
                },
            ]
        )
    for contract in contracts:
        dependencies.append(
            {"from": contract["id"], "to": contract["supplier_id"], "type": "APPROVES"}
        )
    for route in route_legs:
        dependencies.extend(
            [
                {"from": route["id"], "to": route["start_location_id"], "type": "STARTS_AT"},
                {"from": route["id"], "to": route["end_location_id"], "type": "ENDS_AT"},
            ]
        )

    scenario = {
        "id": SCENARIO_ID,
        "name": "The Silicon Cascade",
        "version": 1,
        "source": "synthetic-silicon-cascade-v1",
        "description": "A synthetic upstream foundry failure with two correlated backup vendors.",
        "created_at": "2026-10-18T00:00:00Z",
    }
    incidents: list[dict[str, Any]] = []
    evidence = [
        {
            "id": "EVIDENCE-SILICON-SYNTHETIC",
            "kind": "synthetic_fixture",
            "source": "synthetic-silicon-cascade-v1",
            "verified": True,
            "description": "Team-authored synthetic scenario facts; not a real disruption.",
        }
    ]
    organizations = [
        {"id": f"ORG-{code}", "name": f"Synthetic organization {code}", "country": code}
        for code, *_ in COUNTRIES
    ]
    policies = [
        {
            "id": "POLICY-SIMULATION-ONLY",
            "mode": "SIMULATION",
            "allow_mutations": True,
            "source": "anchor-default-policy-v1",
        }
    ]
    return {
        "Supplier": suppliers,
        "Facility": facilities,
        "Product": products,
        "Inventory": inventories,
        "Order": orders,
        "Customer": customers,
        "Location": locations,
        "Contract": contracts,
        "RouteLeg": route_legs,
        "Incident": incidents,
        "Evidence": evidence,
        "RecoveryPlan": [],
        "Action": [],
        "ExecutionReceipt": [],
        "Scenario": [scenario],
        "Policy": policies,
        "Organization": organizations,
        "relationships": dependencies,
    }
