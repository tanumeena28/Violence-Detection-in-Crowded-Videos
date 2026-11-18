# Supervised RWF frozen-video reference

Frozen Kinetics-400 R3D-18 encoder, two 16-frame windows, fresh logistic head. Source-grouped validation comes only from released training footage.

| Partition | Clips | Accuracy | Macro-F1 | AUC |
|---|---:|---:|---:|---:|
| Training | 1271 | 91.0% | 0.910 | 0.976 |
| Validation | 317 | 82.0% | 0.819 | 0.901 |
| Released evaluation | 400 | 84.0% | 0.840 | 0.900 |

Selected C: 0.01; validation-selected threshold: 0.50. The head was sealed before evaluation features were loaded.

Supervised RWF development experiment with a frozen Kinetics-400 encoder and logistic head. Released training footage supplies both fitting and source-grouped validation. The 400 released evaluation clips have already been inspected/scored in earlier transfer experiments, so this is exploratory development evaluation, not an untouched test claim or direct accuracy improvement over crowd-only transfer. Source IDs and byte hashes do not rule out renamed/shared footage. Independent labels and pretraining/source overlap remain unaudited. Scores are not calibrated.

[Protocol](protocol.json) | [Source audit](source_audit.json) | [Fit selection](selection.json) | [Verification](audit.json) | [Metrics](metrics.json)
