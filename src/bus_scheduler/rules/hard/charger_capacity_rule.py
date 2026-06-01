"""Hard rule: station must have a valid charger slot index."""

from __future__ import annotations

from bus_scheduler.rules.base import HardRuleResult, RuleContext


class ChargerCapacityHardRule:
    """Ensure chosen charger slot exists for the station."""

    name = "ChargerCapacityHardRule"

    def validate(self, context: RuleContext) -> HardRuleResult:
        station_state = context.runtime.station_states.get(context.candidate.station_id)
        if station_state is None:
            return HardRuleResult(
                rule_name=self.name,
                is_valid=False,
                reason="Station state not found.",
            )
        slot_count = len(station_state.charger_available_at)
        if context.candidate.candidate_index >= slot_count:
            return HardRuleResult(
                rule_name=self.name,
                is_valid=False,
                reason="Charger slot index out of range.",
            )
        return HardRuleResult(rule_name=self.name, is_valid=True)

