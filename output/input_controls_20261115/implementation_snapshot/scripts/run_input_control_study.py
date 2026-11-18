"""Fresh matched-GPU fits with full, detection-only and time-shuffled inputs."""
from __future__ import annotations

import argparse
import csv
import html
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import completed_run, digest, mark_complete, validate_plan
from affective.data import read_manifest, write_json
from affective.demo import load_model
from affective.input_controls import INPUT_CONTROLS
from affective.train import choose_threshold, load_features, metrics, normalize_training, predict, train_one

LIMITS = ("Exploratory comparisons on inspected crowd footage. Same 110-channel combined TCN dimensions, "
          "source-grouped folds, seeds, training budget, GPU and validation-only selection. "
          "Detection-only removes coordinates, body velocities and six interaction kinematic channels; "
          "confidence, joint validity, observation masks, neighbor counts and explicit coverage remain. "
          "Time-shuffling permutes already-derived feature/mask slices consistently per clip: velocity vectors "
          "remain available. It tests ordering, not removal of all motion. Fold/seed SD and paired changes "
          "are descriptive, not significance tests. No independent label review or RWF claim is made.")


def rows_at(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def prepare(source, out):
    if out.exists():
        return json.loads((out / "protocol.json").read_text())
    plan = validate_plan(source, source / "implementation_snapshot" / "affective")
    out.mkdir(parents=True)
    shutil.copy2(source / "assignments.csv", out / "assignments.csv")
    shutil.copytree(source / "cache", out / "cache")
    for control in INPUT_CONTROLS:
        for part in plan["partitions"]:
            folder = out / control / f"fold_{part['fold']}"
            folder.mkdir(parents=True)
            shutil.copy2(source / f"fold_{part['fold']}" / "manifest.csv", folder / "manifest.csv")
    snapshot = out / "implementation_snapshot"
    shutil.copytree(ROOT / "affective", snapshot / "affective", ignore=shutil.ignore_patterns("__pycache__"))
    (snapshot / "scripts").mkdir()
    shutil.copy2(Path(__file__), snapshot / "scripts" / Path(__file__).name)
    protocol = {"schema": "combined-input-controls-v1", "source": str(source),
                "source_protocol_sha256": digest(source / "protocol.json"), "clips": plan["clips"],
                "source_groups": plan["source_groups"], "partitions": plan["partitions"],
                "assignments_sha256": digest(out / "assignments.csv"), "cache_sha256": plan["cache_sha256"],
                "conditions": list(INPUT_CONTROLS), "seeds": plan["settings"]["seeds"],
                "epochs": plan["settings"]["epochs"], "patience": plan["settings"]["patience"],
                "hidden": plan["settings"]["hidden"], "feature_schema": plan["settings"]["feature_schema"],
                "use_coverage": True, "device": "cuda", "variant": "combined",
                "script_sha256": digest(Path(__file__)),
                "implementation_sha256": {p.name: digest(p) for p in (ROOT / "affective").glob("*.py")},
                "limitations": LIMITS}
    write_json(out / "protocol.json", protocol)
    (out / "run_snapshot.py").write_text(
        'import sys\nfrom pathlib import Path\ne=Path(__file__).resolve().parent\n'
        'sys.path.insert(0,str(e/"implementation_snapshot"))\n'
        'from scripts.run_input_control_study import main\n'
        'sys.argv=[sys.argv[0],"--out",str(e),*sys.argv[1:]]\nmain()\n', encoding="utf-8")
    return protocol


def validate(out, plan):
    if digest(Path(__file__)) != plan["script_sha256"]:
        raise ValueError("Use the frozen control-study script")
    implementation = Path(__file__).resolve().parents[1] / "affective"
    for name, expected in plan["implementation_sha256"].items():
        if digest(implementation / name) != expected:
            raise ValueError("Use the frozen control-study implementation")
    if digest(out / "assignments.csv") != plan["assignments_sha256"]:
        raise ValueError("Control assignments changed")
    for clip_id, expected in plan["cache_sha256"].items():
        if digest(out / "cache" / f"{clip_id}.npz") != expected:
            raise ValueError("Control pose cache changed")
    for control in plan["conditions"]:
        for part in plan["partitions"]:
            if digest(out / control / f"fold_{part['fold']}" / "manifest.csv") != part["manifest_sha256"]:
                raise ValueError("Control fold manifest changed")


def fit(out, plan):
    fingerprint = digest(out / "protocol.json")
    for control in plan["conditions"]:
        for part in plan["partitions"]:
            folder = out / control / f"fold_{part['fold']}"
            for seed in plan["seeds"]:
                run = folder / "runs" / f"combined_seed{seed}"
                if completed_run(run, fingerprint):
                    continue
                train_one(folder, "combined", seed=seed, epochs=plan["epochs"], patience=plan["patience"],
                          hidden=plan["hidden"], device="cuda", cache_dir=out / "cache",
                          feature_schema=plan["feature_schema"], input_control=control,
                          protocol=LIMITS)
                mark_complete(run, fingerprint, ("model.pt", "metrics.json", "predictions.csv", "history.json"))
                print(f"Completed {control} fold {part['fold']} seed {seed}", flush=True)


def verify_report(out, plan):
    torch.set_num_threads(4)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    fingerprint = digest(out / "protocol.json")
    records, audits, predictions = [], [], []
    for control in plan["conditions"]:
        for part in plan["partitions"]:
            fold = part["fold"]
            folder = out / control / f"fold_{fold}"
            groups, signature = load_features(folder, "combined", out / "cache", plan["feature_schema"], control)
            mean, std = normalize_training(groups)
            for seed in plan["seeds"]:
                run = folder / "runs" / f"combined_seed{seed}"
                if not completed_run(run, fingerprint):
                    raise ValueError("Complete every control fit before reporting")
                model, checkpoint = load_model(run / "model.pt")
                model.to("cuda")
                if (checkpoint["input_control"] != control or checkpoint["pose_signature"] != signature
                        or checkpoint["manifest_sha256"] != part["manifest_sha256"]):
                    raise ValueError("Control checkpoint provenance differs")
                np.testing.assert_allclose(mean, checkpoint["mean"].numpy(), atol=1e-6, rtol=0)
                np.testing.assert_allclose(std, checkpoint["std"].numpy(), atol=1e-6, rtol=0)
                result = json.loads((run / "metrics.json").read_text())
                saved = rows_at(run / "predictions.csv")
                maximum_drift = 0.
                for split, key in (("val", "validation"), ("test", "test")):
                    subset = [r for r in saved if r["split"] == split]
                    if [(r["id"], int(r["label"])) for r in subset] != [(r["id"], r["label"]) for r in groups[split]["rows"]]:
                        raise ValueError("Control prediction IDs differ")
                    expected = np.array([float(r["score"]) for r in subset])
                    actual = predict(model, groups[split], "cuda")
                    np.testing.assert_allclose(actual, expected, atol=3e-4, rtol=0)
                    np.testing.assert_array_equal(actual >= checkpoint["threshold"], [int(r["prediction"]) for r in subset])
                    if metrics(groups[split]["y"], expected, checkpoint["threshold"]) != result[key]:
                        raise ValueError("Control metrics do not reproduce")
                    if split == "val" and choose_threshold(groups[split]["y"], expected) != checkpoint["threshold"]:
                        raise ValueError("Control threshold does not reproduce")
                    maximum_drift = max(maximum_drift, float(np.max(np.abs(actual - expected))))
                records.append({"condition": control, "fold": fold, "seed": seed, "parameters": result["parameters"],
                                "test": result["test"], "validation": result["validation"]})
                audits.append({"condition": control, "fold": fold, "seed": seed, "maximum_score_drift": maximum_drift,
                               "normalization_verified": True, "decisions_reproduced": True, "validation_threshold_verified": True})
                predictions.extend({"condition": control, "fold": fold, "seed": seed, **r} for r in saved if r["split"] == "test")
    if len({r["parameters"] for r in records}) != 1:
        raise ValueError("Control network dimensions changed")
    expected_ids = {r["id"] for r in read_manifest(out / "assignments.csv")}
    for condition in plan["conditions"]:
        for seed in plan["seeds"]:
            subset = [r for r in predictions if r["condition"] == condition and r["seed"] == seed]
            if len(subset) != len(expected_ids) or {r["id"] for r in subset} != expected_ids:
                raise ValueError("Every condition/seed must predict each clip exactly once")
    names = ("accuracy", "macro_f1", "roc_auc", "precision_violent", "recall_violent")
    models = []
    full = {(r["fold"], r["seed"]): r for r in records if r["condition"] == "full"}
    for control in plan["conditions"]:
        selected = [r for r in records if r["condition"] == control]
        models.append({"condition": control, "fits": len(selected),
                       "fold_seed_mean": {name: {"mean": float(np.mean([r["test"][name] for r in selected])),
                         "descriptive_std": float(np.std([r["test"][name] for r in selected], ddof=1))} for name in names},
                       "paired_accuracy_change": float(np.mean([r["test"]["accuracy"] - full[r["fold"], r["seed"]]["test"]["accuracy"] for r in selected]))})
    summary = {"status": "complete", "clips": plan["clips"], "source_groups": plan["source_groups"],
               "models": models, "runs": records, "limitations": LIMITS}
    write_json(out / "summary.json", summary)
    write_json(out / "audit.json", {"status": "pass", "fits_verified": audits, "verification_device": "cuda"})
    with (out / "out_of_fold_predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)
    table = "| Condition | Mean accuracy | Macro-F1 | AUC | Accuracy change (pp) |\n|---|---:|---:|---:|---:|\n" + "\n".join(
        f"| {m['condition']} | {m['fold_seed_mean']['accuracy']['mean']:.1%} | {m['fold_seed_mean']['macro_f1']['mean']:.3f} | {m['fold_seed_mean']['roc_auc']['mean']:.3f} | {m['paired_accuracy_change']*100:+.2f} |" for m in models)
    notes = "# Matched input controls\n\n" + table + "\n\n" + LIMITS + f"\n\nAll {len(audits)} saved fits reproduce scores, decisions, training-only normalization and validation thresholds.\n"
    (out / "RESULTS.md").write_text(notes, encoding="utf-8")
    (out / "index.html").write_text('<!doctype html><meta charset="utf-8"><title>Input controls</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;padding:20px;line-height:1.6}pre{white-space:pre-wrap}</style><h1>Detection and time-order controls</h1><pre>' + html.escape(notes) + '</pre><p><a href="summary.json">Summary</a> | <a href="audit.json">Verification</a> | <a href="protocol.json">Protocol</a></p>', encoding="utf-8")
    print(table, flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("output/centering_corrected_cpu_20261115"))
    parser.add_argument("--out", type=Path, default=Path("output/input_controls_20261115"))
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    out = args.out.resolve()
    plan = prepare(args.source.resolve(), out)
    validate(out, plan)
    if not args.verify_only:
        fit(out, plan)
    verify_report(out, plan)


if __name__ == "__main__":
    main()
