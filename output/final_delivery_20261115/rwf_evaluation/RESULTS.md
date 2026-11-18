# Sealed fine-tuned RWF evaluation

Exploratory supervised evaluation on 400 previously inspected RWF clips. Epoch 2 and threshold 0.23 were selected solely on validation and sealed before evaluation.

| Model | Clips | Accuracy | Macro-F1 | AUC | Fight recall | False alarms | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| rwf_frozen_video (threshold 0.50) | 400 | 84.00% | 0.840 | 0.900 | 78.5% | 21 | 43 |
| rwf_finetuned_video (threshold 0.23) | 400 | 83.75% | 0.837 | 0.929 | 87.5% | 40 | 25 |

Every model retains its development threshold and normalization. All supplied labels are unchanged.

[Predictions](predictions.csv) | [Metrics](metrics.json) | [Audit](audit.json) | [Protocol](protocol.json)
