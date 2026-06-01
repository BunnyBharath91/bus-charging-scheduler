"""Main scheduling engine."""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Set, Tuple

from bus_scheduler.models.results import (
    BusTimelineResult,
    ChargingEvent,
    ObjectiveBreakdown,
    RuleDiagnostic,
    ScheduleResult,
    StationTimelineResult,
)
from bus_scheduler.models.runtime import BusRuntimeState, RuntimeContext, StationRuntimeState
from bus_scheduler.models.scenario import ScenarioConfig
from bus_scheduler.rules.registry import build_hard_rules, build_soft_rules
from bus_scheduler.scheduler.candidate_builder import (
    build_charging_candidates,
    build_direction_nodes,
    build_segment_distances,
    distance_between_nodes,
)
from bus_scheduler.scheduler.decision import evaluate_candidate, select_best_candidate


@dataclass(slots=True)
class BusBookkeeping:
    """Cached route helpers for each bus."""

    ordered_nodes: List[str]
    ordered_distances: List[int]
    destination_node: str


class SchedulerEngine:
    """Event-driven scheduler implementation."""

    def run(self, scenario: ScenarioConfig) -> ScheduleResult:
        hard_rules = build_hard_rules(scenario)
        soft_rules = build_soft_rules(scenario)

        simulation_start = datetime.combine(date(2026, 1, 1), datetime.min.time())
        station_states = self._build_station_states(scenario, simulation_start)
        runtime_context = RuntimeContext(
            operator_total_wait_minutes={operator: 0 for operator in scenario.operators},
            station_states=station_states,
        )
        bus_states, bus_helpers, event_heap = self._build_bus_states(
            scenario,
            simulation_start,
        )
        per_station_events: Dict[str, List[ChargingEvent]] = {station.station_id: [] for station in scenario.stations}
        diagnostics: List[RuleDiagnostic] = []
        completed_bus_ids: Set[str] = set()

        while event_heap:
            _, bus_id = heapq.heappop(event_heap)
            if bus_id in completed_bus_ids:
                continue
            bus_state = bus_states[bus_id]
            bus_helper = bus_helpers[bus_id]
            remaining_trip_distance = distance_between_nodes(
                bus_helper.ordered_nodes,
                bus_helper.ordered_distances,
                bus_state.current_node,
                bus_helper.destination_node,
            )
            if remaining_trip_distance <= bus_state.remaining_range_km:
                travel_minutes = (remaining_trip_distance / scenario.constants.speed_kmph) * 60
                bus_state.current_time = bus_state.current_time + timedelta(minutes=travel_minutes)
                completed_bus_ids.add(bus_id)
                continue

            candidates = build_charging_candidates(scenario, bus_state, station_states)
            evaluated_candidates = []
            for candidate in candidates:
                evaluated = evaluate_candidate(
                    candidate=candidate,
                    runtime_context=runtime_context,
                    hard_rules=hard_rules,
                    soft_rules=soft_rules,
                    weights=scenario.weights,
                )
                if evaluated is not None:
                    evaluated_candidates.append(evaluated)

            if not evaluated_candidates:
                raise ValueError(f"No valid charging candidate found for bus {bus_id}.")

            selected = select_best_candidate(evaluated_candidates)
            chosen_candidate = selected.candidate
            charging_event = ChargingEvent(
                bus_id=chosen_candidate.bus_id,
                operator_id=chosen_candidate.operator_id,
                station_id=chosen_candidate.station_id,
                arrival_time=chosen_candidate.arrival_time,
                wait_minutes=chosen_candidate.wait_minutes,
                charge_start_time=chosen_candidate.charge_start_time,
                charge_end_time=chosen_candidate.charge_end_time,
                charger_slot_index=chosen_candidate.candidate_index,
            )
            per_station_events[charging_event.station_id].append(charging_event)
            bus_state.charging_events.append(charging_event.model_dump_json())
            bus_state.total_wait_minutes += charging_event.wait_minutes

            runtime_context.operator_total_wait_minutes[charging_event.operator_id] += charging_event.wait_minutes
            station_states[charging_event.station_id].charger_available_at[
                charging_event.charger_slot_index
            ] = charging_event.charge_end_time

            bus_state.current_node = charging_event.station_id
            bus_state.current_time = charging_event.charge_end_time
            bus_state.remaining_range_km = scenario.constants.battery_range_km

            diagnostics.append(
                RuleDiagnostic(
                    bus_id=chosen_candidate.bus_id,
                    station_id=chosen_candidate.station_id,
                    hard_rule_results=selected.hard_results,
                    soft_rule_scores=selected.soft_scores,
                    weighted_total_score=selected.total_weighted_score,
                )
            )
            heapq.heappush(event_heap, (bus_state.current_time, bus_id))

        per_bus_results = self._build_per_bus_results(scenario, bus_states)
        per_station_results = self._build_per_station_results(per_station_events)
        network_completion_minutes = self._compute_network_completion_minutes(
            per_bus_results=per_bus_results,
            simulation_start=simulation_start,
        )
        objective_breakdown = ObjectiveBreakdown(
            total_wait_minutes=sum(result.total_wait_minutes for result in per_bus_results),
            operator_wait_minutes=runtime_context.operator_total_wait_minutes,
            network_completion_minutes=network_completion_minutes,
        )
        return ScheduleResult(
            scenario_id=scenario.scenario_id,
            per_bus=per_bus_results,
            per_station=per_station_results,
            objective_breakdown=objective_breakdown,
            diagnostics=diagnostics,
        )

    def _build_station_states(
        self,
        scenario: ScenarioConfig,
        simulation_start: datetime,
    ) -> Dict[str, StationRuntimeState]:
        station_states: Dict[str, StationRuntimeState] = {}
        for station in scenario.stations:
            station_states[station.station_id] = StationRuntimeState(
                station_id=station.station_id,
                charger_available_at=[simulation_start for _ in range(station.chargers_count)],
            )
        return station_states

    def _build_bus_states(
        self,
        scenario: ScenarioConfig,
        simulation_start: datetime,
    ) -> Tuple[Dict[str, BusRuntimeState], Dict[str, BusBookkeeping], List[Tuple[datetime, str]]]:
        bus_states: Dict[str, BusRuntimeState] = {}
        bus_helpers: Dict[str, BusBookkeeping] = {}
        event_heap: List[Tuple[datetime, str]] = []
        for bus in scenario.buses:
            ordered_nodes = build_direction_nodes(scenario, bus.direction)
            ordered_distances = build_segment_distances(scenario, bus.direction)
            origin_node = ordered_nodes[0]
            departure_datetime = simulation_start.replace(
                hour=bus.departure_time.hour,
                minute=bus.departure_time.minute,
            )
            bus_states[bus.bus_id] = BusRuntimeState(
                bus=bus,
                current_node=origin_node,
                current_time=departure_datetime,
                remaining_range_km=scenario.constants.battery_range_km,
            )
            bus_helpers[bus.bus_id] = BusBookkeeping(
                ordered_nodes=ordered_nodes,
                ordered_distances=ordered_distances,
                destination_node=ordered_nodes[-1],
            )
            heapq.heappush(event_heap, (departure_datetime, bus.bus_id))
        return bus_states, bus_helpers, event_heap

    def _build_per_bus_results(
        self,
        scenario: ScenarioConfig,
        bus_states: Dict[str, BusRuntimeState],
    ) -> List[BusTimelineResult]:
        per_bus_results: List[BusTimelineResult] = []
        for bus in sorted(scenario.buses, key=lambda item: item.bus_id):
            state = bus_states[bus.bus_id]
            charging_events = [
                ChargingEvent.model_validate_json(event_text) for event_text in state.charging_events
            ]
            timeline_result = BusTimelineResult(
                bus_id=bus.bus_id,
                operator_id=bus.operator_id,
                direction=bus.direction.value,
                departure_time=datetime.combine(date(2026, 1, 1), bus.departure_time),
                destination_time=state.current_time,
                total_wait_minutes=state.total_wait_minutes,
                charging_events=charging_events,
            )
            per_bus_results.append(timeline_result)
        return per_bus_results

    def _build_per_station_results(
        self,
        per_station_events: Dict[str, List[ChargingEvent]],
    ) -> List[StationTimelineResult]:
        station_results: List[StationTimelineResult] = []
        for station_id in sorted(per_station_events):
            events = sorted(
                per_station_events[station_id],
                key=lambda event: (event.charge_start_time, event.bus_id),
            )
            station_results.append(StationTimelineResult(station_id=station_id, events=events))
        return station_results

    def _compute_network_completion_minutes(
        self,
        per_bus_results: List[BusTimelineResult],
        simulation_start: datetime,
    ) -> int:
        if not per_bus_results:
            return 0
        latest_destination_time = max(result.destination_time for result in per_bus_results)
        elapsed = latest_destination_time - simulation_start
        return int(elapsed.total_seconds() // 60)

