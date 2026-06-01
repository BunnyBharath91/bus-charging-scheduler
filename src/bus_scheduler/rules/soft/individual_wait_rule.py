"""Soft rule: minimize individual bus waiting."""

from __future__ import annotations

from bus_scheduler.rules.base import RuleContext, SoftRuleResult


class IndividualWaitSoftRule:
    """Score by candidate wait minutes."""

    name = "IndividualWaitSoftRule"
    weight_key = "individual"

    def score(self, context: RuleContext) -> SoftRuleResult:
        return SoftRuleResult(rule_name=self.name, score=float(context.candidate.wait_minutes))

