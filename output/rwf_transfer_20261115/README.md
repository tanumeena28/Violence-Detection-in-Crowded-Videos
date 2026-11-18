# One-time local-GPU RWF-2000 evaluation

Prepared 15 November 2026 at Vishal's request. The local RTX 3050 Laptop GPU
runs the existing crowd classifier on the released RWF-2000 `val` split:
200 Fight and 200 NonFight clips. The saved source-corrected combined model
uses seed 42 and its original crowd-validation threshold of 0.54.

No RWF model training, standardization fitting or threshold selection is
performed. The original crowd checkpoint's mean and standard deviation are
reused. Fresh YOLO11n-pose extraction retains the recorded 32 sampled frames,
eight-track cap, image size 640 and batch size 12. Each clip is fully decoded.

`protocol.json` freezes the model, pose weights, input inventory, known prior
demo clip, code and settings before the scoring pass. All 400 clips remain in
primary metrics. A supplementary result excludes the one known earlier demo
clip. A second supplementary result reports the subset above the original
25% usable-pose cutoff with its coverage; it does not replace the primary result.

The one-time run is complete: 56.0% accuracy, macro-F1 0.506 and ROC-AUC 0.578
across all 400 clips, in about 3 minutes 10 seconds. There are 154 false positives
and 22 false negatives. The 399-clip result excluding the known earlier demo
has 56.1% accuracy. All 400 full decodes match their container frame counts.
The original crowd artifacts are unchanged, and metrics reproduce from the
saved scores. The 26-test suite passed; the completed-run check performed no
new extraction or inference.

Inspect [the results page](index.html), [research notes](RESULTS.md),
[predictions](predictions.csv), [metrics](metrics.json) and [artifact audit](audit.json).
The execution log is `evaluation.log`.

Run the frozen helper from the project root to verify the completed record:

```powershell
& '.\.venv\Scripts\python.exe' output/rwf_transfer_20261115/run_snapshot.py
```

When `evaluation_complete.json` exists, the runner verifies source videos,
original crowd artifacts, frozen implementation and saved output hashes, then
returns the saved result. It does not extract poses or score the clips again.
An interrupted run can reuse matching pose caches under the same frozen plan.

The primary result measures transfer of a crowd-trained model to surveillance
footage. It differs from supervised RWF training/evaluation and from a stronger
RGB baseline. Supplied labels are retained; one known clip was previously
inspected, and other viewing or shared footage cannot be ruled out. Treat this
as an exploratory transfer result. Whole-evaluation wall time includes model
initialization and the staged decode/pose/feature/classification workflow; it
is not a separate cold/warm per-video latency benchmark.
