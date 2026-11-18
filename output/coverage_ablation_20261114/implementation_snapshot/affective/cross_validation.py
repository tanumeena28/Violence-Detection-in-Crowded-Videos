"""Frozen source-grouped folds using portable, immutable per-video caches."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from importlib.metadata import version
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

from .data import canonicalize_source_groups, read_manifest, write_json
from .motion import CONTROL_CONFIG, QUALITY_NAMES, fit_control, load_cached_motion, quality_features
from .train import VARIANTS, train_one

PROTOCOL = (
    "Custom stratified source-grouped outer folds with the preceding fold used "
    "for validation and remaining folds for training. Training-only normalization; "
    "validation-selected checkpoints and thresholds. Existing videos have been "
    "inspected previously: exploratory repeated evaluation, not a fresh untouched "
    "test or reproduction of the dataset's supplied five-fold protocol. "
    "Filename grouping does not replace full-video source/label review."
)
CONTROL_PROTOCOL = PROTOCOL + (
    " Linear controls use training-only scaling and fitting; validation log loss "
    "selects motion regularization and validation macro-F1 selects thresholds. "
    "Each deterministic control is fitted once per fold, not repeated per TCN seed."
)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_manifest(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def atomic_json(path, value):
    # Other fold jobs must never see a partially written completion marker.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     suffix=".tmp", delete=False) as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        temporary = Path(stream.name)
    temporary.replace(path)


def grouped_folds(rows, folds=5, split_seed=42, source_merges=()):
    if folds < 3:
        raise ValueError("At least three folds are required for separate train/val/test")
    rows, aliases = canonicalize_source_groups(rows)
    rows = sorted(rows, key=lambda row: row["id"])
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate clip IDs in manifest")
    if len({row["sha256"] for row in rows}) != len(rows):
        raise ValueError("Remove byte-identical videos before cross-validation")
    by_id = {row["id"]: row for row in rows}
    # Manual review may merge source groups, but cannot split a known group.
    parent = {row["source_group"]: row["source_group"] for row in rows}

    def find(group):
        while parent[group] != group:
            group = parent[group]
        return group

    for merge in source_merges:
        if len(merge) < 2 or any(clip_id not in by_id for clip_id in merge):
            raise ValueError("Each source merge needs at least two known clip IDs")
        groups = sorted({find(by_id[clip_id]["source_group"]) for clip_id in merge})
        for group in groups:
            parent[group] = groups[0]
    rows = [{**row, "source_group": find(row["source_group"])} for row in rows]
    labels = np.array([row["label"] for row in rows])
    groups = np.array([row["source_group"] for row in rows])
    if len(set(groups)) < folds or set(labels) != {0, 1}:
        raise ValueError("Need enough source groups and both classes")
    assignment = np.empty(len(rows), dtype=int)
    splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=split_seed)
    for number, (_, test) in enumerate(splitter.split(np.zeros(len(rows)), labels, groups), 1):
        assignment[test] = number
    rows = [{**row, "evaluation_fold": int(number)} for row, number in zip(rows, assignment)]
    partitions = []
    for test_fold in range(1, folds + 1):
        val_fold = (test_fold - 2) % folds + 1
        partition = [{**row, "split": "test" if row["evaluation_fold"] == test_fold else
                      "val" if row["evaluation_fold"] == val_fold else "train"} for row in rows]
        sets = {split: {row["source_group"] for row in partition if row["split"] == split}
                for split in ("train", "val", "test")}
        if sets["train"] & sets["val"] or sets["train"] & sets["test"] or sets["val"] & sets["test"]:
            raise ValueError("Source overlap in generated folds")
        for split in sets:
            if {row["label"] for row in partition if row["split"] == split} != {0, 1}:
                raise ValueError(f"Fold {test_fold} has a single-class {split}; revise grouping/protocol")
        partitions.append(partition)
    return rows, partitions, aliases


def prepare_cv(source: Path, out: Path, folds=5, split_seed=42, seeds=(42, 123, 2026),
               variants=tuple(VARIANTS), epochs=180, patience=30, hidden=48, merges=None,
               controls=tuple(CONTROL_CONFIG), source_review=None, use_coverage=True):
    source, out = Path(source).resolve(), Path(out).resolve()
    if out.exists():
        raise FileExistsError("Choose a new output directory; an existing plan is never overwritten")
    if not seeds or len(set(seeds)) != len(seeds) or not variants or len(set(variants)) != len(variants):
        raise ValueError("Seeds and variants must be nonempty and unique")
    if (set(variants) - set(VARIANTS) or set(controls) - set(CONTROL_CONFIG)
            or len(set(controls)) != len(controls) or min(epochs, patience, hidden) < 1):
        raise ValueError("Invalid model configuration")
    if not isinstance(use_coverage, bool):
        raise ValueError("use_coverage must be a boolean")
    source_merges = json.loads(Path(merges).read_text(encoding="utf-8")) if merges else []
    rows, partitions, aliases = grouped_folds(read_manifest(source / "manifest.csv"), folds,
                                             split_seed, source_merges)
    caches, signature = {}, None
    quality = []
    # Validate before creating outputs. Never reuse training statistics or models.
    for row in rows:
        path = source / "cache" / f"{row['id']}.npz"
        with np.load(path, allow_pickle=False) as saved:
            if str(saved["source_sha256"]) != row["sha256"]:
                raise ValueError(f"Pose source mismatch: {row['id']}")
            current = str(saved["signature"])
            if signature is not None and signature != current:
                raise ValueError("Mixed extraction settings in source cache")
            signature = current
            report = json.loads(str(saved["quality"]))
            if report["id"] != row["id"] or report["label"] != row["label"]:
                raise ValueError(f"Pose quality metadata mismatch: {row['id']}")
            quality.append(report)
        caches[row["id"]] = digest(path)
    pose_settings = json.loads((source / "pose_settings.json").read_text(encoding="utf-8"))
    if pose_settings["signature"] != signature:
        raise ValueError("Pose settings and cache signatures differ")
    motion_hashes, motion_signature = {}, None
    if "pose_quality_only" in controls:
        quality_features(source, rows)
    if "motion_linear" in controls:
        _, motion_signature = load_cached_motion(source, rows)
        motion_hashes = {row["id"]: digest(source / "motion" / "cache" / f"{row['id']}.npz") for row in rows}
    review = json.loads(Path(source_review).read_text(encoding="utf-8")) if source_review else None
    if review and review.get("source_manifest_sha256") != digest(source / "manifest.csv"):
        raise ValueError("Source review refers to a different source manifest")
    if review and "manual_source_merges" in review and review["manual_source_merges"] != source_merges:
        raise ValueError("Source merges differ from the reviewed source links")
    out.mkdir(parents=True)
    (out / "cache").mkdir()
    for row in rows:
        shutil.copy2(source / "cache" / f"{row['id']}.npz", out / "cache" / f"{row['id']}.npz")
    write_manifest(out / "assignments.csv", rows)
    write_json(out / "pose_quality.json", {"signature": signature, "clips": quality})
    write_json(out / "pose_settings.json", pose_settings)
    if motion_hashes:
        (out / "motion" / "cache").mkdir(parents=True)
        for row in rows:
            shutil.copy2(source / "motion" / "cache" / f"{row['id']}.npz",
                         out / "motion" / "cache" / f"{row['id']}.npz")
        shutil.copy2(source / "motion" / "feature_settings.json", out / "motion" / "feature_settings.json")
    if review:
        write_json(out / "source_review.json", review)
    fold_info = []
    for number, partition in enumerate(partitions, 1):
        folder = out / f"fold_{number}"
        folder.mkdir()
        write_manifest(folder / "manifest.csv", partition)
        fold_info.append({"fold": number, "manifest_sha256": digest(folder / "manifest.csv"),
                          "split_counts": {split: dict(Counter(str(row["label"]) for row in partition
                                                               if row["split"] == split))
                                           for split in ("train", "val", "test")}})
    settings = {"folds": folds, "split_seed": split_seed, "seeds": list(seeds),
                "variants": list(variants), "controls": list(controls),
                "epochs": epochs, "patience": patience, "hidden": hidden,
                "use_coverage": use_coverage}
    write_json(out / "protocol.json", {"schema": "source-grouped-cv-v2", "protocol": PROTOCOL,
              "control_protocol": CONTROL_PROTOCOL, "control_config": {name: CONTROL_CONFIG[name] for name in controls},
              "source_manifest_sha256": digest(source / "manifest.csv"), "clips": len(rows),
              "source_groups": len({row["source_group"] for row in rows}), "source_group_aliases": aliases,
              "manual_source_merges": source_merges,
              "source_review_status": review.get("review_scope", "Limited review") if review else "Not certified by this script",
              "source_review_sha256": digest(out / "source_review.json") if review else None,
              "settings": settings, "pose_signature": signature, "cache_sha256": caches,
              "pose_settings_sha256": digest(out / "pose_settings.json"),
              "pose_quality_sha256": digest(out / "pose_quality.json"),
              "motion_signature": motion_signature, "motion_cache_sha256": motion_hashes,
              "motion_settings_sha256": digest(out / "motion" / "feature_settings.json") if motion_hashes else None,
              "assignments_sha256": digest(out / "assignments.csv"), "partitions": fold_info,
              "implementation_sha256": {name: digest(Path(__file__).with_name(name)) for name in
                                        ("cross_validation.py", "train.py", "features.py", "model.py", "data.py", "motion.py",
                                         "demo.py", "cv_report.py", "ablation.py", "cli.py")}})
    snapshot = out / "implementation_snapshot" / "affective"
    snapshot.mkdir(parents=True)
    for module in Path(__file__).parent.glob("*.py"):
        shutil.copy2(module, snapshot / module.name)
    requirements = Path(__file__).resolve().parents[1] / "requirements-pilot.txt"
    if requirements.exists():
        shutil.copy2(requirements, snapshot.parent / requirements.name)
    (out / "run_snapshot.py").write_text(
        '"""Inspect this experiment with its frozen implementation."""\n'
        'import sys\nfrom pathlib import Path\n'
        'experiment = Path(__file__).resolve().parent\n'
        'sys.path.insert(0, str(experiment / "implementation_snapshot"))\n'
        'from affective.cli import main\n'
        'sys.argv = [sys.argv[0], "--out", str(experiment), *sys.argv[1:]]\nmain()\n', encoding="utf-8")
    print(f"Prepared {folds} source-grouped folds, {len(rows)} clips, "
          f"{folds * len(seeds) * len(variants)} TCN fits and {folds * len(controls)} control fits: {out}", flush=True)
    return json.loads((out / "protocol.json").read_text(encoding="utf-8"))


def validate_plan(out, implementation_dir=None):
    plan = json.loads((out / "protocol.json").read_text(encoding="utf-8"))
    if digest(out / "assignments.csv") != plan["assignments_sha256"]:
        raise ValueError("Fold assignments changed after freezing")
    if digest(out / "pose_settings.json") != plan["pose_settings_sha256"]:
        raise ValueError("Pose settings changed after freezing")
    if digest(out / "pose_quality.json") != plan["pose_quality_sha256"]:
        raise ValueError("Pose-quality features changed after freezing")
    if plan.get("source_review_sha256") and digest(out / "source_review.json") != plan["source_review_sha256"]:
        raise ValueError("Source review changed after freezing")
    if plan.get("motion_settings_sha256") and digest(out / "motion" / "feature_settings.json") != plan["motion_settings_sha256"]:
        raise ValueError("Motion settings changed after freezing")
    for name, expected in plan["implementation_sha256"].items():
        implementation = Path(implementation_dir) if implementation_dir is not None else Path(__file__).parent
        if digest(implementation / name) != expected:
            raise ValueError(f"Implementation changed ({name}); prepare a new plan")
    for partition in plan["partitions"]:
        if digest(out / f"fold_{partition['fold']}" / "manifest.csv") != partition["manifest_sha256"]:
            raise ValueError("Fold manifest changed after freezing")
    for clip_id, expected in plan["cache_sha256"].items():
        if digest(out / "cache" / f"{clip_id}.npz") != expected:
            raise ValueError(f"Pose cache changed after freezing: {clip_id}")
    for clip_id, expected in plan.get("motion_cache_sha256", {}).items():
        if digest(out / "motion" / "cache" / f"{clip_id}.npz") != expected:
            raise ValueError(f"Motion cache changed after freezing: {clip_id}")
    return plan


def completed_run(run, fingerprint):
    marker = run / "cv_complete.json"
    if not marker.exists():
        return False
    saved = json.loads(marker.read_text(encoding="utf-8"))
    if saved["protocol_sha256"] != fingerprint or any(digest(run / name) != expected
                                                    for name, expected in saved["artifacts"].items()):
        raise ValueError(f"Completed run changed: {run}")
    return True


def mark_complete(run, fingerprint, artifacts):
    write_json(run / "environment.json", {name: version(name) for name in
                                          ("torch", "numpy", "scikit-learn", "scipy")})
    atomic_json(run / "cv_complete.json", {"protocol_sha256": fingerprint, "artifacts":
                                           {name: digest(run / name) for name in (*artifacts, "environment.json")}})


def run_cv(out: Path, device="auto", folds=None):
    out = Path(out).resolve()
    plan = validate_plan(out)
    config = plan["settings"]
    selected = list(folds) if folds is not None else list(range(1, config["folds"] + 1))
    if not selected or len(set(selected)) != len(selected) or any(number < 1 or number > config["folds"] for number in selected):
        raise ValueError("Invalid fold selection")
    fingerprint = digest(out / "protocol.json")
    for number in selected:
        folder = out / f"fold_{number}"
        lock = folder / ".running"
        try:
            lock.mkdir()
        except FileExistsError as error:
            raise RuntimeError(f"Fold {number} is already running or has a stale lock after interruption: {lock}") from error
        try:
            for seed in config["seeds"]:
                for variant in config["variants"]:
                    run = folder / "runs" / f"{variant}_seed{seed}"
                    if completed_run(run, fingerprint):
                        print(f"Verified completed run: fold {number}, {variant}, seed {seed}", flush=True)
                        continue
                    train_one(folder, variant, seed=seed, epochs=config["epochs"], patience=config["patience"],
                              hidden=config["hidden"], device=device, cache_dir=out / "cache", protocol=PROTOCOL,
                              use_coverage=config.get("use_coverage", True))
                    mark_complete(run, fingerprint, ("model.pt", "metrics.json", "predictions.csv", "history.json"))
            for name in config["controls"]:
                run = folder / "motion" / name
                if completed_run(run, fingerprint):
                    print(f"Verified completed control: fold {number}, {name}", flush=True)
                    continue
                rows = read_manifest(folder / "manifest.csv")
                if name == "motion_linear":
                    features, signature = load_cached_motion(out, rows)
                    if signature != plan["motion_signature"]:
                        raise ValueError("Motion signature differs from the frozen plan")
                else:
                    features = quality_features(out, rows)
                    signature = hashlib.sha256(json.dumps(QUALITY_NAMES).encode()).hexdigest()
                fit_control(folder, rows, features, name, signature,
                            plan["control_config"][name]["regularization"], protocol=CONTROL_PROTOCOL)
                mark_complete(run, fingerprint, ("model.json", "metrics.json", "predictions.csv"))
        finally:
            lock.rmdir()
    return summarize_cv(out)


def summarize_cv(out, *, implementation_dir=None, write=True):
    """Keep folds and seeds separate; incomplete runs never become final results."""
    plan = validate_plan(out, implementation_dir)
    config = plan["settings"]
    fingerprint = digest(out / "protocol.json")
    summary = []
    for variant in config["variants"]:
        records = []
        for number in range(1, config["folds"] + 1):
            for seed in config["seeds"]:
                run = out / f"fold_{number}" / "runs" / f"{variant}_seed{seed}"
                if not completed_run(run, fingerprint):
                    continue
                result = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
                records.append({"fold": number, "seed": seed, "test": result["test"]})
        summary.append(aggregate_runs(variant, records, config["folds"] * len(config["seeds"]), "TCN"))
    for name in config["controls"]:
        records = []
        for number in range(1, config["folds"] + 1):
            run = out / f"fold_{number}" / "motion" / name
            if completed_run(run, fingerprint):
                result = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
                records.append({"fold": number, "seed": None, "test": result["test"]})
        summary.append(aggregate_runs(name, records, config["folds"], "deterministic linear control"))
    report = {"protocol": PROTOCOL, "control_protocol": CONTROL_PROTOCOL, "protocol_sha256": fingerprint,
              "status": "complete" if all(row["complete"] for row in summary) else "incomplete",
              "aggregation": "Equal weight per fold/seed for TCNs; one deterministic fit per fold for controls. "
                             "Standard deviations are descriptive, not confidence intervals. "
                             "Folds/seeds are dependent and are not independent test samples.",
              "models": summary}
    if write:
        atomic_json(out / "summary.json", report)
    return report


def aggregate_runs(name, records, expected, fit_kind):
    aggregate = {}
    for metric in ("accuracy", "macro_f1", "precision_violent", "recall_violent", "roc_auc"):
        values = np.array([record["test"][metric] for record in records], dtype=float)
        aggregate[metric] = {"mean": float(values.mean()) if len(values) else None,
                             "descriptive_std": float(values.std(ddof=1)) if len(values) > 1 else None}
    return {"variant": name, "fit_kind": fit_kind, "completed_runs": len(records),
            "expected_runs": expected, "complete": len(records) == expected,
            "fold_seed_mean": aggregate, "runs": records}
