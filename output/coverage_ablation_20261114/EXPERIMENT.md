# Explicit pose-coverage ablation

Prepared 14 November 2026 before completing the new training run.

The November 7 quality-only control reaches 77.6% mean accuracy without joint
positions or trajectories. This experiment tests the narrower question of how
the TCN's explicit observed-track coverage input affects the four skeleton
variants. It does not test whether every prediction depends on detection cues.

The only intended model change is replacing the scalar `mean(presence_mask)`
with a constant zero. The classifier still has 97 inputs: 48 pooled means,
48 pooled maxima and the now-zero scalar. Keeping that slot preserves parameter
shapes, initial weights and random-number draws for each seed. Nominal parameter
counts are unchanged; the 48 weights connected to the constant zero receive no
data-dependent gradient. Observation masks, per-joint missingness, confidence
and validity channels, and interaction neighbor counts retain detection cues.

The reference is `../cross_validation_20261107/`. Both experiments use 245 clips,
204 reviewed source groups, the same five outer folds, split seed 42 and training
seeds 42, 123 and 2026. Each rotation uses 147 training, 49 validation and 49 test
clips. All four variants are included. All 60 TCN fits are trained afresh with
hidden size 48, up to 180 epochs and patience 30. The unchanged motion and
quality-only controls are fitted once per fold, for ten additional fits.

Training observations define normalization and fitting. Validation data selects
checkpoints, motion regularization and thresholds using the original rules.
No training choice is selected from test results. The preparation preflight
checks matching inputs, source review, source links, fold manifests, settings
and feature-construction hashes before launching the run.

The primary comparison is coverage-off minus coverage-on accuracy, paired by
variant, fold and seed. Macro-F1 and ROC-AUC changes and per-seed decision changes
are descriptive secondary measures. Every planned variant and seed is reported,
including unfavorable outcomes. Variation across dependent fold/seed runs is
descriptive; no significance test or confidence interval is inferred from it.

The reference artifacts remain unchanged. A file-hash inventory captured before
training is stored in `reference_integrity_before.json`. Reports verify saved
scores, classification decisions, training-only normalization and
validation-selected thresholds in both experiments. The new implementation
snapshot and immutable plan allow later inspection after source changes.

The completed outputs will include `index.html`, `audit.json`,
`coverage_ablation.html`, `COVERAGE_ABLATION.md`, `coverage_comparison.json` and
`coverage_paired_runs.csv`. Existing footage has been inspected previously.
These are exploratory development results, not an untouched benchmark.
