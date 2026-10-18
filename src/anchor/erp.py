"""Persistent, simulation-only ERP adapter backed by SQLite."""

from __future__ import annotations

import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from .config import settings
from .models import ActionReceipt, Allocation


class SimulationOnlyError(RuntimeError):
    """Raised if the adapter is configured for anything but simulation."""


class ERPError(RuntimeError):
    """Base error for invalid or infeasible simulated ERP operations."""


class InsufficientInventory(ERPError):
    pass


class InsufficientCapacity(ERPError):
    pass


class ConflictingAllocation(ERPError):
    pass


class InjectedExecutionFailure(ERPError):
    pass


class ERP:
    """A durable mock ERP; all mutations are local and simulation-only.

    ``seed_state`` for :meth:`reset` is a mapping containing ``sources`` and
    ``orders`` arrays. Source records need ``id``, ``kind`` (``inventory`` or
    ``supplier``), and integer ``capacity``; order records need ``id``,
    ``product_id``, and integer ``quantity``. Optional source fields are
    ``available``, ``unit_price_minor``, ``lead_days``; optional order fields
    are ``status`` and ``scheduled_days``.
    """

    def __init__(self, path: str | Path | None = None, mode: str = "SIMULATION") -> None:
        if mode != "SIMULATION":
            raise SimulationOnlyError("The ERP adapter supports SIMULATION mode only")
        self.path = str(path if path is not None else settings.erp_path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS sources (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL CHECK(kind IN ('inventory', 'supplier')),
                    product_id TEXT NOT NULL,
                    capacity INTEGER NOT NULL CHECK(capacity >= 0),
                    available INTEGER NOT NULL CHECK(available IN (0, 1)),
                    unit_price_minor INTEGER NOT NULL CHECK(unit_price_minor >= 0),
                    lead_days INTEGER NOT NULL CHECK(lead_days >= 0)
                );
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    status TEXT NOT NULL,
                    scheduled_days INTEGER NOT NULL CHECK(scheduled_days >= 0)
                );
                CREATE TABLE IF NOT EXISTS allocations (
                    id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    source_id TEXT NOT NULL REFERENCES sources(id),
                    order_id TEXT NOT NULL REFERENCES orders(id),
                    product_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    unit_price_minor INTEGER NOT NULL CHECK(unit_price_minor >= 0),
                    lead_days INTEGER NOT NULL CHECK(lead_days >= 0),
                    created_at TEXT NOT NULL,
                    released INTEGER NOT NULL DEFAULT 0 CHECK(released IN (0, 1))
                );
                CREATE UNIQUE INDEX IF NOT EXISTS one_active_source_order
                    ON allocations(source_id, order_id) WHERE released = 0;
                CREATE TABLE IF NOT EXISTS releases (
                    id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    allocation_id TEXT NOT NULL REFERENCES allocations(id),
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS execution_faults (
                    source_id TEXT PRIMARY KEY
                );
                """
            )

    @staticmethod
    def _nonnegative_int(value: Any, field: str, *, positive: bool = False) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < (1 if positive else 0):
            raise ValueError(f"{field} must be an integer >= {1 if positive else 0}")
        return value

    def reset(self, seed_state: dict[str, Any]) -> None:
        """Atomically replace local mock inventory, supplier, and order state."""
        sources = seed_state.get("sources")
        orders = seed_state.get("orders")
        if not isinstance(sources, list) or not isinstance(orders, list):
            raise TypeError("seed_state requires sources and orders lists")
        validated_sources = []
        for source in sources:
            kind = source.get("kind")
            if kind not in ("inventory", "supplier"):
                raise ValueError("source kind must be inventory or supplier")
            validated_sources.append(
                (
                    str(source["id"]),
                    kind,
                    str(source["product_id"]),
                    self._nonnegative_int(source["capacity"], "capacity"),
                    int(bool(source.get("available", True))),
                    self._nonnegative_int(source.get("unit_price_minor", 0), "unit_price_minor"),
                    self._nonnegative_int(source.get("lead_days", 0), "lead_days"),
                )
            )
        validated_orders = []
        for order in orders:
            validated_orders.append(
                (
                    str(order["id"]),
                    str(order["product_id"]),
                    self._nonnegative_int(order["quantity"], "order quantity", positive=True),
                    str(order.get("status", "OPEN")),
                    self._nonnegative_int(order.get("scheduled_days", 0), "scheduled_days"),
                )
            )
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM execution_faults")
            db.execute("DELETE FROM releases")
            db.execute("DELETE FROM allocations")
            db.execute("DELETE FROM orders")
            db.execute("DELETE FROM sources")
            db.executemany("INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?)", validated_sources)
            db.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", validated_orders)
            db.commit()

    def inject_reservation_failure_once(self, source_id: str) -> None:
        """Reject the next reservation attempt for one synthetic supplier."""
        with self._connect() as db:
            source = db.execute("SELECT kind FROM sources WHERE id = ?", (source_id,)).fetchone()
            if source is None or source["kind"] != "supplier":
                raise ERPError(f"unknown simulated supplier '{source_id}'")
            db.execute(
                "INSERT OR REPLACE INTO execution_faults (source_id) VALUES (?)", (source_id,)
            )

    def current_state(self) -> dict[str, Any]:
        """Return the durable source, order, and allocation state."""
        with self._connect() as db:
            sources = [dict(row) for row in db.execute("SELECT * FROM sources ORDER BY id")]
            orders = [dict(row) for row in db.execute("SELECT * FROM orders ORDER BY id")]
            allocations = self.read_allocations()
        for source in sources:
            source["available"] = bool(source["available"])
        return {
            "mode": "SIMULATION",
            "sources": sources,
            "orders": orders,
            "allocations": allocations,
        }

    def set_capacity(self, source_id: str, capacity: int) -> None:
        """Apply an allowlisted simulated capacity change to the ERP source record."""
        value = self._nonnegative_int(capacity, "capacity")
        with self._connect() as db:
            cursor = db.execute("UPDATE sources SET capacity = ? WHERE id = ?", (value, source_id))
            if cursor.rowcount != 1:
                raise ERPError(f"unknown simulated source '{source_id}'")

    def apply_allocation(
        self, allocation: Allocation | dict[str, Any], idempotency_key: str
    ) -> ActionReceipt:
        """Reserve inventory or supplier capacity and persist its purchase allocation.

        Repeating an idempotency key returns its original receipt as DUPLICATE.
        A different key for an already allocated source/order pair is rejected.
        """
        item = Allocation.model_validate(allocation)
        if not idempotency_key or not idempotency_key.strip():
            raise ValueError("idempotency_key must be non-empty")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            fault = db.execute(
                "SELECT 1 FROM execution_faults WHERE source_id = ?", (item.source_id,)
            ).fetchone()
            if fault:
                db.execute("DELETE FROM execution_faults WHERE source_id = ?", (item.source_id,))
                db.commit()
                raise InjectedExecutionFailure(
                    f"Injected one-time reservation rejection for supplier '{item.source_id}'"
                )
            prior = db.execute(
                "SELECT * FROM allocations WHERE idempotency_key = ?", (idempotency_key,)
            ).fetchone()
            if prior:
                if (
                    prior["source_id"],
                    prior["order_id"],
                    prior["product_id"],
                    prior["quantity"],
                ) != (item.source_id, item.order_id, item.product_id, item.quantity):
                    raise ConflictingAllocation(
                        "idempotency key was already used for another allocation"
                    )
                return self._receipt(prior, "DUPLICATE", "Previously applied request")

            conflict = db.execute(
                "SELECT * FROM allocations WHERE source_id = ? AND order_id = ? AND released = 0",
                (item.source_id, item.order_id),
            ).fetchone()
            if conflict:
                if (
                    conflict["product_id"],
                    conflict["quantity"],
                    conflict["unit_price_minor"],
                    conflict["lead_days"],
                ) == (item.product_id, item.quantity, item.unit_price_minor, item.lead_days):
                    return self._receipt(
                        conflict, "DUPLICATE", "Identical allocation is already active"
                    )
                raise ConflictingAllocation("source/order allocation already exists")
            source = db.execute("SELECT * FROM sources WHERE id = ?", (item.source_id,)).fetchone()
            order = db.execute("SELECT * FROM orders WHERE id = ?", (item.order_id,)).fetchone()
            if source is None or order is None:
                raise ERPError("unknown source or order")
            if not source["available"]:
                raise ERPError("source is unavailable")
            if source["product_id"] != item.product_id or order["product_id"] != item.product_id:
                raise ERPError("source, order, and allocation product IDs must match")
            if (
                item.unit_price_minor != source["unit_price_minor"]
                or item.lead_days != source["lead_days"]
            ):
                raise ERPError("allocation price and lead time must match current source state")
            source_used = db.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM allocations WHERE source_id = ? AND released = 0",
                (item.source_id,),
            ).fetchone()[0]
            order_used = db.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM allocations WHERE order_id = ? AND released = 0",
                (item.order_id,),
            ).fetchone()[0]
            if source_used + item.quantity > source["capacity"]:
                error = (
                    InsufficientInventory if source["kind"] == "inventory" else InsufficientCapacity
                )
                raise error(f"allocation exceeds remaining {source['kind']} quantity")
            if order_used + item.quantity > order["quantity"]:
                raise ERPError("allocation exceeds remaining order demand")

            receipt_id = str(uuid.uuid4())
            created = datetime.now(UTC).isoformat()
            db.execute(
                """INSERT INTO allocations
                (id, idempotency_key, source_id, order_id, product_id, quantity,
                 unit_price_minor, lead_days, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    receipt_id,
                    idempotency_key,
                    item.source_id,
                    item.order_id,
                    item.product_id,
                    item.quantity,
                    item.unit_price_minor,
                    item.lead_days,
                    created,
                ),
            )
            total = order_used + item.quantity
            status = "ALLOCATED" if total == order["quantity"] else "PARTIALLY_ALLOCATED"
            db.execute(
                "UPDATE orders SET status = ?, scheduled_days = MAX(scheduled_days, ?) WHERE id = ?",
                (status, item.lead_days, item.order_id),
            )
            row = db.execute("SELECT * FROM allocations WHERE id = ?", (receipt_id,)).fetchone()
            db.commit()
            return self._receipt(row, "APPLIED", "Allocation persisted and order updated")

    @staticmethod
    def _receipt(row: sqlite3.Row, status: str, detail: str) -> ActionReceipt:
        return ActionReceipt(
            id=row["id"],
            action_id=row["id"],
            idempotency_key=row["idempotency_key"],
            status=status,
            source_id=row["source_id"],
            order_id=row["order_id"],
            quantity=row["quantity"],
            created_at=datetime.fromisoformat(row["created_at"]),
            detail=detail,
        )

    def release_allocation(
        self, source_id: str, order_id: str, idempotency_key: str
    ) -> ActionReceipt:
        """Release a previously applied reservation, exactly once per request key."""
        if not idempotency_key or not idempotency_key.strip():
            raise ValueError("idempotency_key must be non-empty")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                """SELECT a.*, r.idempotency_key AS release_key, r.created_at AS release_time
                FROM releases r JOIN allocations a ON a.id = r.allocation_id
                WHERE r.idempotency_key = ?""",
                (idempotency_key,),
            ).fetchone()
            if prior:
                if (prior["source_id"], prior["order_id"]) != (source_id, order_id):
                    raise ConflictingAllocation(
                        "idempotency key was already used for another release"
                    )
                prior_row = dict(prior)
                prior_row["idempotency_key"] = prior["release_key"]
                prior_row["created_at"] = prior["release_time"]
                return self._receipt(prior_row, "DUPLICATE", "Previously applied release")
            row = db.execute(
                "SELECT * FROM allocations WHERE source_id = ? AND order_id = ? AND released = 0",
                (source_id, order_id),
            ).fetchone()
            if row is None:
                raise ERPError("no active allocation exists for this source and order")
            now = datetime.now(UTC).isoformat()
            release_id = str(uuid.uuid4())
            db.execute("UPDATE allocations SET released = 1 WHERE id = ?", (row["id"],))
            db.execute(
                "INSERT INTO releases VALUES (?, ?, ?, ?)",
                (release_id, idempotency_key, row["id"], now),
            )
            active = db.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM allocations WHERE order_id = ? AND released = 0",
                (order_id,),
            ).fetchone()[0]
            db.execute(
                "UPDATE orders SET status = ? WHERE id = ?",
                ("OPEN" if active == 0 else "PARTIALLY_ALLOCATED", order_id),
            )
            receipt_row = dict(row)
            receipt_row["id"] = release_id
            receipt_row["idempotency_key"] = idempotency_key
            receipt_row["created_at"] = now
            db.commit()
            return self._receipt(receipt_row, "APPLIED", "Allocation released")

    def read_allocations(self) -> list[Allocation]:
        """Read back persisted allocations in a form usable by the planner."""
        with self._connect() as db:
            rows = db.execute(
                """SELECT source_id, order_id, product_id, quantity, unit_price_minor, lead_days
                FROM allocations WHERE released = 0 ORDER BY source_id, order_id"""
            ).fetchall()
        return [Allocation.model_validate(dict(row)) for row in rows]

    def verify(self, plan_allocations: list[Allocation | dict[str, Any]]) -> bool:
        """Return whether ERP read-back exactly matches the requested allocation plan."""
        expected = TypeAdapter(list[Allocation]).validate_python(plan_allocations)
        key = lambda a: (
            a.source_id,
            a.order_id,
            a.product_id,
            a.quantity,
            a.unit_price_minor,
            a.lead_days,
        )
        return sorted(map(key, self.read_allocations())) == sorted(map(key, expected))
