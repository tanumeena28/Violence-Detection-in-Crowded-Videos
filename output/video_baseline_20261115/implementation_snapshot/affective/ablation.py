"""Paired descriptive comparison of frozen explicit-coverage experiments."""
from __future__ import annotations

import html
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .cross_validation import digest, summarize_cv, validate_plan
from .cv_report import LABELS, verify_experiments, write_rows
from .data import write_json
from .features import FEATURE_SCHEMA, LEGACY_FEATURE_SCHEMA

LIMITS = (
    "This is an exploratory paired comparison on previously inspected footage. "
    "Fold/seed observations are dependent; descriptive deviations and win counts are not "
    "confidence intervals or significance tests. Zeroing the explicit scalar leaves observation "
    "masks, missing joints, confidence channels and interaction counts available. "
    "It cannot establish that a model uses only body motion or eliminate all detection cues."
)


def check_coverage_pair(reference, ablation):
    before, after = dict(reference["settings"]), dict(ablation["settings"])
    before.setdefault("feature_schema", LEGACY_FEATURE_SCHEMA)
    after.setdefault("feature_schema", LEGACY_FEATURE_SCHEMA)
    if before.pop("use_coverage", True) is not True or after.pop("use_coverage", True) is not False:
        raise ValueError("Compare a coverage-enabled reference with a coverage-disabled ablation")
    if before != after:
        raise ValueError("Coverage comparison requires identical folds, seeds and training settings")
    for key in ("source_manifest_sha256", "assignments_sha256", "partitions", "cache_sha256",
                "pose_signature", "pose_settings_sha256", "pose_quality_sha256", "source_review_sha256",
                "manual_source_merges", "motion_signature", "motion_cache_sha256", "motion_settings_sha256",
                "control_config", "protocol", "control_protocol"):
        if reference.get(key) != ablation.get(key):
            raise ValueError(f"Coverage comparison inputs differ: {key}")
    for name in ("features.py", "data.py", "motion.py"):
        if reference["implementation_sha256"][name] != ablation["implementation_sha256"][name]:
            raise ValueError(f"Coverage comparison changed feature construction: {name}")


def check_centering_pair(reference, ablation):
    before, after = dict(reference["settings"]), dict(ablation["settings"])
    before.setdefault("use_coverage", True)
    after.setdefault("use_coverage", True)
    if (before.pop("feature_schema", LEGACY_FEATURE_SCHEMA) != LEGACY_FEATURE_SCHEMA
            or after.pop("feature_schema", LEGACY_FEATURE_SCHEMA) != FEATURE_SCHEMA):
        raise ValueError("Compare original v1 features with corrected v2 centering")
    if before != after:
        raise ValueError("Centering comparison requires identical folds, seeds and training settings")
    for key in ("source_manifest_sha256", "assignments_sha256", "partitions", "cache_sha256",
                "pose_signature", "pose_settings_sha256", "pose_quality_sha256", "source_review_sha256",
                "manual_source_merges", "motion_signature", "motion_cache_sha256", "motion_settings_sha256",
                "control_config", "protocol", "control_protocol"):
        if reference.get(key) != ablation.get(key):
            raise ValueError(f"Centering comparison inputs differ: {key}")
    for name in ("data.py", "motion.py", "model.py"):
        if reference["implementation_sha256"][name] != ablation["implementation_sha256"][name]:
            raise ValueError(f"Centering comparison changed an unrelated component: {name}")


def compare_coverage(out, reference, date, verification_device="cpu", implementation_dir=None):
    return compare_experiments(out, reference, date, verification_device, implementation_dir, "coverage")


def compare_centering(out, reference, date, verification_device="cpu", implementation_dir=None):
    return compare_experiments(out, reference, date, verification_device, implementation_dir, "centering")


def compare_experiments(out, reference, date, verification_device, implementation_dir, kind):
    corrected = kind == "centering"
    stem = "centering" if corrected else "coverage"
    title = "Continuous hip-centering correction" if corrected else "Explicit coverage ablation"
    first_key, second_key = ("original", "corrected") if corrected else ("coverage_on", "coverage_off")
    first_label, second_label = ("Original centering", "Continuous centering") if corrected else ("Coverage enabled", "Coverage zeroed")
    notes_file = "CENTERING_COMPARISON.md" if corrected else "COVERAGE_ABLATION.md"
    change = ("Missing hip origins use an interpolated hip-to-box offset within continuous observed track segments. "
              "Reliable hip origins, no-hip fallback, network size and initialization are preserved." if corrected else
              "Explicit pose-coverage input replaced with zero; head dimensions and RNG draws retained.")
    limits = ("Exploratory paired comparison on previously inspected footage. Fold/seed observations are dependent; "
              "deviations and win counts are descriptive, not confidence intervals or significance tests. "
              "Interpolation uses the whole clip and can still be affected by box jitter, incorrect joints and track errors. "
              "Detection masks and confidence remain available. A feature correction does not prove external generalization." if corrected else LIMITS)
    out, reference = Path(out).resolve(), Path(reference).resolve()
    archived = reference / "implementation_snapshot" / "affective"
    implementation = archived if archived.is_dir() else None
    reference_plan = validate_plan(reference, implementation)
    ablation_plan = validate_plan(out, implementation_dir)
    (check_centering_pair if corrected else check_coverage_pair)(reference_plan, ablation_plan)
    # Read and verify the old record without rewriting any of its artifacts.
    before = summarize_cv(reference, implementation_dir=implementation, write=False)
    after = summarize_cv(out, implementation_dir=implementation_dir, write=False)
    if before["status"] != "complete" or after["status"] != "complete":
        raise ValueError("Complete both experiments before comparing")
    old_predictions, old_audits = verify_experiments(reference, reference_plan, verification_device)
    new_predictions, new_audits = verify_experiments(out, ablation_plan, verification_device)
    old_models = {model["variant"]: model for model in before["models"]}
    new_models = {model["variant"]: model for model in after["models"]}
    key = lambda row: (row["variant"], row["seed"], row["fold"], row["id"])
    old_by_key = {key(row): row for row in old_predictions}
    new_by_key = {key(row): row for row in new_predictions}
    if (len(old_by_key) != len(old_predictions) or len(new_by_key) != len(new_predictions)
            or old_by_key.keys() != new_by_key.keys()):
        raise ValueError("Paired predictions must cover the same clip/fold/seed observations")
    if any((row["label"], row["path"]) != (new_by_key[k]["label"], new_by_key[k]["path"])
           for k, row in old_by_key.items()):
        raise ValueError("Paired clip labels or paths differ")
    for name in ablation_plan["settings"]["controls"]:
        if old_models[name]["runs"] != new_models[name]["runs"]:
            raise ValueError(f"Unchanged control metrics differ: {name}")
        for k, row in old_by_key.items():
            if row["variant"] == name:
                paired = new_by_key[k]
                if row["prediction"] != paired["prediction"] or abs(float(row["score"]) - float(paired["score"])) > 1e-10:
                    raise ValueError(f"Unchanged control predictions differ: {name}")
    records, models, training_devices = [], [], set()
    for name in ablation_plan["settings"]["variants"]:
        old_runs = {(row["fold"], row["seed"]): row for row in old_models[name]["runs"]}
        new_runs = {(row["fold"], row["seed"]): row for row in new_models[name]["runs"]}
        if old_runs.keys() != new_runs.keys():
            raise ValueError("Paired fitted runs differ")
        metric_names = ("accuracy", "macro_f1", "roc_auc", "precision_violent", "recall_violent")
        changes = {metric: [] for metric in metric_names}
        for (fold, seed), original in sorted(old_runs.items()):
            run_path = Path(f"fold_{fold}") / "runs" / f"{name}_seed{seed}" / "metrics.json"
            original_fit = json.loads((reference / run_path).read_text(encoding="utf-8"))
            ablated_fit = json.loads((out / run_path).read_text(encoding="utf-8"))
            if any(original_fit[field] != ablated_fit[field] for field in
                   ("parameters", "feature_shape", "train_clips", "val_clips", "test_clips")):
                raise ValueError("Comparison changed network size or fitted input shape")
            if corrected and original_fit["device"] != ablated_fit["device"]:
                raise ValueError("Centering comparison requires matching training devices")
            if corrected:
                old_env = json.loads((reference / run_path.parent / "environment.json").read_text(encoding="utf-8"))
                new_env = json.loads((out / run_path.parent / "environment.json").read_text(encoding="utf-8"))
                if old_env != new_env:
                    raise ValueError("Centering comparison requires matching training package versions")
                training_devices.add(ablated_fit["device"])
            record = {"variant": name, "fold": fold, "seed": seed}
            for metric in metric_names:
                first = original["test"][metric]
                second = new_runs[(fold, seed)]["test"][metric]
                delta = second - first
                record.update({f"{first_key}_{metric}": first, f"{second_key}_{metric}": second,
                               f"delta_{metric}": delta})
                changes[metric].append(delta)
            records.append(record)
        seed_counts = []
        for seed in ablation_plan["settings"]["seeds"]:
            pairs = [(row, new_by_key[k]) for k, row in old_by_key.items()
                     if row["variant"] == name and row["seed"] == seed]
            seed_counts.append({"seed": seed, "clips": len(pairs),
                                "decisions_changed": sum(a["prediction"] != b["prediction"] for a, b in pairs),
                                "errors_corrected": sum(a["prediction"] != a["label"] and b["prediction"] == b["label"] for a, b in pairs),
                                "correct_decisions_broken": sum(a["prediction"] == a["label"] and b["prediction"] != b["label"] for a, b in pairs)})
        models.append({"variant": name, "paired_runs": len(old_runs),
                       first_key: old_models[name]["fold_seed_mean"],
                       second_key: new_models[name]["fold_seed_mean"],
                       "paired_delta": {metric: {"mean": float(np.mean(values)),
                                                 "descriptive_std": float(np.std(values, ddof=1)) if len(values) > 1 else None,
                                                 "minimum": float(min(values)), "maximum": float(max(values)),
                                                 "improved_runs": sum(value > 0 for value in values),
                                                 "tied_runs": sum(value == 0 for value in values),
                                                 "worse_runs": sum(value < 0 for value in values)}
                                        for metric, values in changes.items()},
                       "per_seed_decision_changes": seed_counts})
    comparison = {"date": date, "reference": os.path.relpath(reference, out),
                  "reference_protocol_sha256": digest(reference / "protocol.json"),
                  "ablation_protocol_sha256": digest(out / "protocol.json"),
                  "change": change, "comparison_kind": kind,
                  "clips": ablation_plan["clips"], "source_groups": ablation_plan["source_groups"],
                  "models": models, "controls_identical": True, "paired_runs": records,
                  "verification": {"reference_runs_verified": len(old_audits), "ablation_runs_verified": len(new_audits),
                                   "score_reproduction_device": verification_device,
                                   "maximum_reference_score_drift": max(row["maximum_score_drift"] for row in old_audits),
                                   "maximum_ablation_score_drift": max(row["maximum_score_drift"] for row in new_audits),
                                   "implementation_sha256": {path.name: digest(path) for path in Path(__file__).parent.glob("*.py")}},
                  "limitations": limits}
    if corrected:
        comparison["training_devices"] = sorted(training_devices)
    write_json(out / f"{stem}_comparison.json", comparison)
    write_rows(out / f"{stem}_paired_runs.csv", records)
    figures = out / "figures"
    figures.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    positions = np.arange(len(models))
    for label, field, offset, color in ((first_label, first_key, -.1, "#64748b"),
                                         (second_label, second_key, .1, "#087f8c")):
        axes[0].plot([m[field]["accuracy"]["mean"] * 100 for m in models], positions + offset,
                     "o", color=color, label=label)
    axes[0].legend(loc="lower left")
    axes[0].set(xlabel="Mean accuracy (%)", xlim=(0, 100), title="Same folds and seeds")
    axes[1].errorbar([m["paired_delta"]["accuracy"]["mean"] * 100 for m in models], positions,
                     xerr=[(m["paired_delta"]["accuracy"]["descriptive_std"] or 0) * 100 for m in models],
                     fmt="o", color="#087f8c", capsize=4)
    axes[1].axvline(0, color="#64748b", linewidth=1)
    axes[1].set(xlabel="Accuracy change (percentage points)", title="Paired change, with descriptive SD")
    for ax in axes:
        ax.set_yticks(positions, [LABELS[m["variant"]] for m in models])
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=.2)
    fig.tight_layout()
    fig.savefig(figures / f"{stem}_ablation.png", dpi=220)
    plt.close(fig)
    headings = ["Model", first_label, second_label, "Accuracy change (pp)", "Macro-F1 change", "AUC change", "Improved/tied/worse runs"]
    cells = []
    for model in models:
        delta = model["paired_delta"]
        accuracy = delta["accuracy"]
        cells.append([LABELS[model["variant"]], f"{model[first_key]['accuracy']['mean']:.1%}",
                      f"{model[second_key]['accuracy']['mean']:.1%}", f"{accuracy['mean'] * 100:+.2f}",
                      f"{delta['macro_f1']['mean']:+.4f}", f"{delta['roc_auc']['mean']:+.4f}",
                      f"{accuracy['improved_runs']}/{accuracy['tied_runs']}/{accuracy['worse_runs']}"])
    input_notice = ("Raw pose/motion inputs, splits, training budget and nominal parameter counts match. Only the derived centering definition changes." if corrected else
                    "Pose/motion inputs, feature construction, splits, training budget and nominal parameter counts match.")
    delta_notice = f"Changes are {second_label.lower()} minus {first_label.lower()}."
    lines = ["# " + title, "", f"Recorded {date}.", "", comparison["change"], "",
             f"Matched {ablation_plan['clips']} unique clips, {ablation_plan['source_groups']} reviewed source groups, "
             f"{ablation_plan['settings']['folds']} folds and seeds {ablation_plan['settings']['seeds']}.",
             input_notice + " "
             "Scaling, checkpoint selection and thresholds are fitted afresh using training and validation data.", "",
             "| " + " | ".join(headings) + " |", "|---|---:|---:|---:|---:|---:|---:|",
             *("| " + " | ".join(row) + " |" for row in cells), "",
             delta_notice + " The unchanged linear controls reproduce identical held-out scores and decisions.", "",
             limits, "", f"Both experiments were verified from saved fits: {len(old_audits)} reference and {len(new_audits)} ablation fits. "
             "The reference artifacts were read without modification.", "",
             f"TCN scores were reproduced on {verification_device}; verification implementation hashes are recorded separately. " +
             ("Training devices and package versions match for each pair." if corrected else
              "See the supplemental CPU precision audit for cross-device behavior."), "",
             f"![Paired comparison](figures/{stem}_ablation.png)", "",
             f"[Detailed comparison]({stem}_comparison.json) | [Paired runs]({stem}_paired_runs.csv) | [Experiment results](index.html)", ""]
    (out / notes_file).write_text("\n".join(lines), encoding="utf-8")
    table = "<tr>" + "".join(f"<th>{html.escape(value)}</th>" for value in headings) + "</tr>"
    table += "".join("<tr>" + "".join(f"<td>{html.escape(value)}</td>" for value in row) + "</tr>" for row in cells)
    reference_url = (Path(os.path.relpath(reference, out)) / "index.html").as_posix()
    page = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>body{{font:16px system-ui;background:#f3f5f7;color:#17232d;margin:0}}
main{{max-width:1180px;margin:35px auto;padding:30px;background:white;border-radius:12px}}p{{line-height:1.6}}
table{{border-collapse:collapse;width:100%}}th,td{{padding:12px;border-bottom:1px solid #ddd;text-align:left}}
.scroll{{overflow:auto}}.note{{background:#fff4da;padding:16px}}img{{max-width:100%}}a{{color:#086b86}}</style></head>
<body><main><p>{html.escape(date)}</p><h1>{html.escape(title)}</h1><p>{html.escape(comparison['change'])}</p>
<p>The same {ablation_plan['clips']} clips, {ablation_plan['source_groups']} groups, folds and seeds are used in both experiments.
Training and validation selections are recomputed. Accuracy changes use percentage points. {html.escape(delta_notice)}</p>
<div class="scroll"><table>{table}</table></div><img src="figures/{stem}_ablation.png" alt="Mean accuracy and paired accuracy changes">
<p class="note">{html.escape(limits)}</p><p>All {len(old_audits) + len(new_audits)} saved fits were verified.
The unchanged controls reproduce identical test scores and decisions. TCN score reproduction used {html.escape(verification_device)}.
Reference artifacts were read without modification.</p>
<p><a href="{notes_file}">Research notes</a> | <a href="{stem}_comparison.json">Detailed comparison</a> |
<a href="{stem}_paired_runs.csv">Paired runs</a> | <a href="index.html">New experiment</a> |
<a href="{html.escape(reference_url, quote=True)}">Reference experiment</a></p></main></body></html>'''
    (out / f"{stem}_ablation.html").write_text(page, encoding="utf-8")
    print(f"Verified comparison: {out / (stem + '_ablation.html')}", flush=True)
    return comparison
