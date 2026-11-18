"""Offline full-clip inference and annotated, locally playable MP4 demonstrations."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import time
from pathlib import Path

import cv2
import numpy as np
import torch

from .data import write_json
from .features import FEATURE_SCHEMAS, build_features
from .input_controls import control_inputs
from .model import CrowdTCN
from .train import VARIANTS

EDGES = [(5, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 11), (6, 12),
         (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (0, 5), (0, 6)]
COLORS = [(240, 180, 70), (80, 220, 150), (210, 110, 240), (80, 180, 255), (220, 220, 100)]


def load_model(checkpoint_path):
    ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    if ckpt["feature_schema"] not in FEATURE_SCHEMAS:
        raise ValueError("Checkpoint feature schema mismatch")
    model = CrowdTCN(ckpt["input_dim"], ckpt["hidden"], use_coverage=ckpt.get("use_coverage", True))
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    return model, ckpt


def infer_cache(model, ckpt, cache):
    with np.load(cache, allow_pickle=False) as d:
        if str(d["signature"]) != ckpt["pose_signature"]:
            raise ValueError("Pose extraction settings differ from the trained checkpoint")
        reliability, interactions = VARIANTS[ckpt["variant"]]
        x, mask = build_features(d["keypoints"], d["boxes"], d["present"], d["times"], reliability, interactions,
                                 feature_schema=ckpt["feature_schema"])
        x, mask = control_inputs(x, mask, Path(cache).stem, ckpt.get("input_control", "full"))
        x = np.clip((x - ckpt["mean"].numpy()) / ckpt["std"].numpy(), -10, 10) * mask[..., None]
        device = next(model.parameters()).device
        features = torch.from_numpy(x[None].astype(np.float32)).to(device)
        observation_mask = torch.from_numpy(mask[None].astype(np.float32)).to(device)
        with torch.inference_mode():
            model(features, observation_mask)  # warmup, excluded from model-only timing
            if device.type == 'cuda':
                torch.cuda.synchronize(device)
            started = time.perf_counter()
            score = float(model(features, observation_mask).sigmoid().item())
            if device.type == 'cuda':
                torch.cuda.synchronize(device)
            milliseconds = (time.perf_counter() - started) * 1000
        quality = json.loads(str(d["quality"]))
        abstain = quality["usable_pose_fraction"] < 0.25
        return {"score": score, "threshold": ckpt["threshold"],
                "raw_prediction": int(score >= ckpt["threshold"]),
                "decision": "insufficient pose evidence" if abstain else "violent" if score >= ckpt["threshold"] else "nonviolent",
                "abstain": abstain, "usable_pose_fraction": quality["usable_pose_fraction"],
                "cpu_model_only_ms": milliseconds if device.type == 'cpu' else None,
                "gpu_model_only_ms": milliseconds if device.type == 'cuda' else None,
                "inference_device": str(device), "pose_seconds": quality["seconds_including_decode"],
                "input_shape": list(features.shape), "variant": ckpt["variant"], "seed": ckpt["seed"]}, {k: d[k].copy() for k in ("keypoints", "present", "track_ids", "frame_indices")}


def text(frame, value, position, scale=0.6, color=(230, 235, 240), thickness=1):
    cv2.putText(frame, value, position, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def render_video(video: Path, cache_data, result, target: Path, benchmark_label=None):
    import imageio_ffmpeg

    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS)
    original_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if fps <= 0:
        cap.release()
        raise ValueError(f"Invalid FPS: {video}")
    width, height = 1120, 680
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo",
               "-vcodec", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{width}x{height}",
               "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", "fast",
               "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target)]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    index, snapshot = 0, None
    indices = cache_data["frame_indices"]
    fit = min(760 / original_w, 540 / original_h)
    fitted_w, fitted_h = int(original_w * fit), int(original_h * fit)
    x0, y0 = 20 + (760 - fitted_w) // 2, 88 + (540 - fitted_h) // 2
    try:
        while True:
            ok, raw = cap.read()
            if not ok:
                break
            frame = np.zeros((height, width, 3), np.uint8)
            frame[:] = (25, 31, 42)
            frame[y0:y0 + fitted_h, x0:x0 + fitted_w] = cv2.resize(raw, (fitted_w, fitted_h))
            text(frame, "CROWD VIOLENCE: IMPLEMENTATION PILOT", (24, 38), 0.9, thickness=2)
            text(frame, "Offline full-clip inference | poses sampled uniformly", (24, 67), 0.55)
            nearest = int(np.argmin(np.abs(indices - index)))
            for person in np.flatnonzero(cache_data["present"][nearest]):
                pose = cache_data["keypoints"][nearest, person]
                visible = pose[:, 2] >= 0.25
                coords = pose[:, :2] * [fitted_w, fitted_h] + [x0, y0]
                coords = np.rint(coords).astype(int)
                tid = int(cache_data["track_ids"][person])
                color = COLORS[tid % len(COLORS)]
                for a, b in EDGES:
                    if visible[a] and visible[b]:
                        cv2.line(frame, tuple(coords[a]), tuple(coords[b]), color, 2, cv2.LINE_AA)
                for joint in np.flatnonzero(visible):
                    cv2.circle(frame, tuple(coords[joint]), 3, color, -1, cv2.LINE_AA)
                if visible.any():
                    pos = coords[visible].mean(0).astype(int)
                    pos[0] = np.clip(pos[0], x0, x0 + fitted_w - 90)
                    pos[1] = np.clip(pos[1], y0 + 20, y0 + fitted_h - 10)
                    text(frame, f"Track {tid}", tuple(pos), 0.45, color, 2)
            px = 810
            text(frame, "MODEL OUTPUT", (px, 125), 0.7, thickness=2)
            text(frame, f"Clip score: {result['score']:.3f}", (px, 173), 0.65)
            text(frame, f"Threshold: {result['threshold']:.2f}", (px, 206), 0.6)
            text(frame, "Decision:", (px, 260), 0.6)
            if result["abstain"]:
                text(frame, "INSUFFICIENT POSE", (px, 294), 0.57, (70, 185, 250), 2)
                text(frame, "Manual review needed", (px, 324), 0.5)
            else:
                text(frame, result["decision"].upper(), (px, 299), 0.75, (95, 215, 230), 2)
            text(frame, f"Usable frames: {result['usable_pose_fraction']:.0%}", (px, 382), 0.55)
            text(frame, f"Visible tracks: {int(cache_data['present'][nearest].sum())}", (px, 415), 0.55)
            text(frame, f"Time: {index / fps:.2f}s", (px, 448), 0.55)
            if benchmark_label is not None:
                text(frame, "DATASET LABEL", (px, 514), 0.55, thickness=2)
                text(frame, "violent" if benchmark_label else "nonviolent", (px, 546), 0.65)
            text(frame, "IDs refer to tracks in this clip.", (px, 589), 0.45)
            text(frame, "No person-level attribution.", (px, 612), 0.45)
            text(frame, "Exploratory model score, not a calibrated probability. Sparse poses can produce unreliable predictions.", (24, 657), 0.5)
            encoder.stdin.write(frame.tobytes())
            if index == int(indices[len(indices) // 2]):
                snapshot = frame.copy()
            index += 1
    finally:
        cap.release()
        if encoder.stdin:
            encoder.stdin.close()
    errors = encoder.stderr.read().decode("utf-8", errors="replace")
    returncode = encoder.wait()
    if returncode:
        raise RuntimeError(f"Video encoding failed: {errors}")
    if snapshot is not None:
        cv2.imwrite(str(target.with_suffix(".jpg")), snapshot)
    return index


def infer_new_video(root, out, video, ckpt):
    from .pose import extract

    video = video.resolve()
    digest = hashlib.sha256(video.read_bytes()).hexdigest()
    folder = out / "inference" / digest[:16]
    settings = json.loads((out / "pose_settings.json").read_text())
    cap = cv2.VideoCapture(str(video))
    row = {"id": digest[:16], "path": str(video), "sha256": digest, "source_group": video.stem,
           "label": -1, "fold": 0, "split": "test", "fps": cap.get(cv2.CAP_PROP_FPS),
           "frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
           "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}
    cap.release()
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    extract(root, folder, root / "models" / settings["weights"], device=settings["device"],
            frames=settings["frames"], max_people=settings["max_people"], image_size=settings["image_size"], batch=settings["batch_size"])
    return row, folder / "cache" / f"{digest[:16]}.npz"


def make_demos(root: Path, out: Path, run="combined_seed42", count=2, video=None, device="cuda"):
    torch.set_num_threads(4)
    model, ckpt = load_model(out / "runs" / run / "model.pt")
    model.to(device)
    if video is not None:
        row, cache = infer_new_video(root, out, video, ckpt)
        selected = [(row, cache)]
    else:
        with (out / "runs" / run / "predictions.csv").open(newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["split"] == "test"]
        # First filenames in each class, chosen without looking at prediction quality.
        chosen = []
        for label in ("0", "1"):
            subset = sorted((r for r in rows if r["label"] == label), key=lambda r: r["path"])
            chosen.extend(subset[:max(1, count // 2)])
        selected = [(r, out / "cache" / f"{r['id']}.npz") for r in chosen[:count]]
    demos = []
    for row, cache in selected:
        result, cached = infer_cache(model, ckpt, cache)
        name = "new_video" if video is not None else "nonviolent" if int(row["label"]) == 0 else "violent"
        target = out / "demos" / f"{name}_{row['id']}.mp4"
        frame_count = render_video(root / row["path"], cached, result, target,
                                   None if video is not None else int(row["label"]))
        demos.append({**result, "source": row["path"], "label": None if video is not None else int(row["label"]),
                      "video": target.relative_to(out).as_posix(), "snapshot": target.with_suffix(".jpg").relative_to(out).as_posix(),
                      "encoded_frames": frame_count, "selection": "First filenames in each held-out class; no filtering by correctness." if video is None else "Explicitly selected video passed through the new-video inference path"})
        print(f"Demo {target}: {result['decision']} score={result['score']:.3f}", flush=True)
    write_json(out / ("new_video_demo.json" if video else "demos.json"), demos)
    return demos
