# Crowd violence detection with pose reliability and relative interactions

Methods and results draft, updated 15 November 2026. This is working manuscript text, not the complete 12-page submission. It preserves the corrected single-holdout pilot, completed repeated source-grouped evaluation in section 11, the matched explicit coverage ablation in section 12, and one-time RWF transfer evaluation in section 13.

## 1. Research question

Visible crowd motion is an imperfect indicator of violence: cheering, running and close nonviolent contact can resemble aggressive activity, while crowd occlusion makes body joints difficult to estimate. We study whether explicit joint-reliability handling and relative person interactions improve a fixed skeleton-based temporal baseline. The task is binary classification of a short video clip using its supplied violent or nonviolent label. Person identity, intent, individual guilt and precise event localization are not prediction targets.

The hypothesis is evaluated rather than assumed. A useful outcome can be a bounded finding about when poses fail or when detection and scene cues dominate. The current experiments do not establish superiority of the proposed combination.

## 2. Data and source grouping

The local Violent-Flows release contains 246 low-resolution AVI clips arranged into five supplied folds, with 123 labels per class. One byte-identical nonviolent duplicate within fold 5 was removed, leaving 245 unique video files. All selected videos are decoded fully before frame sampling; sampling therefore uses the actual decoded length rather than assuming the container frame count is exact.

The initial pilot used folds 1-3 for training, fold 4 for validation, and fold 5 for evaluation. Exact stored source keys were disjoint, but a later source review found truncated source IDs that defeated exact filename grouping. Three training clips shared titles/uploaders and prefix-compatible IDs with validation clips. Two Preston crowd clips showed matching footage in sampled review; a Russia/Ukraine pair was conservatively grouped by source ID despite different sampled segments. The affected training clips were excluded while retaining the original validation and test clips.

The corrected pilot has 147 training clips (75 nonviolent, 72 violent), 48 validation clips (24 per class), and 47 test clips (23 nonviolent, 24 violent). Canonical source grouping links matching crowd titles/uploaders when an ID of at least two characters prefixes the longer ID. No known exact or prefix-compatible source-ID overlap remains across the corrected partitions. This rule does not establish that all related footage has been found, and manual source review remains necessary.

The correction was made after inspecting the original pilot test results. All current comparisons are exploratory; they do not constitute evaluation on a fresh, untouched benchmark. Labels were not changed based on model predictions.

## 3. Pose extraction and tracking

A pretrained YOLO11n-pose model estimates COCO's 17 body joints. Each clip supplies 32 uniformly sampled frames, processed at image size 640 with detector confidence 0.2. Coordinates are normalized to the original image. A joint is treated as valid when confidence is at least 0.25.

Within-clip Hungarian association combines box overlap and center distance. Track IDs reset for each clip. Up to eight tracks are retained using observed keypoint signal; detected and discarded track counts are recorded. The system does not re-identify people across videos. Occlusion, camera cuts, fragmented tracks and the track cap can remove useful information.

Per-video caches store keypoints, boxes, presence masks, track IDs, sampled frame indices and times, source SHA-256, extraction settings signature, and quality measurements. Corrected experiments reuse these immutable video features, but recompute training normalization and all classifiers. Cache reuse is conditional on matching source and settings provenance.

## 4. Body-motion and interaction features

Body coordinates are centered at the mean of the two hips when both are valid; otherwise the box center is used. Scale is the box-diagonal length with a lower bound. Missing joints are masked, normalized coordinates are clipped, and joint velocities use actual differences in sampled frame time. A temporal difference is valid only when its joint is valid in both neighboring observations, avoiding artificial velocity spikes from missing joints.

Reliability features multiply positions and velocities by detector confidence and append joint-confidence and validity channels. Detector confidence is not assumed to be calibrated probability of correctness.

Interactions are calculated in shared normalized image coordinates before individual body centering. Each present track uses its nearest present neighbor. Features describe distance, two-dimensional offset, relative velocity, signed radial relative velocity, normalized neighbor count, and neighbor presence. Tracking and pose errors can corrupt this geometry.

The four variants have 68 baseline channels, 102 reliability channels, 76 interaction channels, and 110 combined channels per track per frame. They share pose inputs, observation masks, placeholder policy, splits and encoder family.

## 5. Temporal model and training

A shared per-person temporal convolutional network first projects inputs to 48 hidden channels, then applies residual temporal blocks with dilations 1, 2 and 4. Temporal aggregation masks absent observations. Mean and max pooling across observed people, together with an observed-track coverage scalar, feed a binary classifier. Pooling is invariant to the ordering of person slots; output remains a whole-clip score.

Including coverage means the model can access detection cues explicitly. Masking, track counts, fallback centering and missing joints also expose estimator behavior indirectly. This motivates the quality-only control below.

Training uses AdamW with learning rate 0.001, weight decay 0.01, batches of 16, and gradient clipping at norm 1. Binary cross-entropy weights positives from the training class counts. The maximum budget is 180 epochs with patience 30. This pilot uses seed 42. Normalization statistics come only from observed training features, with standardized values clipped to a fixed range. Validation loss selects the checkpoint, and validation macro-F1 selects a threshold on a fixed 0.10-0.90 grid. Test scores do not select checkpoints or thresholds.

Input-channel changes increase parameter count: 36,001 baseline, 37,633 reliability, 36,385 interactions, and 38,017 combined. Checkpoints include training statistics, manifest hash, feature schema and extraction signature.

## 6. Diagnostic controls

An adjacent-frame motion control summarizes grayscale frame differences and Farneback optical flow at the same sampled time anchors, using a neighboring decoded frame at each anchor. The resized image is 160 by 120. A 2-by-2 grid summarizes absolute grayscale differences, flow speed, median-subtracted flow speed, and horizontal/vertical velocity; mean, standard deviation, 90th percentile and maximum across time produce 80 features. This is a handcrafted linear reference, not a reproduced published RGB/flow deep model. Median subtraction is not validated camera stabilization.

A separate seven-feature quality-only control uses usable-pose fraction, mean people, valid-joint fraction, total tracks, maximum detected people, discarded tracks and frames with people. It has no joint coordinates or trajectories and measures whether aggregate detection cues predict dataset labels.

Both controls use training-only standardization and logistic fitting. Validation log loss chooses motion regularization from C = 0.01, 0.1, 1 and 10; quality-only C is fixed at 1. Validation macro-F1 chooses thresholds. Their architecture, parameter count and temporal input access differ from the TCN, so these are signal diagnostics rather than equal-capacity representation comparisons. They were introduced after inspecting the original pilot results.

## 7. Preliminary corrected results

All 47 selected test clips remain in reported metrics, including low-pose clips.

| Model | Accuracy | Macro-F1 | Violent precision | Violent recall | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Baseline | 68.1% | 0.680 | 0.714 | 0.625 | 0.808 |
| Reliability | 63.8% | 0.638 | 0.652 | 0.625 | 0.781 |
| Interactions | 68.1% | 0.679 | 0.737 | 0.583 | 0.850 |
| Combined | 66.0% | 0.658 | 0.700 | 0.583 | 0.786 |
| Motion linear | 74.5% | 0.744 | 0.800 | 0.667 | 0.766 |
| Quality only | 76.6% | 0.764 | 0.842 | 0.667 | 0.873 |

The test majority-class baseline is 51.1%. Interaction ROC-AUC exceeds baseline ROC-AUC on this split, but the chosen threshold yields the same accuracy and slightly lower macro-F1. Reliability and the combined variant do not improve accuracy. One split and one seed cannot establish significant differences or a general benefit from the candidate additions.

Quality-only performance exceeds all skeleton variants on this split. This is consistent with scene, crowd density or detection behavior carrying label signal, but it does not identify the cause. Strong performance from this control does not by itself establish that every skeleton prediction is driven by those cues. Source-separated folds/seeds and additional ablations are needed.

The combined model has six false positives and ten false negatives. Eleven errors occur with at least 25% usable pose coverage, so absent poses do not explain every failure. Average usable pose coverage over the corrected corpus is 74.3%; 31 clips have coverage below 25%. Short observed tracks and discarded detections are descriptive proxies rather than measured identity switches or confirmed causal failure mechanisms.

## 8. Demonstration and verification

Inference is offline over full clips. Annotated videos display the clip score, threshold, quality status and clip-local tracks. The overlay uses the nearest sampled pose frame, not frame-by-frame tracking. Below 25% usable sampled frames, the demo flags insufficient pose evidence. This is an initial operational cutoff, not a validated rejection system.

Six held-out demonstrations were chosen by the first filenames in each class, without correctness filtering. An additional raw-video execution check used a previously inspected RWF-2000 non-fight clip. Fresh pose extraction succeeded and all 150 encoded output frames decoded. The corrected classifier produced a false positive at score 0.844 with threshold 0.54. This checks pipeline execution and documents a limitation; it is not external benchmark accuracy.

Saved-artifact checks verify source hashes, extraction provenance, training-only normalization, reproduced validation/test scores and unchanged decisions. Both linear checkpoints reproduce all saved scores and split metrics; six held-out videos decode completely. These checks establish artifact consistency, not label correctness or generalization. Bootstrap accuracy intervals in the audit reflect the fixed holdout only, not fold, training-seed or source-group uncertainty.

## 9. Work required for the final paper

Complete independent label review, inspect actual occlusion and nonviolent high-motion cases using a documented rubric, add a stronger RGB reference and meaningful external evaluation, and measure full-pipeline latency on specified hardware. The 7 November source-grouped experiment below expands the single-holdout comparison; the explicit coverage ablation is complete in section 12 and one-time RWF transfer evaluation is complete in section 13. Treat existing videos and results as previously inspected development evidence. The complete paper, including related work and verified references, remains due before 20 November.

The proposed flagged-window extension is not implemented or evaluated. Clarify its necessity for the final presentation. Avoid adding person attribution, federated training or differential privacy without an explicit scope decision.

## 10. Evidence and references to finalize

- [Corrected results](../output/source_corrected/index.html), [artifact audit](../output/source_corrected/AUDIT.md), [correction provenance](../output/source_corrected/correction.json), and [per-clip diagnostics](../output/source_corrected/failure_analysis/test_diagnostics.csv).
- Hassner, Itcher and Kliper-Gross, *Violent Flows: Real-Time Detection of Violent Crowd Behavior*, CVPR Workshops, 2012. Dataset: https://www.openu.ac.il/home/hassner/data/violentflows/
- Cheng, Cai and Li, *RWF-2000: An Open Large Scale Video Database for Violence Detection*, ICPR 2020. https://arxiv.org/abs/1911.05913
- Famouri, Hossain and Imteaj, *Pose to Protect*, ICCV Workshops, 2025. Local reference PDF is available in the project.
- Ultralytics pose-model documentation: https://docs.ultralytics.com/tasks/pose/

Complete the related-work comparison and verify every bibliographic detail before submission. This draft makes no claim that skeleton violence detection or interaction modeling is new.

## 11. Repeated evaluation protocol: 7 November 2026

Source triage fully decoded all 245 unique clips, containing 22,027 decoded frames. Sampling near four frames per second produced 3,638 observations. Full-frame and central-crop perceptual hashes, grayscale correlation and temporal alignment screened 29,856 pairs from different filename-derived source groups. The fixed heuristic flagged five pairs. Visual review of 20 candidate sheets supported 13 source links, including recordings under different uploaders and footage with different cropping or watermarks. Two links were redundant through existing groups; the known source-group count decreased from 215 to 204.

These links record shared recordings, including different segments. The review preserved supplied labels and does not certify every frame's violence label or absence of other shared footage. [The source-review record](../output/source_review_20261107/REVIEW.md) includes decisions and image evidence.

The new experiment uses all 245 clips, assigning each whole source group to one of five custom stratified outer folds. Each rotation uses 147 training, 49 validation and 49 test clips. The preceding outer fold supplies validation. Every unique clip is evaluated once per TCN seed and once per deterministic control. This differs from the dataset's supplied five-fold protocol and from the earlier corrected 242-clip holdout. The three clips excluded from that holdout can participate here because their related footage is kept in the same source group.

Four TCN variants use seeds 42, 123 and 2026, giving 60 fits. The two linear controls use the same rotations and are fitted once per fold, giving 10 additional fits. Repeating deterministic linear fits under several seed labels would not add training-seed variation. Motion regularization uses the original validation log-loss grid; quality-only regularization remains fixed at C=1. Training-only scaling and validation-selected checkpoints and thresholds are recomputed within every rotation.

The plan freezes source links, partitions, extraction provenance, per-video pose/motion caches, quality descriptors, code and fitting settings. Completed artifacts are hashed for resumability. Per-fold AUC is averaged across runs; classification decisions can also be pooled per seed over all 245 clips. AUC is not pooled across separately fitted classifiers because their score calibration differs. Reported standard deviations describe dependent fold/seed runs and are not confidence intervals or significance tests.

The experiment is stored in `output/cross_validation_20261107/`. The older pilot artifacts remain separate. Cached-feature fitting does not measure full-pipeline latency or establish real-time performance.

All 70 fits completed locally, with the 60 TCN fits using the RTX 3050 Laptop GPU. The table reports equal-weight means over 15 fold/seed runs per TCN variant and five fold runs per deterministic control.

| Model | Fits | Accuracy mean | Accuracy SD (pp) | Macro-F1 mean +/- SD | ROC-AUC mean +/- SD |
|---|---:|---:|---:|---:|---:|
| Skeleton baseline | 15 | 76.1% | 4.8 | 0.756 +/- 0.054 | 0.860 +/- 0.035 |
| Reliability | 15 | 76.9% | 5.5 | 0.766 +/- 0.056 | 0.864 +/- 0.039 |
| Interactions | 15 | 76.1% | 6.0 | 0.755 +/- 0.064 | 0.854 +/- 0.052 |
| Combined | 15 | 74.8% | 6.1 | 0.739 +/- 0.071 | 0.860 +/- 0.045 |
| Adjacent-frame motion control | 5 | 75.1% | 5.3 | 0.748 +/- 0.053 | 0.798 +/- 0.072 |
| Pose-quality-only control | 5 | 77.6% | 6.1 | 0.773 +/- 0.064 | 0.861 +/- 0.045 |

Accuracy SD is in percentage points. All standard deviations are descriptive variation across dependent runs, not confidence intervals. Reliability exceeds baseline mean accuracy by approximately 0.8 percentage points and has the highest mean ROC-AUC among the skeleton variants. Interactions match baseline mean accuracy, while combined is approximately 1.2 percentage points lower. These small differences do not establish a significant or consistent benefit from the proposed additions.

Quality-only slightly leads mean accuracy and macro-F1 without joint positions or trajectories. Aggregate detection behavior therefore carries predictive signal under these custom source-grouped rotations. This does not establish which detection cues explain the result or that every skeleton prediction depends on them. Section 12 records the subsequent focused explicit-coverage ablation; masks, track availability and missing joints still provide indirect detection cues.

These scores should not be described as an accuracy improvement over the 47-clip pilot. The number of clips, source grouping, partitions and seed aggregation differ, and both stages used previously inspected data. The new evaluation improves the breadth and reproducibility of the comparison while preserving the limitations of exploratory development evidence.

The saved-artifact verifier reproduced all 70 fits, including training-only normalization, validation-selected thresholds and identical classification decisions. Maximum CPU score drift was 0.0002628565, within the 0.0003 verification tolerance. Motion regularization also matched the validation choice. These checks establish artifact consistency and split provenance, not complete source independence, independently validated violence labels or external generalization. The implementation suite passed 20 tests.

[The results page](../output/cross_validation_20261107/index.html), [fold/seed summary](../output/cross_validation_20261107/summary.json), [out-of-fold predictions](../output/cross_validation_20261107/out_of_fold_predictions.csv), [verification record](../output/cross_validation_20261107/audit.json), and [comparison figure](../output/cross_validation_20261107/figures/comparison.png) provide the supporting artifacts. [The experiment guide](../output/cross_validation_20261107/README.md) explains how to inspect the run with its archived implementation after later code changes.

## 12. Explicit coverage ablation: 14 November 2026

The quality-only control motivates an isolated test of the TCN's explicit observed-track coverage input. A new experiment replaces that scalar with a constant zero. The classifier retains its original 97 input slots: 48 pooled means, 48 pooled maxima and the zeroed scalar. This preserves nominal parameter counts, initial weights and random-number draws under each seed. The 48 first-layer weights connected to the zeroed slot receive no data-dependent gradient. Observation masks, temporal pooling, joint features and interaction features are otherwise unchanged. The experiment therefore tests access to this one direct scalar, rather than removing all detection information.

The new plan reuses exactly the November 7 source links, 204 groups, 245 unique clips, five fold assignments, split seed 42 and training seeds 42, 123 and 2026. Each rotation again uses 147 training, 49 validation and 49 test clips. All four variants receive 15 fresh fits; the two unchanged linear controls receive five fresh fits each. Training normalization, model fitting, validation-selected checkpoints and thresholds are recomputed. Pose/motion inputs, feature-construction hashes, training budget, nominal parameter counts and fitted input shapes match the reference. The intended comparison was recorded before the new fits completed.

The table pairs coverage-off minus coverage-on within each variant, fold and seed. Accuracy changes and their descriptive standard deviations use percentage points. The other changes use their original metric scales.

| Model | Coverage on accuracy | Coverage off accuracy | Accuracy change mean +/- SD (pp) | Macro-F1 change | ROC-AUC change | Accuracy improved/tied/worse runs |
|---|---:|---:|---:|---:|---:|---:|
| Skeleton baseline | 76.1% | 76.1% | 0.00 +/- 0.77 | +0.0003 | -0.0009 | 1/13/1 |
| Reliability | 76.9% | 76.9% | 0.00 +/- 0.00 | -0.0001 | +0.0014 | 0/15/0 |
| Interactions | 76.1% | 75.9% | -0.14 +/- 0.53 | -0.0007 | +0.0022 | 0/14/1 |
| Combined | 74.8% | 74.8% | 0.00 +/- 0.00 | 0.0000 | -0.0009 | 0/15/0 |

Zeroing explicit coverage leaves three mean accuracies unchanged and lowers interaction accuracy by approximately 0.14 percentage points. It changes 19 of 2,940 repeated TCN test decisions: four baseline, two reliability, thirteen interactions and zero combined. Nine previous errors are corrected and ten previously correct decisions become errors. Each variant has 735 decisions across three seeds, with the same 245 clips repeated, so these observations are not independent test samples. Accuracy ties can still contain changed decisions, as in the reliability variant. The unchanged linear controls reproduce identical test scores, thresholds and decisions; quality-only remains at 77.6% mean accuracy.

Under these settings, the explicit scalar has little effect on measured accuracy. This result does not resolve the broader detection-cue dependence question. Missing observations affect pooling; joint confidence, validity and missingness remain available; interaction channels still encode neighbor counts and presence. A model can obtain related information through those paths. The ablation cannot establish that the remaining predictive signal comes only from body motion, nor that detection behavior explains every prediction. Small ROC-AUC changes and descriptive run counts do not establish significance. Existing footage was inspected previously, and label correctness and unknown source relationships remain limitations.

The initial CPU reproduction attempt failed the unchanged absolute score tolerance of 0.0003. A full supplemental CPU audit checked 5,880 validation/test scores: one exceeded tolerance, with maximum absolute drift 0.0003354549. No classification decisions or validation-selected thresholds changed on CPU. Verification was extended to support the training GPU, and the updated verification implementation was archived separately. All 140 reference/new fits reproduced their saved scores exactly on the RTX 3050, including identical decisions, training-only normalization and validation-selected thresholds. The frozen training protocol, original implementation and fitted models were preserved; no model was refitted to address the audit difference. All 947 reference files match their pre-experiment hash inventory. The implementation suite passed 24 tests.

The new experiment is stored in `output/coverage_ablation_20261114/`. The [paired report](../output/coverage_ablation_20261114/coverage_ablation.html), [fold/seed changes](../output/coverage_ablation_20261114/coverage_paired_runs.csv), [detailed comparison](../output/coverage_ablation_20261114/coverage_comparison.json), [GPU audit](../output/coverage_ablation_20261114/audit.json), [CPU precision audit](../output/coverage_ablation_20261114/cpu_precision_audit.json), [reference preservation record](../output/coverage_ablation_20261114/reference_integrity_verified.json) and [experiment guide](../output/coverage_ablation_20261114/README.md) provide the evidence and reproduction commands. This cached-feature experiment does not measure full-pipeline latency or external generalization.

## 13. One-time RWF-2000 transfer: 15 November 2026

A single exploratory evaluation uses the existing source-corrected `combined_seed42` crowd checkpoint on all 400 clips in the released RWF-2000 evaluation partition: 200 Fight and 200 NonFight. This is the canonical checkpoint already used for the pipeline demonstration, trained on 147 crowd clips with checkpoint selection and threshold selection from the corrected crowd validation partition. Its threshold remains 0.54. Its saved crowd-training feature means and standard deviations are reused. RWF observations do not fit weights, normalization or a new threshold.

The clip inventory, checkpoint, pose weights, extraction settings, implementation and known prior inspection are frozen before the scoring pass. Fresh extraction uses the original 32 sampled frames, eight retained tracks, image size 640 and batch size 12. Both pose extraction and classification run on the local RTX 3050 Laptop GPU. All 400 clips decode completely, and decoded frame counts match their container headers. No byte-identical overlap with the crowd development manifest was found; other source relationships and label ambiguity remain unverified.

| Evaluation | Clips | Accuracy | Macro-F1 | Fight precision | Fight recall | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|
| All released evaluation clips | 400 | 56.0% | 0.506 | 0.536 | 0.890 | 0.578 |
| Excluding the known prior demo clip | 399 | 56.1% | 0.508 | 0.538 | 0.890 | 0.577 |
| Pose-supported subset, secondary | 347 | 54.2% | 0.410 | 0.557 | 0.903 | 0.508 |

The primary confusion matrix, with rows representing supplied NonFight/Fight labels and columns representing NonFight/Fight predictions, is [[46, 154], [22, 178]]. The model detects 178 of 200 Fight clips, but misclassifies 154 of 200 NonFight clips. Its false-positive rate among NonFight clips is 77%. This indicates weak transfer under the frozen protocol, despite high Fight recall. The balanced evaluation's majority-class accuracy is 50%. The result does not establish external robustness or a successful improvement from the proposed additions.

One NonFight clip was inspected in the earlier raw-video demonstration and had already produced a false positive. It remains in primary metrics, with a supplementary 399-clip result excluding it. Exclusion changes the numerical result only slightly. Fifty-three clips fall below the pre-existing 25% usable-pose cutoff. All remain in primary metrics. The pose-supported subset covers 86.75% of released clips and is reported separately; its performance does not replace the all-clip result. Additional prior viewing or shared footage cannot be ruled out, so the remaining 399 clips are not certified as untouched evaluation evidence.

The complete staged evaluation took 190.33 seconds, including model initialization, full-video decoding, sampled pose extraction, cache writes/loads, fixed feature normalization and classification. It excludes inventory preparation and report generation. The classifier pass itself took 0.303 seconds for all 400 cached feature tensors. These are different measurement boundaries. The whole-evaluation wall time is not a controlled cold/warm per-video latency benchmark and does not establish streaming real-time behavior.

The verification checks frozen checkpoint/settings, source and pose-cache hashes, complete clip coverage, reuse of saved normalization, preservation of the original crowd artifacts and reproduction of metrics from saved prediction scores. Reopening the completed record verifies its hashes and returns the stored result without new extraction or inference. The implementation suite passed 26 tests, including saved-normalization independence and completed-evaluation reuse protection.

[The results page](../output/rwf_transfer_20261115/index.html), [per-clip predictions](../output/rwf_transfer_20261115/predictions.csv), [metrics](../output/rwf_transfer_20261115/metrics.json), [frozen protocol](../output/rwf_transfer_20261115/protocol.json), [audit](../output/rwf_transfer_20261115/audit.json) and [experiment guide](../output/rwf_transfer_20261115/README.md) provide the evidence. This study measures transfer of a crowd-trained classifier. A stronger RGB reference or supervised RWF experiment would require a separately defined protocol and an explicit account of previously evaluated footage.

