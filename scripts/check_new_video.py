"""Verify the latest raw-video output against its saved model and full decode."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.data import write_json
from affective.demo import infer_cache, load_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "output" / "source_corrected")
    args = parser.parse_args()
    out = args.out.resolve()
    torch.set_num_threads(4)
    records = json.loads((out / "new_video_demo.json").read_text(encoding="utf-8"))
    checks = []
    for record in records:
        source = Path(record["source"])
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        folder = out / "inference" / digest[:16]
        cache = folder / "cache" / f"{digest[:16]}.npz"
        with np.load(cache, allow_pickle=False) as cached:
            if str(cached["source_sha256"]) != digest:
                raise ValueError("Selected video and cache source differ")
        model, checkpoint = load_model(out / "runs" / f"{record['variant']}_seed{record.get('seed', 42)}" / "model.pt")
        reproduced, _ = infer_cache(model, checkpoint, cache)
        if abs(reproduced["score"] - record["score"]) > 3e-4:
            raise ValueError("Raw-video score does not reproduce")
        for key in ("decision", "raw_prediction", "abstain", "threshold", "usable_pose_fraction"):
            if reproduced[key] != record[key]:
                raise ValueError(f"Raw-video inference field differs: {key}")
        cap = cv2.VideoCapture(str(out / record["video"]))
        decoded = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame.shape != (680, 1120, 3):
                raise ValueError("Unexpected raw-video output frame size")
            decoded += 1
        cap.release()
        if decoded != record["encoded_frames"] or decoded < 1:
            raise ValueError("Raw-video output failed full decode")
        if cv2.imread(str(out / record["snapshot"])) is None:
            raise ValueError("Raw-video poster is unreadable")
        checks.append({"source_sha256": digest, "source": str(source), "video": record["video"],
                       "decoded_frames": decoded, "score_reproduced": True,
                       "maximum_score_drift": abs(reproduced["score"] - record["score"]),
                       "decision": reproduced["decision"], "pose_signature": checkpoint["pose_signature"]})
    write_json(out / "new_video_audit.json", {"status": "pass", "checks": checks,
                                             "claim_boundary": "Raw-video source/cache provenance, saved-model prediction reproduction and complete annotated-video decode. Not label verification or accuracy evaluation."})
    print(f"Raw-video audit passed: {len(checks)} output(s).", flush=True)


if __name__ == "__main__":
    main()
