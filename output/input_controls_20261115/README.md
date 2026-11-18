# Completed detection and ordering controls

All 45 fresh GPU fits are verified: three input conditions, five source-grouped
folds, seeds 42/123/2026, the same corrected 110-channel combined TCN and
identical training budgets. Detection-only input zeros all body coordinates,
velocities and six interaction kinematic channels while retaining confidence,
validity, observation masks, neighbor counts and coverage. Shuffled time uses
a fixed label-blind permutation per clip after velocities are derived.

Mean accuracies are 75.4% full, 72.5% detection-only and 75.4% shuffled. This
shows substantial detection-cue signal. The ordering result does not remove
all motion evidence or prove time never matters. Results remain exploratory.

[Results](index.html), [audit](audit.json), [summary](summary.json) and
[protocol](protocol.json) preserve the evidence. Inspect without refitting:

```powershell
& '.\.venv\Scripts\python.exe' output/input_controls_20261115/run_snapshot.py --verify-only
```
