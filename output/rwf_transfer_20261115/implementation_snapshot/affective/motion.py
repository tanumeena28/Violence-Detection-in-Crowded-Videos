"""Lightweight adjacent-frame motion control on the frozen crowd pilot split.

Features contain frame differences and dense optical flow, not pose detections.
Descriptor and regularization grid are fixed before this run's test scoring.
"""
from __future__ import annotations

import csv
import hashlib
import json
import time
from pathlib import Path

import cv2
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

from .data import read_manifest, write_json
from .train import choose_threshold, metrics

SETTINGS = {
    "schema": "adjacent-flow-difference-grid2-v1", "opencv": cv2.__version__,
    "resize": [160, 120], "anchors": "existing pose-cache frame indices",
    "pair": "anchor and next decoded frame; final anchor uses preceding frame",
    "grid": [2, 2], "flow": "Farneback", "pyr_scale": 0.5,
    "levels": 3, "winsize": 15, "iterations": 3, "poly_n": 5, "poly_sigma": 1.2,
    "channels": ["absolute_gray_difference", "flow_speed", "median_subtracted_flow_speed", "horizontal_velocity", "vertical_velocity"],
    "temporal_statistics": ["mean", "std", "p90", "max"],
    "velocity_units": "fraction of resized image width or height per second",
}


def summarize_pairs(values):
    values = np.asarray(values, dtype=np.float32)
    if values.ndim != 2 or len(values) < 1 or not np.isfinite(values).all():
        raise ValueError("Expected finite motion descriptors for at least one pair")
    return np.concatenate([values.mean(0), values.std(0), np.quantile(values, .9, axis=0), values.max(0)]).astype(np.float32)


def motion_features(grays, indices, fps):
    if len(grays) < 2 or fps <= 0 or not np.isfinite(fps):
        raise ValueError("At least two decoded frames and a positive FPS required")
    if np.any(indices < 0) or np.any(indices >= len(grays)):
        raise ValueError("Anchor outside decoded video")
    descriptors = []
    for anchor in indices:
        first = min(int(anchor), len(grays) - 2)
        before, after = grays[first], grays[first + 1]
        flow = cv2.calcOpticalFlowFarneback(before, after, None, .5, 3, 15, 3, 5, 1.2, 0)
        h, w = before.shape
        velocity = flow * np.array([fps / w, fps / h], dtype=np.float32)
        residual = velocity - np.median(velocity.reshape(-1, 2), axis=0)
        channels = np.stack([cv2.absdiff(before, after).astype(np.float32) / 255,
                             np.linalg.norm(velocity, axis=-1), np.linalg.norm(residual, axis=-1),
                             velocity[..., 0], velocity[..., 1]], axis=-1)
        descriptors.append(np.array([cell.mean((0, 1)) for stripe in np.array_split(channels, 2, axis=0)
                                      for cell in np.array_split(stripe, 2, axis=1)]).reshape(-1))
    return summarize_pairs(descriptors)


def decode_gray(path):
    cap = cv2.VideoCapture(str(path))
    fps, frames = float(cap.get(cv2.CAP_PROP_FPS)), []
    while True:
        ok, image = cap.read()
        if not ok:
            break
        frames.append(cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), (160, 120), interpolation=cv2.INTER_AREA))
    cap.release()
    return frames, fps


def extract_motion(root, out):
    cache = out / "motion" / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    signature = hashlib.sha256(json.dumps(SETTINGS, sort_keys=True).encode()).hexdigest()
    rows = read_manifest(out / "manifest.csv")
    features = []
    started = time.perf_counter()
    for number, row in enumerate(rows, 1):
        path = root / row["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError(f"Source changed: {path}")
        with np.load(out / "cache" / f"{row['id']}.npz", allow_pickle=False) as pose:
            indices = pose["frame_indices"].copy()
            source_digest = str(pose["source_sha256"])
            quality = json.loads(str(pose["quality"]))
        if source_digest != row["sha256"]:
            raise ValueError("Pose cache source mismatch")
        target = cache / f"{row['id']}.npz"
        vector = None
        if target.exists():
            with np.load(target, allow_pickle=False) as saved:
                if str(saved["signature"]) == signature and str(saved["source_sha256"]) == source_digest and np.array_equal(saved["frame_indices"], indices):
                    vector = saved["features"].copy()
        if vector is None:
            grays, fps = decode_gray(path)
            if len(grays) != quality["decoded_frames"]:
                raise ValueError("Motion and pose decoding lengths differ")
            vector = motion_features(grays, indices, fps)
            temporary = target.with_suffix(".tmp.npz")
            np.savez_compressed(temporary, features=vector, frame_indices=indices,
                                signature=np.array(signature), source_sha256=np.array(source_digest))
            temporary.replace(target)
        if vector.shape != (80,) or not np.isfinite(vector).all():
            raise ValueError("Invalid motion feature vector")
        features.append(vector)
        if number == 1 or number % 25 == 0 or number == len(rows):
            print(f"Motion features {number}/{len(rows)}", flush=True)
    write_json(out / "motion" / "feature_settings.json", {**SETTINGS, "signature": signature, "clips": len(rows), "wall_seconds": time.perf_counter() - started})
    return rows, np.stack(features), signature


def score_linear(features, checkpoint):
    standardized = (features - np.array(checkpoint["mean"])) / np.array(checkpoint["std"])
    logits = standardized @ np.array(checkpoint["coefficients"]) + checkpoint["intercept"]
    return 1 / (1 + np.exp(-np.clip(logits, -700, 700)))


def fit_control(out, rows, features, name, signature, cs, protocol=None):
    # Use the same float64 arithmetic for fitting and JSON checkpoint inference.
    features = np.asarray(features, dtype=np.float64)
    if features.ndim != 2 or len(features) != len(rows) or not np.isfinite(features).all():
        raise ValueError("Control features must be finite and match the manifest")
    masks = {s: np.array([r["split"] == s for r in rows]) for s in ("train", "val", "test")}
    labels = np.array([r["label"] for r in rows])
    if not cs or any(c <= 0 for c in cs) or any(set(labels[mask]) != {0, 1} for mask in masks.values()):
        raise ValueError("Controls require positive regularization values and both classes in every split")
    mean = features[masks["train"]].mean(0)
    std = np.maximum(features[masks["train"]].std(0), .01)
    standardized = (features - mean) / std
    candidates = []
    best, best_loss, best_c = None, float("inf"), None
    for c in cs:
        model = LogisticRegression(C=c, max_iter=2000, solver="lbfgs", random_state=42)
        model.fit(standardized[masks["train"]], labels[masks["train"]])
        loss = float(log_loss(labels[masks["val"]], model.predict_proba(standardized[masks["val"]])[:, 1]))
        candidates.append({"C": c, "validation_log_loss": loss})
        if loss < best_loss:
            best, best_loss, best_c = model, loss, c
    val_scores = best.predict_proba(standardized[masks["val"]])[:, 1]
    threshold = choose_threshold(labels[masks["val"]], val_scores)
    # Freeze model, normalization, and threshold before reading test metrics.
    checkpoint = {"schema": "standardized-logistic-v1", "name": name, "feature_signature": signature,
                  "mean": mean.tolist(), "std": std.tolist(), "coefficients": best.coef_[0].tolist(),
                  "intercept": float(best.intercept_[0]), "threshold": threshold, "selected_C": best_c,
                  "manifest_sha256": hashlib.sha256((out / "manifest.csv").read_bytes()).hexdigest()}
    scores = score_linear(features, checkpoint)
    np.testing.assert_allclose(scores, best.predict_proba(standardized)[:, 1], atol=1e-8)
    result = {"variant": name, "features": features.shape[1], "classifier_parameters": features.shape[1] + 1,
              "threshold": threshold, "selected_C": best_c, "candidates": candidates,
              "train_clips": int(masks["train"].sum()), "val_clips": int(masks["val"].sum()), "test_clips": int(masks["test"].sum()),
              "train": metrics(labels[masks["train"]], scores[masks["train"]], threshold),
              "validation": metrics(labels[masks["val"]], scores[masks["val"]], threshold),
              "test": metrics(labels[masks["test"]], scores[masks["test"]], threshold),
              "protocol": protocol or "Fixed existing pilot split. Train-only scaling and classifier fit; validation log-loss selects C, validation macro-F1 selects threshold. All test clips retained. Test results are exploratory after prior pilot test inspection.",
              "limitations": ("Handcrafted linear control, not a reproduced published RGB or optical-flow deep model. Camera motion and edits can influence motion features; median subtraction is not validated camera stabilization."
                              if name == "motion_linear" else "Aggregate detection counts and quality can encode scene, crowd density and pose-estimator behavior. This is a confound diagnostic, not a skeleton-motion classifier.")}
    if name == "pose_quality_only":
        result["feature_names"] = QUALITY_NAMES
    folder = out / "motion" / name
    write_json(folder / "model.json", checkpoint)
    write_json(folder / "metrics.json", result)
    with (folder / "predictions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "path", "split", "label", "score", "prediction"])
        writer.writeheader()
        writer.writerows({"id": r["id"], "path": r["path"], "split": r["split"], "label": r["label"],
                          "score": float(s), "prediction": int(s >= threshold)} for r, s in zip(rows, scores))
    print(f"{name}: validation accuracy {result['validation']['accuracy']:.1%}, test accuracy {result['test']['accuracy']:.1%}, test macro-F1 {result['test']['macro_f1']:.3f}", flush=True)
    return result


QUALITY_NAMES = ["usable_pose_fraction", "mean_people", "valid_joint_fraction", "total_tracks", "max_people_detected", "discarded_tracks", "frames_with_people"]
CONTROL_CONFIG = {"motion_linear": {"features": 80, "regularization": [.01, .1, 1., 10.]},
                  "pose_quality_only": {"features": len(QUALITY_NAMES), "regularization": [1.]}}


def quality_features(out, rows):
    by_id = {r["id"]: r for r in json.loads((out / "pose_quality.json").read_text(encoding="utf-8"))["clips"]}
    if any(r["id"] not in by_id or by_id[r["id"]]["label"] != r["label"] for r in rows):
        raise ValueError("Pose-quality metadata does not match manifest IDs and labels")
    values = np.array([[by_id[r["id"]][k] for k in QUALITY_NAMES] for r in rows], dtype=np.float32)
    if not np.isfinite(values).all():
        raise ValueError("Non-finite pose-quality features")
    return values


def load_cached_motion(out, rows):
    """Load immutable descriptors, including on a machine with a different OpenCV version."""
    out = Path(out)
    settings = json.loads((out / "motion" / "feature_settings.json").read_text(encoding="utf-8"))
    # The OpenCV version records extraction provenance. Cached-feature fitting
    # does not rerun optical flow and must not replace it with the host version.
    recorded = {key: settings[key] for key in SETTINGS}
    signature = hashlib.sha256(json.dumps(recorded, sort_keys=True).encode()).hexdigest()
    if signature != settings["signature"]:
        raise ValueError("Motion settings signature mismatch")
    for key, expected in SETTINGS.items():
        if key != "opencv" and recorded[key] != expected:
            raise ValueError(f"Unsupported cached motion setting: {key}")
    vectors = []
    for row in rows:
        with np.load(out / "cache" / f"{row['id']}.npz", allow_pickle=False) as pose:
            indices = pose["frame_indices"].copy()
        with np.load(out / "motion" / "cache" / f"{row['id']}.npz", allow_pickle=False) as cached:
            if (str(cached["signature"]) != signature or str(cached["source_sha256"]) != row["sha256"]
                    or not np.array_equal(cached["frame_indices"], indices)):
                raise ValueError(f"Motion cache provenance mismatch: {row['id']}")
            vectors.append(cached["features"].copy())
    features = np.asarray(vectors, dtype=np.float64)
    if features.shape != (len(rows), CONTROL_CONFIG["motion_linear"]["features"]) or not np.isfinite(features).all():
        raise ValueError("Invalid cached motion features")
    return features, signature


def audit_controls(out: Path):
    """Reproduce saved controls from cached inputs without fitting new models."""
    rows = read_manifest(out / "manifest.csv")
    manifest_digest = hashlib.sha256((out / "manifest.csv").read_bytes()).hexdigest()
    signature = hashlib.sha256(json.dumps(SETTINGS, sort_keys=True).encode()).hexdigest()
    settings = json.loads((out / "motion" / "feature_settings.json").read_text(encoding="utf-8"))
    if settings["signature"] != signature or settings["clips"] != len(rows):
        raise ValueError("Motion settings differ from the saved feature corpus")
    vectors = []
    for row in rows:
        with np.load(out / "cache" / f"{row['id']}.npz", allow_pickle=False) as pose:
            indices = pose["frame_indices"].copy()
        with np.load(out / "motion" / "cache" / f"{row['id']}.npz", allow_pickle=False) as cached:
            if (str(cached["signature"]) != signature or str(cached["source_sha256"]) != row["sha256"]
                    or not np.array_equal(cached["frame_indices"], indices)):
                raise ValueError(f"Motion cache provenance mismatch: {row['id']}")
            vectors.append(cached["features"].copy())
    summary = json.loads((out / "motion" / "summary.json").read_text(encoding="utf-8"))
    if {r["variant"] for r in summary} != {"motion_linear", "pose_quality_only"}:
        raise ValueError("Expected both follow-up controls")
    labels = np.array([r["label"] for r in rows])
    train = np.array([r["split"] == "train" for r in rows])
    audits = []
    for result in summary:
        name = result["variant"]
        features = np.asarray(vectors if name == "motion_linear" else quality_features(out, rows), dtype=np.float64)
        if features.shape != (len(rows), result["features"]) or not np.isfinite(features).all():
            raise ValueError("Invalid control feature corpus")
        folder = out / "motion" / name
        checkpoint = json.loads((folder / "model.json").read_text(encoding="utf-8"))
        expected_signature = signature if name == "motion_linear" else hashlib.sha256(json.dumps(QUALITY_NAMES).encode()).hexdigest()
        if checkpoint["manifest_sha256"] != manifest_digest or checkpoint["feature_signature"] != expected_signature:
            raise ValueError("Control checkpoint provenance mismatch")
        np.testing.assert_allclose(checkpoint["mean"], features[train].mean(0), atol=1e-12, rtol=0)
        np.testing.assert_allclose(checkpoint["std"], np.maximum(features[train].std(0), .01), atol=1e-12, rtol=0)
        if json.loads((folder / "metrics.json").read_text(encoding="utf-8")) != result:
            raise ValueError("Control summary and metrics differ")
        winner = min(result["candidates"], key=lambda c: c["validation_log_loss"])["C"]
        if checkpoint["selected_C"] != result["selected_C"] or winner != result["selected_C"]:
            raise ValueError("Selected regularization does not match validation records")
        scores = score_linear(features, checkpoint)
        with (folder / "predictions.csv").open(newline="", encoding="utf-8") as f:
            saved = list(csv.DictReader(f))
        if [(r["id"], r["path"], r["split"], int(r["label"])) for r in saved] != [(r["id"], r["path"], r["split"], r["label"]) for r in rows]:
            raise ValueError("Control predictions do not match manifest order and labels")
        saved_scores = np.array([float(r["score"]) for r in saved])
        np.testing.assert_allclose(scores, saved_scores, atol=1e-10, rtol=0)
        np.testing.assert_array_equal(scores >= checkpoint["threshold"], [int(r["prediction"]) for r in saved])
        val = np.array([r["split"] == "val" for r in rows])
        if checkpoint["threshold"] != result["threshold"] or choose_threshold(labels[val], scores[val]) != result["threshold"]:
            raise ValueError("Control threshold is not reproduced by validation scores")
        for split, key in (("train", "train"), ("val", "validation"), ("test", "test")):
            mask = np.array([r["split"] == split for r in rows])
            if metrics(labels[mask], saved_scores[mask], result["threshold"]) != result[key]:
                raise ValueError("Control metrics do not match saved predictions")
        audits.append({"variant": name, "predictions_reproduced": True,
                       "maximum_score_drift": float(np.abs(scores - saved_scores).max()),
                       "train_scaling_verified": True, "validation_threshold_verified": True,
                       "model_sha256": hashlib.sha256((folder / "model.json").read_bytes()).hexdigest()})
    report = {"status": "pass", "manifest_sha256": manifest_digest,
              "motion_caches_verified": len(rows), "controls": audits,
              "claim_boundary": "Cached-input provenance and saved-checkpoint consistency. Does not establish source independence, label validity, or unbiased generalization."}
    write_json(out / "motion" / "audit.json", report)
    return report


def run_motion(root: Path, out: Path):
    rows, features, signature = extract_motion(root, out)
    motion = fit_control(out, rows, features, "motion_linear", signature, [.01, .1, 1., 10.])
    # Diagnostic control: can aggregate detection quality/counts predict labels
    # without positions, trajectories or motion? Its C is fixed at 1.
    quality_signature = hashlib.sha256(json.dumps(QUALITY_NAMES).encode()).hexdigest()
    control = fit_control(out, rows, quality_features(out, rows), "pose_quality_only", quality_signature, [1.])
    control["feature_names"] = QUALITY_NAMES
    write_json(out / "motion" / "pose_quality_only" / "metrics.json", control)
    write_json(out / "motion" / "summary.json", [motion, control])
    return [motion, control]
