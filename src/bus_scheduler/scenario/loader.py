"""Scenario loading and validation utilities."""

from __future__ import annotations

import json
from pathlib import Path

from bus_scheduler.models.scenario import ScenarioConfig


def load_scenario_file(file_path: Path) -> ScenarioConfig:
    """Read and validate one scenario JSON file."""
    with file_path.open("r", encoding="utf-8") as scenario_file:
        raw_payload = json.load(scenario_file)
    return ScenarioConfig.model_validate(raw_payload)

