# Failure analysis and motion controls

| Model | Test accuracy | Macro-F1 | ROC-AUC |
|---|---:|---:|---:|
| baseline | 66.0% | 0.658 | 0.810 |
| reliability | 63.8% | 0.638 | 0.792 |
| interactions | 70.2% | 0.701 | 0.864 |
| combined | 68.1% | 0.681 | 0.777 |
| motion_linear | 72.3% | 0.721 | 0.777 |
| pose_quality_only | 76.6% | 0.764 | 0.870 |

Combined model: 15 errors, including 7 false positives and 8 false negatives. 11 errors occur with at least 25% usable pose coverage. All skeleton variants miss 13 of the same clips.

The 80-dimensional motion descriptor uses real adjacent decoded frames near the original 32 anchors, not flow between distant sampled frames. Train-only normalization and logistic fitting; validation log-loss selects regularization from C=0.01,0.1,1,10; validation macro-F1 selects threshold. The seven-feature quality-only control uses fixed C=1 and no joint positions or trajectories.

This follow-up is exploratory because the original pilot test results were already inspected. The test set did not select these controls' coefficients, regularization or thresholds. No skeleton checkpoint or test partition was changed.

| Skeleton model | Motion correct, skeleton wrong | Skeleton correct, motion wrong | Both wrong |
|---|---:|---:|---:|
| baseline | 13 | 10 | 3 |
| interactions | 12 | 11 | 2 |
| combined | 13 | 11 | 2 |

Cross-split triage compared 16506 video pairs; 0 passed its heuristic. Inspect similarity.json and the twelve candidate sheets before treating any pair as related source footage.

Source-ID review finds 3 cross-split candidate pairs with matching titles/uploaders and prefix-compatible IDs. Exact filename grouping missed them. Sampled frames show matching footage in the Preston crowd pair. Zero hash flags do not establish source independence. The pilot must be regrouped and retrained before claiming source-independent performance.

Contact sheets cover all 47 test clips with six frames each. This is sparse visual triage; it cannot verify full-clip labels. No labels have been changed. Track observations and discarded detections are descriptive proxies, not measured tracking errors.

Next: review complete videos for suspicious labels and source overlap; validate the signal comparison across seeds and source-separated folds. If aggregate pose quality predicts violence well, investigate scene and detection confounds. Compare a stronger motion/RGB baseline before making representation-superiority claims.

![Motion comparison and pose coverage](comparison.png)
