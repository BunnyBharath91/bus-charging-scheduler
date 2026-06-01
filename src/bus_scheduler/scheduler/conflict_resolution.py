"""Conflict resolution and deterministic tie-break helpers."""

from __future__ import annotations

from typing import Tuple

from bus_scheduler.rules.base import ChargingCandidate


def build_tie_break_key(candidate: ChargingCandidate) -> Tuple[float, str, str]:
    """Build deterministic key used after score comparison."""
    return (
        candidate.charge_start_time.timestamp(),
        candidate.station_id,
        candidate.bus_id,
    )

