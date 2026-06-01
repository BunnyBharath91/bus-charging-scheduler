"""Weight tuning behavior tests."""

from __future__ import annotations

from datetime import datetime

from bus_scheduler.models.runtime import RuntimeContext, StationRuntimeState
from bus_scheduler.models.scenario import WeightConfig
from bus_scheduler.rules.base import ChargingCandidate, HardRuleResult, RuleContext, SoftRuleResult
from bus_scheduler.scheduler.decision import evaluate_candidate


class AlwaysValidHardRule:
    name = "AlwaysValidHardRule"

    def validate(self, context: RuleContext) -> HardRuleResult:
        return HardRuleResult(rule_name=self.name, is_valid=True)


class UnitIndividualSoftRule:
    name = "UnitIndividualSoftRule"
    weight_key = "individual"

    def score(self, context: RuleContext) -> SoftRuleResult:
        return SoftRuleResult(rule_name=self.name, score=2.0)


class UnitOperatorSoftRule:
    name = "UnitOperatorSoftRule"
    weight_key = "operator"

    def score(self, context: RuleContext) -> SoftRuleResult:
        return SoftRuleResult(rule_name=self.name, score=3.0)


def test_weight_values_change_total_score() -> None:
    now = datetime(2026, 1, 1, 19, 0)
    candidate = ChargingCandidate(
        bus_id="bus-1",
        operator_id="kpn",
        station_id="A",
        candidate_index=0,
        arrival_time=now,
        wait_minutes=0,
        charge_start_time=now,
        charge_end_time=now,
    )
    runtime = RuntimeContext(
        operator_total_wait_minutes={"kpn": 0},
        station_states={"A": StationRuntimeState(station_id="A", charger_available_at=[now])},
    )
    base_weights = WeightConfig(individual=1.0, operator=1.0, overall=1.0)
    adjusted_weights = WeightConfig(individual=2.0, operator=4.0, overall=1.0)

    base_result = evaluate_candidate(
        candidate=candidate,
        runtime_context=runtime,
        hard_rules=[AlwaysValidHardRule()],
        soft_rules=[UnitIndividualSoftRule(), UnitOperatorSoftRule()],
        weights=base_weights,
    )
    adjusted_result = evaluate_candidate(
        candidate=candidate,
        runtime_context=runtime,
        hard_rules=[AlwaysValidHardRule()],
        soft_rules=[UnitIndividualSoftRule(), UnitOperatorSoftRule()],
        weights=adjusted_weights,
    )

    assert base_result is not None
    assert adjusted_result is not None
    assert base_result.total_weighted_score == 5.0
    assert adjusted_result.total_weighted_score == 16.0

