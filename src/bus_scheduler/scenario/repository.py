"""Scenario file repository abstraction."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from bus_scheduler.models.scenario import ScenarioConfig
from bus_scheduler.scenario.loader import load_scenario_file


class ScenarioRepository:
    """Reads all scenario files from a directory."""

    def __init__(self, scenarios_directory: Path) -> None:
        self._scenarios_directory = scenarios_directory

    def list_scenario_ids(self) -> List[str]:
        """Return all scenario file stems sorted by filename."""
        scenario_files = sorted(self._scenarios_directory.glob("scenario_*.json"))
        return [scenario_file.stem for scenario_file in scenario_files]

    def load_by_id(self, scenario_id: str) -> ScenarioConfig:
        """Load one scenario by id."""
        scenario_file_path = self._scenarios_directory / f"{scenario_id}.json"
        if not scenario_file_path.exists():
            raise FileNotFoundError(f"Scenario file not found: {scenario_file_path}")
        return load_scenario_file(scenario_file_path)

    def load_all(self) -> Dict[str, ScenarioConfig]:
        """Load all scenarios keyed by scenario id."""
        scenarios: Dict[str, ScenarioConfig] = {}
        for scenario_file in sorted(self._scenarios_directory.glob("scenario_*.json")):
            scenario = load_scenario_file(scenario_file)
            scenarios[scenario.scenario_id] = scenario
        return scenarios

