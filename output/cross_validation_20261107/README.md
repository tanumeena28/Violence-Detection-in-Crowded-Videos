# Completed source-grouped experiment

Recorded 7 November 2026. All 70 fits and saved-artifact verification are
complete: 245 unique clips, 204 source groups, five custom outer folds.
Each rotation has 147 training, 49 validation and 49 test clips.

The four TCN variants use seeds 42, 123 and 2026, giving 60 fits. Motion and
quality-only logistic controls are each fitted once per fold, giving 10 fits.
Training data defines scaling and classifier fitting; validation data selects
TCN checkpoints, motion regularization and decision thresholds.

## Results and evidence

- [Results page](index.html) and [research notes](RESULTS.md).
- [Fold/seed summary](summary.json), [pooled classification decisions](pooled_metrics.json),
  and [out-of-fold predictions](out_of_fold_predictions.csv).
- [Verification record](audit.json), [frozen protocol](protocol.json),
  [frozen source review](source_review.json), and [training log](training.log).
- [Comparison figure](figures/comparison.png).
- Fitted artifacts in `fold_1/` through `fold_5/`.

Reliability has the highest mean skeleton accuracy at 76.9%; quality-only
reaches 77.6% without joint coordinates or trajectories. Combined reaches
74.8%, so the proposed combination has no established benefit. Differences are
small relative to descriptive variation.

The audit reproduced all 70 saved fits and their decisions, training-only
normalization and validation-selected thresholds. Maximum CPU score drift was
0.0002628565, within the 0.0003 tolerance.

## Inspect with the archived implementation

Run these commands from the project root:

```powershell
& '.\.venv\Scripts\python.exe' output/cross_validation_20261107/run_snapshot.py summarize-cv
& '.\.venv\Scripts\python.exe' output/cross_validation_20261107/run_snapshot.py report-cv --date 2026-11-07
```

`run_snapshot.py` selects this experiment directory and imports
`implementation_snapshot/affective/` before current project code. The copied
training modules match the frozen implementation hashes. Keep the snapshot,
protocol, inputs and fitted artifacts together. The report command verifies
the fits and regenerates the report; it does not train new models.

The recorded environment used PyTorch 2.11.0+cu128, OpenCV 4.14.0 and
scikit-learn 1.9.1. Package provenance is also stored with the fitted artifacts.
For later model changes, prepare a separate named experiment and retain this
completed record.

## Interpretation limits

Existing footage was inspected during earlier development. These are
exploratory custom source-grouped rotations, not an untouched benchmark or the
supplied Violent-Flows fold protocol. Source review used sampled visual evidence;
unknown shared footage remains possible and violence labels were not
independently re-annotated.

Standard deviations describe dependent fold/seed runs and are not confidence
intervals. ROC-AUC is averaged within folds rather than pooled across separately
fitted classifiers. Cached-feature fitting does not measure full-pipeline
latency. The remaining work is tracked in [the project plan](../../NEXT_STEPS.md).
