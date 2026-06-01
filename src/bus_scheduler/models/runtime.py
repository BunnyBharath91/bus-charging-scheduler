"""Runtime models used during scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from bus_scheduler.models.scenario import BusTripRequest


@dataclass(slots=True)
class BusRuntimeState:
    """Mutable state for one bus while scheduling."""

    bus: BusTripRequest
    current_node: str
    current_time: datetime
    remaining_range_km: int
    charging_events: List[str] = field(default_factory=list)
    total_wait_minutes: int = 0


@dataclass(slots=True)
class StationRuntimeState:
    """Mutable charger availability for one station."""

    station_id: str
    charger_available_at: List[datetime]


@dataclass(slots=True)
class RuntimeContext:
    """Global state that rules can inspect."""

    operator_total_wait_minutes: Dict[str, int]
    station_states: Dict[str, StationRuntimeState]

