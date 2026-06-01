"""Soft rule: minimize network-level completion latency."""

from __future__ import annotations

from bus_scheduler.rules.base import RuleContext, SoftRuleResult


class NetworkEfficiencySoftRule:
    """Use charge end timestamp as a local proxy for network congestion."""

    name = "NetworkEfficiencySoftRule"
    weight_key = "overall"

    def score(self, context: RuleContext) -> SoftRuleResult:
        midnight = context.candidate.charge_end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        elapsed_minutes = (context.candidate.charge_end_time - midnight).total_seconds() / 60
        score_value = float(elapsed_minutes)
        return SoftRuleResult(rule_name=self.name, score=score_value)

