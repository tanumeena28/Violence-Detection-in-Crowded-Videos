# Implementation discussion: pilot run 22 October 2026

## Opening explanation

My pipeline now runs from raw crowd videos to pose extraction, tracking, motion and interaction features, a trained temporal model, and video predictions. I have implemented the four variants in the presentation on identical inputs and splits. This is a feasibility pilot; I am showing actual outputs and failure cases rather than claiming completed benchmark performance.

## Source overlap found

The original filename keys missed 3 training/validation candidate pairs with matching titles/uploaders and truncated source IDs. Sampled Preston footage matches visually. All current scores describe the archived pilot and do not establish source-independent performance. The grouping rule now links these IDs for future runs. Regroup and retrain before reporting corrected results.


## Demonstration order

1. Open `index.html` and explain the pipeline.
2. Show a held-out nonviolent and violent video. Explain that the IDs are clip-local tracks, not person-level violence labels.
3. Show the results table and actual loss curves.
4. Explain pose misses, track fragmentation, and the small single-split evaluation.
5. Discuss the next validation experiments and scope with the professor.

## What was implemented

- Video inventory, exact duplicate removal, and source-group split checks.
- Pretrained YOLO11n-pose, 32 uniformly sampled frames per clip, COCO-17 joints.
- Hungarian matching using box overlap and center distance, reset for every clip.
- Up to 8 tracks, chosen by observed keypoint signal. Report discarded tracks.
- Body-centered positions, temporal changes, confidence weighting and validity masks.
- Nearest-person distances, offsets, relative velocities, and approach rate in shared scene coordinates.
- Shared per-person TCN, masked temporal and person pooling, binary clip classifier.
- Real training on 150 clips, validation on 48, final pilot test on 47.
- Validation-selected checkpoint and threshold; saved model, manifest, feature statistics, and extraction signature.
- Offline video demos and new-video inference. No person labels or timestamp annotations were available.

## Actual pilot results

| Variant | Parameters | Accuracy | Macro-F1 | ROC-AUC |
|---|---:|---:|---:|---:|
| baseline | 36,001 | 66.0% | 0.658 | 0.810 |
| reliability | 37,633 | 63.8% | 0.638 | 0.792 |
| interactions | 36,385 | 70.2% | 0.701 | 0.864 |
| combined | 38,017 | 68.1% | 0.681 | 0.777 |

These results use one seed and one holdout, not five-fold/three-seed evaluation. Mean usable pose coverage is 74.0%; 32 clips fall below 25%. The original dataset labels are used as supplied. A pose model failing to see people is not evidence of a nonviolent event.

## Follow-up controls

| Control | Accuracy | Macro-F1 | ROC-AUC |
|---|---:|---:|---:|
| motion_linear | 72.3% | 0.721 | 0.777 |
| pose_quality_only | 76.6% | 0.764 | 0.870 |

Motion uses adjacent-frame differences and optical flow summarized into 80 features. Quality-only uses seven detection descriptors and no joint positions or trajectories. Training clips define scaling and coefficients; validation clips select regularization and thresholds. These are exploratory results after prior test inspection. Check the source review before interpreting the comparison.

Investigate scene and detection confounds before claiming the model learned violent body motion. The saved-control audit reproduces scores and decisions and checks training normalization and validation thresholds.

The combined model has 7 false positives and 8 false negatives; 11 errors occur with at least 25% pose coverage. Review [every test clip and source candidate](failure_analysis/index.html).


## Important technical details

The combined feature tensor per clip is [32, 8, 110]: time, track slots, feature channels. Only training observations define normalization statistics. The same temporal encoder size and tuning budget are used for the four variants; extra input channels change parameter count, which is reported. Demo scores are offline full-clip scores and are not calibrated probabilities. The sampled skeleton overlay is held until the nearest next sampled frame, so it is a visualization of sampled inputs rather than full-frame pose tracking.

The pose confidence threshold is 0.25. A frame is called usable when at least five joints pass this threshold anywhere among retained people. Demo abstention below 25% usable frames is an initial quality rule, not a tuned or validated rejection system. Test metrics include every selected clip regardless of pose quality.

## Questions to discuss

- Is clip-level violence detection with reliability/interaction ablations the agreed final scope?
- Should the next stage prioritize an RGB reference, external RWF-2000 validation, or full crowd cross-validation?
- What date applies to this group's final presentation?
- What paper format should be used for the required draft before 20 November?

## Next stage

First regroup related source footage and retrain on the corrected split. Then compare the skeleton and quality/motion signals across source-separated folds and seeds. Review full videos and labels; compare a stronger RGB/motion model and external RWF-2000 performance. Write methods now and expand the results after those experiments.
