"""Decision scoring for charging candidates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

from bus_scheduler.models.runtime import RuntimeContext
from bus_scheduler.models.scenario import WeightConfig
from bus_scheduler.rules.base import ChargingCandidate, HardRule, RuleContext, SoftRule
from bus_scheduler.scheduler.conflict_resolution import build_tie_break_key


@dataclass(slots=True)
class EvaluatedCandidate:
    """Candidate plus rule diagnostics and weighted score."""

    candidate: ChargingCandidate
    hard_results: Dict[str, bool]
    soft_scores: Dict[str, float]
    total_weighted_score: float


def evaluate_candidate(
    candidate: ChargingCandidate,
    runtime_context: RuntimeContext,
    hard_rules: Iterable[HardRule],
    soft_rules: Iterable[SoftRule],
    weights: WeightConfig,
) -> Optional[EvaluatedCandidate]:
    """Run hard and soft rule evaluation for one candidate."""
    rule_context = RuleContext(runtime=runtime_context, candidate=candidate)
    hard_results: Dict[str, bool] = {}
    for hard_rule in hard_rules:
        hard_result = hard_rule.validate(rule_context)
        hard_results[hard_result.rule_name] = hard_result.is_valid
        if not hard_result.is_valid:
            return None

    soft_scores: Dict[str, float] = {}
    total_weighted_score = 0.0
    for soft_rule in soft_rules:
        score_result = soft_rule.score(rule_context)
        soft_scores[score_result.rule_name] = score_result.score
        weight_value = _read_weight(soft_rule.weight_key, weights)
        total_weighted_score += score_result.score * weight_value

    return EvaluatedCandidate(
        candidate=candidate,
        hard_results=hard_results,
        soft_scores=soft_scores,
        total_weighted_score=total_weighted_score,
    )


def select_best_candidate(
    evaluated_candidates: Iterable[EvaluatedCandidate],
) -> EvaluatedCandidate:
    """Pick the best candidate by weighted score then deterministic key."""
    return min(
        evaluated_candidates,
        key=lambda item: (
            item.total_weighted_score,
            *build_tie_break_key(item.candidate),
        ),
    )


def _read_weight(weight_key: str, weights: WeightConfig) -> float:
    if weight_key == "individual":
        return weights.individual
    if weight_key == "operator":
        return weights.operator
    if weight_key == "overall":
        return weights.overall
    return weights.extra_weights.get(weight_key, 1.0)

