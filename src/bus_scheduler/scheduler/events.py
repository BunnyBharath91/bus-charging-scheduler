"""Event types for the scheduling simulation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum


class EventPriority(IntEnum):
    """Lower value means processed earlier at same timestamp."""

    BUS_DEPARTURE = 1
    CHARGING_DECISION = 2


@dataclass(order=True, slots=True)
class SchedulerEvent:
    """Comparable event object for priority queue usage."""

    event_time: datetime
    priority: int
    bus_id: str
    event_type: str

