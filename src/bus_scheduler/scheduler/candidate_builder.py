"""Charging candidate generation."""

from __future__ import annotations

from datetime import timedelta
from typing import Dict, List, Tuple

from bus_scheduler.models.runtime import BusRuntimeState, StationRuntimeState
from bus_scheduler.models.scenario import Direction, ScenarioConfig
from bus_scheduler.rules.base import ChargingCandidate


def build_direction_nodes(scenario: ScenarioConfig, direction: Direction) -> List[str]:
    """Return ordered route nodes for the given direction."""
    forward_nodes: List[str] = [scenario.route.segments[0].from_node]
    for segment in scenario.route.segments:
        forward_nodes.append(segment.to_node)
    if direction == Direction.BENGALURU_TO_KOCHI:
        return forward_nodes
    return list(reversed(forward_nodes))


def build_segment_distances(scenario: ScenarioConfig, direction: Direction) -> List[int]:
    """Return segment distances ordered for direction nodes."""
    forward_distances = [segment.distance_km for segment in scenario.route.segments]
    if direction == Direction.BENGALURU_TO_KOCHI:
        return forward_distances
    return list(reversed(forward_distances))


def distance_between_nodes(
    ordered_nodes: List[str],
    ordered_distances: List[int],
    from_node: str,
    to_node: str,
) -> int:
    """Compute directional distance from one node to a later node."""
    from_index = ordered_nodes.index(from_node)
    to_index = ordered_nodes.index(to_node)
    if to_index <= from_index:
        return 0
    return sum(ordered_distances[from_index:to_index])


def build_charging_candidates(
    scenario: ScenarioConfig,
    bus_state: BusRuntimeState,
    station_states: Dict[str, StationRuntimeState],
) -> List[ChargingCandidate]:
    """Build all reachable station candidates for a bus decision point."""
    direction_nodes = build_direction_nodes(scenario, bus_state.bus.direction)
    direction_distances = build_segment_distances(scenario, bus_state.bus.direction)
    station_ids = {station.station_id for station in scenario.stations}

    current_index = direction_nodes.index(bus_state.current_node)
    candidates: List[ChargingCandidate] = []
    for next_index in range(current_index + 1, len(direction_nodes)):
        node = direction_nodes[next_index]
        if node not in station_ids:
            continue
        travel_distance = distance_between_nodes(
            direction_nodes,
            direction_distances,
            bus_state.current_node,
            node,
        )
        if travel_distance > bus_state.remaining_range_km:
            continue
        travel_minutes = (travel_distance / scenario.constants.speed_kmph) * 60
        arrival_time = bus_state.current_time + timedelta(minutes=travel_minutes)
        station_state = station_states[node]
        best_slot_index, best_slot_available_time = _choose_best_slot(station_state)
        charge_start_time = max(arrival_time, best_slot_available_time)
        wait_minutes = int((charge_start_time - arrival_time).total_seconds() // 60)
        charge_end_time = charge_start_time + timedelta(
            minutes=scenario.constants.charge_duration_minutes
        )
        candidate = ChargingCandidate(
            bus_id=bus_state.bus.bus_id,
            operator_id=bus_state.bus.operator_id,
            station_id=node,
            candidate_index=best_slot_index,
            arrival_time=arrival_time,
            wait_minutes=wait_minutes,
            charge_start_time=charge_start_time,
            charge_end_time=charge_end_time,
        )
        candidates.append(candidate)
    return candidates


def _choose_best_slot(station_state: StationRuntimeState) -> Tuple[int, object]:
    earliest_index = 0
    earliest_value = station_state.charger_available_at[0]
    for index, available_at in enumerate(station_state.charger_available_at):
        if available_at < earliest_value:
            earliest_index = index
            earliest_value = available_at
    return earliest_index, earliest_value

