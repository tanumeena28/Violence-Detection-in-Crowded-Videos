# Technical direction review

Recorded 15 November 2026. Paper drafting is deferred at Vishal's request.
This review used existing predictions and a CPU-only feature check. No new
GPU evaluation or training was launched.

The pipeline is complete within its current clip-level scope: raw video,
pretrained COCO poses, tracking, features, four TCN variants and a clip score.
The evidence supports continuing the research, while performance needs work.
Reliability's crowd mean accuracy is 76.9% against baseline 76.1%; combined is
74.8%, and quality-only is 77.6%. The proposed additions have no established
consistent benefit. The tested combined checkpoint reaches 56.0% accuracy and
0.578 AUC on RWF transfer, with 154 false positives among 200 NonFight clips.

Among the 152 NonFight clips above the pre-existing pose-coverage cutoff,
140 are false positives (92.1%). That cutoff measures usable detections rather
than independently verified pose correctness. Missing poses alone do not
explain these errors. Detection cues, feature artifacts, scene differences,
label ambiguity and action representation remain candidate explanations.

## Confirmed feature artifact

A synthetic person and box remain stationary across three frames. Hip
confidence drops only in the middle frame. Body centering switches from the
hip midpoint to the box center, then switches back. The shoulder coordinates
remain fixed in the image, yet the derived velocity changes from zero to
[-1.0, 1.5] and [1.0, -1.5] normalized units per second. The same root center
also feeds scene and relative velocities in interaction features.

[The check](centering_check.json) establishes that root-reference switching
can create artificial motion. It does not establish how many real errors it
causes or how much accuracy a correction will improve. The immediate feature
work is to handle reference changes consistently and add a regression check
for stationary joints with hip-confidence dropouts. Corrected feature semantics
must be versioned and evaluated with fresh model fitting in a new experiment.
The original checkpoints, feature definitions and reports remain preserved.

## Technical work order

1. Correct the confirmed centering/velocity artifact and test missing-hip,
   scaling and tracking-transition cases using CPU-only synthetic inputs.
2. Review the 40 predefined diagnostic cases: ten FP, FN, TN and TP each.
   Record visible motion, camera movement, crowd density, occlusion, hip
   fallback changes, track switches and suspicious labels. Independent label
   review should use a separate view without model predictions.
3. Freeze controls that test detection-only input and temporal-order dependence.
   Use saved caches for preliminary CPU diagnostics. Report diagnostic
   perturbations separately from newly trained representation ablations.
4. Establish a credible pretrained RGB/video reference on the same reviewed
   crowd folds. A frozen encoder with a small classifier and small batches is
   feasible on the local GPU; larger fine-tuning can use the college server.
5. Choose the next motion or interaction change from the observed failures,
   then compare fresh fits with identical source groups, folds, seeds,
   training budgets and validation-only selection. A stronger skeleton
   encoder is a candidate after these controls establish the bottleneck.
6. Finish controlled cold/warm full-pipeline timing and update the demonstration
   with representative correct predictions, false positives and misses.

Current RWF scores are already inspected. Future RWF training must choose
hyperparameters and thresholds using a separately defined training/validation
protocol and disclose reuse of previously evaluated footage. The low current
AUC indicates weak ranking; a threshold change alone cannot be assumed to
produce a strong detector.

[Diagnostic case list](review_cases.json) | [Current plan](../../NEXT_STEPS.md) |
[Completion estimate](../../PROJECT_STATUS.md)
