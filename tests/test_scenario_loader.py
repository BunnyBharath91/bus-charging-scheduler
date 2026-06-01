"""Scenario loading tests."""

from __future__ import annotations

from pathlib import Path

from bus_scheduler.scenario.loader import load_scenario_file
from bus_scheduler.scenario.repository import ScenarioRepository


def test_load_scenario_file_parses_expected_fields() -> None:
    scenario_path = Path("scenarios/scenario_1_even_spacing.json")
    scenario = load_scenario_file(scenario_path)
    assert scenario.scenario_id == "scenario_1_even_spacing"
    assert len(scenario.buses) == 20
    assert scenario.constants.battery_range_km == 240


def test_repository_lists_all_required_scenarios() -> None:
    repository = ScenarioRepository(Path("scenarios"))
    scenario_ids = repository.list_scenario_ids()
    assert len(scenario_ids) == 5
    assert "scenario_5_worst_case_convergence" in scenario_ids

