# Matched input controls

| Condition | Mean accuracy | Macro-F1 | AUC | Accuracy change (pp) |
|---|---:|---:|---:|---:|
| full | 75.4% | 0.747 | 0.859 | +0.00 |
| detection_only | 72.5% | 0.716 | 0.834 | -2.86 |
| shuffled_time | 75.4% | 0.744 | 0.863 | +0.00 |

Exploratory comparisons on inspected crowd footage. Same 110-channel combined TCN dimensions, source-grouped folds, seeds, training budget, GPU and validation-only selection. Detection-only removes coordinates, body velocities and six interaction kinematic channels; confidence, joint validity, observation masks, neighbor counts and explicit coverage remain. Time-shuffling permutes already-derived feature/mask slices consistently per clip: velocity vectors remain available. It tests ordering, not removal of all motion. Fold/seed SD and paired changes are descriptive, not significance tests. No independent label review or RWF claim is made.

All 45 saved fits reproduce scores, decisions, training-only normalization and validation thresholds.
