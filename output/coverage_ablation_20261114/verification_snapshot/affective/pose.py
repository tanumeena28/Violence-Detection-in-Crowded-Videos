"""Pretrained multi-person pose extraction with provenance and resumable caches."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import cv2
import numpy as np

from .data import decode_sample, read_manifest, write_json
from .features import FEATURE_SCHEMA
from .tracking import ClipTracker, pack_tracks


def extract(root: Path, out: Path, weights: Path, device="auto", frames=32, max_people=8,
            image_size=640, batch=12, limit=0):
    import torch
    import ultralytics
    from ultralytics import YOLO

    if device == "auto":
        device = "0" if torch.cuda.is_available() else "cpu"
    rows = read_manifest(out / "manifest.csv")
    if limit:
        rows = rows[:limit]
    model = YOLO(str(weights))
    actual_weights = Path(model.ckpt_path)
    weight_hash = hashlib.sha256(actual_weights.read_bytes()).hexdigest()
    settings = {"weights": actual_weights.name, "weights_sha256": weight_hash,
                "ultralytics": ultralytics.__version__, "torch": torch.__version__,
                "frames": frames, "max_people": max_people, "image_size": image_size,
                "box_confidence": 0.2, "joint_threshold": 0.25, "max_detections": 100,
                "tracking": "hungarian-iou-center-v1", "feature_schema": FEATURE_SCHEMA,
                "device": device, "batch_size": batch}
    signature = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()
    cache = out / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    write_json(out / "pose_settings.json", {**settings, "signature": signature})
    reports, failures = [], []
    wall = time.perf_counter()
    for number, row in enumerate(rows, 1):
        target = cache / f"{row['id']}.npz"
        if target.exists():
            with np.load(target, allow_pickle=False) as saved:
                if str(saved["signature"]) == signature and str(saved["source_sha256"]) == row["sha256"]:
                    reports.append(json.loads(str(saved["quality"])))
                    print(f"[{number}/{len(rows)}] cached {row['path']}", flush=True)
                    continue
        try:
            started = time.perf_counter()
            video = root / row["path"]
            if hashlib.sha256(video.read_bytes()).hexdigest() != row["sha256"]:
                raise ValueError("Source video changed after manifest creation")
            images, indices, fps, decoded_frames = decode_sample(video, frames)
            tracker = ClipTracker()
            detections = []
            for start in range(0, frames, batch):
                results = model.predict(images[start:start + batch], device=device, imgsz=image_size,
                                        conf=0.2, max_det=100, verbose=False)
                for result in results:
                    if result.keypoints is None or result.boxes is None or len(result.boxes) == 0:
                        boxes = np.zeros((0, 4), np.float32)
                        points = np.zeros((0, 17, 3), np.float32)
                    else:
                        boxes = result.boxes.xyxyn.cpu().numpy().astype(np.float32)
                        points = np.concatenate([result.keypoints.xyn.cpu().numpy(),
                                                 result.keypoints.conf.cpu().numpy()[..., None]], axis=-1).astype(np.float32)
                    ids = tracker.update(boxes, len(detections))
                    detections.append({"boxes": boxes, "keypoints": points, "ids": ids})
            keypoints, boxes, present, track_ids, total_tracks = pack_tracks(detections, max_people)
            valid = (keypoints[..., 2] >= 0.25) & present[..., None]
            usable_frame = valid.sum((1, 2)) >= 5
            elapsed = time.perf_counter() - started
            quality = {"id": row["id"], "path": row["path"], "label": row["label"], "split": row["split"],
                       "sampled_frames": frames, "decoded_frames": decoded_frames,
                       "header_frames": row["frames"], "full_decode_matches_header": decoded_frames == row["frames"],
                       "frames_with_people": float(present.any(1).mean()),
                       "usable_pose_fraction": float(usable_frame.mean()),
                       "mean_people": float(present.sum(1).mean()),
                       "max_people_detected": max(len(d["ids"]) for d in detections),
                       "total_tracks": total_tracks, "retained_tracks": int((track_ids >= 0).sum()),
                       "discarded_tracks": max(0, total_tracks - max_people),
                       "valid_joint_fraction": float(valid.sum() / max(present.sum() * 17, 1)),
                       "seconds_including_decode": elapsed}
            temporary = target.with_suffix(".tmp.npz")
            np.savez_compressed(temporary, keypoints=keypoints, boxes=boxes, present=present,
                                track_ids=track_ids, frame_indices=indices,
                                times=indices.astype(np.float32) / fps, fps=np.float32(fps),
                                original_size=np.array([images[0].shape[1], images[0].shape[0]]),
                                signature=np.array(signature), source_sha256=np.array(row["sha256"]),
                                quality=np.array(json.dumps(quality)))
            temporary.replace(target)
            reports.append(quality)
            print(f"[{number}/{len(rows)}] {row['split']} label={row['label']} usable={quality['usable_pose_fraction']:.0%} "
                  f"people={quality['mean_people']:.1f} tracks={total_tracks} {elapsed:.1f}s", flush=True)
        except Exception as exc:
            failures.append({"path": row["path"], "error": str(exc)})
            print(f"FAILED {row['path']}: {exc}", flush=True)
    write_json(out / "pose_quality.json", {"settings": settings, "signature": signature,
               "clips": reports, "failures": failures, "wall_seconds": time.perf_counter() - wall,
               "limitation": "Detector confidence is not calibrated. Crowds, occlusion, camera cuts, and track caps can lose people. Missing poses do not establish absence of violence."})
    if failures:
        raise RuntimeError(f"{len(failures)} pose extraction failures; see pose_quality.json")
    print(f"Pose caches ready: {len(reports)} clips", flush=True)
