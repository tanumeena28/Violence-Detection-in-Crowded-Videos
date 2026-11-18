"""Freeze, fit and verify a source-grouped supervised RWF frozen-video head."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import shutil
import sys
import time
from importlib.metadata import version
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import log_loss
from torchvision.models.video import R3D_18_Weights, r3d_18

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import digest, write_manifest
from affective.data import decode_sample, read_manifest, write_json
from affective.motion import score_linear
from affective.rwf_supervised import fit_development_head, partition_rows
from affective.train import choose_threshold, metrics

LIMITS = ("Supervised RWF development experiment with a frozen Kinetics-400 encoder and logistic head. "
          "Released training footage supplies both fitting and source-grouped validation. The 400 released "
          "evaluation clips have already been inspected/scored in earlier transfer experiments, so this "
          "is exploratory development evaluation, not an untouched test claim or direct accuracy improvement "
          "over crowd-only transfer. Source IDs and byte hashes do not rule out renamed/shared footage. "
          "Independent labels and pretraining/source overlap remain unaudited. Scores are not calibrated.")


def write_rows(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def prepare(root, inventory, baseline, evaluation_cache, out):
    if out.exists():
        raise FileExistsError("A frozen supervised plan is never overwritten")
    raw = json.loads(inventory.read_text())["rows"]
    if any(sum(r["released_partition"] == released and r["label"] == label for r in raw) != expected
           for released, expected in (("train", 800), ("val", 200)) for label in (0, 1)):
        raise ValueError("Expected complete released RWF partitions: 800/800 development and 200/200 evaluation")
    rows, source_audit = partition_rows(raw)
    encoder = json.loads((baseline / "protocol.json").read_text())
    old_eval = json.loads((evaluation_cache / "protocol.json").read_text())
    completion = json.loads((evaluation_cache / "completion.json").read_text())
    for relative, expected in completion["artifacts_sha256"].items():
        if digest(evaluation_cache / relative) != expected:
            raise ValueError("Existing video transfer artifact changed")
    test_rows = [r for r in rows if r["split"] == "test"]
    cached_manifest = read_manifest(evaluation_cache / "manifest.csv")
    if sorted((r["id"], r["sha256"], r["label"]) for r in test_rows) != sorted((r["id"], r["sha256"], r["label"]) for r in cached_manifest):
        raise ValueError("Cached evaluation embeddings refer to different clips or labels")
    if any(old_eval[key] != encoder[key] for key in ("weights_sha256", "sampling", "preprocessing")):
        raise ValueError("Cached evaluation encoder settings differ")
    weights = baseline / "weights" / encoder["weights_file"]
    if digest(weights) != encoder["weights_sha256"]:
        raise ValueError("Pretrained weights changed")
    out.mkdir(parents=True)
    write_manifest(out / "source_inventory.csv", raw)
    write_manifest(out / "manifest.csv", rows)
    write_json(out / "source_audit.json", source_audit)
    (out / "weights").mkdir()
    shutil.copy2(weights, out / "weights" / weights.name)
    # Only the fixed pretrained encoder is inherited. No crowd head is copied.
    encoder_settings = {key: encoder[key] for key in ("encoder", "weights_file", "weights_sha256", "weights_url",
        "frames", "windows", "frames_per_window", "embedding_size", "encoder_parameters", "sampling", "preprocessing")}
    protocol = {"schema": "rwf-supervised-frozen-r3d18-v1", "date": "2026-11-15", "encoder": encoder_settings,
                "encoder_signature": hashlib.sha256(json.dumps(encoder_settings, sort_keys=True).encode()).hexdigest(),
                "manifest_sha256": digest(out / "manifest.csv"), "inventory_sha256": digest(out / "source_inventory.csv"),
                "source_audit_sha256": digest(out / "source_audit.json"),
                "split": {"method": "First fold of StratifiedGroupKFold(5, shuffle=True, seed=42) used as validation; rest train",
                          "counts": source_audit["split_counts"], "groups": source_audit["source_group_counts"]},
                "regularization": [.001, .01, .1, 1., 10.], "head_solver": "lbfgs", "maximum_iterations": 2000,
                "C_selection": "Validation log loss; listed C order breaks exact ties",
                "threshold_selection": "Validation macro-F1 across 0.10 to 0.90 at 0.01 steps; nearest 0.5 breaks ties",
                "device": "cuda", "precision": "float32 encoder; float64 head", "cpu_threads": 4,
                "evaluation_cache": {"path": str(evaluation_cache), "features_sha256": digest(evaluation_cache / "features.npz"),
                    "manifest_sha256": digest(evaluation_cache / "manifest.csv"), "protocol_sha256": digest(evaluation_cache / "protocol.json")},
                "selection_boundary": "Freeze fitted head and all development artifacts before reading evaluation feature arrays or scoring test clips",
                "packages": {name: version(name) for name in ("torch", "torchvision", "numpy", "opencv-python", "scikit-learn")},
                "script_sha256": digest(Path(__file__)),
                "implementation_sha256": {p.name: digest(p) for p in (ROOT / "affective").glob("*.py")}, "limitations": LIMITS}
    write_json(out / "protocol.json", protocol)
    snapshot = out / "implementation_snapshot"
    shutil.copytree(ROOT / "affective", snapshot / "affective", ignore=shutil.ignore_patterns("__pycache__"))
    (snapshot / "scripts").mkdir()
    shutil.copy2(Path(__file__), snapshot / "scripts" / Path(__file__).name)
    (out / "run_snapshot.py").write_text(
        'import sys\nfrom pathlib import Path\ne=Path(__file__).resolve().parent\n'
        'sys.path.insert(0,str(e/"implementation_snapshot"))\n'
        'from scripts.run_rwf_supervised import main\n'
        'sys.argv=[sys.argv[0],"--out",str(e),*sys.argv[1:]]\nmain()\n', encoding="utf-8")
    return protocol


def validate(out, plan):
    if digest(Path(__file__)) != plan["script_sha256"]:
        raise ValueError("Run the frozen supervised script")
    implementation = Path(__file__).resolve().parents[1] / "affective"
    for name, expected in plan["implementation_sha256"].items():
        if digest(implementation / name) != expected:
            raise ValueError("Run the frozen supervised implementation")
    for name, key in (("manifest.csv", "manifest_sha256"), ("source_inventory.csv", "inventory_sha256"), ("source_audit.json", "source_audit_sha256")):
        if digest(out / name) != plan[key]:
            raise ValueError("Frozen supervised inputs changed")
    if digest(out / "weights" / plan["encoder"]["weights_file"]) != plan["encoder"]["weights_sha256"]:
        raise ValueError("Frozen encoder weights changed")
    for name, expected in plan["packages"].items():
        if version(name) != expected:
            raise ValueError("Use the recorded package versions")


def extract_development(root, out, plan):
    torch.set_num_threads(4)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    model = r3d_18(weights=None)
    model.load_state_dict(torch.load(out / "weights" / plan["encoder"]["weights_file"], map_location="cpu", weights_only=True))
    model.fc = torch.nn.Identity()
    model.eval().to("cuda")
    transform = R3D_18_Weights.KINETICS400_V1.transforms()
    rows = [r for r in read_manifest(out / "manifest.csv") if r["split"] in ("train", "val")]
    cache = out / "development_cache"
    cache.mkdir(exist_ok=True)
    records = []
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    for number, row in enumerate(rows, 1):
        target = cache / f"{row['id']}.npz"
        if target.exists():
            with np.load(target, allow_pickle=False) as saved:
                if str(saved["source_sha256"]) != row["sha256"] or str(saved["encoder_signature"]) != plan["encoder_signature"]:
                    raise ValueError("Development feature cache changed")
                records.append(json.loads(str(saved["record"])))
            continue
        path = root / row["path"]
        if digest(path) != row["sha256"]:
            raise ValueError("Raw development video changed")
        images, indices, fps, decoded = decode_sample(path, 32)
        rgb = torch.from_numpy(np.stack([im[..., ::-1].copy() for im in images])).permute(0, 3, 1, 2)
        tensor = torch.stack([transform(rgb[:16]), transform(rgb[16:])]).to("cuda")
        with torch.inference_mode():
            vector = model(tensor).mean(0).cpu().numpy().astype(np.float32)
        if vector.shape != (512,) or not np.isfinite(vector).all():
            raise ValueError("Invalid development embedding")
        record = {"id": row["id"], "split": row["split"], "decoded_frames": decoded,
                  "header_frames": row["frames"], "fps": fps, "duration_seconds": decoded / fps}
        temporary = target.with_suffix(".tmp.npz")
        np.savez_compressed(temporary, features=vector, frame_indices=indices, source_sha256=np.array(row["sha256"]),
                            encoder_signature=np.array(plan["encoder_signature"]), record=np.array(json.dumps(record)))
        temporary.replace(target)
        records.append(record)
        if number % 100 == 0 or number == 1:
            print(f"Development video features {number}/{len(rows)}", flush=True)
    write_json(out / "development_feature_audit.json", {"clips": records, "clips_encoded": len(records),
                "header_discrepancies": [r for r in records if r["header_frames"] != r["decoded_frames"]],
                "wall_seconds": time.perf_counter() - started, "gpu": torch.cuda.get_device_name(0),
                "peak_allocated_gpu_bytes": torch.cuda.max_memory_allocated(),
                "cache_sha256": {p.stem: digest(p) for p in sorted(cache.glob("*.npz"))}})


def development_arrays(out, plan):
    rows = [r for r in read_manifest(out / "manifest.csv") if r["split"] in ("train", "val")]
    audit = json.loads((out / "development_feature_audit.json").read_text())
    if set(audit["cache_sha256"]) != {r["id"] for r in rows}:
        raise ValueError("Incomplete development features")
    vectors = []
    for row in rows:
        path = out / "development_cache" / f"{row['id']}.npz"
        if digest(path) != audit["cache_sha256"][row["id"]]:
            raise ValueError("Development feature bytes changed")
        with np.load(path, allow_pickle=False) as saved:
            if str(saved["source_sha256"]) != row["sha256"] or str(saved["encoder_signature"]) != plan["encoder_signature"]:
                raise ValueError("Development feature provenance changed")
            vectors.append(saved["features"])
    return rows, np.asarray(vectors, np.float64)


def freeze_head(out, plan):
    rows, features = development_arrays(out, plan)
    train = np.array([r["split"] == "train" for r in rows])
    val = ~train
    labels = np.array([r["label"] for r in rows])
    checkpoint, selection = fit_development_head(features[train], labels[train], features[val], labels[val], plan["regularization"])
    if any(r["iterations"] >= plan["maximum_iterations"] for r in selection["candidates"]):
        raise ValueError("A head fit reached its iteration limit; do not evaluate this incomplete fit")
    checkpoint.update({"manifest_sha256": plan["manifest_sha256"], "feature_signature": plan["encoder_signature"],
                       "protocol_sha256": digest(out / "protocol.json")})
    write_json(out / "model.json", checkpoint)
    write_json(out / "selection.json", selection)
    scores = score_linear(features, checkpoint)
    write_rows(out / "development_predictions.csv", [{"id": r["id"], "path": r["path"], "split": r["split"],
                 "label": r["label"], "score": float(s), "prediction": int(s >= checkpoint["threshold"])} for r, s in zip(rows, scores)])
    # This seal is written before evaluation feature arrays are loaded.
    write_json(out / "head_frozen.json", {"status": "selected_before_evaluation", "protocol_sha256": digest(out / "protocol.json"),
        "artifacts_sha256": {name: digest(out / name) for name in ("model.json", "selection.json", "development_predictions.csv", "development_feature_audit.json")},
        "boundary": plan["selection_boundary"]})
    print(f"Frozen head: C={checkpoint['selected_C']}, threshold={checkpoint['threshold']:.2f}, validation accuracy={selection['validation']['accuracy']:.1%}", flush=True)


def validate_head(out):
    seal = json.loads((out / "head_frozen.json").read_text())
    if digest(out / "protocol.json") != seal["protocol_sha256"]:
        raise ValueError("Selected head protocol changed")
    for name, expected in seal["artifacts_sha256"].items():
        if digest(out / name) != expected:
            raise ValueError("Selected development artifact changed")


def evaluate(out, plan):
    validate_head(out)
    checkpoint = json.loads((out / "model.json").read_text())
    cache = Path(plan["evaluation_cache"]["path"])
    for name, key in (("features.npz", "features_sha256"), ("manifest.csv", "manifest_sha256"), ("protocol.json", "protocol_sha256")):
        if digest(cache / name) != plan["evaluation_cache"][key]:
            raise ValueError("Fixed evaluation feature corpus changed")
    rows = [r for r in read_manifest(out / "manifest.csv") if r["split"] == "test"]
    with np.load(cache / "features.npz", allow_pickle=False) as saved:
        by_id = {clip_id: vector for clip_id, vector in zip(saved["ids"].tolist(), saved["features"])}
    features = np.array([by_id[r["id"]] for r in rows], dtype=np.float64)
    scores = score_linear(features, checkpoint)
    predictions = [{"id": r["id"], "path": r["path"], "split": "test", "label": r["label"], "score": float(s),
                    "prediction": int(s >= checkpoint["threshold"])} for r, s in zip(rows, scores)]
    write_rows(out / "evaluation_predictions.csv", predictions)
    selection = json.loads((out / "selection.json").read_text())
    result = {"status": "complete", "model": checkpoint["name"], "train": selection["train"],
              "validation": selection["validation"], "test": metrics([r["label"] for r in rows], scores, checkpoint["threshold"]),
              "threshold": checkpoint["threshold"], "selected_C": checkpoint["selected_C"],
              "train_clips": selection["train"]["n"], "val_clips": selection["validation"]["n"], "test_clips": len(rows),
              "head_frozen_before_evaluation": True, "encoder_frozen": True, "limitations": LIMITS}
    write_json(out / "metrics.json", result)
    validate_head(out)
    return result


def verify(out, plan):
    validate_head(out)
    checkpoint = json.loads((out / "model.json").read_text())
    selection = json.loads((out / "selection.json").read_text())
    rows, features = development_arrays(out, plan)
    labels = np.array([r["label"] for r in rows])
    train = np.array([r["split"] == "train" for r in rows])
    val = ~train
    np.testing.assert_allclose(checkpoint["mean"], features[train].mean(0), atol=1e-12, rtol=0)
    np.testing.assert_allclose(checkpoint["std"], np.maximum(features[train].std(0), .01), atol=1e-12, rtol=0)
    scores = score_linear(features, checkpoint)
    with (out / "development_predictions.csv").open(newline="") as stream:
        saved = list(csv.DictReader(stream))
    if [(r["id"], int(r["label"]), r["split"]) for r in saved] != [(r["id"], r["label"], r["split"]) for r in rows]:
        raise ValueError("Development predictions changed order or labels")
    np.testing.assert_allclose(scores, [float(r["score"]) for r in saved], atol=1e-12, rtol=0)
    np.testing.assert_array_equal(scores >= checkpoint["threshold"], [int(r["prediction"]) for r in saved])
    if choose_threshold(labels[val], scores[val]) != checkpoint["threshold"]:
        raise ValueError("Threshold differs from validation choice")
    chosen = min(selection["candidates"], key=lambda r: r["validation_log_loss"])
    if chosen["C"] != checkpoint["selected_C"] or abs(chosen["validation_log_loss"] - log_loss(labels[val], scores[val])) > 1e-10:
        raise ValueError("Selected C record differs from validation scores")
    for split, mask in (("train", train), ("validation", val)):
        if metrics(labels[mask], scores[mask], checkpoint["threshold"]) != selection[split]:
            raise ValueError("Development metrics do not reproduce")
    cache = Path(plan["evaluation_cache"]["path"])
    if digest(cache / "features.npz") != plan["evaluation_cache"]["features_sha256"]:
        raise ValueError("Evaluation feature bytes changed")
    test_rows = [r for r in read_manifest(out / "manifest.csv") if r["split"] == "test"]
    with np.load(cache / "features.npz", allow_pickle=False) as saved:
        by_id = dict(zip(saved["ids"].tolist(), saved["features"]))
    scores = score_linear(np.array([by_id[r["id"]] for r in test_rows]), checkpoint)
    with (out / "evaluation_predictions.csv").open(newline="") as stream:
        saved = list(csv.DictReader(stream))
    if [(r["id"], int(r["label"])) for r in saved] != [(r["id"], r["label"]) for r in test_rows]:
        raise ValueError("Evaluation labels/order changed")
    np.testing.assert_allclose(scores, [float(r["score"]) for r in saved], atol=1e-12, rtol=0)
    np.testing.assert_array_equal(scores >= checkpoint["threshold"], [int(r["prediction"]) for r in saved])
    result = json.loads((out / "metrics.json").read_text())
    if metrics([r["label"] for r in test_rows], scores, checkpoint["threshold"]) != result["test"]:
        raise ValueError("Evaluation metrics do not reproduce")
    if len(test_rows) != 400 or len({r["id"] for r in test_rows}) != 400:
        raise ValueError("All 400 released evaluation clips must remain included")
    audit = {"status": "pass", "development_caches_verified": len(rows), "evaluation_clips_verified": len(test_rows),
             "source_groups_disjoint": True, "train_only_scaling_verified": True,
             "validation_threshold_and_selected_C_record_verified": True, "scores_and_decisions_reproduced": True,
             "head_seal_unchanged_after_evaluation": True, "verification": "Saved features and head; no fitting or GPU extraction"}
    write_json(out / "audit.json", audit)
    return result


def report(out, result):
    rows = "\n".join(f"| {split} | {result[key]['n']} | {result[key]['accuracy']:.1%} | {result[key]['macro_f1']:.3f} | {result[key]['roc_auc']:.3f} |"
                     for split, key in (("Training", "train"), ("Validation", "validation"), ("Released evaluation", "test")))
    notes = "# Supervised RWF frozen-video reference\n\nFrozen Kinetics-400 R3D-18 encoder, two 16-frame windows, fresh logistic head. Source-grouped validation comes only from released training footage.\n\n| Partition | Clips | Accuracy | Macro-F1 | AUC |\n|---|---:|---:|---:|---:|\n" + rows + f"\n\nSelected C: {result['selected_C']}; validation-selected threshold: {result['threshold']:.2f}. The head was sealed before evaluation features were loaded.\n\n" + LIMITS + "\n\n[Protocol](protocol.json) | [Source audit](source_audit.json) | [Fit selection](selection.json) | [Verification](audit.json) | [Metrics](metrics.json)\n"
    (out / "RESULTS.md").write_text(notes, encoding="utf-8")
    (out / "index.html").write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Supervised RWF experiment</title><style>body{font:17px system-ui;max-width:1050px;margin:35px auto;padding:20px;line-height:1.6}pre{white-space:pre-wrap}a{color:#087f8c}</style><h1>Supervised RWF frozen-video reference</h1><pre>' + html.escape(notes) + '</pre><p><a href="protocol.json">Frozen protocol</a> | <a href="source_audit.json">Source audit</a> | <a href="metrics.json">Metrics</a> | <a href="audit.json">Verification</a></p>', encoding="utf-8")
    print(notes, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--inventory", type=Path, default=Path("tmp/rwf_inventory_20261115.json"))
    parser.add_argument("--baseline", type=Path, default=Path("output/video_baseline_v2_20261115"))
    parser.add_argument("--evaluation-cache", type=Path, default=Path("output/video_transfer_20261115"))
    parser.add_argument("--out", type=Path, default=Path("output/rwf_supervised_20261115"))
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    plan = json.loads((out / "protocol.json").read_text()) if out.exists() else prepare(root, args.inventory.resolve(), args.baseline.resolve(), args.evaluation_cache.resolve(), out)
    validate(out, plan)
    completion = out / "completion.json"
    if completion.exists():
        for relative, expected in json.loads(completion.read_text())["artifacts_sha256"].items():
            if digest(out / relative) != expected:
                raise ValueError("Completed supervised artifact changed")
        report(out, verify(out, plan))
        return
    if args.prepare_only:
        print(json.dumps(plan["split"], indent=2), flush=True)
        return
    if not args.verify_only:
        if not (out / "head_frozen.json").exists():
            extract_development(root, out, plan)
            freeze_head(out, plan)
        if not (out / "metrics.json").exists():
            evaluate(out, plan)
    result = verify(out, plan)
    report(out, result)
    files = [out / name for name in ("protocol.json", "manifest.csv", "source_inventory.csv", "source_audit.json", "model.json", "selection.json", "head_frozen.json", "development_predictions.csv", "development_feature_audit.json", "evaluation_predictions.csv", "metrics.json")]
    write_json(completion, {"status": "complete", "artifacts_sha256": {p.relative_to(out).as_posix(): digest(p) for p in files}})


if __name__ == "__main__":
    main()
