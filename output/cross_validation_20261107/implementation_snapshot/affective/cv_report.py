"""Verify completed repeated experiments and publish a readable research report."""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from .cross_validation import summarize_cv, validate_plan
from .data import read_manifest, write_json
from .demo import load_model
from .motion import load_cached_motion, quality_features, score_linear
from .train import choose_threshold, load_features, metrics, normalize_training, predict

LABELS = {"baseline": "Skeleton baseline", "reliability": "Reliability", "interactions": "Interactions",
          "combined": "Combined", "motion_linear": "Motion control", "pose_quality_only": "Quality-only control"}


def read_predictions(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def verify_experiments(out, plan):
    """Reproduce saved scores; never refit models or change thresholds."""
    torch.set_num_threads(4)
    prediction_rows, audits = [], []
    config = plan["settings"]
    for number in range(1, config["folds"] + 1):
        folder = out / f"fold_{number}"
        manifest = read_manifest(folder / "manifest.csv")
        test_ids = {r["id"] for r in manifest if r["split"] == "test"}
        for name in config["variants"]:
            parts, signature = load_features(folder, name, out / "cache")
            mean, std = normalize_training(parts)
            for seed in config["seeds"]:
                run = folder / "runs" / f"{name}_seed{seed}"
                model, checkpoint = load_model(run / "model.pt")
                if checkpoint["pose_signature"] != signature or checkpoint["manifest_sha256"] != plan["partitions"][number - 1]["manifest_sha256"]:
                    raise ValueError("TCN checkpoint provenance differs from the frozen fold")
                np.testing.assert_allclose(mean, checkpoint["mean"].numpy(), atol=1e-6)
                np.testing.assert_allclose(std, checkpoint["std"].numpy(), atol=1e-6)
                saved = read_predictions(run / "predictions.csv")
                result = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
                if result["threshold"] != checkpoint["threshold"]:
                    raise ValueError("TCN recorded threshold differs from its checkpoint")
                maximum_drift = 0.
                for split, key in (("val", "validation"), ("test", "test")):
                    rows = [r for r in saved if r["split"] == split]
                    expected = np.array([float(r["score"]) for r in rows])
                    if [r["id"] for r in rows] != [r["id"] for r in parts[split]["rows"]]:
                        raise ValueError("TCN predictions differ from fold order")
                    if [int(r["label"]) for r in rows] != parts[split]["y"].tolist():
                        raise ValueError("TCN prediction labels differ from the fold")
                    actual = predict(model, parts[split], "cpu")
                    np.testing.assert_allclose(actual, expected, atol=3e-4, rtol=0)
                    np.testing.assert_array_equal(actual >= checkpoint["threshold"], expected >= checkpoint["threshold"])
                    np.testing.assert_array_equal(expected >= checkpoint["threshold"], [int(r["prediction"]) for r in rows])
                    if metrics(parts[split]["y"], expected, checkpoint["threshold"]) != result[key]:
                        raise ValueError("TCN metrics do not reproduce from saved predictions")
                    if split == "val" and choose_threshold(parts[split]["y"], expected) != checkpoint["threshold"]:
                        raise ValueError("TCN threshold does not reproduce from validation scores")
                    maximum_drift = max(maximum_drift, float(np.abs(actual - expected).max()))
                audits.append({"fold": number, "variant": name, "seed": seed,
                               "maximum_cpu_score_drift": maximum_drift, "training_normalization_verified": True,
                               "validation_threshold_verified": True, "saved_decisions_reproduced": True})
                prediction_rows.extend({"fold": number, "variant": name, "seed": seed,
                                        **{k: r[k] for k in ("id", "path", "label", "score", "prediction")}}
                                       for r in saved if r["split"] == "test")
        for name in config["controls"]:
            run = folder / "motion" / name
            features, _ = load_cached_motion(out, manifest) if name == "motion_linear" else (quality_features(out, manifest), None)
            features = np.asarray(features, dtype=np.float64)
            train = np.array([r["split"] == "train" for r in manifest])
            checkpoint = json.loads((run / "model.json").read_text(encoding="utf-8"))
            if checkpoint["manifest_sha256"] != plan["partitions"][number - 1]["manifest_sha256"]:
                raise ValueError("Control checkpoint provenance differs from the frozen fold")
            np.testing.assert_allclose(checkpoint["mean"], features[train].mean(0), atol=1e-12, rtol=0)
            np.testing.assert_allclose(checkpoint["std"], np.maximum(features[train].std(0), .01), atol=1e-12, rtol=0)
            saved = read_predictions(run / "predictions.csv")
            result = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
            if result["threshold"] != checkpoint["threshold"]:
                raise ValueError("Control recorded threshold differs from its checkpoint")
            if [(r["id"], int(r["label"]), r["split"]) for r in saved] != [(r["id"], r["label"], r["split"]) for r in manifest]:
                raise ValueError("Control predictions differ from the frozen fold")
            expected = np.array([float(r["score"]) for r in saved])
            actual = score_linear(features, checkpoint)
            np.testing.assert_allclose(actual, expected, atol=1e-10, rtol=0)
            np.testing.assert_array_equal(actual >= checkpoint["threshold"], [int(r["prediction"]) for r in saved])
            labels = np.array([r["label"] for r in manifest])
            for split, key in (("train", "train"), ("val", "validation"), ("test", "test")):
                mask = np.array([r["split"] == split for r in manifest])
                if metrics(labels[mask], expected[mask], checkpoint["threshold"]) != result[key]:
                    raise ValueError("Control metrics do not reproduce from saved scores")
                if split == "val" and choose_threshold(labels[mask], expected[mask]) != checkpoint["threshold"]:
                    raise ValueError("Control threshold does not reproduce from validation scores")
            if min(result["candidates"], key=lambda r: r["validation_log_loss"])["C"] != checkpoint["selected_C"]:
                raise ValueError("Control regularization differs from the validation choice")
            audits.append({"fold": number, "variant": name, "seed": None,
                           "maximum_cpu_score_drift": float(np.abs(actual - expected).max()),
                           "training_normalization_verified": True, "validation_threshold_verified": True,
                           "saved_decisions_reproduced": True})
            prediction_rows.extend({"fold": number, "variant": name, "seed": "",
                                    **{k: r[k] for k in ("id", "path", "label", "score", "prediction")}}
                                   for r in saved if r["split"] == "test")
        for name in [*config["variants"], *config["controls"]]:
            for seed in config["seeds"] if name in config["variants"] else [""]:
                rows = [r for r in prediction_rows if r["fold"] == number and r["variant"] == name and r["seed"] == seed]
                if {r["id"] for r in rows} != test_ids or len(rows) != len(test_ids):
                    raise ValueError("Every model must predict each outer test clip exactly once")
        print(f"Verified fold {number}: saved scores, decisions, normalization and validation choices", flush=True)
    return prediction_rows, audits


def pooled_results(predictions, plan):
    expected_ids = {r["id"] for r in read_manifest(plan["assignments_path"])}
    results = []
    config = plan["settings"]
    for name in [*config["variants"], *config["controls"]]:
        for seed in config["seeds"] if name in config["variants"] else [""]:
            rows = [r for r in predictions if r["variant"] == name and r["seed"] == seed]
            if len(rows) != len(expected_ids) or {r["id"] for r in rows} != expected_ids:
                raise ValueError("Pooled evaluation must cover every unique clip exactly once per model/seed")
            labels = np.array([int(r["label"]) for r in rows])
            decisions = np.array([int(r["prediction"]) for r in rows])
            result = metrics(labels, decisions, .5)
            result.pop("roc_auc")
            results.append({"variant": name, "seed": seed, **result})
    return results


def write_cv_report(out, date):
    out = Path(out)
    plan = validate_plan(out)
    config = plan["settings"]
    summary = summarize_cv(out)
    if summary["status"] != "complete":
        raise ValueError("Complete all frozen experiments before publishing the results report")
    predictions, audits = verify_experiments(out, plan)
    pooled = pooled_results(predictions, {**plan, "assignments_path": out / "assignments.csv"})
    write_rows(out / "out_of_fold_predictions.csv", predictions)
    write_json(out / "pooled_metrics.json", {"models": pooled,
               "note": "Classification uses each fold's validation-selected threshold. ROC-AUC is reported within folds, "
                       "not pooled across classifiers with different score calibration."})
    write_json(out / "audit.json", {"status": "pass", "protocol_sha256": summary["protocol_sha256"],
               "clips": plan["clips"], "runs_verified": len(audits), "runs": audits,
               "limitations": "Checks artifact consistency and split provenance. Does not certify all source relationships, "
                              "violence labels, generalization to new datasets or full-pipeline speed."})
    figures = out / "figures"
    figures.mkdir(exist_ok=True)
    names = [LABELS[r["variant"]] for r in summary["models"]]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    for ax, metric, title in zip(axes, ("accuracy", "roc_auc"), ("Accuracy", "ROC-AUC")):
        means = [r["fold_seed_mean"][metric]["mean"] for r in summary["models"]]
        deviations = [r["fold_seed_mean"][metric]["descriptive_std"] or 0. for r in summary["models"]]
        ax.errorbar(means, np.arange(len(names)), xerr=deviations, fmt="o", capsize=4, color="#087f8c")
        ax.set_yticks(np.arange(len(names)), names)
        ax.invert_yaxis()
        ax.set_xlim(0., 1.)
        ax.set_title(title)
        ax.grid(axis="x", alpha=.2)
    fig.suptitle(f"{config['folds']} source-grouped folds; error bars show descriptive variation")
    fig.tight_layout()
    fig.savefig(figures / "comparison.png", dpi=220)
    plt.close(fig)
    table_rows, md_rows = [], []
    for model in summary["models"]:
        values = model["fold_seed_mean"]
        cells = [LABELS[model["variant"]], str(model["completed_runs"]),
                 f"{values['accuracy']['mean']:.1%} +/- {values['accuracy']['descriptive_std']:.1%}",
                 f"{values['macro_f1']['mean']:.3f} +/- {values['macro_f1']['descriptive_std']:.3f}",
                 f"{values['roc_auc']['mean']:.3f} +/- {values['roc_auc']['descriptive_std']:.3f}"]
        table_rows.append("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in cells) + "</tr>")
        md_rows.append("| " + " | ".join(cells) + " |")
    review_label = "<a href='source_review.json'>Frozen source review</a>" if plan.get("source_review_sha256") else "Source review"
    review_notice = f"<p>{review_label}: {html.escape(plan['source_review_status'])}</p>"
    pool_rows = "".join(f"<tr><td>{LABELS[r['variant']]}</td><td>{r['seed'] if r['seed'] != '' else 'deterministic'}</td>"
                        f"<td>{r['n']}</td><td>{r['accuracy']:.1%}</td><td>{r['macro_f1']:.3f}</td>"
                        f"<td>{r['precision_violent']:.3f}</td><td>{r['recall_violent']:.3f}</td></tr>" for r in pooled)
    details = "".join(f"<tr><td>{LABELS[m['variant']]}</td><td>{r['fold']}</td>"
                      f"<td>{r['seed'] if r['seed'] is not None else 'deterministic'}</td>"
                      f"<td>{r['test']['accuracy']:.1%}</td><td>{r['test']['macro_f1']:.3f}</td>"
                      f"<td>{r['test']['roc_auc']:.3f}</td></tr>" for m in summary["models"] for r in m["runs"])
    page = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Repeated crowd violence evaluation</title><style>body{{font:16px system-ui;background:#f3f5f7;color:#17232d;margin:0}}
main{{max-width:1180px;margin:35px auto;padding:30px;background:white;border-radius:12px}}h1{{font-size:30px}}
table{{border-collapse:collapse;width:100%;font-size:15px}}td,th{{padding:10px;border-bottom:1px solid #ddd;text-align:left}}
.scroll{{overflow:auto}}img{{max-width:100%}}.note{{background:#fff4da;padding:16px;line-height:1.5}}a{{color:#086b86}}
details{{margin:20px 0}}p{{line-height:1.6}}</style></head><body><main>
<p>{html.escape(date)}</p><h1>Repeated crowd violence evaluation</h1>
<p>{plan['clips']} unique clips, {plan['source_groups']} source groups, {config['folds']} outer folds.
{len(config['variants'])} TCN variants each use {len(config['seeds'])} training seeds. Each linear control is fitted once per fold.</p>
<p class="note">These are exploratory results on previously inspected videos. Grouping and sampled source review reduce known overlap,
but do not establish a fresh untouched benchmark or independently validated labels. Variation across folds and seeds is descriptive,
not a confidence interval or proof of a significant difference.</p>{review_notice}
<h2>Mean results across fold runs</h2><div class="scroll"><table><tr><th>Model</th><th>Fits</th><th>Accuracy</th><th>Macro-F1</th><th>ROC-AUC</th></tr>
{''.join(table_rows)}</table></div><img src="figures/comparison.png" alt="Accuracy and AUC with descriptive variation">
<h2>All clips evaluated once per model and seed</h2><p>Each row pools classification decisions for all {plan['clips']} clips using the threshold selected
on that fold's validation data. ROC-AUC remains reported within folds because score calibration differs across trained classifiers.</p>
<div class="scroll"><table><tr><th>Model</th><th>Seed</th><th>Clips</th><th>Accuracy</th><th>Macro-F1</th><th>Violent precision</th><th>Violent recall</th></tr>{pool_rows}</table></div>
<details><summary>Per-fold results</summary><div class="scroll"><table><tr><th>Model</th><th>Fold</th><th>Seed</th><th>Accuracy</th><th>Macro-F1</th><th>ROC-AUC</th></tr>{details}</table></div></details>
<h2>Verification and remaining work</h2><p>All {len(audits)} saved fits reproduce their predictions and decisions. Training-only normalization,
validation-selected thresholds and frozen inputs were checked. These experiments use cached features and do not measure full-pipeline latency.</p>
<p>Next: inspect detection-cue dependence and high-motion failures, add a stronger RGB reference, and evaluate transfer to suitable uninspected RWF-2000 videos.</p>
<p><a href="RESULTS.md">Research notes</a> | <a href="summary.json">Fold summary</a> | <a href="pooled_metrics.json">Pooled decisions</a> |
<a href="out_of_fold_predictions.csv">Per-clip predictions</a> | <a href="audit.json">Verification</a> | <a href="protocol.json">Frozen protocol</a></p>
</main></body></html>"""
    (out / "index.html").write_text(page, encoding="utf-8")
    lines = ["# Repeated source-grouped evaluation", "", f"Recorded {date}. {plan['clips']} unique clips and {plan['source_groups']} source groups.", "",
             f"{config['folds']} custom source-grouped folds: {config['folds'] - 2} train, one validates and one tests. TCN seeds: {', '.join(map(str, config['seeds']))}.",
             "Each deterministic linear control is fitted once per fold. Scaling and fitting use training data; validation selects checkpoints, regularization and thresholds.", "",
             "| Model | Fits | Accuracy | Macro-F1 | ROC-AUC |", "|---|---:|---:|---:|---:|", *md_rows, "",
             "Means and standard deviations describe fold/seed runs, which are dependent. They are not confidence intervals or significance tests.", "",
             "Source review: " + plan["source_review_status"], "",
             "Known shared recordings were grouped before training. Existing clips and pilot results have been inspected previously. These remain exploratory results, not an untouched benchmark.",
             "The custom rotations differ from the supplied Violent-Flows protocol. Full-video label validation and unknown shared footage remain limitations.", "",
             f"Verification reproduced {len(audits)} saved fits, including decisions, training-only scaling and validation-selected thresholds.",
             "Cached-feature experiments do not establish real-time inference or full-pipeline latency.", "",
             "[Results page](index.html) | [Fold summary](summary.json) | [Pooled decisions](pooled_metrics.json) | [Per-clip predictions](out_of_fold_predictions.csv) | [Audit](audit.json)", ""]
    (out / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Verified results report: {out / 'index.html'}", flush=True)
    return summary
