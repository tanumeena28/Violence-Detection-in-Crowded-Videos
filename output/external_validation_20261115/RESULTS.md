# Fixed-model Hockey Fight external evaluation

Sports broadcast domain, not a surveillance deployment benchmark. Mirror class labels are supplied and unreviewed. Filenames do not identify source games, so source independence, near-duplicates and Kinetics pretraining overlap remain unaudited. Primary: fixed frozen-video reference. All 1,000 released clips retained, including three duplicate files; 997 unique byte hashes. No byte overlap with the compared prior inventory, which does not establish source independence.

| Model | Clips | Accuracy | Macro-F1 | AUC | Fight recall | False alarms | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| rwf_frozen_video (threshold 0.50) | 1000 | 70.80% | 0.686 | 0.886 | 44.4% | 14 | 278 |
| rwf_finetuned_video (threshold 0.23) | 1000 | 81.10% | 0.810 | 0.893 | 73.6% | 57 | 132 |
| crowd_pose_interactions (threshold 0.62) | 1000 | 40.90% | 0.361 | 0.420 | 68.2% | 432 | 159 |

Every model retains its development threshold and normalization. All supplied labels are unchanged.

[Predictions](predictions.csv) | [Metrics](metrics.json) | [Audit](audit.json) | [Protocol](protocol.json)
