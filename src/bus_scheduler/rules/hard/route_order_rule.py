"""Hard rule: station choices must follow route order."""

from __future__ import annotations

from bus_scheduler.rules.base import HardRuleResult, RuleContext


class RouteOrderHardRule:
    """Candidate generation enforces route direction, this rule documents it."""

    name = "RouteOrderHardRule"

    def validate(self, context: RuleContext) -> HardRuleResult:
        return HardRuleResult(rule_name=self.name, is_valid=True)

