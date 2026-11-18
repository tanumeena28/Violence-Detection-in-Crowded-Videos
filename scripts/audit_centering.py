"""Quantify changed features from cached poses without fitting or scoring models."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from affective.data import read_manifest
from affective.features import FEATURE_SCHEMA, LEGACY_FEATURE_SCHEMA, build_features, track_centers


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def synthetic_check():
    points = np.zeros((3, 1, 17, 3), dtype=np.float32)
    points[..., :2] = [.4, .45]
    points[..., 2] = .9
    points[:, :, 11, :2] = [.35, .65]
    points[:, :, 12, :2] = [.45, .65]
    boxes = np.tile(np.array([.2, .1, .8, .9], np.float32), (3, 1, 1))
    present = np.ones((3, 1), dtype=bool)
    times = np.arange(3, dtype=np.float32) / 10
    points[1, 0, [11, 12], 2] = 0
    velocities = {}
    for schema in (LEGACY_FEATURE_SCHEMA, FEATURE_SCHEMA):
        features, _ = build_features(points, boxes, present, times, feature_schema=schema)
        velocities[schema] = features[:, 0, 44:46].tolist()
    assert np.max(np.abs(velocities[FEATURE_SCHEMA])) < 1e-6
    assert np.max(np.abs(velocities[LEGACY_FEATURE_SCHEMA])) > 1
    return {"definition": "Stationary joints and box; hip confidence drops only in the middle frame",
            "shoulder_velocity": velocities, "corrected_artificial_motion_removed": True}


def audit(source, out):
    plan = json.loads((source / "protocol.json").read_text(encoding="utf-8"))
    if digest(source / "assignments.csv") != plan["assignments_sha256"]:
        raise ValueError("Assignments changed from the frozen plan")
    records = []
    for row in read_manifest(source / "assignments.csv"):
        path = source / "cache" / f"{row['id']}.npz"
        if digest(path) != plan["cache_sha256"][row["id"]]:
            raise ValueError(f"Cached pose changed: {row['id']}")
        with np.load(path, allow_pickle=False) as saved:
            points, boxes = saved["keypoints"], saved["boxes"]
            present, times = saved["present"].astype(bool), saved["times"]
            valid = (points[..., 2] >= .25) & present[..., None]
            hips_ok = valid[..., 11] & valid[..., 12]
            legacy = np.where(hips_ok[..., None], (points[..., 11, :2] + points[..., 12, :2]) / 2,
                              (boxes[..., :2] + boxes[..., 2:]) / 2)
            corrected = track_centers(points[..., :2], boxes, present, hips_ok, times)
            displacement = np.linalg.norm(corrected - legacy, axis=-1)
            changed = (displacement > 1e-7) & present
            switches = (hips_ok[1:] != hips_ok[:-1]) & present[1:] & present[:-1]
            old_features, _ = build_features(points, boxes, present, times, interactions=True,
                                             feature_schema=LEGACY_FEATURE_SCHEMA)
            new_features, _ = build_features(points, boxes, present, times, interactions=True,
                                             feature_schema=FEATURE_SCHEMA)
            difference = np.abs(new_features - old_features)
            body_velocity = difference[..., 34:68]
            relative_velocity = difference[..., -5:-3]
            records.append({"id": row["id"], "label": row["label"], "path": row["path"],
                            "observed_person_frames": int(present.sum()),
                            "missing_hip_person_frames": int((present & ~hips_ok).sum()),
                            "hip_reference_switches": int(switches.sum()),
                            "corrected_center_person_frames": int(changed.sum()),
                            "frames_with_corrected_centers": int(changed.any(axis=1).sum()),
                            "body_velocity_changed_person_frames": int((body_velocity.max(axis=-1) > 1e-6).sum()),
                            "relative_velocity_changed_person_frames": int((relative_velocity.max(axis=-1) > 1e-6).sum()),
                            "maximum_center_displacement_image_units": float(displacement[present].max()) if present.any() else 0.,
                            "maximum_body_velocity_channel_change": float(body_velocity.max()),
                            "maximum_relative_velocity_channel_change": float(relative_velocity.max())})
    count_fields = [key for key, value in records[0].items() if isinstance(value, int) and key != "label"]
    groups = []
    for label in (None, 0, 1):
        selected = records if label is None else [r for r in records if r["label"] == label]
        totals = {key: sum(r[key] for r in selected) for key in count_fields}
        affected = sum(r["corrected_center_person_frames"] > 0 for r in selected)
        groups.append({"label": "all" if label is None else label, "clips": len(selected),
                       "clips_with_corrected_centers": affected,
                       "affected_clip_fraction": affected / len(selected), **totals,
                       "corrected_observed_person_frame_fraction": totals["corrected_center_person_frames"] / max(totals["observed_person_frames"], 1)})
    report = {"source": str(source), "source_protocol_sha256": digest(source / "protocol.json"),
              "feature_implementation_sha256": digest(Path(__file__).resolve().parents[1] / "affective" / "features.py"),
              "old_schema": LEGACY_FEATURE_SCHEMA, "new_schema": FEATURE_SCHEMA,
              "center_difference_tolerance": 1e-7, "feature_difference_tolerance": 1e-6,
              "synthetic_check": synthetic_check(), "aggregate": groups, "clips": records,
              "interpretation": "Counts quantify changed derived features, not false-motion ground truth or classification benefit. Interpolation is offline within continuously observed track segments. Pose tensors are unchanged."}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"synthetic_check": report["synthetic_check"], "aggregate": groups}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    audit(args.source.resolve(), args.out.resolve())
