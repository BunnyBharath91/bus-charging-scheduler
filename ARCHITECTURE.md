# Architecture

## Scheduler approach

The solution uses an event-driven simulation with a pluggable rule engine:

- Hard rules enforce feasibility and must pass for every charging decision.
- Soft rules assign weighted scores to feasible candidates.
- A deterministic tie-breaker resolves equal scores.

This pattern supports correctness and extensibility while keeping the implementation explainable in interviews.

## Why this approach

Compared to pure FIFO or ad-hoc greedy ordering, event-driven simulation better models time-dependent resource contention. Compared to CP/MIP solvers, this design is easier to explain, debug, and extend quickly for evolving business rules.

## Data structure design

Scenarios are JSON files that fully define the world:

- Route segments and distances.
- Charging stations and charger counts.
- Operators.
- Bus departures and directions.
- Rule activation.
- Rule weights.

The scheduler does not hardcode station names, route shape, or operator set.

## Rule engine design

- Hard rules live in `src/bus_scheduler/rules/hard/`.
- Soft rules live in `src/bus_scheduler/rules/soft/`.
- `registry.py` maps rule names to classes and builds active sets from scenario data.

### Add a new rule without rewriting engine

1. Implement the rule class.
2. Register it in `registry.py`.
3. Add it to `rules.hard` or `rules.soft` in the scenario.
4. Add tests.

No scheduler loop rewrite is needed.

## Weight tunability

Weights are read from one place in scenario data:

```json
"weights": {
  "individual": 1.0,
  "operator": 1.0,
  "overall": 1.0
}
```

Changing weights requires only data edits.

## Correctness guarantees

Hard-rule gate keeps invalid candidates out:

- Range feasibility.
- Charger capacity slot validity.
- Route order adherence.

Each selected charging event is stored with explicit wait, start, and end times for traceability.

## Scalability posture

- Event queue processing: approximately `O(E log E)`.
- Candidate evaluation: `O(S * R)` per decision where `S` is reachable stations and `R` is active rules.
- Adding stations/routes/operators/scenarios scales through data, not architecture rewrites.

## Future changes anticipated

Handled with the existing model and minimal code extension:

- More stations.
- Multiple chargers per station.
- Additional operators.
- Multiple routes.
- Priority buses.
- Driver shift constraints.
- Electricity cost windows.
- Maintenance windows that reduce temporary charger capacity.

## Assumptions

- Constant speed per scenario.
- Full charge is fixed duration.
- Endpoints always provide full departure charge and are outside scheduling contention.

## Limitations and next steps

- Current scoring uses local heuristics rather than global optimization.
- Future work can add look-ahead penalties for stronger congestion avoidance.
- Performance profiling can guide optimizations for much larger fleets.

