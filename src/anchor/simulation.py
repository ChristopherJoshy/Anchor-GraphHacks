"""Deterministic production impact calculations over validated graph-derived inputs."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from anchor.models import OrderDemand, Source
from anchor.optimizer import solve_allocation


def simulate_production_impact(
    sources: Sequence[Source],
    orders: Sequence[OrderDemand],
    *,
    failed_entity_ids: Iterable[str] = (),
) -> dict[str, object]:
    """Calculate deterministic order shortfall after outages in the supplied source set.

    Inputs are operational facts already resolved by the caller (typically from FalkorDB).
    This function does not infer dependencies, probabilities, or supplier facts.
    """
    failed = set(failed_entity_ids)
    allocations, unmet = solve_allocation(sources, orders, failed_entity_ids=failed)
    demand = sum(order.quantity for order in orders)
    shortfall = sum(unmet.values())
    weighted_demand = sum(order.quantity * order.priority for order in orders)
    weighted_shortfall = sum(unmet[o.id] * o.priority for o in orders)
    return {
        "failed_entity_ids": sorted(failed),
        "affected_source_ids": sorted(source.id for source in sources if source.id in failed),
        "orders": [
            {
                "order_id": order.id,
                "product_id": order.product_id,
                "required_units": order.quantity,
                "unmet_units": unmet[order.id],
                "fulfilled_units": order.quantity - unmet[order.id],
                "priority": order.priority,
                "due_days": order.due_days,
            }
            for order in orders
        ],
        "allocations": [allocation.model_dump(mode="json") for allocation in allocations],
        "total_demand_units": demand,
        "fulfilled_units": demand - shortfall,
        "unmet_units": shortfall,
        "weighted_unmet_demand": weighted_shortfall,
        "cascade_exposure_score": weighted_shortfall / weighted_demand if weighted_demand else 0.0,
        "assumptions": [
            "Source capacity is available within the order due date only when lead_days <= due_days.",
            "The caller supplies graph-resolved source availability and capacity; no upstream facts are inferred here.",
            "Exposure is weighted unmet demand divided by weighted demand, not an established external risk index.",
        ],
    }
