from anchor.erp import ERP
from anchor.models import Allocation, RecoveryPlan
from anchor.service import AnchorService


class GraphFixture:
    def __init__(self):
        self.current_version = 1
        self.saved_plans = {}
        self.receipts = []
        self.outcomes = []

    def version(self):
        return self.current_version

    def get_plan(self, plan_id):
        return self.saved_plans.get(plan_id)

    def persist_receipt(self, run_id, receipt):
        self.receipts.append(dict(receipt, run_id=run_id))

    def run_receipts(self, run_id):
        return [row for row in self.receipts if row["run_id"] == run_id]

    def record_run_outcome(self, plan_id, incident_id, status):
        self.outcomes.append((plan_id, incident_id, status))


def test_execute_replaces_prior_plan_and_verifies_run_readback(tmp_path):
    erp = ERP(tmp_path / "erp.sqlite3")
    sources = [
        {"id": "INV", "kind": "inventory", "product_id": "MCU", "capacity": 350},
        {
            "id": "D",
            "kind": "supplier",
            "product_id": "MCU",
            "capacity": 650,
            "unit_price_minor": 900,
        },
        {
            "id": "E",
            "kind": "supplier",
            "product_id": "MCU",
            "capacity": 250,
            "unit_price_minor": 1250,
        },
    ]
    erp.reset(
        {"sources": sources, "orders": [{"id": "ORDER", "product_id": "MCU", "quantity": 1000}]}
    )
    graph = GraphFixture()
    service = AnchorService(graph=graph, erp=erp)
    first = RecoveryPlan(
        id="PLAN-1",
        incident_id="INC-1",
        graph_version=1,
        allocations=[
            Allocation(
                source_id="INV",
                order_id="ORDER",
                product_id="MCU",
                quantity=350,
                unit_price_minor=0,
                lead_days=0,
            ),
            Allocation(
                source_id="D",
                order_id="ORDER",
                product_id="MCU",
                quantity=650,
                unit_price_minor=900,
                lead_days=0,
            ),
        ],
        unmet_by_order={"ORDER": 0},
        objective={
            "current_weighted_shortfall": 0,
            "worst_single_failure_shortfall": 0,
            "worst_correlated_pair_shortfall": 0,
            "incremental_cost_minor": 585000,
            "supplier_changes": 1,
        },
    )
    service._plans[first.id] = first
    first_run = service.execute(first.id)
    assert first_run["status"] == "RECOVERED"
    assert service.verify(first_run["run_id"])["verified"]

    erp.set_capacity("D", 450)
    graph.current_version = 2
    second = RecoveryPlan(
        id="PLAN-2",
        incident_id="INC-1",
        graph_version=2,
        allocations=[
            Allocation(
                source_id="INV",
                order_id="ORDER",
                product_id="MCU",
                quantity=350,
                unit_price_minor=0,
                lead_days=0,
            ),
            Allocation(
                source_id="D",
                order_id="ORDER",
                product_id="MCU",
                quantity=450,
                unit_price_minor=900,
                lead_days=0,
            ),
            Allocation(
                source_id="E",
                order_id="ORDER",
                product_id="MCU",
                quantity=200,
                unit_price_minor=1250,
                lead_days=0,
            ),
        ],
        unmet_by_order={"ORDER": 0},
        objective={
            "current_weighted_shortfall": 0,
            "worst_single_failure_shortfall": 0,
            "worst_correlated_pair_shortfall": 0,
            "incremental_cost_minor": 655000,
            "supplier_changes": 2,
        },
    )
    service._plans[second.id] = second
    second_run = service.execute(second.id)
    assert second_run["status"] == "RECOVERED"
    assert {a.source_id: a.quantity for a in erp.read_allocations()} == {
        "INV": 350,
        "D": 450,
        "E": 200,
    }
    assert service.verify(second_run["run_id"])["verified"]
    assert not service.verify(first_run["run_id"])["verified"]
