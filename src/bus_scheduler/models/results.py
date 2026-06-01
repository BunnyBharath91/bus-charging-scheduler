"""Output models for scheduler results."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field


class ChargingEvent(BaseModel):
    """One charging action for one bus at one station."""

    bus_id: str
    operator_id: str
    station_id: str
    arrival_time: datetime
    wait_minutes: int = Field(ge=0)
    charge_start_time: datetime
    charge_end_time: datetime
    charger_slot_index: int = Field(ge=0)


class BusTimelineResult(BaseModel):
    """Ordered timeline for a bus."""

    bus_id: str
    operator_id: str
    direction: str
    departure_time: datetime
    destination_time: datetime
    total_wait_minutes: int
    charging_events: List[ChargingEvent]


class StationTimelineResult(BaseModel):
    """Ordered timeline for one station."""

    station_id: str
    events: List[ChargingEvent]


class RuleDiagnostic(BaseModel):
    """Rule-level trace for one decision."""

    bus_id: str
    station_id: str
    hard_rule_results: Dict[str, bool]
    soft_rule_scores: Dict[str, float]
    weighted_total_score: float


class ObjectiveBreakdown(BaseModel):
    """Aggregate objective values for explainability."""

    total_wait_minutes: int
    operator_wait_minutes: Dict[str, int]
    network_completion_minutes: int


class ScheduleResult(BaseModel):
    """Top-level schedule result payload."""

    scenario_id: str
    per_bus: List[BusTimelineResult]
    per_station: List[StationTimelineResult]
    objective_breakdown: ObjectiveBreakdown
    diagnostics: List[RuleDiagnostic]

