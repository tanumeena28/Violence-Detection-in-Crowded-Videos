# Repeated source-grouped evaluation

Recorded 2026-11-14. 245 unique clips and 204 source groups.

5 custom source-grouped folds: 3 train, one validates and one tests. TCN seeds: 42, 123, 2026.
Each deterministic linear control is fitted once per fold. Scaling and fitting use training data; validation selects checkpoints, regularization and thresholds.

The explicit TCN coverage scalar is replaced with zero. Network size and initialization are unchanged; observation masks, missing joints and reliability/interaction channels still expose detection cues.

| Model | Fits | Accuracy | Macro-F1 | ROC-AUC |
|---|---:|---:|---:|---:|
| Skeleton baseline | 15 | 76.1% +/- 5.0% | 0.756 +/- 0.055 | 0.859 +/- 0.036 |
| Reliability | 15 | 76.9% +/- 5.5% | 0.766 +/- 0.056 | 0.866 +/- 0.040 |
| Interactions | 15 | 75.9% +/- 6.0% | 0.755 +/- 0.064 | 0.856 +/- 0.052 |
| Combined | 15 | 74.8% +/- 6.1% | 0.739 +/- 0.071 | 0.859 +/- 0.045 |
| Motion control | 5 | 75.1% +/- 5.3% | 0.748 +/- 0.053 | 0.798 +/- 0.072 |
| Quality-only control | 5 | 77.6% +/- 6.1% | 0.773 +/- 0.064 | 0.861 +/- 0.045 |

Means and standard deviations describe fold/seed runs, which are dependent. They are not confidence intervals or significance tests.

Source review: All 245 clips fully decoded; source overlap reviewed in densely sampled evidence for 20 candidate pairs. Violence labels were not independently re-annotated.

Known shared recordings were grouped before training. Existing clips and pilot results have been inspected previously. These remain exploratory results, not an untouched benchmark.
The custom rotations differ from the supplied Violent-Flows protocol. Full-video label validation and unknown shared footage remain limitations.

Verification reproduced 70 saved fits, including decisions, training-only scaling and validation-selected thresholds.
TCN score reproduction used cuda, with absolute tolerance 0.0003 and identical decisions. The audit records the verification implementation separately from the frozen training implementation.
Cached-feature experiments do not establish real-time inference or full-pipeline latency.

[Results page](index.html) | [Fold summary](summary.json) | [Pooled decisions](pooled_metrics.json) | [Per-clip predictions](out_of_fold_predictions.csv) | [Audit](audit.json)
