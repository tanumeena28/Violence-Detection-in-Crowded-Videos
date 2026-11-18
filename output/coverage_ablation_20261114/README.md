# Explicit coverage ablation: 14 November 2026

This experiment pairs the four coverage-disabled TCN variants with the completed
[November 7 reference](../cross_validation_20261107/README.md). It uses the same
245 clips, 204 reviewed source groups, five outer folds and three seeds. The
explicit coverage input is zeroed while preserving head dimensions and
initialization. Other detection cues remain available.

[The experiment rationale](EXPERIMENT.md) records the intended change and
comparison measures. `protocol.json` freezes the inputs and settings. The
training log is `training.log`; fitted artifacts are in `fold_1/` to `fold_5/`.

Inspect the completed results:

- [Paired coverage comparison](coverage_ablation.html) and [research notes](COVERAGE_ABLATION.md).
- [Coverage-disabled results](index.html), [fold summary](summary.json), [GPU audit](audit.json)
  and [CPU precision audit](cpu_precision_audit.json).
- [Detailed changes](coverage_comparison.json), [paired fold/seed runs](coverage_paired_runs.csv)
  and [out-of-fold predictions](out_of_fold_predictions.csv).
- `reference_integrity_before.json` and `reference_integrity_verified.json`
  document that the earlier experiment's files were preserved.

From the project root, use the frozen training implementation to inspect the
summary, and the separately archived GPU verifier to reproduce the reports:

```powershell
& '.\.venv\Scripts\python.exe' output/coverage_ablation_20261114/run_snapshot.py summarize-cv
& '.\.venv\Scripts\python.exe' output/coverage_ablation_20261114/run_verification.py report-cv --date 2026-11-14
& '.\.venv\Scripts\python.exe' output/coverage_ablation_20261114/run_verification.py compare-coverage --reference output/cross_validation_20261107 --date 2026-11-14
& '.\.venv\Scripts\python.exe' output/coverage_ablation_20261114/verification_snapshot/scripts/audit_cv_cpu_precision.py --out output/coverage_ablation_20261114
```

The comparison validates the reference against its own implementation snapshot
and reads its saved fits without rewriting its artifacts. Both experiments must
be complete. It checks matching inputs, settings, nominal parameter counts,
score reproduction and unchanged linear controls before publishing a comparison.

The initial CPU report failed its unchanged absolute score tolerance of 0.0003.
The verifier was extended to support the training GPU, with its code and hashes
stored in `verification_snapshot/` and `verification_implementation.json`.
The frozen training protocol, original implementation and fitted artifacts were
preserved. `report_audit.log` retains the failed CPU attempt; the complete
cross-device measurements are in `cpu_precision_audit.json`. A CPU score outside
tolerance remains a failed CPU score check, even if its binary decision agrees.
GPU report and comparison logs are `gpu_report_audit.log` and `comparison_audit.log`.

For a new experiment, choose a new output directory. The current commands are:

```powershell
& '.\.venv\Scripts\python.exe' -m affective.cli --out output/coverage_ablation_new prepare-cv --source output/pilot --source-merges output/source_review_20261107/source_merges.json --source-review output/source_review_20261107/review.json --no-coverage
& '.\.venv\Scripts\python.exe' -m affective.cli --out output/coverage_ablation_new run-cv --device cuda
& '.\.venv\Scripts\python.exe' -m affective.cli --out output/coverage_ablation_new report-cv --date 2026-11-14 --verification-device cuda
& '.\.venv\Scripts\python.exe' -m affective.cli --out output/coverage_ablation_new compare-coverage --reference output/cross_validation_20261107 --date 2026-11-14 --verification-device cuda
```

Omit `--no-coverage` to retain the original explicit coverage input. A completed
experiment is never overwritten. Legacy checkpoints without a coverage setting
retain their original behavior.

These results use previously inspected footage. Fold/seed variation is
descriptive and does not establish significance. This single-component ablation
cannot eliminate all detection cues or establish external generalization.
