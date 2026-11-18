"""Describe CPU reproduction drift without changing saved scores or tolerance."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import torch

from affective.cross_validation import digest, summarize_cv, validate_plan
from affective.cv_report import read_predictions
from affective.data import write_json
from affective.demo import load_model
from affective.train import choose_threshold, load_features, normalize_training, predict


def audit_cpu_precision(out, implementation_dir):
    out = Path(out).resolve()
    plan = validate_plan(out, implementation_dir)
    if summarize_cv(out, implementation_dir=implementation_dir, write=False)["status"] != "complete":
        raise ValueError("Complete the experiment before auditing CPU precision")
    torch.set_num_threads(4)
    records = []
    for fold in range(1, plan["settings"]["folds"] + 1):
        folder = out / f"fold_{fold}"
        for variant in plan["settings"]["variants"]:
            parts, _ = load_features(folder, variant, out / "cache")
            normalize_training(parts)
            for seed in plan["settings"]["seeds"]:
                run = folder / "runs" / f"{variant}_seed{seed}"
                model, checkpoint = load_model(run / "model.pt")
                saved = read_predictions(run / "predictions.csv")
                for split in ("val", "test"):
                    rows = [row for row in saved if row["split"] == split]
                    if [row["id"] for row in rows] != [row["id"] for row in parts[split]["rows"]]:
                        raise ValueError("Prediction ordering differs from frozen inputs")
                    expected = np.array([float(row["score"]) for row in rows])
                    actual = predict(model, parts[split], "cpu")
                    drift = np.abs(actual - expected)
                    records.append({"fold": fold, "variant": variant, "seed": seed, "split": split,
                                    "scores": len(expected), "maximum_absolute_score_drift": float(drift.max()),
                                    "scores_outside_original_0_0003_tolerance": int((drift > 3e-4).sum()),
                                    "classification_decisions_changed": int(((actual >= checkpoint["threshold"]) !=
                                                                               (expected >= checkpoint["threshold"])).sum()),
                                    "cpu_validation_threshold_matches_saved":
                                        choose_threshold(parts[split]["y"], actual) == checkpoint["threshold"] if split == "val" else None})
        print(f"CPU precision checked: fold {fold}", flush=True)
    result = {"protocol_sha256": digest(out / "protocol.json"), "device": "cpu", "absolute_tolerance": 3e-4,
              "maximum_absolute_score_drift": max(row["maximum_absolute_score_drift"] for row in records),
              "scores_checked": sum(row["scores"] for row in records),
              "scores_outside_original_tolerance": sum(row["scores_outside_original_0_0003_tolerance"] for row in records),
              "classification_decisions_changed": sum(row["classification_decisions_changed"] for row in records),
              "validation_thresholds_differing_on_cpu": sum(row["cpu_validation_threshold_matches_saved"] is False for row in records),
              "script_sha256": digest(Path(__file__)), "runs": records,
              "interpretation": "Describes cross-device numerical behavior. Saved GPU scores and thresholds are unchanged. "
                                "A score outside tolerance remains a failed CPU score check, even when its classification is unchanged. "
                                "Use the separate same-device audit to assess fitted-artifact score reproduction."}
    write_json(out / "cpu_precision_audit.json", result)
    print(json.dumps({key: value for key, value in result.items() if key != "runs"}, indent=2), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--implementation-dir", type=Path)
    args = parser.parse_args()
    implementation = args.implementation_dir or args.out / "implementation_snapshot" / "affective"
    audit_cpu_precision(args.out, implementation)
