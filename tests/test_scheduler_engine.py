"""Scheduler engine integration tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bus_scheduler.models.scenario import ScenarioConfig
from bus_scheduler.scheduler.engine import SchedulerEngine
from bus_scheduler.scenario.loader import load_scenario_file


def test_scheduler_runs_and_generates_timelines() -> None:
    scenario = load_scenario_file(Path("scenarios/scenario_1_even_spacing.json"))
    result = SchedulerEngine().run(scenario)
    assert len(result.per_bus) == len(scenario.buses)
    assert len(result.per_station) == len(scenario.stations)
    assert result.objective_breakdown.total_wait_minutes >= 0


def test_station_events_do_not_overlap_for_single_charger() -> None:
    scenario = load_scenario_file(Path("scenarios/scenario_2_bunched_start.json"))
    result = SchedulerEngine().run(scenario)
    for station in result.per_station:
        for first, second in zip(station.events, station.events[1:]):
            assert first.charge_end_time <= second.charge_start_time


def test_scheduler_is_deterministic_for_same_input() -> None:
    scenario = load_scenario_file(Path("scenarios/scenario_4_operator_heavy.json"))
    scheduler = SchedulerEngine()
    first_result = scheduler.run(scenario)
    second_result = scheduler.run(scenario)
    assert first_result.model_dump() == second_result.model_dump()


def test_scheduler_raises_on_unreachable_route(tmp_path: Path) -> None:
    base_payload = json.loads(Path("scenarios/scenario_1_even_spacing.json").read_text(encoding="utf-8"))
    base_payload["constants"]["battery_range_km"] = 50
    invalid_path = tmp_path / "invalid_scenario.json"
    invalid_path.write_text(json.dumps(base_payload), encoding="utf-8")
    invalid_scenario = ScenarioConfig.model_validate_json(invalid_path.read_text(encoding="utf-8"))
    with pytest.raises(ValueError):
        SchedulerEngine().run(invalid_scenario)

