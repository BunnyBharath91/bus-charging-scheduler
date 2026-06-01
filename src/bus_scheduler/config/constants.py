"""Project-wide constants and defaults."""

from __future__ import annotations

DEFAULT_BATTERY_RANGE_KM = 240
DEFAULT_CHARGE_DURATION_MINUTES = 25
DEFAULT_SPEED_KMPH = 60

DEFAULT_INDIVIDUAL_WEIGHT = 1.0
DEFAULT_OPERATOR_WEIGHT = 1.0
DEFAULT_OVERALL_WEIGHT = 1.0

DEFAULT_RULES_HARD = (
    "RangeHardRule",
    "ChargerCapacityHardRule",
    "RouteOrderHardRule",
)
DEFAULT_RULES_SOFT = (
    "IndividualWaitSoftRule",
    "OperatorBalanceSoftRule",
    "NetworkEfficiencySoftRule",
)

