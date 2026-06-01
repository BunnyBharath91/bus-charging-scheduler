"""Rule registry and composition utilities."""

from __future__ import annotations

from typing import Dict, List

from bus_scheduler.models.scenario import ScenarioConfig
from bus_scheduler.rules.base import HardRule, SoftRule
from bus_scheduler.rules.hard import ChargerCapacityHardRule, RangeHardRule, RouteOrderHardRule
from bus_scheduler.rules.soft import (
    IndividualWaitSoftRule,
    NetworkEfficiencySoftRule,
    OperatorBalanceSoftRule,
)

HARD_RULE_REGISTRY: Dict[str, type[HardRule]] = {
    "RangeHardRule": RangeHardRule,
    "ChargerCapacityHardRule": ChargerCapacityHardRule,
    "RouteOrderHardRule": RouteOrderHardRule,
}

SOFT_RULE_REGISTRY: Dict[str, type[SoftRule]] = {
    "IndividualWaitSoftRule": IndividualWaitSoftRule,
    "OperatorBalanceSoftRule": OperatorBalanceSoftRule,
    "NetworkEfficiencySoftRule": NetworkEfficiencySoftRule,
}


def build_hard_rules(scenario: ScenarioConfig) -> List[HardRule]:
    """Instantiate active hard rules for the scenario."""
    hard_rules: List[HardRule] = []
    for rule_name in scenario.rules.hard:
        rule_type = HARD_RULE_REGISTRY.get(rule_name)
        if rule_type is None:
            raise ValueError(f"Unknown hard rule: {rule_name}")
        hard_rules.append(rule_type())
    return hard_rules


def build_soft_rules(scenario: ScenarioConfig) -> List[SoftRule]:
    """Instantiate active soft rules for the scenario."""
    soft_rules: List[SoftRule] = []
    for rule_name in scenario.rules.soft:
        rule_type = SOFT_RULE_REGISTRY.get(rule_name)
        if rule_type is None:
            raise ValueError(f"Unknown soft rule: {rule_name}")
        soft_rules.append(rule_type())
    return soft_rules

