from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Mode(StrEnum):
    SIMULATION = "SIMULATION"
    LIVE_READ_ONLY = "LIVE_READ_ONLY"


class IncidentStatus(StrEnum):
    DETECTED = "DETECTED"
    VALIDATED = "VALIDATED"
    ANALYZED = "ANALYZED"
    PLANNED = "PLANNED"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    VERIFIED = "VERIFIED"
    RECOVERED = "RECOVERED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    REPLAN_REQUIRED = "REPLAN_REQUIRED"
    PARTIALLY_RECOVERED = "PARTIALLY_RECOVERED"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"


class Source(BaseModel):
    id: str
    label: str
    kind: Literal["supplier", "inventory"]
    product_id: str
    capacity: int = Field(ge=0)
    unit_price_minor: int = Field(ge=0)
    currency: str = "USD"
    lead_days: int = Field(ge=0)
    available: bool = True
    contract_approved: bool = True
    evidence_ids: list[str] = Field(default_factory=list)


class OrderDemand(BaseModel):
    id: str
    product_id: str
    quantity: int = Field(gt=0)
    priority: int = Field(default=1, ge=1, le=5)
    due_days: int = Field(default=30, ge=0)


class Allocation(BaseModel):
    source_id: str
    order_id: str
    product_id: str
    quantity: int = Field(gt=0)
    unit_price_minor: int = Field(ge=0)
    lead_days: int = Field(ge=0)


class FailureScenario(BaseModel):
    id: str
    failed_entity_ids: list[str] = Field(min_length=1, max_length=2)
    paths: list[list[str]] = Field(default_factory=list)
    label: str


class PlanObjective(BaseModel):
    current_weighted_shortfall: int
    worst_single_failure_shortfall: int
    worst_correlated_pair_shortfall: int
    incremental_cost_minor: int
    supplier_changes: int


class RecoveryPlan(BaseModel):
    id: str
    incident_id: str
    graph_version: int
    allocations: list[Allocation]
    unmet_by_order: dict[str, int]
    objective: PlanObjective
    tested_scenarios: list[FailureScenario] = Field(default_factory=list)
    worst_counterexample: FailureScenario | None = None
    stress_passed: bool = False
    stress_iterations: int = 0
    evidence_ids: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class Incident(BaseModel):
    id: str
    scenario_id: str
    entity_id: str
    incident_type: str
    severity: int = Field(ge=1, le=5)
    status: IncidentStatus = IncidentStatus.DETECTED
    mode: Mode = Mode.SIMULATION
    graph_version: int
    created_at: datetime = Field(default_factory=utc_now)


class ActionReceipt(BaseModel):
    id: str
    action_id: str
    idempotency_key: str
    status: Literal["APPLIED", "REJECTED", "DUPLICATE"]
    source_id: str
    order_id: str
    quantity: int
    created_at: datetime = Field(default_factory=utc_now)
    detail: str


class RecoveryResult(BaseModel):
    run_id: str
    incident_id: str
    status: IncidentStatus
    receipts: list[ActionReceipt]
    verified_allocations: list[Allocation]
    remaining_shortfall: int
    graph_version: int
