# Matched CPU centering study

The corrected feature schema is `coco17-continuous-hip-offset-v2`. The paired
reference is [the fresh legacy CPU experiment](../centering_reference_cpu_20261115/).
Both use the same 245 crowd clips, 204 reviewed source groups, five folds,
three seeds, four TCN variants and two deterministic controls. Each experiment
requires 60 TCN fits and 10 control fits. Coverage remains enabled.

Both schemas are fitted on CPU because the laptop GPU was authorized for one
saved-model RWF evaluation. The November 7 GPU experiment is preserved. Its
legacy features, coverage-enabled architecture, initialization and CPU model
outputs match the current legacy implementation exactly in
[the compatibility audit](../technical_review_20261115/legacy_compatibility.json).
Fresh CPU fitting avoids attributing CPU/GPU training differences to centering.

Normalization is fitted on training clips. Validation clips select checkpoints
and thresholds. No weights, normalization or thresholds are inherited from
previous fitted models. Reported variation across folds/seeds is descriptive.
The footage has already been inspected, so the study remains exploratory.

Inspect or resume the frozen study from the project root:

```powershell
& '.\.venv\Scripts\python.exe' output/centering_corrected_cpu_20261115/run_snapshot.py run-cv --device cpu
& '.\.venv\Scripts\python.exe' output/centering_corrected_cpu_20261115/run_snapshot.py report-cv --date 2026-11-15 --verification-device cpu
& '.\.venv\Scripts\python.exe' output/centering_corrected_cpu_20261115/run_snapshot.py compare-centering --reference output/centering_reference_cpu_20261115 --date 2026-11-15 --verification-device cpu
```

After completion, [the comparison](centering_ablation.html),
[comparison notes](CENTERING_COMPARISON.md), [experiment results](index.html),
[saved-fit audit](audit.json) and [frozen protocol](protocol.json) record the
evidence. `training_cpu.log` records the local fits. The [feature schema guide](../../FEATURE_SCHEMAS.md)
explains the correction and compatibility policy. Whole-clip interpolation is
offline and still depends on detected joint and box quality. This crowd study
does not establish improved RWF transfer.
