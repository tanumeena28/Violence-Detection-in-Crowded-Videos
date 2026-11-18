# Repeated source-grouped evaluation

Recorded 2026-11-15. 245 unique clips and 204 source groups.

5 custom source-grouped folds: 3 train, one validates and one tests. TCN seeds: 42, 123, 2026.
Each deterministic linear control is fitted once per fold. Scaling and fitting use training data; validation selects checkpoints, regularization and thresholds.

The TCN uses the explicit pose-coverage scalar.

Derived feature schema: coco17-hip-box-center-v1

| Model | Fits | Accuracy | Macro-F1 | ROC-AUC |
|---|---:|---:|---:|---:|
| Skeleton baseline | 15 | 77.6% +/- 4.8% | 0.773 +/- 0.052 | 0.860 +/- 0.035 |
| Reliability | 15 | 77.1% +/- 5.8% | 0.769 +/- 0.060 | 0.863 +/- 0.042 |
| Interactions | 15 | 76.5% +/- 6.1% | 0.759 +/- 0.069 | 0.856 +/- 0.051 |
| Combined | 15 | 75.0% +/- 5.6% | 0.741 +/- 0.069 | 0.859 +/- 0.046 |
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
