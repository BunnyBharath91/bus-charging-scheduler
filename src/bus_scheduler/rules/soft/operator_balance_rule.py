"""Soft rule: reduce operator-level delay skew."""

from __future__ import annotations

from bus_scheduler.rules.base import RuleContext, SoftRuleResult


class OperatorBalanceSoftRule:
    """Penalize candidates that increase already-high operator delay."""

    name = "OperatorBalanceSoftRule"
    weight_key = "operator"

    def score(self, context: RuleContext) -> SoftRuleResult:
        current_operator_wait = context.runtime.operator_total_wait_minutes.get(
            context.candidate.operator_id,
            0,
        )
        projected_wait = current_operator_wait + context.candidate.wait_minutes
        return SoftRuleResult(rule_name=self.name, score=float(projected_wait))

