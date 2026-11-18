"""Check saved pilot predictions, provenance and playable demos; report uncertainty.

Run with .venv/Scripts/python.exe scripts/audit_pilot.py from the project folder.
This checks saved artifacts and never changes checkpoints or decision thresholds.
"""
from __future__ import annotations

import csv
import argparse
import hashlib
import json
import sys
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.data import read_manifest, source_overlap_candidates, write_json
from affective.demo import load_model
from affective.features import FEATURE_SCHEMAS
from affective.train import load_features, metrics, normalize_training, predict
from affective.motion import audit_controls


def main():
    parser = argparse.ArgumentParser(description="Verify saved crowd pilot artifacts")
    parser.add_argument("--out", type=Path, default=ROOT / "output" / "pilot")
    args = parser.parse_args()
    torch.set_num_threads(4)
    out = args.out.resolve()
    manifest = read_manifest(out / "manifest.csv")
    manifest_hash = hashlib.sha256((out / "manifest.csv").read_bytes()).hexdigest()
    quality = json.loads((out / "pose_quality.json").read_text(encoding="utf-8"))
    inventory = json.loads((out / "inventory.json").read_text(encoding="utf-8"))
    settings = json.loads((out / "pose_settings.json").read_text(encoding="utf-8"))
    weights = ROOT / "models" / settings["weights"]
    assert hashlib.sha256(weights.read_bytes()).hexdigest() == settings["weights_sha256"]
    assert not quality["failures"]
    assert len(quality["clips"]) == len(manifest) == inventory["usable_count"]
    assert len({r["sha256"] for r in manifest}) == len(manifest)
    source_groups = {s: {r["source_group"] for r in manifest if r["split"] == s} for s in ("train", "val", "test")}
    assert all(source_groups.values())
    assert not (source_groups["train"] & source_groups["val"] or source_groups["train"] & source_groups["test"] or source_groups["val"] & source_groups["test"])
    overlap_candidates = source_overlap_candidates(manifest, inventory["dataset"])
    for row in manifest:
        assert hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"]
    summary = json.loads((out / "training_summary.json").read_text(encoding="utf-8"))
    assert {r["variant"] for r in summary} == {"baseline", "reliability", "interactions", "combined"}
    audits = []
    fig, axes = plt.subplots(1, len(summary), figsize=(13, 3.5))
    for result, ax in zip(summary, axes):
        run = out / "runs" / f"{result['variant']}_seed{result['seed']}"
        model, ckpt = load_model(run / "model.pt")
        assert ckpt["manifest_sha256"] == manifest_hash
        assert ckpt["pose_signature"] == settings["signature"] == result["pose_signature"]
        assert ckpt["feature_schema"] in FEATURE_SCHEMAS
        assert ckpt["threshold"] == result["threshold"]
        parts, signature = load_features(out, result["variant"], feature_schema=ckpt["feature_schema"])
        assert signature == ckpt["pose_signature"]
        mean, std = normalize_training(parts)
        np.testing.assert_allclose(mean, ckpt["mean"].numpy(), atol=1e-6)
        np.testing.assert_allclose(std, ckpt["std"].numpy(), atol=1e-6)
        with (run / "predictions.csv").open(newline="", encoding="utf-8") as f:
            saved = list(csv.DictReader(f))
        maximum_cpu_drift, maximum_cuda_drift = 0.0, 0.0
        for split in ("val", "test"):
            rows = [r for r in saved if r["split"] == split]
            group = parts[split]
            assert [r["id"] for r in rows] == [r["id"] for r in group["rows"]]
            assert [int(r["label"]) for r in rows] == group["y"].tolist()
            scores = predict(model.cpu(), group, "cpu")
            saved_scores = np.array([float(r["score"]) for r in rows])
            # CPU and CUDA convolution arithmetic can differ slightly; verify
            # that the small numerical drift does not change any clip decision.
            # CUDA's TF32 path produced measured drift below 0.0002 in this run.
            np.testing.assert_allclose(scores, saved_scores, atol=3e-4, rtol=0)
            np.testing.assert_array_equal(scores >= ckpt["threshold"], saved_scores >= ckpt["threshold"])
            maximum_cpu_drift = max(maximum_cpu_drift, float(np.max(np.abs(scores - saved_scores))))
            if torch.cuda.is_available():
                cuda_scores = predict(model.cuda(), group, "cuda")
                np.testing.assert_allclose(cuda_scores, saved_scores, atol=1e-6, rtol=0)
                maximum_cuda_drift = max(maximum_cuda_drift, float(np.max(np.abs(cuda_scores - saved_scores))))
            computed = metrics(group["y"], saved_scores, ckpt["threshold"])
            recorded = result["validation" if split == "val" else "test"]
            assert computed == recorded
        test_rows = [r for r in saved if r["split"] == "test"]
        labels = np.array([int(r["label"]) for r in test_rows])
        scores = np.array([float(r["score"]) for r in test_rows])
        correct = (scores >= ckpt["threshold"]) == labels
        rng = np.random.default_rng(20261021)
        # Resample independent test clips, keeping each class count fixed.
        accuracy_samples = np.zeros(10000)
        for label in (0, 1):
            choices = np.flatnonzero(labels == label)
            accuracy_samples += correct[rng.choice(choices, size=(10000, len(choices)))].sum(1)
        ci = np.quantile(accuracy_samples / len(labels), [.025, .975]).tolist()
        coverage = np.array([float(r["usable_pose_fraction"]) for r in test_rows])
        strata = {}
        for name, mask in (("below_25_percent", coverage < .25), ("at_least_25_percent", coverage >= .25)):
            strata[name] = {"n": int(mask.sum()), "accuracy": float(correct[mask].mean()) if mask.any() else None}
        audit = {"variant": result["variant"], "seed": result["seed"],
                 "saved_predictions_reproduced_on_cpu": True,
                 "maximum_cpu_score_drift": maximum_cpu_drift,
                 "maximum_cuda_score_drift": maximum_cuda_drift if torch.cuda.is_available() else None,
                 "cpu_threshold_decisions_identical": True,
                 "accuracy": result["test"]["accuracy"], "accuracy_95_percent_bootstrap_ci": ci,
                 "pose_quality_strata": strata,
                 "checkpoint_sha256": hashlib.sha256((run / "model.pt").read_bytes()).hexdigest()}
        audits.append(audit)
        cm = np.array(result["test"]["confusion_matrix"])
        ax.imshow(cm, cmap="Blues", vmin=0, vmax=24)
        for (i, j), value in np.ndenumerate(cm):
            ax.text(j, i, str(value), ha="center", va="center", color="white" if value > 12 else "#14243a")
        ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["Nonviolent", "Violent"],
               yticklabels=["Nonviolent", "Violent"], xlabel="Predicted label", title=result["variant"])
    axes[0].set_ylabel("Dataset label")
    fig.tight_layout()
    figures = out / "figures"
    figures.mkdir(exist_ok=True)
    fig.savefig(figures / "confusion_matrices.png", dpi=160)
    plt.close(fig)
    demos = json.loads((out / "demos.json").read_text(encoding="utf-8"))
    video_checks = []
    for demo in demos:
        cap = cv2.VideoCapture(str(out / demo["video"]))
        decoded = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            assert frame.shape == (680, 1120, 3)
            decoded += 1
        cap.release()
        assert decoded == demo["encoded_frames"] > 0
        assert cv2.imread(str(out / demo["snapshot"])) is not None
        source = next(r for r in manifest if r["path"] == demo["source"])
        assert source["split"] == "test"
        assert demo["raw_prediction"] == int(demo["score"] >= demo["threshold"])
        assert demo["abstain"] == (demo["usable_pose_fraction"] < .25)
        video_checks.append({"video": demo["video"], "decoded_frames": decoded, "snapshot_readable": True})
    control_audit = audit_controls(out) if (out / "motion" / "summary.json").exists() else None
    report = {"status": "pass", "manifest_sha256": manifest_hash, "source_videos_verified": len(manifest),
              "pose_caches_verified": len(manifest), "runs": audits, "demos": video_checks,
              "mean_usable_pose_coverage": float(np.mean([r["usable_pose_fraction"] for r in quality["clips"]])),
              "clips_below_25_percent_pose_coverage": sum(r["usable_pose_fraction"] < .25 for r in quality["clips"]),
              "decode_header_mismatches": [r["path"] for r in quality["clips"] if not r["full_decode_matches_header"]],
              "clips_with_discarded_tracks": sum(r["discarded_tracks"] > 0 for r in quality["clips"]),
              "source_independence_status": "review_required" if overlap_candidates else "no_known_id_overlap",
              "source_id_overlap_candidates": overlap_candidates,
              "control_audit": control_audit,
              "uncertainty_method": "10,000 class-stratified clip bootstrap resamples; percentile 95% intervals. These reflect this holdout only, not training-seed, fold, or source-group uncertainty.",
              "claim_boundary": "Artifact consistency, source hashes, CPU prediction reproduction, and full video decoding. This does not verify labels, remove near-duplicates, or establish deployment readiness."}
    write_json(out / "audit.json", report)
    lines = ["# Pilot verification and limitations", "", "Saved artifacts passed verification.", "",
             f"All {len(manifest)} source video hashes match the manifest. Exact stored source keys are disjoint across splits, but this does not establish source independence. All four checkpoints reproduce saved validation/test scores on CPU within 0.0003 absolute tolerance, with identical threshold decisions. The CUDA check uses 0.000001 absolute tolerance. Measured drift is saved per model in audit.json; CUDA TF32 and CPU arithmetic differ slightly. Reported metrics match the prediction CSV files. Every demo video decodes fully and has a readable poster image.", "",
             "| Variant | Test accuracy | Approximate 95% interval | Accuracy with pose coverage below 25% | Accuracy with coverage at least 25% |",
             "|---|---:|---:|---:|---:|"]
    for a in audits:
        low, high = a["accuracy_95_percent_bootstrap_ci"]
        poor, usable = a["pose_quality_strata"].values()
        lines.append(f"| {a['variant']} | {a['accuracy']:.1%} | {low:.1%} to {high:.1%} | {poor['accuracy']:.1%} (n={poor['n']}) | {usable['accuracy']:.1%} (n={usable['n']}) |")
    lines += ["", report["uncertainty_method"], "",
              "Mean usable pose coverage is {:.1%}. {} clips fall below 25% coverage. Track selection discards some detected tracks in {} clips. One clip's full decode length differs from its container header; extraction samples the fully decoded clip.".format(report["mean_usable_pose_coverage"], report["clips_below_25_percent_pose_coverage"], report["clips_with_discarded_tracks"]), "",
              "The models overfit quickly, so validation loss selects an early checkpoint. Do not tune thresholds on the test set, report a filtered test subset as overall accuracy, or treat small differences between variants as statistically established.", "",
              "The six demos use the first three filenames from each held-out class, including abstentions and a missed violent clip. They are not selected by correctness.", "",
              "Remaining research: source/label review, multiple seeds and folds, stronger motion/RGB controls, external evaluation, and annotated person-level attribution. The current system outputs a full-clip score.", "",
              "![Held-out confusion matrices](figures/confusion_matrices.png)", ""]
    if overlap_candidates:
        lines += ["## Source overlap warning", "",
                  f"{len(overlap_candidates)} cross-split pairs have matching source titles/uploaders and prefix-compatible IDs. Truncated filenames defeated the original exact-key grouping. The sampled Preston footage overlaps visually. The artifact consistency check passes, but source independence requires regrouping and retraining. Original checkpoints, metrics and manifest are retained as an archived pilot.", "",
                  "See [source review and contact sheets](failure_analysis/index.html) and `source_id_overlap_candidates` in audit.json.", ""]
    if control_audit:
        lines += ["## Follow-up control verification", "",
                  f"All {control_audit['motion_caches_verified']} motion caches match source hashes, frame anchors and feature settings. Both linear checkpoints reproduce every saved score and decision. Training-only normalization, validation-selected thresholds and all reported split metrics were verified. This checks saved artifacts; source and label review remains necessary.", ""]
    (out / "AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Pilot audit passed: {len(audits)} checkpoints and {len(video_checks)} fully decoded demo videos.")


if __name__ == "__main__":
    main()
