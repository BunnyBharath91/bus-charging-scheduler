"""Input models for scenarios."""

from __future__ import annotations

from datetime import time
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field, field_validator, model_validator

from bus_scheduler.config.constants import (
    DEFAULT_BATTERY_RANGE_KM,
    DEFAULT_CHARGE_DURATION_MINUTES,
    DEFAULT_INDIVIDUAL_WEIGHT,
    DEFAULT_OPERATOR_WEIGHT,
    DEFAULT_OVERALL_WEIGHT,
    DEFAULT_RULES_HARD,
    DEFAULT_RULES_SOFT,
    DEFAULT_SPEED_KMPH,
)


class Direction(str, Enum):
    """Supported trip direction labels."""

    BENGALURU_TO_KOCHI = "BengaluruToKochi"
    KOCHI_TO_BENGALURU = "KochiToBengaluru"


class RouteSegment(BaseModel):
    """One directional route segment."""

    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    distance_km: int = Field(gt=0)


class RouteDefinition(BaseModel):
    """Route shape used by the scheduler."""

    route_id: str
    segments: List[RouteSegment]

    @model_validator(mode="after")
    def validate_continuity(self) -> "RouteDefinition":
        if not self.segments:
            raise ValueError("Route must have at least one segment.")
        for index in range(len(self.segments) - 1):
            current_segment = self.segments[index]
            next_segment = self.segments[index + 1]
            if current_segment.to_node != next_segment.from_node:
                raise ValueError("Route segments must form a contiguous path.")
        return self


class StationDefinition(BaseModel):
    """Charging station definition."""

    station_id: str
    chargers_count: int = Field(ge=1)
    metadata: Dict[str, str] = Field(default_factory=dict)


class BusTripRequest(BaseModel):
    """A bus departure request."""

    bus_id: str
    operator_id: str
    direction: Direction
    departure_time: time

    @field_validator("departure_time", mode="before")
    @classmethod
    def parse_time(cls, value: str | time) -> time:
        if isinstance(value, time):
            return value
        hour_text, minute_text = value.split(":")
        return time(hour=int(hour_text), minute=int(minute_text))


class ConstantsConfig(BaseModel):
    """Physical constants used in simulation."""

    battery_range_km: int = Field(default=DEFAULT_BATTERY_RANGE_KM, ge=1)
    charge_duration_minutes: int = Field(default=DEFAULT_CHARGE_DURATION_MINUTES, ge=1)
    speed_kmph: int = Field(default=DEFAULT_SPEED_KMPH, ge=1)


class WeightConfig(BaseModel):
    """Weights for soft rules."""

    individual: float = DEFAULT_INDIVIDUAL_WEIGHT
    operator: float = DEFAULT_OPERATOR_WEIGHT
    overall: float = DEFAULT_OVERALL_WEIGHT
    extra_weights: Dict[str, float] = Field(default_factory=dict)


class RulesConfig(BaseModel):
    """Active rule names for the scenario."""

    hard: List[str] = Field(default_factory=lambda: list(DEFAULT_RULES_HARD))
    soft: List[str] = Field(default_factory=lambda: list(DEFAULT_RULES_SOFT))


class ScenarioConfig(BaseModel):
    """Top-level scenario payload."""

    scenario_id: str
    description: str
    constants: ConstantsConfig = Field(default_factory=ConstantsConfig)
    weights: WeightConfig = Field(default_factory=WeightConfig)
    route: RouteDefinition
    stations: List[StationDefinition]
    operators: List[str]
    buses: List[BusTripRequest]
    rules: RulesConfig = Field(default_factory=RulesConfig)

    @model_validator(mode="after")
    def validate_station_and_operator_refs(self) -> "ScenarioConfig":
        station_ids = {station.station_id for station in self.stations}
        route_nodes = {segment.from_node for segment in self.route.segments} | {
            segment.to_node for segment in self.route.segments
        }
        if not station_ids.issubset(route_nodes):
            raise ValueError("All stations must exist on route nodes.")

        operator_set = set(self.operators)
        for bus in self.buses:
            if bus.operator_id not in operator_set:
                raise ValueError(f"Unknown operator for bus {bus.bus_id}.")
        return self

