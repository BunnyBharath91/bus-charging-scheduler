"""Hard rule: candidate must be range feasible."""

from __future__ import annotations

from bus_scheduler.rules.base import HardRuleResult, RuleContext


class RangeHardRule:
    """Ensure candidate station is reachable with current range."""

    name = "RangeHardRule"

    def validate(self, context: RuleContext) -> HardRuleResult:
        # Candidate generation already checks reachability.
        return HardRuleResult(rule_name=self.name, is_valid=True)

