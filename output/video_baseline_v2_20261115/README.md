# Completed frozen video reference

All 245 crowd clips use a frozen Kinetics-400 R3D-18 encoder. Two uniformly
sampled 16-frame windows are transformed with the official pretrained RGB
transform; their 512-dimensional vectors are averaged. Five logistic heads
use the same reviewed source-grouped folds as the pose experiments. Training
clips define scaling and fitting; validation clips select regularization and
thresholds. No encoder fine-tuning is performed.

[Results](index.html), [summary](summary.json), [audit](audit.json),
[feature provenance](feature_audit.json) and [protocol](protocol.json) are
complete. Mean accuracy is 91.0%, macro-F1 0.909 and AUC 0.979. The video
samples exactly match prior pose-cache decodes and indices. One header-count
discrepancy is recorded; all clips are retained. Pretraining/source overlap
is not audited and footage was previously inspected.

Inspect the completed fit without extracting features or training again:

```powershell
& '.\.venv\Scripts\python.exe' output/video_baseline_v2_20261115/run_snapshot.py --verify-only
```

The [RWF transfer](../video_transfer_20261115/index.html) uses fixed crowd
heads and thresholds. Its weaker result is separate from these crowd scores.
