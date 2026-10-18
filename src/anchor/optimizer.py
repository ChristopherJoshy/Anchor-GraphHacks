"""Deterministic, integer constrained recovery and bounded stress testing."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from ortools.sat.python import cp_model

from anchor.models import (
    Allocation,
    FailureScenario,
    OrderDemand,
    PlanObjective,
    RecoveryPlan,
    Source,
)


def _eligible(source: Source, order: OrderDemand, failed: set[str]) -> bool:
    return (
        source.id not in failed
        and source.available
        and source.contract_approved
        and source.product_id == order.product_id
        and source.lead_days <= order.due_days
    )


def _allocation_model(
    sources: Sequence[Source],
    orders: Sequence[OrderDemand],
    failed_entity_ids: set[str],
    stress_scenarios: Sequence[FailureScenario],
    prior_supplier_ids: set[str],
) -> tuple[
    cp_model.CpModel,
    dict[tuple[str, str], cp_model.IntVar],
    dict[str, cp_model.IntVar],
    dict[str, cp_model.LinearExpr | int],
    dict[str, cp_model.IntVar],
]:
    model = cp_model.CpModel()
    source_by_id = {source.id: source for source in sources}
    x: dict[tuple[str, str], cp_model.IntVar] = {}
    unmet: dict[str, cp_model.IntVar] = {}
    for order in orders:
        unmet[order.id] = model.NewIntVar(0, order.quantity, f"unmet_{order.id}")
        vars_for_order = []
        for source in sources:
            if _eligible(source, order, failed_entity_ids):
                var = model.NewIntVar(
                    0, min(source.capacity, order.quantity), f"x_{source.id}_{order.id}"
                )
                x[(source.id, order.id)] = var
                vars_for_order.append(var)
        model.Add(sum(vars_for_order) + unmet[order.id] == order.quantity)
    for source in sources:
        source_vars = [var for (sid, _), var in x.items() if sid == source.id]
        if source_vars:
            model.Add(sum(source_vars) <= source.capacity)

    weighted = sum(order.priority * unmet[order.id] for order in orders)
    cost = sum(source_by_id[sid].unit_price_minor * var for (sid, _), var in x.items())
    activated: dict[str, cp_model.IntVar] = {}
    for source in sources:
        if source.kind != "supplier":
            continue
        used_vars = [var for (sid, _), var in x.items() if sid == source.id]
        if not used_vars:
            continue
        active = model.NewBoolVar(f"active_{source.id}")
        model.Add(sum(used_vars) <= source.capacity * active)
        if source.capacity:
            model.Add(sum(used_vars) >= active)
        activated[source.id] = active
    changes = sum(var for sid, var in activated.items() if sid not in prior_supplier_ids)

    single_shortfalls: list[cp_model.IntVar] = []
    pair_shortfalls: list[cp_model.IntVar] = []
    for scenario in stress_scenarios:
        failed = set(scenario.failed_entity_ids)
        scenario_unmet: dict[str, cp_model.IntVar] = {}
        recourse: dict[tuple[str, str], cp_model.IntVar] = {}
        for order in orders:
            remaining = model.NewIntVar(0, order.quantity, f"stress_unmet_{scenario.id}_{order.id}")
            scenario_unmet[order.id] = remaining
            recovered = []
            survivors = [
                var for (sid, oid), var in x.items() if oid == order.id and sid not in failed
            ]
            for source in sources:
                if not _eligible(source, order, failed_entity_ids | failed):
                    continue
                var = model.NewIntVar(
                    0,
                    min(source.capacity, order.quantity),
                    f"rec_{scenario.id}_{source.id}_{order.id}",
                )
                recourse[(source.id, order.id)] = var
                recovered.append(var)
            model.Add(sum(survivors) + sum(recovered) + remaining == order.quantity)
        for source in sources:
            rec_vars = [var for (sid, _), var in recourse.items() if sid == source.id]
            if rec_vars:
                # Surviving first-stage allocations consume capacity; failed allocations are lost.
                surviving_base = [
                    var for (sid, _), var in x.items() if sid == source.id and sid not in failed
                ]
                if source.id not in failed:
                    model.Add(sum(rec_vars) + sum(surviving_base) <= source.capacity)
                else:
                    model.Add(sum(rec_vars) == 0)
        weighted_stress = sum(order.priority * scenario_unmet[order.id] for order in orders)
        worst = model.NewIntVar(
            0, sum(o.priority * o.quantity for o in orders), f"score_{scenario.id}"
        )
        model.Add(worst == weighted_stress)
        (pair_shortfalls if len(scenario.failed_entity_ids) == 2 else single_shortfalls).append(
            worst
        )

    bound = sum(order.priority * order.quantity for order in orders)
    worst_single = model.NewIntVar(0, bound, "worst_single")
    worst_pair = model.NewIntVar(0, bound, "worst_pair")
    model.AddMaxEquality(worst_single, single_shortfalls or [0])
    model.AddMaxEquality(worst_pair, pair_shortfalls or [0])
    objectives: dict[str, cp_model.LinearExpr | int] = {
        "current": weighted,
        "single": worst_single,
        "pair": worst_pair,
        "cost": cost,
        "changes": changes,
    }
    return model, x, unmet, objectives, activated


def _solve_lexicographic(
    sources: Sequence[Source],
    orders: Sequence[OrderDemand],
    failed_entity_ids: set[str],
    scenarios: Sequence[FailureScenario],
    prior_supplier_ids: set[str],
) -> tuple[list[Allocation], dict[str, int], dict[str, int]]:
    model, variables, unmet_vars, objectives, _ = _allocation_model(
        sources, orders, failed_entity_ids, scenarios, prior_supplier_ids
    )
    values: dict[str, int] = {}
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    solver.parameters.max_time_in_seconds = 20
    for key in ("current", "single", "pair", "cost", "changes"):
        expr = objectives[key]
        model.Minimize(expr)
        status = solver.Solve(model)
        if status != cp_model.OPTIMAL:
            raise RuntimeError(
                f"CP-SAT did not prove the lexicographic optimum (status={solver.StatusName(status)})"
            )
        optimum = int(solver.Value(expr)) if not isinstance(expr, int) else expr
        values[key] = optimum
        model.Add(expr == optimum)
    source_by_id = {source.id: source for source in sources}
    allocations = [
        Allocation(
            source_id=sid,
            order_id=oid,
            product_id=source_by_id[sid].product_id,
            quantity=solver.Value(var),
            unit_price_minor=source_by_id[sid].unit_price_minor,
            lead_days=source_by_id[sid].lead_days,
        )
        for (sid, oid), var in sorted(variables.items())
        if solver.Value(var) > 0
    ]
    residuals = {oid: solver.Value(var) for oid, var in unmet_vars.items()}
    return allocations, residuals, values


def _scenario_shortfall(
    scenario: FailureScenario,
    sources: Sequence[Source],
    orders: Sequence[OrderDemand],
    allocations: Sequence[Allocation],
    incident_failed: set[str],
) -> int:
    """Evaluate recourse after first-stage allocations from failed sources are lost."""
    failed = incident_failed | set(scenario.failed_entity_ids)
    lost_quantities: dict[str, int] = {order.id: order.quantity for order in orders}
    for allocation in allocations:
        if allocation.source_id not in failed:
            lost_quantities[allocation.order_id] -= allocation.quantity
    if not any(lost_quantities.values()):
        return 0
    model = cp_model.CpModel()
    remaining: dict[str, cp_model.IntVar] = {}
    recourse: dict[tuple[str, str], cp_model.IntVar] = {}
    for order in orders:
        quantity = lost_quantities[order.id]
        remaining[order.id] = model.NewIntVar(0, quantity, f"remain_{scenario.id}_{order.id}")
        eligible = []
        if quantity:
            for source in sources:
                if source.id in failed or not source.available or not source.contract_approved:
                    continue
                if source.product_id != order.product_id or source.lead_days > order.due_days:
                    continue
                variable = model.NewIntVar(0, quantity, f"rec_{scenario.id}_{source.id}_{order.id}")
                recourse[(source.id, order.id)] = variable
                eligible.append(variable)
        model.Add(sum(eligible) + remaining[order.id] == quantity)
    for source in sources:
        variables = [var for (sid, _), var in recourse.items() if sid == source.id]
        if variables:
            used = sum(a.quantity for a in allocations if a.source_id == source.id)
            model.Add(sum(variables) <= max(0, source.capacity - used))
    model.Minimize(sum(order.priority * remaining[order.id] for order in orders))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    solver.parameters.max_time_in_seconds = 20
    status = solver.Solve(model)
    if status != cp_model.OPTIMAL:
        raise RuntimeError(
            f"CP-SAT could not prove stress recourse optimum (status={solver.StatusName(status)})"
        )
    return sum(order.priority * solver.Value(remaining[order.id]) for order in orders)


def optimize_recovery(
    incident_id: str,
    graph_version: int,
    sources: Sequence[Source],
    orders: Sequence[OrderDemand],
    *,
    failed_entity_ids: Iterable[str] = (),
    correlated_scenarios: Sequence[FailureScenario] = (),
    max_iterations: int = 8,
    prior_supplier_ids: Iterable[str] = (),
) -> RecoveryPlan:
    """Solve current recovery and add the worst unseen single/correlated outage per iteration.

    ``correlated_scenarios`` must be derived by graph traversal; failed IDs must identify
    source IDs represented in ``sources``. Amounts are integer units and prices are minor units.
    """
    cost_units = {(source.currency, source.minor_units_per_major) for source in sources}
    if len(cost_units) > 1:
        raise ValueError("recovery sources must use one currency and minor-unit scale")
    currency, minor_units_per_major = next(iter(cost_units), ("USD", 100))
    if max_iterations < 0:
        raise ValueError("max_iterations must be non-negative")
    if len({s.id for s in sources}) != len(sources) or len({o.id for o in orders}) != len(orders):
        raise ValueError("source and order IDs must be unique")
    sources = sorted(sources, key=lambda item: item.id)
    orders = sorted(orders, key=lambda item: item.id)
    failed = set(failed_entity_ids)
    if any(s.capacity < 0 or s.unit_price_minor < 0 for s in sources):
        raise ValueError("source capacity and minor-unit price must be non-negative")
    candidates = [
        FailureScenario(
            id=f"single:{s.id}", failed_entity_ids=[s.id], label=f"Single outage: {s.label}"
        )
        for s in sorted(sources, key=lambda item: item.id)
        if s.available and s.id not in failed
    ] + [
        scenario
        for scenario in correlated_scenarios
        if not (set(scenario.failed_entity_ids) & failed)
    ]
    candidates_by_id = {scenario.id: scenario for scenario in candidates}
    known_source_ids = {source.id for source in sources}
    for scenario in correlated_scenarios:
        unknown = set(scenario.failed_entity_ids) - known_source_ids
        if unknown:
            raise ValueError(
                f"correlated scenario {scenario.id!r} contains non-source failure IDs: {sorted(unknown)}"
            )
    selected: list[FailureScenario] = []
    added = 0
    while True:
        allocations, unmet, values = _solve_lexicographic(
            sources, orders, failed, selected, set(prior_supplier_ids)
        )
        unseen = [s for s in candidates if s.id not in {item.id for item in selected}]
        if not unseen or added >= max_iterations:
            break
        scored = [
            (_scenario_shortfall(s, sources, orders, allocations, failed), s.id, s) for s in unseen
        ]
        score, _, counterexample = max(scored, key=lambda item: (item[0], item[1]))
        if score == 0:
            break
        selected.append(counterexample)
        added += 1

    tested = list(candidates_by_id.values())
    scores = [(s, _scenario_shortfall(s, sources, orders, allocations, failed)) for s in tested]
    worst_single = max((score for s, score in scores if len(s.failed_entity_ids) == 1), default=0)
    worst_pair = max((score for s, score in scores if len(s.failed_entity_ids) == 2), default=0)
    worst_scenario = max(scores, key=lambda item: (item[1], item[0].id), default=(None, 0))
    evidence = sorted({e for source in sources for e in source.evidence_ids})
    return RecoveryPlan(
        id=f"plan:{incident_id}:{graph_version}",
        incident_id=incident_id,
        graph_version=graph_version,
        allocations=allocations,
        unmet_by_order=unmet,
        objective=PlanObjective(
            current_weighted_shortfall=values["current"],
            worst_single_failure_shortfall=worst_single,
            worst_correlated_pair_shortfall=worst_pair,
            incremental_cost_minor=values["cost"],
            supplier_changes=values["changes"],
            currency=currency,
            minor_units_per_major=minor_units_per_major,
        ),
        tested_scenarios=tested,
        worst_counterexample=worst_scenario[0] if worst_scenario[0] and worst_scenario[1] else None,
        stress_passed=values["current"] == 0 and all(score == 0 for _, score in scores),
        stress_iterations=added,
        evidence_ids=evidence,
        assumptions=[
            "Stress scenarios are deterministic modeled outages; no failure probabilities are assumed.",
            "Scenario recourse may use only unused capacity after surviving first-stage allocations.",
        ],
    )


def solve_allocation(
    sources: Sequence[Source],
    orders: Sequence[OrderDemand],
    *,
    failed_entity_ids: Iterable[str] = (),
) -> tuple[list[Allocation], dict[str, int]]:
    """Return the minimum-shortfall, then minimum-cost allocation for an impact snapshot."""
    sources = sorted(sources, key=lambda item: item.id)
    orders = sorted(orders, key=lambda item: item.id)
    allocations, unmet, _ = _solve_lexicographic(sources, orders, set(failed_entity_ids), (), set())
    return allocations, unmet
