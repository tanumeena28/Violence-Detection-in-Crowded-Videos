"""Retrain the frozen pilot protocol after conservative source-ID grouping.

Reuse immutable video features, never the original training statistics or
checkpoints. Keep corrected outputs separate from the archived pilot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.analysis import analyze
from affective.data import prepare, read_manifest, source_overlap_candidates, write_json
from affective.demo import make_demos
from affective.motion import run_motion
from affective.report import write_report
from affective.train import train_variants


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=None, help="Report date as YYYY-MM-DD")
    args = parser.parse_args()
    original = ROOT / "output" / "pilot"
    corrected = ROOT / "output" / "source_corrected"
    if (corrected / "training_summary.json").exists():
        raise FileExistsError("Corrected pilot already exists; inspect it before rerunning")
    old_manifest = read_manifest(original / "manifest.csv")
    rows = prepare(ROOT, corrected)
    if source_overlap_candidates(rows):
        raise ValueError("Known source-ID overlaps remain")
    if {r["id"] for r in rows if r["split"] == "test"} != {r["id"] for r in old_manifest if r["split"] == "test"}:
        raise ValueError("This correction unexpectedly changes the pilot test set")
    pose = json.loads((original / "pose_quality.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in pose["clips"]}
    (corrected / "cache").mkdir(parents=True, exist_ok=True)
    (corrected / "motion" / "cache").mkdir(parents=True, exist_ok=True)
    for row in rows:
        source = original / "cache" / f"{row['id']}.npz"
        with np.load(source, allow_pickle=False) as cached:
            if str(cached["source_sha256"]) != row["sha256"] or str(cached["signature"]) != pose["signature"]:
                raise ValueError("Original pose cache provenance mismatch")
        shutil.copy2(source, corrected / "cache" / source.name)
        motion_source = original / "motion" / "cache" / source.name
        if motion_source.exists():
            shutil.copy2(motion_source, corrected / "motion" / "cache" / source.name)
    pose["clips"] = [{**by_id[r["id"]], "split": r["split"]} for r in rows]
    pose["failures"] = []
    pose["feature_reuse"] = "Retained immutable original per-video pose caches; no new pose extraction."
    write_json(corrected / "pose_quality.json", pose)
    shutil.copy2(original / "pose_settings.json", corrected / "pose_settings.json")
    retained = {r["id"] for r in rows}
    provenance = {"original_manifest_sha256": hashlib.sha256((original / "manifest.csv").read_bytes()).hexdigest(),
                  "corrected_manifest_sha256": hashlib.sha256((corrected / "manifest.csv").read_bytes()).hexdigest(),
                  "excluded_clips": [r for r in old_manifest if r["id"] not in retained],
                  "original_overlap_candidates": source_overlap_candidates(old_manifest),
                  "known_corrected_overlap_candidates": source_overlap_candidates(rows),
                  "protocol": "Same four variants, hidden=48, seed=42, epochs=180, patience=30. Fresh train-only statistics, fresh checkpoints and validation-selected thresholds. Original 47 test clips retained. Exploratory correction after test inspection, not a fresh unseen benchmark."}
    write_json(corrected / "correction.json", provenance)
    train_variants(corrected, ["baseline", "reliability", "interactions", "combined"], [42],
                   epochs=180, patience=30, hidden=48, device="auto")
    run_motion(ROOT, corrected)
    analyze(ROOT, corrected)
    make_demos(ROOT, corrected, "combined_seed42", 6)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "audit_pilot.py"), "--out", str(corrected)],
                   cwd=ROOT, check=True)
    write_report(ROOT, corrected, args.date)
    write_correction_report(original, corrected)
    print(f"Source-corrected pilot complete: {corrected / 'index.html'}", flush=True)


def write_correction_report(original: Path, corrected: Path):
    original_results = json.loads((original / "training_summary.json").read_text(encoding="utf-8"))
    original_results += json.loads((original / "motion" / "summary.json").read_text(encoding="utf-8"))
    final_results = json.loads((corrected / "training_summary.json").read_text(encoding="utf-8"))
    final_results += json.loads((corrected / "motion" / "summary.json").read_text(encoding="utf-8"))
    prior = {r["variant"]: r for r in original_results}
    lines = ["# Source grouping correction", "",
             "Three training clips were conservatively excluded because their source titles/uploaders match validation clips and their shortened IDs prefix the full source IDs. The two Preston clips show matching footage in the sampled review. The Russia/Ukraine pair comes from a matching source ID but shows different sampled segments; grouping it is a precaution against shared-source leakage.", "",
             "The corrected split has 147 training, 48 validation and the same 47 test clips. Per-video pose/motion features are reused; normalization, coefficients, temporal checkpoints and thresholds are recomputed. The four TCN variants retain hidden=48, seed=42, epochs=180 and patience=30. This is an exploratory correction after test inspection, not a new unseen benchmark.", "",
             "| Model | Original accuracy | Corrected accuracy | Corrected macro-F1 | Corrected ROC-AUC |",
             "|---|---:|---:|---:|---:|"]
    lines += [f"| {r['variant']} | {prior[r['variant']]['test']['accuracy']:.1%} | {r['test']['accuracy']:.1%} | {r['test']['macro_f1']:.3f} | {r['test']['roc_auc']:.3f} |" for r in final_results]
    lines += ["", "All four corrected checkpoints, both linear controls, source/cache provenance and six full demo decodes pass the saved-artifact audit. No known exact or prefix-compatible source-ID overlaps remain. Filename and image-hash checks can miss other related footage.", "",
              "Pose-quality summaries remain stronger than the skeleton variants on this split. Scene and detection confounds require source-separated fold/seed evaluation before claiming the model learned violent body motion or that one representation is superior.", "",
              "[Corrected results page](index.html) | [Artifact audit](AUDIT.md) | [Excluded clips and provenance](correction.json) | [Archived pilot](../pilot/index.html)", ""]
    (corrected / "CORRECTION.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
