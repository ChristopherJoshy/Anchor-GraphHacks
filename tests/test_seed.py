from anchor.seed import TARGET_PRODUCT_ID, build_seed_records


def test_synthetic_seed_builds_full_network_and_silicon_scenario():
    records = build_seed_records()

    assert len(records["Supplier"]) == 40
    assert len(records["Facility"]) == 20
    assert len(records["Product"]) == 30
    assert len(records["Order"]) == 60
    assert len(records["Inventory"]) == 20
    assert len(records["RouteLeg"]) == 30
    locations = {item["id"]: item for item in records["Location"]}
    assert locations["LOC-TW"]["name"] == "Taipei"
    assert locations["LOC-TW"]["lat"] == 25.053056
    assert locations["LOC-TW"]["source"] == "GeoNames"
    relationships = records["relationships"]
    assert {(edge["from"], edge["to"]) for edge in relationships if edge["type"] == "PRODUCES"} >= {
        ("FAC-MCU-ASSEMBLY", TARGET_PRODUCT_ID),
        ("FAC-TAIWAN-FOUNDRY", "PROD-002"),
    }
    assert all(edge["from"] and edge["to"] for edge in relationships)
    suppliers = {item["id"]: item for item in records["Supplier"]}
    assert suppliers["SUP-TAIWAN-FOUNDRY"]["capacity"] == 1000
    assert suppliers["SUP-TAIWAN-FOUNDRY"]["available"] is True
    assert ("SUP-TAIWAN-FOUNDRY", "PROD-002") in {
        (edge["from"], edge["to"]) for edge in relationships if edge["type"] == "SUPPLIES"
    }
    assert ("FAC-TAIWAN-FOUNDRY", "PROD-002") in {
        (edge["from"], edge["to"]) for edge in relationships if edge["type"] == "PRODUCES"
    }
    assert ("SUP-TAIWAN-FOUNDRY", TARGET_PRODUCT_ID) not in {
        (edge["from"], edge["to"]) for edge in relationships if edge["type"] == "SUPPLIES"
    }
