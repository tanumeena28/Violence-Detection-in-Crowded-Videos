"""Render diagnostic demonstrations of the corrected interactions checkpoint."""
from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import digest
from affective.data import write_json
from affective.demo import infer_cache, load_model, render_video


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path, default=Path("output/centering_corrected_cpu_20261115"))
    parser.add_argument("--out", type=Path, default=Path("output/demo_20261115"))
    args = parser.parse_args()
    root, source, out = args.root.resolve(), args.source.resolve(), args.out.resolve()
    if out.exists():
        raise FileExistsError("Keep the existing demonstration package")
    run = source / "fold_1" / "runs" / "interactions_seed42"
    model, checkpoint = load_model(run / "model.pt")
    torch.set_num_threads(4)
    with (run / "predictions.csv").open(newline="", encoding="utf-8") as stream:
        rows = [r for r in csv.DictReader(stream) if r["split"] == "test"]
    selected = []
    for name, label, prediction in (("true_positive", 1, 1), ("true_negative", 0, 0), ("false_positive", 0, 1), ("false_negative", 1, 0)):
        candidates = [r for r in rows if int(r["label"]) == label and int(r["prediction"]) == prediction and float(r["usable_pose_fraction"]) >= .25]
        if candidates:
            selected.append((name, sorted(candidates, key=lambda r: r["path"])[0]))
    out.mkdir(parents=True)
    records = []
    for outcome, row in selected:
        cache = source / "cache" / f"{row['id']}.npz"
        result, points = infer_cache(model, checkpoint, cache)
        if abs(result["score"] - float(row["score"])) > 3e-4 or result["raw_prediction"] != int(row["prediction"]):
            raise ValueError("Demonstration inference differs from the saved result")
        target = out / "videos" / f"{outcome}.mp4"
        encoded = render_video(root / row["path"], points, result, target, int(row["label"]))
        cap = cv2.VideoCapture(str(target))
        decoded = 0
        while cap.read()[0]:
            decoded += 1
        cap.release()
        if decoded != encoded:
            raise ValueError("Demonstration does not decode completely")
        records.append({"outcome": outcome, "id": row["id"], "source": row["path"], "label": int(row["label"]),
                        **result, "feature_schema": checkpoint["feature_schema"], "encoded_frames": encoded,
                        "decoded_frames_verified": decoded, "video": target.relative_to(out).as_posix(),
                        "poster": target.with_suffix(".jpg").relative_to(out).as_posix()})
        print(f"Rendered {outcome}: {decoded} verified frames", flush=True)
    write_json(out / "demos.json", records)
    write_json(out / "protocol.json", {"checkpoint": str(run / "model.pt"), "checkpoint_sha256": digest(run / "model.pt"),
                "selection": "First filename in each TP/TN/FP/FN category above the pre-existing 25% usable-pose cutoff in fold 1. Outcome-selected diagnostic examples, not representative error-rate estimates.",
                "feature_schema": checkpoint["feature_schema"], "threshold": checkpoint["threshold"],
                "script_sha256": digest(Path(__file__)), "scope": "Offline whole-clip prediction with sampled pose overlays; track IDs do not identify aggressors."})
    cards = "".join(f'<section><h2>{html.escape(r["outcome"].replace("_", " ").title())}</h2><video controls preload="none" poster="{r["poster"]}" src="{r["video"]}"></video><p>Score {r["score"]:.3f}; threshold {r["threshold"]:.2f}; dataset label {"violent" if r["label"] else "nonviolent"}.</p></section>' for r in records)
    page = '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Corrected crowd-model demonstrations</title><style>body{font:17px system-ui;max-width:1120px;margin:35px auto;padding:20px;line-height:1.6;background:#f4f6f8;color:#17232d}section{background:white;border-radius:10px;margin:25px 0;padding:20px}video{width:100%}a{color:#086b86}</style><h1>Corrected crowd-model demonstrations</h1><p>Interactions TCN, continuous hip centering, fixed fold 1 and seed 42. These four examples were selected from known outcomes to show correct decisions and failures. Scores apply to the whole clip; poses are sampled and track IDs provide no person-level attribution.</p>' + cards + '<p><a href="../centering_corrected_cpu_20261115/centering_ablation.html">Centering comparison</a> | <a href="../video_baseline_v2_20261115/index.html">Pretrained video baseline</a> | <a href="../input_controls_20261115/index.html">Input controls</a> | <a href="../runtime_20261115/RESULTS.md">Measured runtime</a> | <a href="demos.json">Demonstration records</a></p>'
    (out / "index.html").write_text(page, encoding="utf-8")
    (out / "README.md").write_text("# Refreshed diagnostic demonstrations\n\nOpen `index.html`. Corrected interactions checkpoint from crowd fold 1, seed 42. The clips are outcome-selected diagnostics, including false positives and misses. Every encoded video was decoded fully and its inference reproduced the saved classification. Track IDs are local to each clip; predictions are clip-level. Paper drafting remains deferred.\n", encoding="utf-8")
    write_json(out / "audit.json", {"status": "pass", "videos_verified": len(records),
                "artifacts_sha256": {p.relative_to(out).as_posix(): digest(p) for p in out.rglob("*") if p.is_file()}})


if __name__ == "__main__":
    main()
