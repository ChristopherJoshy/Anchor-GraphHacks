from anchor.seed import TARGET_PRODUCT_ID, build_seed_records


def test_synthetic_seed_builds_full_network_and_silicon_scenario():
    records = build_seed_records()

    assert len(records["Supplier"]) == 40
    assert len(records["Facility"]) == 20
    assert len(records["Product"]) == 30
    assert len(records["Order"]) == 60
    assert len(records["Inventory"]) == 20
    assert len(records["RouteLeg"]) == 30
    relationships = records["relationships"]
    assert {(edge["from"], edge["to"]) for edge in relationships if edge["type"] == "PRODUCES"} >= {
        ("FAC-MCU-ASSEMBLY", TARGET_PRODUCT_ID),
        ("FAC-TAIWAN-FOUNDRY", "PROD-003"),
    }
    assert all(edge["from"] and edge["to"] for edge in relationships)
