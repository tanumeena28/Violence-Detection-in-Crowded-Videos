# Supervised RWF frozen-video experiment

This is a new supervised RWF experiment. It does not reuse a crowd-trained
classifier. The frozen Kinetics-400 R3D-18 encoder is reused, and a fresh
logistic head is fitted on the released RWF training footage.

The audited split is:

| Partition | NonFight | Fight | Total | Source groups |
|---|---:|---:|---:|---:|
| Training | 633 | 638 | 1,271 | 603 |
| Validation from training release | 158 | 159 | 317 | 153 |
| Released evaluation | 200 | 200 | 400 | 180 |

The 1,600 released training clips have 765 filename source groups. Source IDs
are extracted without using the class folder, and source groups linked by
identical video SHA256 are merged. This matters because 150 groups contain
both supplied labels. Mixed-label groups remain whole across train/validation.
The first fold of five-way StratifiedGroupKFold with seed 42 supplies validation.
No model score determines the split.

The byte audit found six cross-release duplicate pairs that filename grouping
missed. All training clips in the linked evaluation source groups are excluded,
removing seven clips. Five additional same-label development duplicates are
removed. All 400 evaluation clips are retained and have unique byte hashes.
The [source audit](source_audit.json) records exclusions and exact evidence;
[source inventory](source_inventory.csv) preserves original source IDs.
Renamed or near-duplicate footage may still remain beyond these checks.

Features use the same predefined two chronological 16-frame windows and
official pretrained RGB transform as the earlier video reference. The encoder
is frozen. Training data defines scaling and logistic coefficients. Validation
log loss selects C from 0.001, 0.01, 0.1, 1 and 10; validation macro-F1 selects
the threshold. The head and development artifacts are sealed before evaluation
feature arrays are loaded. Existing fixed pretrained encoder embeddings of
the evaluation clips are reused after their hashes and settings are checked.
No evaluation scores select fitting settings or thresholds.

The 400 released evaluation clips have already been scored and inspected in
the earlier transfer work. Results are exploratory development evidence,
not an untouched benchmark or a directly matched improvement over crowd-only
transfer. Independent labels and pretraining/source overlap are not audited.
Paper drafting remains deferred.

Run or inspect this experiment from the project root:

```powershell
& '.\.venv\Scripts\python.exe' output/rwf_supervised_20261115/run_snapshot.py
& '.\.venv\Scripts\python.exe' output/rwf_supervised_20261115/run_snapshot.py --verify-only
```

Completed runs verify saved artifacts and scores without feature extraction
or refitting. [Protocol](protocol.json), [head selection](selection.json),
[sealed head](head_frozen.json), [metrics](metrics.json), [verification](audit.json)
and [results page](index.html) preserve the full experiment. New experiments
must use new output directories; do not modify this frozen plan.

The completed result is 82.0% validation accuracy and 84.0% released-evaluation
accuracy, macro-F1 0.840 and AUC 0.900. At the validation-selected 0.50 threshold,
there are 21 NonFight false positives and 43 missed Fight clips. C=0.01 was
selected by validation log loss. All 48 project tests pass.

[Fixed-threshold diagnostics](figures/evaluation_diagnostics.png) and
[raw-video demonstrations](demos/index.html) include correct predictions and
errors. The four raw-video scores reproduce saved evaluation scores and all
600 encoded frames decode successfully. Examples are outcome-selected
diagnostics, not a representative sample or independent label review.

To score another raw clip using the sealed model:

```powershell
& '.\.venv\Scripts\python.exe' scripts/predict_video_model.py --experiment output/rwf_supervised_20261115 --video 'path/to/clip.avi' --device cuda
```

Optional `--output-json` saves the prediction; `--render` writes an annotated
MP4. These are whole-clip predictions with fixed normalization and threshold.
