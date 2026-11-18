# Pose feature schemas

Raw pose extraction is unchanged. The cached COCO-17 tensors, tracking and
pose signatures are compatible with both derived-feature schemas. A checkpoint
records its feature schema, and inference builds the features that checkpoint
was trained on. New training defaults to the corrected schema; old checkpoints
retain their original behavior.

| Schema | Center when both hips are reliable | Center when hips are missing |
|---|---|---|
| `coco17-hip-box-center-v1` | Measured hip midpoint | Bounding-box center for that frame |
| `coco17-continuous-hip-offset-v2` | Measured hip midpoint | Box center plus interpolated hip-to-box offset within the continuous observed track segment |

The correction interpolates the offset using sampled timestamps. At segment
edges it extends the nearest reliable offset. Segments without reliable hips
keep box-center fallback. Missing-track gaps split segments and are not filled.
The same center supplies body normalization and interaction geometry/velocity.
Joint validity, confidence weighting, box scale and velocity clipping are
unchanged.

The legacy fallback can move the reference point while a person is stationary.
The regression example produces shoulder velocities of `[-1.0, 1.5]` and
`[1.0, -1.5]` when hip confidence drops and returns. Corrected velocities are
zero. This correction uses the whole offline clip; it does not establish causal
streaming behavior or eliminate box jitter, incorrect joints or tracking errors.

The audit of 245 crowd caches changes centers in 166 clips and 3,390 of 22,557
observed person-frames. These are feature-change counts, not a count of proven
false motions or corrected classifications. [The audit](output/technical_review_20261115/centering_feature_audit.json)
records per-clip changes. [Legacy compatibility](output/technical_review_20261115/legacy_compatibility.json)
confirms exact features/masks for all 980 clip/variant builds against the
November 7 snapshot, plus matching coverage-enabled network initialization and
CPU outputs for all four variants.

Select a schema explicitly when preparing a new experiment:

```powershell
& '.\.venv\Scripts\python.exe' -m affective.cli --out output/new_centering_study prepare-cv --source output/pilot --source-merges output/source_review_20261107/source_merges.json --source-review output/source_review_20261107/review.json --feature-schema coco17-continuous-hip-offset-v2
```

Never apply corrected inputs to a legacy checkpoint to claim a model
improvement. Compare fresh fits in separate directories, using matching data,
folds, seeds, budgets, training devices and package versions. Training data
defines normalization; validation data selects checkpoints and thresholds.
Use each experiment's `run_snapshot.py` to inspect it after source changes.

The centering study uses CPU for both schemas to match training conditions.
It began while GPU use was limited to the one-time saved-model evaluation.
Vishal subsequently authorized further GPU work overnight; input controls and
the video baseline/transfer are recorded separately. A crowd-only centering
comparison cannot measure an improvement in RWF transfer.
