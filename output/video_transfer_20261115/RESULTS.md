# Frozen video-model RWF transfer

All 400 released evaluation clips, including low-pose clips.

| Frozen predictor | Accuracy | Macro-F1 | AUC |
|---|---:|---:|---:|
| Primary crowd fold 1 head | 63.2% | 0.619 | 0.712 |
| Predeclared five-head ensemble | 63.7% | 0.615 | 0.743 |

Exploratory transfer to previously evaluated RWF footage. No RWF fitting, normalization, threshold optimization or model selection. Primary head is crowd fold 1 by fixed convention, not selected for test performance. Other crowd fold heads and a predeclared equal-weight ensemble are supplementary. The ensemble threshold is the arithmetic mean of the five crowd-validation-selected thresholds. Scores are not calibrated probabilities. No supervised RWF or untouched benchmark claim is made; pretraining/source overlap is unaudited.

Full video decodes/frame indices verified. Saved features and heads reproduce all scores.
