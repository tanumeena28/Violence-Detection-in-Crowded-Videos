"""Cold-process and warmed raw-video crowd-pipeline timings on a fixed sample."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

PROCESS_START = time.perf_counter()
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from affective.cross_validation import digest
from affective.data import decode_sample, read_manifest, write_json
from affective.demo import load_model
from affective.features import build_features
from affective.tracking import ClipTracker, pack_tracks
from affective.train import VARIANTS


def models(weights, checkpoint):
    from ultralytics import YOLO
    started = time.perf_counter()
    pose = YOLO(str(weights))
    classifier, saved = load_model(checkpoint)
    classifier.to("cuda").eval()
    torch.cuda.synchronize()
    return pose, classifier, saved, time.perf_counter() - started


def process_clip(root, row, pose, classifier, checkpoint):
    torch.cuda.synchronize()
    started = time.perf_counter()
    images, indices, fps, decoded = decode_sample(root / row["path"], 32)
    decode_finished = time.perf_counter()
    tracker, detections = ClipTracker(), []
    for start in range(0, 32, 12):
        results = pose.predict(images[start:start + 12], device="0", imgsz=640, conf=.2, max_det=100, verbose=False)
        for result in results:
            if result.keypoints is None or result.boxes is None or len(result.boxes) == 0:
                boxes = np.zeros((0, 4), np.float32)
                points = np.zeros((0, 17, 3), np.float32)
            else:
                boxes = result.boxes.xyxyn.cpu().numpy().astype(np.float32)
                points = np.concatenate([result.keypoints.xyn.cpu().numpy(), result.keypoints.conf.cpu().numpy()[..., None]], -1).astype(np.float32)
            ids = tracker.update(boxes, len(detections))
            detections.append({"boxes": boxes, "keypoints": points, "ids": ids})
    points, boxes, present, _, _ = pack_tracks(detections, 8)
    torch.cuda.synchronize()
    pose_finished = time.perf_counter()
    reliability, interactions = VARIANTS[checkpoint["variant"]]
    features, mask = build_features(points, boxes, present, indices.astype(np.float32) / fps,
                                    reliability, interactions, feature_schema=checkpoint["feature_schema"])
    normalized = np.clip((features - checkpoint["mean"].numpy()) / checkpoint["std"].numpy(), -10, 10) * mask[..., None]
    x = torch.from_numpy(normalized[None].astype(np.float32)).to("cuda")
    observed = torch.from_numpy(mask[None]).to("cuda")
    torch.cuda.synchronize()
    feature_finished = time.perf_counter()
    with torch.inference_mode():
        score = float(classifier(x, observed).sigmoid().item())
    torch.cuda.synchronize()
    finished = time.perf_counter()
    return {"id": row["id"], "path": row["path"], "label": row["label"], "decoded_frames": decoded,
            "header_frames": row["frames"], "duration_seconds": decoded / fps,
            "decode_seconds": decode_finished - started, "pose_tracking_seconds": pose_finished - decode_finished,
            "features_transfer_seconds": feature_finished - pose_finished,
            "classifier_seconds": finished - feature_finished, "pipeline_seconds": finished - started,
            "score": score, "threshold": checkpoint["threshold"], "prediction": int(score >= checkpoint["threshold"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path, default=Path("output/centering_corrected_cpu_20261115"))
    parser.add_argument("--checkpoint", type=Path, default=Path("output/centering_corrected_cpu_20261115/fold_1/runs/interactions_seed42/model.pt"))
    parser.add_argument("--weights", type=Path, default=Path("models/yolo11n-pose.pt"))
    parser.add_argument("--out", type=Path, default=Path("output/runtime_20261115"))
    parser.add_argument("--child", type=str)
    args = parser.parse_args()
    root, out, source = args.root.resolve(), args.out.resolve(), args.source.resolve()
    checkpoint, weights = args.checkpoint.resolve(), args.weights.resolve()
    torch.set_num_threads(4)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    if args.child:
        plan = json.loads((out / "protocol.json").read_text())
        row = next(r for r in plan["sample"] if r["id"] == args.child)
        pose, classifier, saved, initialization = models(weights, checkpoint)
        record = process_clip(root, row, pose, classifier, saved)
        record["model_initialization_seconds"] = initialization
        record["child_seconds_including_imports"] = time.perf_counter() - PROCESS_START
        write_json(out / "cold" / f"{row['id']}.json", record)
        return
    if out.exists():
        raise FileExistsError("Preserve the completed timing run; choose a new directory")
    rows = read_manifest(source / "assignments.csv")
    selected = []
    for label in (0, 1):
        ordered = sorted([r for r in rows if r["label"] == label], key=lambda r: (r["frames"] / r["fps"], r["id"]))
        selected.extend(ordered[index] for index in np.rint(np.linspace(0, len(ordered) - 1, 5)).astype(int))
    for row in selected:
        if digest(root / row["path"]) != row["sha256"]:
            raise ValueError("Timing source changed")
    plan = {"sample": selected, "selection": "Five evenly spaced duration ranks in each supplied class, fixed before timing",
            "sample_size": 10, "warm_repeats": 3, "frames": 32, "max_people": 8,
            "weights_sha256": digest(weights), "checkpoint_sha256": digest(checkpoint),
            "device": torch.cuda.get_device_name(0), "torch": torch.__version__, "cpu_threads": 4,
            "script_sha256": digest(Path(__file__)),
            "boundary": "Warm includes full video decode, sampled-frame pose extraction/tracking, corrected features, normalization/transfer and GPU classifier. Cold external-process wall adds Python launch/imports and model initialization. Overlay/export excluded. No competing project GPU job during measurement.",
            "limitations": "Offline full-clip timing on ten duration-selected crowd clips; not streaming latency, a hardware-independent speed claim or a real-time demonstration."}
    write_json(out / "protocol.json", plan)
    (out / "cold").mkdir()
    cold = []
    for number, row in enumerate(selected, 1):
        command = [sys.executable, str(Path(__file__).resolve()), "--root", str(root), "--source", str(source),
                   "--out", str(out), "--weights", str(weights), "--checkpoint", str(checkpoint), "--child", row["id"]]
        started = time.perf_counter()
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode:
            raise RuntimeError(completed.stderr)
        record = json.loads((out / "cold" / f"{row['id']}.json").read_text())
        record["external_process_wall_seconds"] = time.perf_counter() - started
        cold.append(record)
        print(f"Cold timing {number}/10", flush=True)
    pose, classifier, saved, initialization = models(weights, checkpoint)
    process_clip(root, selected[0], pose, classifier, saved)  # Declared warmup, excluded.
    warm = []
    rng = np.random.default_rng(42)
    for repeat in range(1, 4):
        for index in rng.permutation(len(selected)):
            record = process_clip(root, selected[index], pose, classifier, saved)
            record["repeat"] = repeat
            warm.append(record)
        print(f"Warm repeat {repeat}/3", flush=True)
    stats = lambda values: {"median": float(np.median(values)), "p95": float(np.percentile(values, 95)), "minimum": float(min(values)), "maximum": float(max(values))}
    summary = {"status": "complete", "cold_clips": 10, "warm_runs": 30,
               "cold_external_process_seconds": stats([r["external_process_wall_seconds"] for r in cold]),
               "cold_pipeline_seconds": stats([r["pipeline_seconds"] for r in cold]),
               "warm_pipeline_seconds": stats([r["pipeline_seconds"] for r in warm]),
               "warm_stage_seconds": {stage: stats([r[stage] for r in warm]) for stage in ("decode_seconds", "pose_tracking_seconds", "features_transfer_seconds", "classifier_seconds")},
               "warm_model_initialization_seconds": initialization, "cold": cold, "warm": warm,
               "boundary": plan["boundary"], "limitations": plan["limitations"]}
    write_json(out / "summary.json", summary)
    notes = f"# Controlled raw-video runtime\n\nRTX 3050 Laptop GPU, 32 sampled frames, ten fixed clips, three warmed repeats.\n\nWarm full-pipeline median: {summary['warm_pipeline_seconds']['median']:.3f} s; p95: {summary['warm_pipeline_seconds']['p95']:.3f} s.\n\nCold process median: {summary['cold_external_process_seconds']['median']:.3f} s; p95: {summary['cold_external_process_seconds']['p95']:.3f} s.\n\n" + plan["boundary"] + "\n\n" + plan["limitations"] + "\n"
    (out / "RESULTS.md").write_text(notes, encoding="utf-8")
    print(notes, flush=True)


if __name__ == "__main__":
    main()
