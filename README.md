# Bus Charging Scheduler

Single-process Python + Streamlit scheduler for the Bengaluru-Kochi electric bus assignment.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start the app (runs on port 8000 via `.streamlit/config.toml`):
   - `streamlit run app.py`
   - Or explicitly: `streamlit run app.py --server.port 8000`

## Project structure

- `app.py`: Streamlit UI entrypoint.
- `scenarios/`: Data-driven scenario files.
- `src/bus_scheduler/models/`: Pydantic input and output models.
- `src/bus_scheduler/scenario/`: Scenario loading and repository.
- `src/bus_scheduler/rules/`: Hard and soft rules plus registry.
- `src/bus_scheduler/scheduler/`: Candidate generation, decision scoring, and engine.
- `src/bus_scheduler/ui/`: View-model builders for UI tables.
- `tests/`: Unit and integration tests.

## How to change weights

Edit the selected scenario file in `scenarios/`:

```json
"weights": {
  "individual": 1.0,
  "operator": 2.0,
  "overall": 1.0
}
```

No code changes are required.

## How to add a new soft rule

1. Create a new file under `src/bus_scheduler/rules/soft/`.
2. Implement `name`, `weight_key`, and `score(context)` on the rule class.
3. Register it in `src/bus_scheduler/rules/registry.py`.
4. Add the rule name to the scenario `rules.soft` list.
5. Add the new weight key to `weights.extra_weights` (or map it directly in `decision.py`).
6. Add tests for the rule behavior.

## Notes

- Scheduler is deterministic (tie-breakers use fixed ordering).
- Scenario data is externalized for easy world changes (stations, operators, routes, chargers, weights).

