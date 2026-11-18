# Local GPU demonstration

Run commands from the AffectiveProject folder in PowerShell. The existing
`.venv` contains CUDA PyTorch and the local models. No download, retraining or
threshold choice is required for inference.

The active video model is chosen by its sealed RWF validation promotion rule:
epoch 2, threshold 0.23. The frozen RWF reference and corrected crowd pose
checkpoint remain available as separate models. The external protocol keeps
the original frozen video model as its primary result.

## Predict a new video

```powershell
& .venv/Scripts/python.exe scripts/predict_final_video.py --video 'C:/path/to/video.mp4' --output-json output/my_video.json --render output/my_video.mp4
```

Choose `--model fine`, `--model frozen` or `--model pose` explicitly when
comparing models. The pose option writes predictions and pose-support status;
the previous [pose demonstrations](../demo_20261115/index.html) show skeleton
overlays. Video scores are not calibrated probabilities. Track IDs do not
identify which person is violent.

## Process a longer video in windows

```powershell
& .venv/Scripts/python.exe scripts/predict_final_video.py --video 'C:/path/to/long_video.mp4' --window-seconds 5 --output-json output/long_video_windows.json
```

This processes nonoverlapping closed windows offline. It stores at most one
window of frames and records a single-frame tail without predicting it.
The model was trained for clip classification. Window scores have no
validated event-localization or streaming accuracy. A whole-clip prediction
uniformly samples 32 frames across the entire video, so it can miss brief events.

## Verify the delivered results

```powershell
& .venv/Scripts/python.exe scripts/score_final_evaluations.py --verify-only
& .venv/Scripts/python.exe -m pytest -q
```

The result verifier checks sealed protocols/models, pinned external archives,
the evaluation implementation and all recorded output hashes. A code change
requires a separate evaluation record. Running without `--verify-only` resumes
the fixed evaluation and verifies existing clip records.

Open [RWF evaluation](rwf_evaluation/index.html),
[Hockey Fight evaluation](../external_validation_20261115/index.html), or
[the final delivery page](index.html). The RWF clips were already inspected in
prior experiments. Hockey Fight contains 1,000 released mirror clips with 997
unique byte hashes. Its sports-broadcast domain differs from surveillance.
Source-game independence, near-duplicates and Kinetics pretraining overlap
remain unaudited.

## Independent review remains pending

No independent reviewer is available at present. The
[neutral 40-clip review pack](../blind_review_20261115/index.html) remains
unreviewed. A future reviewer should watch full videos and export their labels
and difficulty notes before seeing model results or the coordinator mapping.
Keep the supplied experiment labels unchanged. Paper drafting remains deferred.
