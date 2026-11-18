# Frozen temporal follow-up

The single candidate is complete and rejected by the predeclared development
rule. The original supervised reference remains retained. Paper drafting was
outside this work.

The same frozen Kinetics-400 R3D-18 encodes four 16-frame local windows at roughly
15 sampled FPS. Evenly spaced window starts include the beginning and end of
each clip. The input concatenates the original global 512-vector, local mean
512-vector, and local componentwise maximum 512-vector. No encoder fine-tuning
or new pretrained downloads occurred. Encoder batches contain two windows.

The source split, duplicate exclusions, labels, regularization grid, train-only
normalization, and validation-only selection are inherited from the sealed
supervised reference. Validation selects C=0.001 and threshold=0.53. The original
head selects C=0.01 and threshold=0.50. A new fitted head, not the earlier head,
is used for the temporal features.

| Validation measure | Original reference | Temporal candidate |
|---|---:|---:|
| Accuracy | 82.02% | 81.70% |
| Macro-F1 | 0.81897 | 0.81623 |
| Fight recall | 0.73585 | 0.74843 |
| AUC | 0.90068 | 0.90041 |
| Log loss | 0.39298 | 0.39543 |
| Missed Fight clips | 42 | 40 |
| NonFight false alarms | 15 | 18 |

The candidate fixes 12 original errors and introduces 13 new ones. Nine source
groups have a positive net change and ten a negative net change. These are
descriptive development comparisons with dependent source clips, not an
independent significance or generalization claim.

Strictly improved validation log loss and macro-F1 with nondecreasing Fight
recall were required to qualify for evaluation. The candidate fails two of
those three criteria. No evaluation arrays were loaded and no candidate
evaluation features or predictions were created. The original reference's
previously reported 84.0% evaluation accuracy remains unchanged. Previously
inspected evaluation footage does not establish an untouched benchmark.

All 53 project tests pass. Full cached feature, sampling, pooling, normalization,
selection, score, source split, and seal checks pass. Four raw validation clips,
including errors, reproduce saved scores and fully decode after export. Nine
earlier completed experiment inventories are preserved byte-exact. Independent
human label review remains pending.

Run the frozen implementation for verification:

```powershell
& '.\.venv\Scripts\python.exe' output/rwf_temporal_20261115/run_snapshot.py --verify-only
& '.\.venv\Scripts\python.exe' -m pytest tests -q
```

Raw inference can explicitly use this rejected experimental candidate for
reproduction. The command's default model remains the original reference:

```powershell
& '.\.venv\Scripts\python.exe' scripts/predict_video_model.py --experiment output/rwf_temporal_20261115 --video 'path/to/video.mp4'
```

[Results](RESULTS.md) | [Paired comparison](COMPARISON.md) |
[Protocol](protocol.json) | [Promotion decision](promotion.json) |
[Verification](audit.json) | [Raw demonstrations](demos/index.html) |
[Preservation audit](../rwf_validation_review_20261115/final_audit.json)
