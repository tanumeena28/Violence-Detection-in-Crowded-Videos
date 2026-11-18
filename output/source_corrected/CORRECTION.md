# Source grouping correction

Three training clips were conservatively excluded because their source titles/uploaders match validation clips and their shortened IDs prefix the full source IDs. The two Preston clips show matching footage in the sampled review. The Russia/Ukraine pair comes from a matching source ID but shows different sampled segments; grouping it is a precaution against shared-source leakage.

The corrected split has 147 training, 48 validation and the same 47 test clips. Per-video pose/motion features are reused; normalization, coefficients, temporal checkpoints and thresholds are recomputed. The four TCN variants retain hidden=48, seed=42, epochs=180 and patience=30. This is an exploratory correction after test inspection, not a new unseen benchmark.

| Model | Original accuracy | Corrected accuracy | Corrected macro-F1 | Corrected ROC-AUC |
|---|---:|---:|---:|---:|
| baseline | 66.0% | 68.1% | 0.680 | 0.808 |
| reliability | 63.8% | 63.8% | 0.638 | 0.781 |
| interactions | 70.2% | 68.1% | 0.679 | 0.850 |
| combined | 68.1% | 66.0% | 0.658 | 0.786 |
| motion_linear | 72.3% | 74.5% | 0.744 | 0.766 |
| pose_quality_only | 76.6% | 76.6% | 0.764 | 0.873 |

All four corrected checkpoints, both linear controls, source/cache provenance and six full demo decodes pass the saved-artifact audit. No known exact or prefix-compatible source-ID overlaps remain. Filename and image-hash checks can miss other related footage.

Pose-quality summaries remain stronger than the skeleton variants on this split. Scene and detection confounds require source-separated fold/seed evaluation before claiming the model learned violent body motion or that one representation is superior.

[Corrected results page](index.html) | [Artifact audit](AUDIT.md) | [Excluded clips and provenance](correction.json) | [Archived pilot](../pilot/index.html)
