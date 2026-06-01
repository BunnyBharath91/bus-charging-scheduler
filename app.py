"""Streamlit entrypoint for the bus charging scheduler."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from bus_scheduler.scenario.repository import ScenarioRepository
from bus_scheduler.scheduler.engine import SchedulerEngine
from bus_scheduler.ui.views import (
    build_bus_timetable_rows,
    build_scenario_summary_rows,
    build_station_timetable_rows,
)


def main() -> None:
    """Render scheduler app UI."""
    st.set_page_config(page_title="Bus Charging Scheduler", layout="wide")
    st.title("Bus Charging Scheduler")

    scenario_repository = ScenarioRepository(PROJECT_ROOT / "scenarios")
    scenario_ids = scenario_repository.list_scenario_ids()
    if not scenario_ids:
        st.error("No scenario files found in the scenarios directory.")
        return

    selected_scenario_id = st.selectbox("Select scenario", scenario_ids, index=0)
    selected_scenario = scenario_repository.load_by_id(selected_scenario_id)

    st.subheader("Scenario Input View")
    st.table(build_scenario_summary_rows(selected_scenario))
    st.json(selected_scenario.model_dump(mode="json"), expanded=False)

    scheduler = SchedulerEngine()
    schedule_result = scheduler.run(selected_scenario)

    st.subheader("Per-Bus Timetable")
    st.dataframe(build_bus_timetable_rows(schedule_result), use_container_width=True)

    st.subheader("Per-Station Timetable")
    st.dataframe(build_station_timetable_rows(schedule_result), use_container_width=True)

    st.subheader("Objective Breakdown")
    st.json(schedule_result.objective_breakdown.model_dump(mode="json"), expanded=True)


if __name__ == "__main__":
    main()

