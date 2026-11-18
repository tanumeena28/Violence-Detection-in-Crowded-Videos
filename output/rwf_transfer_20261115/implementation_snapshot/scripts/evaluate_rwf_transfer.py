"""Freeze and evaluate one saved crowd classifier on the released RWF-2000 val split."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import shutil
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cv2
import numpy as np
import torch

from affective.cross_validation import digest, write_manifest
from affective.data import read_manifest, write_json
from affective.demo import load_model
from affective.features import build_features
from affective.pose import extract
from affective.train import VARIANTS, metrics, predict

MODULES = ("data.py", "pose.py", "tracking.py", "features.py", "model.py", "demo.py", "train.py", "cross_validation.py")
LIMITS = ("Exploratory transfer of a crowd-trained classifier to the released RWF-2000 evaluation split. "
          "No RWF training, normalization fitting, checkpoint selection or threshold tuning is performed. "
          "This is different from supervised training and evaluation on RWF. Supplied labels are retained. "
          "One known clip was inspected in an earlier demo; other prior viewing and unknown shared footage cannot be ruled out. "
          "Scores are not calibrated probabilities. All clips remain in primary metrics, including low-pose cases.")


def prepare_transfer(root, source, out, date, expected_per_class=200):
    root, source, out = Path(root).resolve(), Path(source).resolve(), Path(out).resolve()
    if out.exists():
        raise FileExistsError("Choose a new transfer directory; the frozen plan is never overwritten")
    model_path = source / "runs" / "combined_seed42" / "model.pt"
    _, checkpoint = load_model(model_path)
    settings = json.loads((source / "pose_settings.json").read_text(encoding="utf-8"))
    if settings.get("torch", torch.__version__) != torch.__version__ or settings.get("ultralytics", version("ultralytics")) != version("ultralytics"):
        raise ValueError("Use the recorded extraction package versions for this frozen transfer")
    if checkpoint["pose_signature"] != settings["signature"]:
        raise ValueError("Saved model and source extraction signatures differ")
    weights = root / "models" / settings["weights"]
    if digest(weights) != settings["weights_sha256"]:
        raise ValueError("Pose weights differ from those used for the saved crowd model")
    inspected = set()
    for folder in (source, root / "output" / "pilot"):
        evidence = folder / "new_video_demo.json"
        if evidence.exists():
            for entry in json.loads(evidence.read_text(encoding="utf-8")):
                path = Path(entry["source"])
                if path.is_file():
                    inspected.add(digest(path))
    rows = []
    for label, class_name in ((0, "NonFight"), (1, "Fight")):
        files = sorted((root / "data" / "RWF-2000" / "val" / class_name).glob("*.avi"))
        if len(files) != expected_per_class:
            raise ValueError(f"Expected {expected_per_class} {class_name} clips, found {len(files)}")
        for path in files:
            relative = path.relative_to(root).as_posix()
            source_hash = digest(path)
            cap = cv2.VideoCapture(str(path))
            ok, frame = cap.read()
            fps, frame_count = float(cap.get(cv2.CAP_PROP_FPS)), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            if not ok or fps <= 0 or frame_count < 2:
                raise ValueError(f"Unreadable evaluation clip: {relative}")
            rows.append({"id": hashlib.sha256(relative.encode()).hexdigest()[:16], "path": relative,
                         "sha256": source_hash, "source_group": path.stem.rsplit("_", 1)[0].casefold(),
                         "label": label, "fold": 0, "split": "test", "fps": fps, "frames": frame_count,
                         "width": frame.shape[1], "height": frame.shape[0]})
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Evaluation IDs are not unique")
    old_manifest = read_manifest(source / "manifest.csv")
    byte_overlaps = [row["id"] for row in rows if row["sha256"] in {old["sha256"] for old in old_manifest}]
    if byte_overlaps:
        raise ValueError("RWF evaluation has byte-identical overlap with the crowd development manifest")
    out.mkdir(parents=True)
    shutil.copy2(model_path, out / "model.pt")
    (out / "weights").mkdir()
    shutil.copy2(weights, out / "weights" / weights.name)
    write_manifest(out / "manifest.csv", rows)
    snapshot = out / "implementation_snapshot"
    (snapshot / "affective").mkdir(parents=True)
    (snapshot / "scripts").mkdir()
    for module in (ROOT / "affective").glob("*.py"):
        shutil.copy2(module, snapshot / "affective" / module.name)
    shutil.copy2(Path(__file__), snapshot / "scripts" / Path(__file__).name)
    protocol = {"date": date, "model": "source-corrected crowd combined_seed42", "source": str(source),
                "threshold": checkpoint["threshold"], "variant": checkpoint["variant"], "seed": checkpoint["seed"],
                "use_coverage": checkpoint.get("use_coverage", True), "clips": len(rows),
                "class_counts": dict(Counter(str(row["label"]) for row in rows)), "pose_settings": settings,
                "manifest_sha256": digest(out / "manifest.csv"), "model_sha256": digest(out / "model.pt"),
                "weights_sha256": digest(out / "weights" / weights.name),
                "previously_inspected_ids": [row["id"] for row in rows if row["sha256"] in inspected],
                "duplicate_video_hashes": {value: count for value, count in Counter(row["sha256"] for row in rows).items() if count > 1},
                "byte_overlap_with_crowd_manifest": byte_overlaps,
                "source_artifacts_sha256": {str(path): digest(path) for path in (model_path, source / "manifest.csv", source / "pose_settings.json")},
                "implementation_sha256": {name: digest(ROOT / "affective" / name) for name in MODULES},
                "script_sha256": digest(Path(__file__)), "limitations": LIMITS}
    write_json(out / "protocol.json", protocol)
    (out / "run_snapshot.py").write_text(
        'import sys\nfrom pathlib import Path\nexperiment = Path(__file__).resolve().parent\n'
        'sys.path.insert(0, str(experiment / "implementation_snapshot"))\n'
        'from scripts.evaluate_rwf_transfer import main\n'
        'sys.argv = [sys.argv[0], "--root", str(experiment.parents[1]), "--out", str(experiment), *sys.argv[1:]]\nmain()\n',
        encoding="utf-8")
    print(f"Frozen transfer plan: {len(rows)} clips, threshold {checkpoint['threshold']}, no RWF fitting", flush=True)
    return protocol


def validate_transfer(root, out):
    protocol = json.loads((out / "protocol.json").read_text(encoding="utf-8"))
    for path, expected in ((out / "manifest.csv", protocol["manifest_sha256"]),
                           (out / "model.pt", protocol["model_sha256"]),
                           (out / "weights" / protocol["pose_settings"]["weights"], protocol["weights_sha256"]),
                           (Path(__file__), protocol["script_sha256"])):
        if digest(path) != expected:
            raise ValueError(f"Frozen transfer artifact changed: {path}")
    for name, expected in protocol["implementation_sha256"].items():
        if digest(ROOT / "affective" / name) != expected:
            raise ValueError(f"Transfer implementation changed: {name}; use the snapshot")
    for path, expected in protocol["source_artifacts_sha256"].items():
        if digest(Path(path)) != expected:
            raise ValueError("Original crowd source artifact changed")
    rows = read_manifest(out / "manifest.csv")
    if len(rows) != protocol["clips"]:
        raise ValueError("Transfer manifest coverage changed")
    for row in rows:
        if digest(root / row["path"]) != row["sha256"]:
            raise ValueError(f"Evaluation video changed: {row['path']}")
    return protocol, rows


def normalize_saved(features, mask, checkpoint):
    return (np.clip((features - checkpoint["mean"].numpy()) / checkpoint["std"].numpy(), -10, 10)
            * mask[..., None]).astype(np.float32)


def run_transfer(root, out, device="cuda"):
    root, out = Path(root).resolve(), Path(out).resolve()
    protocol, rows = validate_transfer(root, out)
    marker = out / "evaluation_complete.json"
    if marker.exists():
        saved = json.loads(marker.read_text(encoding="utf-8"))
        if saved["protocol_sha256"] != digest(out / "protocol.json") or any(digest(out / name) != expected for name, expected in saved["artifacts"].items()):
            raise ValueError("Completed transfer evaluation changed")
        print("Verified completed one-time evaluation; no new inference performed", flush=True)
        return json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    torch.set_num_threads(4)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    settings = protocol["pose_settings"]
    started = time.perf_counter()
    extract(root, out, out / "weights" / settings["weights"], device=settings["device"],
            frames=settings["frames"], max_people=settings["max_people"], image_size=settings["image_size"], batch=settings["batch_size"])
    actual_settings = json.loads((out / "pose_settings.json").read_text(encoding="utf-8"))
    if actual_settings["signature"] != settings["signature"]:
        raise ValueError("Fresh RWF extraction settings differ from the trained model")
    model, checkpoint = load_model(out / "model.pt")
    if checkpoint["threshold"] != protocol["threshold"] or checkpoint.get("use_coverage", True) != protocol["use_coverage"]:
        raise ValueError("Frozen classifier setting changed")
    model.to(device)
    features, masks, quality, cache_hashes = [], [], [], {}
    feature_started = time.perf_counter()
    for row in rows:
        path = out / "cache" / f"{row['id']}.npz"
        with np.load(path, allow_pickle=False) as cache:
            if str(cache["signature"]) != checkpoint["pose_signature"] or str(cache["source_sha256"]) != row["sha256"]:
                raise ValueError("RWF pose cache provenance mismatch")
            x, mask = build_features(cache["keypoints"], cache["boxes"], cache["present"], cache["times"], *VARIANTS[checkpoint["variant"]])
            report = json.loads(str(cache["quality"]))
        features.append(normalize_saved(x, mask, checkpoint))
        masks.append(mask)
        quality.append(report)
        cache_hashes[f"cache/{row['id']}.npz"] = digest(path)
    parts = {"x": np.array(features), "mask": np.array(masks), "y": np.array([row["label"] for row in rows])}
    feature_seconds = time.perf_counter() - feature_started
    if device.startswith("cuda"):
        torch.cuda.synchronize()
    score_started = time.perf_counter()
    scores = predict(model, parts, device)
    if device.startswith("cuda"):
        torch.cuda.synchronize()
    score_seconds = time.perf_counter() - score_started
    if not np.isfinite(scores).all() or len(scores) != protocol["clips"]:
        raise ValueError("Incomplete or non-finite transfer predictions")
    seen = np.array([row["id"] in protocol["previously_inspected_ids"] for row in rows])
    abstain = np.array([report["usable_pose_fraction"] < .25 for report in quality])
    threshold = checkpoint["threshold"]
    results = {"date": protocol["date"], "model": protocol["model"], "threshold": threshold,
               "primary_all_released_clips": metrics(parts["y"], scores, threshold),
               "excluding_known_prior_demo": metrics(parts["y"][~seen], scores[~seen], threshold) if (~seen).any() else None,
               "previously_inspected_clips": int(seen.sum()), "low_pose_clips": int(abstain.sum()),
               "pose_supported_coverage": float((~abstain).mean()),
               "pose_supported_subset": metrics(parts["y"][~abstain], scores[~abstain], threshold) if (~abstain).any() else None,
               "device": device, "feature_cache_load_and_normalization_seconds": feature_seconds,
               "classifier_pass_seconds": score_seconds, "evaluation_wall_seconds": time.perf_counter() - started,
               "runtime_boundary": "Fresh full-video decode and sampled pose extraction, cache writes/loads, fixed feature normalization and GPU classification. "
                                   "Includes model initialization; excludes inventory preparation and report generation. Not a cold/warm per-video latency benchmark.",
               "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None, "limitations": protocol["limitations"]}
    predictions = [{**{key: row[key] for key in ("id", "path", "sha256", "label")}, "score": float(score),
                    "prediction": int(score >= threshold), "threshold": threshold,
                    "usable_pose_fraction": report["usable_pose_fraction"], "demo_abstain": bool(reject),
                    "known_prior_demo": bool(prior), "decoded_frames": report["decoded_frames"]}
                   for row, score, report, reject, prior in zip(rows, scores, quality, abstain, seen)]
    with (out / "predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)
    write_json(out / "metrics.json", results)
    with (out / "predictions.csv").open(encoding="utf-8", newline="") as stream:
        saved_rows = list(csv.DictReader(stream))
    if [(row["id"], int(row["label"])) for row in saved_rows] != [(row["id"], row["label"]) for row in rows]:
        raise ValueError("Saved transfer predictions do not cover the evaluation manifest")
    reproduced = metrics(np.array([int(row["label"]) for row in saved_rows]), np.array([float(row["score"]) for row in saved_rows]), threshold)
    if reproduced != results["primary_all_released_clips"]:
        raise ValueError("Transfer metrics do not reproduce from saved prediction scores")
    write_json(out / "audit.json", {"status": "pass", "clips": len(rows), "source_and_cache_hashes_verified": True,
               "frozen_model_and_threshold_verified": True, "training_normalization_reused": True,
               "rwf_fitting_performed": False, "all_clips_fully_decoded": True,
               "header_decode_mismatches": [row["id"] for row, report in zip(rows, quality) if not report["full_decode_matches_header"]],
               "metrics_reproduced_from_saved_scores": True,
               "cache_sha256": cache_hashes, "limitations": protocol["limitations"]})
    write_report(out, protocol, results)
    artifact_names = ("model.pt", "manifest.csv", "pose_settings.json", "pose_quality.json", "predictions.csv", "metrics.json", "audit.json", "RESULTS.md", "index.html", "figures/transfer.png")
    write_json(marker, {"protocol_sha256": digest(out / "protocol.json"),
                        "artifacts": {**cache_hashes, **{name: digest(out / name) for name in artifact_names}}})
    print(json.dumps(results, indent=2), flush=True)
    return results


def write_report(out, protocol, result):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    primary = result["primary_all_released_clips"]
    matrix = np.array(primary["confusion_matrix"])
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.imshow(matrix, cmap="Blues", vmin=0)
    for (y, x), value in np.ndenumerate(matrix):
        ax.text(x, y, str(value), ha="center", va="center", fontsize=20, color="white" if value > matrix.max()/2 else "#17232d")
    ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["NonFight", "Fight"], yticklabels=["NonFight", "Fight"],
           xlabel="Predicted", ylabel="Dataset label", title=f"Crowd-model transfer: {primary['n']} RWF clips")
    fig.tight_layout()
    (out / "figures").mkdir(exist_ok=True)
    fig.savefig(out / "figures" / "transfer.png", dpi=200)
    plt.close(fig)
    table = []
    for label, value in (("All released evaluation clips", primary),
                         ("Excluding known prior demo", result["excluding_known_prior_demo"]),
                         ("Pose-supported subset (secondary)", result["pose_supported_subset"])):
        if value:
            table.append([label, str(value["n"]), f"{value['accuracy']:.1%}", f"{value['macro_f1']:.3f}",
                          f"{value['roc_auc']:.3f}" if value["roc_auc"] is not None else "unavailable"])
    headings = ["Evaluation", "Clips", "Accuracy", "Macro-F1", "ROC-AUC"]
    lines = ["# One-time RWF-2000 transfer evaluation", "", f"Recorded {protocol['date']}.", "",
             f"Saved model: {protocol['model']}. Frozen threshold: {protocol['threshold']}. Device: {result['device']}.", "",
             "| " + " | ".join(headings) + " |", "|---|---:|---:|---:|---:|",
             *("| " + " | ".join(row) + " |" for row in table), "",
             f"Violent precision: {primary['precision_violent']:.3f}; recall: {primary['recall_violent']:.3f}. "
             f"Low-pose clips: {result['low_pose_clips']}; pose-supported coverage: {result['pose_supported_coverage']:.1%}.", "",
             f"Evaluation wall time: {result['evaluation_wall_seconds']/60:.2f} minutes. " + result["runtime_boundary"], "",
             protocol["limitations"], "",
             "All 400 released clips are retained in the primary real-data result. The pose-supported subset is secondary and selected by the pre-existing 25% usable-pose rule.", "",
             "![Transfer confusion matrix](figures/transfer.png)", "",
             "[Predictions](predictions.csv) | [Metrics](metrics.json) | [Audit](audit.json) | [Frozen protocol](protocol.json)", ""]
    (out / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    table_html = "<tr>" + "".join(f"<th>{html.escape(value)}</th>" for value in headings) + "</tr>"
    table_html += "".join("<tr>" + "".join(f"<td>{html.escape(value)}</td>" for value in row) + "</tr>" for row in table)
    page = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>One-time RWF transfer evaluation</title><style>body{{font:16px system-ui;background:#f3f5f7;color:#17232d;margin:0}}
main{{max-width:1080px;margin:35px auto;padding:30px;background:white;border-radius:12px}}p{{line-height:1.6}}
table{{border-collapse:collapse;width:100%}}td,th{{padding:12px;border-bottom:1px solid #ddd;text-align:left}}
.scroll{{overflow:auto}}.note{{padding:16px;background:#fff4da}}img{{max-width:100%}}a{{color:#086b86}}</style></head>
<body><main><p>{html.escape(protocol['date'])}</p><h1>One-time RWF-2000 transfer evaluation</h1>
<p>The saved combined crowd model was evaluated with its fixed threshold {protocol['threshold']} on the released RWF evaluation split.
Its crowd-training normalization is reused. One known earlier demo clip is also excluded in a supplementary result.</p>
<div class="scroll"><table>{table_html}</table></div><p>Fight precision: {primary['precision_violent']:.3f}; recall: {primary['recall_violent']:.3f}.
Low-pose clips: {result['low_pose_clips']}. All clips remain in primary metrics.</p>
<img src="figures/transfer.png" alt="Transfer classification confusion matrix"><p class="note">{html.escape(protocol['limitations'])}</p>
<p>Evaluation wall time: {result['evaluation_wall_seconds']/60:.2f} minutes. {html.escape(result['runtime_boundary'])}</p>
<p><a href="RESULTS.md">Research notes</a> | <a href="predictions.csv">Predictions</a> | <a href="metrics.json">Metrics</a> |
<a href="audit.json">Audit</a> | <a href="protocol.json">Frozen protocol</a></p></main></body></html>'''
    (out / "index.html").write_text(page, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source", type=Path, default=Path("output/source_corrected"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--date", default=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d"))
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    selected_out = args.out or Path("output") / f"rwf_transfer_{args.date.replace('-', '')}"
    out = selected_out.resolve() if selected_out.is_absolute() else root / selected_out
    source = args.source.resolve() if args.source.is_absolute() else root / args.source
    if not out.exists():
        prepare_transfer(root, source, out, args.date)
    if not args.prepare_only:
        if not torch.cuda.is_available() and not (out / "evaluation_complete.json").exists():
            raise RuntimeError("This run requires the local CUDA GPU")
        run_transfer(root, out)


if __name__ == "__main__":
    main()
