"""View-model builders for Streamlit rendering."""

from __future__ import annotations

from typing import Dict, List

from bus_scheduler.models.results import ScheduleResult
from bus_scheduler.models.scenario import ScenarioConfig


def build_scenario_summary_rows(scenario: ScenarioConfig) -> List[Dict[str, object]]:
    """Return simple summary rows for the selected scenario."""
    return [
        {"field": "scenario_id", "value": scenario.scenario_id},
        {"field": "description", "value": scenario.description},
        {"field": "bus_count", "value": len(scenario.buses)},
        {"field": "station_count", "value": len(scenario.stations)},
        {"field": "battery_range_km", "value": scenario.constants.battery_range_km},
        {"field": "charge_duration_minutes", "value": scenario.constants.charge_duration_minutes},
        {"field": "speed_kmph", "value": scenario.constants.speed_kmph},
        {"field": "weight_individual", "value": scenario.weights.individual},
        {"field": "weight_operator", "value": scenario.weights.operator},
        {"field": "weight_overall", "value": scenario.weights.overall},
    ]


def build_bus_timetable_rows(result: ScheduleResult) -> List[Dict[str, object]]:
    """Flatten per-bus timeline into table rows."""
    rows: List[Dict[str, object]] = []
    for bus_result in result.per_bus:
        if not bus_result.charging_events:
            rows.append(
                {
                    "bus_id": bus_result.bus_id,
                    "operator": bus_result.operator_id,
                    "direction": bus_result.direction,
                    "station": "-",
                    "arrival_at_station": "-",
                    "wait_minutes": 0,
                    "charge_start": "-",
                    "charge_end": "-",
                    "arrival_at_destination": bus_result.destination_time.strftime("%H:%M"),
                    "total_wait_minutes": bus_result.total_wait_minutes,
                }
            )
            continue
        for event_index, event in enumerate(bus_result.charging_events):
            rows.append(
                {
                    "bus_id": bus_result.bus_id,
                    "operator": bus_result.operator_id,
                    "direction": bus_result.direction,
                    "station": event.station_id,
                    "arrival_at_station": event.arrival_time.strftime("%H:%M"),
                    "wait_minutes": event.wait_minutes,
                    "charge_start": event.charge_start_time.strftime("%H:%M"),
                    "charge_end": event.charge_end_time.strftime("%H:%M"),
                    "arrival_at_destination": (
                        bus_result.destination_time.strftime("%H:%M")
                        if event_index == len(bus_result.charging_events) - 1
                        else ""
                    ),
                    "total_wait_minutes": (
                        bus_result.total_wait_minutes
                        if event_index == len(bus_result.charging_events) - 1
                        else ""
                    ),
                }
            )
    return rows


def build_station_timetable_rows(result: ScheduleResult) -> List[Dict[str, object]]:
    """Flatten per-station ordering into table rows."""
    rows: List[Dict[str, object]] = []
    for station_result in result.per_station:
        for order_index, event in enumerate(station_result.events, start=1):
            rows.append(
                {
                    "station": station_result.station_id,
                    "order": order_index,
                    "bus_id": event.bus_id,
                    "operator": event.operator_id,
                    "arrival_at_station": event.arrival_time.strftime("%H:%M"),
                    "wait_minutes": event.wait_minutes,
                    "charge_start": event.charge_start_time.strftime("%H:%M"),
                    "charge_end": event.charge_end_time.strftime("%H:%M"),
                    "charger_slot": event.charger_slot_index,
                }
            )
    return rows

