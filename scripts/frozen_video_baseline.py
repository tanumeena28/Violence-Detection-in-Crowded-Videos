"""Frozen Kinetics R3D-18 features and source-grouped crowd logistic heads."""
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
from torchvision.models.video import R3D_18_Weights, r3d_18

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import digest, validate_plan
from affective.data import decode_sample, read_manifest, write_json
from affective.motion import fit_control, score_linear
from affective.train import choose_threshold, metrics

NAME = "rgb_r3d18_frozen"
LIMITS = ("Exploratory crowd evaluation on previously inspected footage. Frozen Kinetics-400 pretraining, "
          "two uniformly sampled 16-frame windows and a logistic head; no encoder fine-tuning. "
          "This is a pretrained video reference, not reproduction of a published violence benchmark. "
          "Pretraining/source overlap has not been audited. Fold SD is descriptive; the folds are dependent. "
          "This experiment does not measure RWF transfer or establish independent label correctness.")


def write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def prepare(source, out):
    if out.exists():
        return json.loads((out / "protocol.json").read_text(encoding="utf-8"))
    plan = validate_plan(source, source / "implementation_snapshot" / "affective")
    decode_reference = {}
    for row in read_manifest(source / "assignments.csv"):
        with np.load(source / "cache" / f"{row['id']}.npz", allow_pickle=False) as saved:
            quality = json.loads(str(saved["quality"]))
            decode_reference[row["id"]] = {"decoded_frames": quality["decoded_frames"],
                                          "frame_indices": saved["frame_indices"].tolist()}
    weights = R3D_18_Weights.KINETICS400_V1
    weights.get_state_dict(progress=False, check_hash=True)
    downloaded = Path(torch.hub.get_dir()) / "checkpoints" / Path(weights.url).name
    parameter_model = r3d_18(weights=None)
    encoder_parameters = sum(p.numel() for p in parameter_model.parameters()) - sum(p.numel() for p in parameter_model.fc.parameters())
    out.mkdir(parents=True)
    shutil.copy2(source / "assignments.csv", out / "assignments.csv")
    for fold in range(1, plan["settings"]["folds"] + 1):
        folder = out / f"fold_{fold}"
        folder.mkdir()
        shutil.copy2(source / f"fold_{fold}" / "manifest.csv", folder / "manifest.csv")
    (out / "weights").mkdir()
    shutil.copy2(downloaded, out / "weights" / downloaded.name)
    protocol = {"schema": "frozen-r3d18-crowd-v1", "source": str(source),
                "source_protocol_sha256": digest(source / "protocol.json"),
                "assignments_sha256": digest(out / "assignments.csv"),
                "partitions": plan["partitions"], "clips": plan["clips"], "source_groups": plan["source_groups"],
                "encoder": "torchvision R3D-18 KINETICS400_V1", "weights_url": weights.url,
                "weights_file": downloaded.name, "weights_sha256": digest(downloaded),
                "frames": 32, "windows": 2, "frames_per_window": 16, "embedding_size": 512,
                "encoder_parameters": encoder_parameters,
                "preprocessing": "Official weights transform: RGB, resize [128,171], center crop [112,112], mean [0.43216,0.394666,0.37645], std [0.22803,0.22145,0.216989]",
                "sampling": "Uniform 32-frame whole-clip samples; two chronological nonoverlapping 16-frame windows; average pooled encoder vectors",
                "decode_reference": decode_reference,
                "decode_policy": "Match prior full pose-cache decodes and sampled frame indices; record header discrepancies without removing clips",
                "regularization": [.01, .1, 1., 10.], "device": "cuda", "precision": "float32",
                "packages": {name: version(name) for name in ("torch", "torchvision", "numpy", "opencv-python", "scikit-learn")},
                "script_sha256": digest(Path(__file__)), "limitations": LIMITS}
    snapshot = out / "implementation_snapshot"
    (snapshot / "scripts").mkdir(parents=True)
    shutil.copytree(ROOT / "affective", snapshot / "affective", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(Path(__file__), snapshot / "scripts" / Path(__file__).name)
    protocol["implementation_sha256"] = {p.name: digest(p) for p in (ROOT / "affective").glob("*.py")}
    write_json(out / "protocol.json", protocol)
    (out / "run_snapshot.py").write_text(
        'import sys\nfrom pathlib import Path\ne=Path(__file__).resolve().parent\n'
        'sys.path.insert(0,str(e/"implementation_snapshot"))\n'
        'from scripts.frozen_video_baseline import main\n'
        'sys.argv=[sys.argv[0],"--out",str(e),*sys.argv[1:]]\nmain()\n', encoding="utf-8")
    return protocol


def validate(out, protocol):
    if digest(Path(__file__)) != protocol["script_sha256"]:
        raise ValueError("Use the frozen baseline script")
    if digest(out / "assignments.csv") != protocol["assignments_sha256"]:
        raise ValueError("Baseline assignments changed")
    for partition in protocol["partitions"]:
        if digest(out / f"fold_{partition['fold']}" / "manifest.csv") != partition["manifest_sha256"]:
            raise ValueError("Baseline fold manifest changed")
    if digest(out / "weights" / protocol["weights_file"]) != protocol["weights_sha256"]:
        raise ValueError("Pretrained encoder weights changed")
    implementation = Path(__file__).resolve().parents[1] / "affective"
    for name, expected in protocol["implementation_sha256"].items():
        if digest(implementation / name) != expected:
            raise ValueError("Use the frozen baseline implementation")


def extract(root, out, protocol):
    torch.set_num_threads(4)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    model = r3d_18(weights=None)
    model.load_state_dict(torch.load(out / "weights" / protocol["weights_file"], map_location="cpu", weights_only=True))
    model.fc = torch.nn.Identity()
    model.eval().to("cuda")
    transform = R3D_18_Weights.KINETICS400_V1.transforms()
    cache = out / "cache"
    cache.mkdir(exist_ok=True)
    fingerprint = digest(out / "protocol.json")
    records = []
    torch.cuda.reset_peak_memory_stats()
    for number, row in enumerate(read_manifest(out / "assignments.csv"), 1):
        target = cache / f"{row['id']}.npz"
        if target.exists():
            with np.load(target, allow_pickle=False) as saved:
                if str(saved["protocol_sha256"]) != fingerprint or str(saved["source_sha256"]) != row["sha256"]:
                    raise ValueError("Incompatible video feature cache")
                records.append(json.loads(str(saved["record"])))
            continue
        path = root / row["path"]
        if digest(path) != row["sha256"]:
            raise ValueError("Video changed since source manifest")
        started = time.perf_counter()
        images, indices, fps, decoded = decode_sample(path, 32)
        reference = protocol["decode_reference"][row["id"]]
        if decoded != reference["decoded_frames"] or indices.tolist() != reference["frame_indices"]:
            raise ValueError("Video sampling differs from the prior full pose-cache decode")
        rgb = torch.from_numpy(np.stack([frame[..., ::-1].copy() for frame in images])).permute(0, 3, 1, 2)
        tensor = torch.stack([transform(rgb[:16]), transform(rgb[16:])]).to("cuda")
        with torch.inference_mode():
            vector = model(tensor).mean(0).cpu().numpy().astype(np.float32)
        torch.cuda.synchronize()
        if vector.shape != (512,) or not np.isfinite(vector).all():
            raise ValueError("Invalid video embedding")
        record = {"id": row["id"], "decoded_frames": decoded, "header_frames": row["frames"],
                  "seconds_decode_transform_encoder": time.perf_counter() - started}
        temporary = target.with_suffix(".tmp.npz")
        np.savez_compressed(temporary, features=vector, frame_indices=indices,
                            source_sha256=np.array(row["sha256"]), protocol_sha256=np.array(fingerprint),
                            record=np.array(json.dumps(record)))
        temporary.replace(target)
        records.append(record)
        if number % 10 == 0 or number == 1:
            print(f"Video features {number}/{protocol['clips']}", flush=True)
    write_json(out / "feature_audit.json", {"clips": records, "full_decodes_match_pose_cache_reference": True,
                "header_discrepancy_clips": sum(r["decoded_frames"] != r["header_frames"] for r in records),
                "peak_allocated_gpu_bytes": torch.cuda.max_memory_allocated(), "device": torch.cuda.get_device_name(0),
                "cache_sha256": {p.stem: digest(p) for p in sorted(cache.glob("*.npz"))}})


def fit_and_verify(out, protocol, fit):
    cache_audit = json.loads((out / "feature_audit.json").read_text(encoding="utf-8"))
    for clip_id, expected in cache_audit["cache_sha256"].items():
        if digest(out / "cache" / f"{clip_id}.npz") != expected:
            raise ValueError("Video embedding changed")
    results, audits, pooled = [], [], []
    signature = digest(out / "protocol.json")
    for partition in protocol["partitions"]:
        fold = partition["fold"]
        folder = out / f"fold_{fold}"
        rows = read_manifest(folder / "manifest.csv")
        vectors = []
        for row in rows:
            with np.load(out / "cache" / f"{row['id']}.npz", allow_pickle=False) as saved:
                if str(saved["source_sha256"]) != row["sha256"] or str(saved["protocol_sha256"]) != signature:
                    raise ValueError("Video embedding provenance mismatch")
                vectors.append(saved["features"])
        features = np.array(vectors, dtype=np.float64)
        run = folder / "motion" / NAME
        if fit and not (run / "model.json").exists():
            fit_control(folder, rows, features, NAME, signature, protocol["regularization"],
                        protocol="Same source-grouped crowd folds. Train-only scaling and logistic head; validation log-loss selects C and macro-F1 selects threshold. Frozen pretrained encoder.")
            result = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
            result["limitations"] = LIMITS
            result["encoder_parameters"] = protocol["encoder_parameters"]
            write_json(run / "metrics.json", result)
        checkpoint = json.loads((run / "model.json").read_text(encoding="utf-8"))
        result = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
        labels = np.array([row["label"] for row in rows])
        train = np.array([row["split"] == "train" for row in rows])
        val = np.array([row["split"] == "val" for row in rows])
        np.testing.assert_allclose(checkpoint["mean"], features[train].mean(0), atol=1e-12, rtol=0)
        np.testing.assert_allclose(checkpoint["std"], np.maximum(features[train].std(0), .01), atol=1e-12, rtol=0)
        scores = score_linear(features, checkpoint)
        saved = read_rows(run / "predictions.csv")
        if [(r["id"], int(r["label"]), r["split"]) for r in saved] != [(r["id"], r["label"], r["split"]) for r in rows]:
            raise ValueError("Saved video predictions differ from manifest")
        np.testing.assert_allclose(scores, [float(r["score"]) for r in saved], atol=1e-10, rtol=0)
        np.testing.assert_array_equal(scores >= checkpoint["threshold"], [int(r["prediction"]) for r in saved])
        if choose_threshold(labels[val], scores[val]) != checkpoint["threshold"]:
            raise ValueError("Video threshold does not reproduce from validation")
        if min(result["candidates"], key=lambda r: r["validation_log_loss"])["C"] != checkpoint["selected_C"]:
            raise ValueError("Video regularization does not reproduce from validation records")
        for split, key in (("train", "train"), ("val", "validation"), ("test", "test")):
            mask = np.array([row["split"] == split for row in rows])
            if metrics(labels[mask], scores[mask], checkpoint["threshold"]) != result[key]:
                raise ValueError("Video metrics do not reproduce")
        result["fold"] = fold
        results.append(result)
        audits.append({"fold": fold, "normalization_verified": True, "scores_and_decisions_reproduced": True,
                       "validation_choices_verified": True, "artifacts_sha256": {p.name: digest(p) for p in run.glob("*") if p.is_file()}})
        pooled.extend({"fold": fold, **r} for r in saved if r["split"] == "test")
    if len(pooled) != protocol["clips"] or len({r["id"] for r in pooled}) != protocol["clips"]:
        raise ValueError("Video out-of-fold predictions must cover every clip exactly once")
    names = ("accuracy", "macro_f1", "roc_auc", "precision_violent", "recall_violent")
    summary = {"status": "complete", "model": NAME, "clips": protocol["clips"], "source_groups": protocol["source_groups"],
               "folds": len(results), "fold_mean": {name: {"mean": float(np.mean([r["test"][name] for r in results])),
                    "descriptive_std": float(np.std([r["test"][name] for r in results], ddof=1))} for name in names},
               "runs": results, "limitations": LIMITS}
    write_rows(out / "out_of_fold_predictions.csv", pooled)
    write_json(out / "summary.json", summary)
    write_json(out / "audit.json", {"status": "pass", "feature_caches_verified": protocol["clips"], "heads_verified": audits})
    table = "| Metric | Fold mean | Descriptive SD |\n|---|---:|---:|\n" + "\n".join(
        f"| {name} | {summary['fold_mean'][name]['mean']:.4f} | {summary['fold_mean'][name]['descriptive_std']:.4f} |" for name in names)
    notes = "# Frozen pretrained video reference\n\n" + protocol["sampling"] + ".\n\n" + table + "\n\n" + LIMITS + f"\n\nAll {protocol['clips']} feature caches and {len(results)} logistic heads are verified. Full decodes and sampled frame indices match the prior pose-cache reference. {cache_audit['header_discrepancy_clips']} clips have header-count discrepancies; all remain included.\n"
    (out / "RESULTS.md").write_text(notes, encoding="utf-8")
    (out / "index.html").write_text('<!doctype html><meta charset="utf-8"><title>Frozen video baseline</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;padding:20px;line-height:1.6}pre{white-space:pre-wrap}</style><h1>Frozen pretrained video reference</h1><pre>' + html.escape(notes) + '</pre><p><a href="summary.json">Summary</a> | <a href="audit.json">Verification</a> | <a href="protocol.json">Protocol</a></p>', encoding="utf-8")
    print(json.dumps(summary["fold_mean"], indent=2), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path, default=Path("output/centering_corrected_cpu_20261115"))
    parser.add_argument("--out", type=Path, default=Path("output/video_baseline_20261115"))
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    root, source, out = args.root.resolve(), args.source.resolve(), args.out.resolve()
    protocol = prepare(source, out)
    validate(out, protocol)
    completion = out / "completion.json"
    if completion.exists():
        for relative, expected in json.loads(completion.read_text())["artifacts_sha256"].items():
            if digest(out / relative) != expected:
                raise ValueError(f"Completed baseline artifact changed: {relative}")
    if not args.verify_only and not completion.exists():
        extract(root, out, protocol)
    fit_and_verify(out, protocol, fit=not args.verify_only and not completion.exists())
    if not completion.exists():
        paths = [out / "protocol.json", out / "feature_audit.json", out / "assignments.csv",
                 *out.glob("fold_*/manifest.csv"), *out.glob("fold_*/motion/*/*.json"),
                 *out.glob("fold_*/motion/*/*.csv")]
        write_json(completion, {"status": "complete", "artifacts_sha256": {p.relative_to(out).as_posix(): digest(p) for p in paths}})


if __name__ == "__main__":
    main()
