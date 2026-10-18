from anchor.models import FailureScenario, OrderDemand, Source
from anchor.optimizer import optimize_recovery, solve_allocation
from anchor.simulation import simulate_production_impact


def source(
    sid: str,
    capacity: int,
    price: int,
    *,
    kind: str = "supplier",
    available: bool = True,
    approved: bool = True,
    product: str = "mcu",
    lead: int = 2,
) -> Source:
    return Source(
        id=sid,
        label=sid,
        kind=kind,
        product_id=product,
        capacity=capacity,
        unit_price_minor=price,
        lead_days=lead,
        available=available,
        contract_approved=approved,
    )


def demand(quantity: int = 1000, due_days: int = 10) -> list[OrderDemand]:
    return [
        OrderDemand(
            id="order-1", product_id="mcu", quantity=quantity, priority=3, due_days=due_days
        )
    ]


def test_silicon_cascade_allocation_and_capacity_change():
    inventory = source("inventory", 350, 2, kind="inventory")
    primary = source("independent-a", 650, 5)
    backup = source("independent-b", 200, 9)
    plan = optimize_recovery(
        "incident", 1, [inventory, primary, backup], demand(), max_iterations=0
    )
    assert sum(a.quantity for a in plan.allocations) == 1000
    assert {a.source_id: a.quantity for a in plan.allocations} == {
        "inventory": 350,
        "independent-a": 650,
    }

    reduced = primary.model_copy(update={"capacity": 450})
    replanned = optimize_recovery(
        "incident", 2, [inventory, reduced, backup], demand(), max_iterations=0
    )
    assert {a.source_id: a.quantity for a in replanned.allocations} == {
        "inventory": 350,
        "independent-a": 450,
        "independent-b": 200,
    }


def test_bounded_stress_reports_risk_and_capacity_change_changes_plan():
    sources = [
        source("inventory", 350, 0, kind="inventory"),
        source("independent-a", 650, 900),
        source("independent-b", 250, 1250),
    ]
    plan = optimize_recovery("incident", 1, sources, demand(), max_iterations=8)
    assert {a.source_id: a.quantity for a in plan.allocations} == {
        "inventory": 350,
        "independent-a": 650,
    }
    assert plan.objective.worst_single_failure_shortfall == 1200
    reduced = [
        s.model_copy(update={"capacity": 450}) if s.id == "independent-a" else s for s in sources
    ]
    replanned = optimize_recovery("incident", 2, reduced, demand(), max_iterations=8)
    assert {a.source_id: a.quantity for a in replanned.allocations} == {
        "inventory": 350,
        "independent-a": 450,
        "independent-b": 200,
    }


def test_standby_capacity_can_keep_recovery_feasible_under_single_failures():
    sources = [
        source("inventory", 350, 0, kind="inventory"),
        source("independent-a", 650, 900),
        source("independent-b", 650, 1250),
        source("independent-c", 200, 2000),
    ]
    plan = optimize_recovery(
        "incident",
        1,
        sources,
        demand(),
        max_iterations=8,
    )

    assert {a.source_id: a.quantity for a in plan.allocations} == {
        "inventory": 350,
        "independent-a": 650,
    }
    assert plan.objective.worst_single_failure_shortfall == 0
    assert plan.stress_passed

    reduced = [
        item.model_copy(update={"capacity": 450}) if item.id == "independent-a" else item
        for item in sources
    ]
    replanned = optimize_recovery("incident", 2, reduced, demand(), max_iterations=8)
    assert {a.source_id: a.quantity for a in replanned.allocations} == {
        "inventory": 350,
        "independent-a": 450,
        "independent-b": 200,
    }
    assert replanned.objective.worst_single_failure_shortfall == 0
    assert replanned.stress_passed


def test_hard_eligibility_contract_availability_product_and_lead_time():
    sources = [
        source("unapproved", 100, 1, approved=False),
        source("offline", 100, 1, available=False),
        source("wrong-product", 100, 1, product="other"),
        source("late", 100, 1, lead=11),
        source("qualified", 25, 8),
    ]
    allocations, unmet = solve_allocation(sources, demand(100), failed_entity_ids=())
    assert [(a.source_id, a.quantity) for a in allocations] == [("qualified", 25)]
    assert unmet["order-1"] == 75


def test_impact_reports_deterministic_shortfall():
    result = simulate_production_impact(
        [source("s1", 100, 1), source("s2", 80, 1)], demand(150), failed_entity_ids={"s1"}
    )
    assert result["fulfilled_units"] == 80
    assert result["unmet_units"] == 70
    assert result["cascade_exposure_score"] == 210 / 450


def test_correlated_pair_stress_uses_only_feasible_scenario_recourse():
    suppliers = [
        source("backup-b", 100, 1),
        source("backup-c", 100, 2),
        source("independent", 100, 5),
    ]
    correlated = FailureScenario(
        id="shared-fab-b-c",
        failed_entity_ids=["backup-b", "backup-c"],
        paths=[["backup-b", "shared-fab"], ["backup-c", "shared-fab"]],
        label="Both apparent backups share the affected fab",
    )
    plan = optimize_recovery(
        "incident",
        7,
        suppliers,
        [OrderDemand(id="o", product_id="mcu", quantity=100, priority=1, due_days=10)],
        correlated_scenarios=[correlated],
        max_iterations=2,
    )
    # The cheap source may serve the initial order; the independent source is a valid
    # scenario-specific recourse source and must keep the correlated outage feasible.
    assert sum(a.quantity for a in plan.allocations) == 100
    assert plan.objective.worst_correlated_pair_shortfall == 0
    assert plan.stress_passed
    assert next(s for s in plan.tested_scenarios if s.id == correlated.id).paths == correlated.paths


def test_infeasibility_is_reported_without_fabricating_supply():
    plan = optimize_recovery(
        "incident", 1, [source("only", 20, 1, approved=False)], demand(100), max_iterations=0
    )
    assert plan.allocations == []
    assert plan.unmet_by_order == {"order-1": 100}
    assert plan.objective.current_weighted_shortfall == 300
    assert not plan.stress_passed


def test_cost_is_minor_units_and_lexicographic_after_service():
    sources = [source("cheap", 100, 75), source("dear", 100, 125)]
    plan = optimize_recovery(
        "incident",
        1,
        sources,
        [OrderDemand(id="o", product_id="mcu", quantity=60, priority=1, due_days=10)],
        max_iterations=0,
    )
    assert [(a.source_id, a.quantity) for a in plan.allocations] == [("cheap", 60)]
    assert plan.objective.incremental_cost_minor == 4500
