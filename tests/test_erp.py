from __future__ import annotations

import pytest

from anchor.erp import (
    ERP,
    ConflictingAllocation,
    InjectedExecutionFailure,
    InsufficientCapacity,
    InsufficientInventory,
)
from anchor.models import ActionReceipt, Allocation


@pytest.fixture
def erp(tmp_path):
    adapter = ERP(tmp_path / "erp.sqlite3")
    adapter.reset(
        {
            "sources": [
                {"id": "warehouse", "kind": "inventory", "product_id": "chip", "capacity": 5},
                {
                    "id": "supplier",
                    "kind": "supplier",
                    "product_id": "chip",
                    "capacity": 10,
                    "unit_price_minor": 125,
                    "lead_days": 3,
                },
            ],
            "orders": [{"id": "order-1", "product_id": "chip", "quantity": 10}],
        }
    )
    return adapter


def allocation(source_id: str, quantity: int, price: int = 0, lead: int = 0) -> Allocation:
    return Allocation(
        source_id=source_id,
        order_id="order-1",
        product_id="chip",
        quantity=quantity,
        unit_price_minor=price,
        lead_days=lead,
    )


def test_success_persists_state_and_typed_receipt(erp, tmp_path):
    receipt = erp.apply_allocation(allocation("warehouse", 5), "reserve-stock-1")

    assert isinstance(receipt, ActionReceipt)
    assert receipt.status == "APPLIED"
    assert erp.read_allocations() == [allocation("warehouse", 5)]
    state = ERP(tmp_path / "erp.sqlite3").current_state()
    assert state["allocations"] == [allocation("warehouse", 5)]
    assert state["orders"][0]["status"] == "PARTIALLY_ALLOCATED"


def test_rejects_insufficient_inventory_and_supplier_capacity(erp):
    with pytest.raises(InsufficientInventory):
        erp.apply_allocation(allocation("warehouse", 6), "too-much-stock")
    with pytest.raises(InsufficientCapacity):
        erp.apply_allocation(allocation("supplier", 11, 125, 3), "too-much-capacity")
    assert erp.read_allocations() == []


def test_injected_reservation_failure_is_one_shot_and_does_not_mutate_state(erp):
    erp.inject_reservation_failure_once("supplier")

    with pytest.raises(InjectedExecutionFailure, match="one-time reservation rejection"):
        erp.apply_allocation(allocation("supplier", 4, 125, 3), "retryable-failure")

    assert erp.read_allocations() == []
    assert (
        erp.apply_allocation(allocation("supplier", 4, 125, 3), "retryable-failure").status
        == "APPLIED"
    )


def test_idempotency_returns_duplicate_receipt_and_conflicts_are_rejected(erp):
    first = erp.apply_allocation(allocation("supplier", 4, 125, 3), "purchase-1")
    second = erp.apply_allocation(allocation("supplier", 4, 125, 3), "purchase-1")
    assert first.status == "APPLIED"
    assert second.status == "DUPLICATE"
    assert second.id == first.id
    assert len(erp.read_allocations()) == 1

    with pytest.raises(ConflictingAllocation):
        erp.apply_allocation(allocation("supplier", 3, 125, 3), "purchase-2")


def test_release_restores_capacity_for_a_later_allocation(erp):
    erp.apply_allocation(allocation("warehouse", 5), "reserve-1")
    released = erp.release_allocation("warehouse", "order-1", "release-1")
    assert released.status == "APPLIED"
    assert erp.read_allocations() == []
    duplicate = erp.release_allocation("warehouse", "order-1", "release-1")
    assert duplicate.status == "DUPLICATE"
    erp.apply_allocation(allocation("warehouse", 5), "reserve-2")
    assert erp.read_allocations() == [allocation("warehouse", 5)]


def test_reset_clears_releases_before_referenced_allocations(erp):
    erp.apply_allocation(allocation("warehouse", 5), "reserve-before-reset")
    erp.release_allocation("warehouse", "order-1", "release-before-reset")

    erp.reset(
        {
            "sources": [
                {"id": "warehouse", "kind": "inventory", "product_id": "chip", "capacity": 5}
            ],
            "orders": [{"id": "order-1", "product_id": "chip", "quantity": 10}],
        }
    )

    assert erp.read_allocations() == []
    assert erp.current_state()["orders"][0]["status"] == "OPEN"


def test_verify_detects_read_back_mismatch(erp):
    planned = [allocation("warehouse", 5)]
    assert erp.verify(planned) is False
    erp.apply_allocation(planned[0], "reserve-stock-1")
    assert erp.verify(planned) is True
    assert erp.verify([allocation("warehouse", 4)]) is False
