"""Rule interfaces and shared rule context."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from bus_scheduler.models.runtime import RuntimeContext


@dataclass(slots=True)
class ChargingCandidate:
    """One possible charging action to evaluate."""

    bus_id: str
    operator_id: str
    station_id: str
    candidate_index: int
    arrival_time: datetime
    wait_minutes: int
    charge_start_time: datetime
    charge_end_time: datetime


@dataclass(slots=True)
class RuleContext:
    """Inputs available to hard and soft rules."""

    runtime: RuntimeContext
    candidate: ChargingCandidate


@dataclass(slots=True)
class HardRuleResult:
    """Hard rule verdict."""

    rule_name: str
    is_valid: bool
    reason: str = ""


@dataclass(slots=True)
class SoftRuleResult:
    """Soft rule scoring output."""

    rule_name: str
    score: float
    reason: str = ""


class HardRule(Protocol):
    """Interface for hard feasibility rules."""

    name: str

    def validate(self, context: RuleContext) -> HardRuleResult:
        """Return whether candidate is feasible."""


class SoftRule(Protocol):
    """Interface for soft optimization rules."""

    name: str
    weight_key: str

    def score(self, context: RuleContext) -> SoftRuleResult:
        """Return score contribution (lower is better)."""

