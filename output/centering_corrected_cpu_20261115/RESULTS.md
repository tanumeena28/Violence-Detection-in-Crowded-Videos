# Repeated source-grouped evaluation

Recorded 2026-11-15. 245 unique clips and 204 source groups.

5 custom source-grouped folds: 3 train, one validates and one tests. TCN seeds: 42, 123, 2026.
Each deterministic linear control is fitted once per fold. Scaling and fitting use training data; validation selects checkpoints, regularization and thresholds.

The TCN uses the explicit pose-coverage scalar.

Derived feature schema: coco17-continuous-hip-offset-v2

| Model | Fits | Accuracy | Macro-F1 | ROC-AUC |
|---|---:|---:|---:|---:|
| Skeleton baseline | 15 | 77.0% +/- 4.7% | 0.765 +/- 0.052 | 0.856 +/- 0.026 |
| Reliability | 15 | 78.1% +/- 6.1% | 0.777 +/- 0.065 | 0.862 +/- 0.044 |
| Interactions | 15 | 78.6% +/- 5.6% | 0.782 +/- 0.061 | 0.851 +/- 0.043 |
| Combined | 15 | 74.7% +/- 5.9% | 0.736 +/- 0.072 | 0.858 +/- 0.037 |
| Motion control | 5 | 75.1% +/- 5.3% | 0.748 +/- 0.053 | 0.798 +/- 0.072 |
| Quality-only control | 5 | 77.6% +/- 6.1% | 0.773 +/- 0.064 | 0.861 +/- 0.045 |

Means and standard deviations describe fold/seed runs, which are dependent. They are not confidence intervals or significance tests.

Source review: All 245 clips fully decoded; source overlap reviewed in densely sampled evidence for 20 candidate pairs. Violence labels were not independently re-annotated.

Known shared recordings were grouped before training. Existing clips and pilot results have been inspected previously. These remain exploratory results, not an untouched benchmark.
The custom rotations differ from the supplied Violent-Flows protocol. Full-video label validation and unknown shared footage remain limitations.

Verification reproduced 70 saved fits, including decisions, training-only scaling and validation-selected thresholds.
TCN score reproduction used cpu, with absolute tolerance 0.0003 and identical decisions. The audit records the verification implementation separately from the frozen training implementation.
Cached-feature experiments do not establish real-time inference or full-pipeline latency.

[Results page](index.html) | [Fold summary](summary.json) | [Pooled decisions](pooled_metrics.json) | [Per-clip predictions](out_of_fold_predictions.csv) | [Audit](audit.json)
