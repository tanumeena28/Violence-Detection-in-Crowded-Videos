"""Descriptive failure review and visual-similarity triage on frozen pilot outputs.

These diagnostics do not relabel videos, exclude test clips, or tune checkpoints.
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import quote

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .data import decode_sample, read_manifest, source_overlap_candidates, write_json


def read_predictions(path):
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["id"]: {**r, "label": int(r["label"]), "prediction": int(r["prediction"]), "score": float(r["score"])} for r in rows}


def image_hash(image):
    gray = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), (32, 32), interpolation=cv2.INTER_AREA)
    block = cv2.dct(gray.astype(np.float32))[:8, :8].ravel()[1:]
    return block > np.median(block)


def review_sheet(rows, thumbnails, target, title):
    width, card_height = 1040, 205
    canvas = np.full((len(rows) * card_height + 65, width, 3), 247, np.uint8)
    cv2.putText(canvas, title, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, .65, (35, 45, 55), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Six uniformly sampled frames. Read full video before confirming its label.", (15, 53), cv2.FONT_HERSHEY_SIMPLEX, .44, (65, 75, 85), 1, cv2.LINE_AA)
    for i, row in enumerate(rows):
        y = 65 + i * card_height
        description = f"{row['id']} | label={row['label']} | combined={row['combined_prediction']} | motion={row.get('motion_linear_prediction', '?')} | pose={row['usable_pose_fraction']:.0%}"
        cv2.putText(canvas, description, (15, y + 23), cv2.FONT_HERSHEY_SIMPLEX, .49, (35, 45, 55), 1, cv2.LINE_AA)
        filename = Path(row["path"]).stem
        cv2.putText(canvas, filename[:112], (15, y + 45), cv2.FONT_HERSHEY_SIMPLEX, .37, (75, 85, 95), 1, cv2.LINE_AA)
        for j, image in enumerate(thumbnails[row["id"]]):
            x = 15 + j * 169
            canvas[y + 55:y + 175, x:x + 160] = image
        cv2.putText(canvas, f"combined score={row['combined_score']:.3f}; tracks total/retained={row['total_tracks']}/{row['retained_tracks']}; discarded={row['discarded_tracks']}",
                    (15, y + 197), cv2.FONT_HERSHEY_SIMPLEX, .43, (65, 75, 85), 1, cv2.LINE_AA)
    if not cv2.imwrite(str(target), canvas):
        raise RuntimeError("Contact sheet write failed")


def similarity_audit(rows, thumbnails, hashes, folder):
    pairs = []
    for i, first in enumerate(rows):
        for second in rows[i + 1:]:
            if first["split"] == second["split"]:
                continue
            a, b = hashes[first["id"]], hashes[second["id"]]
            distances = np.count_nonzero(a[:, None] != b[None, :], axis=-1)
            ordered = np.diag(distances)
            nearest = distances.min(1)
            pairs.append({"first_id": first["id"], "second_id": second["id"],
                          "first_path": first["path"], "second_path": second["path"],
                          "first_split": first["split"], "second_split": second["split"],
                          "same_label": first["label"] == second["label"],
                          "ordered_mean_hamming": float(ordered.mean()),
                          "nearest_mean_hamming": float(nearest.mean()), "minimum_hamming": int(distances.min()),
                          "ordered_frames_at_most_6_bits": int((ordered <= 6).sum()),
                          "triage_flag": bool((ordered.mean() <= 10 and (ordered <= 6).sum() >= 3) or (nearest.mean() <= 9 and (nearest <= 4).sum() >= 2))})
    pairs.sort(key=lambda p: (not p["triage_flag"], p["ordered_mean_hamming"], p["nearest_mean_hamming"]))
    nearest_pairs = pairs[:12]
    for k, pair in enumerate(nearest_pairs, 1):
        canvas = np.full((345, 1040, 3), 247, np.uint8)
        cv2.putText(canvas, f"Cross-split similarity candidate {k}; ordered mean hash distance {pair['ordered_mean_hamming']:.1f}/63", (15, 28), cv2.FONT_HERSHEY_SIMPLEX, .57, (35, 45, 55), 1, cv2.LINE_AA)
        for i, key in enumerate(("first", "second")):
            y = 42 + i * 147
            cv2.putText(canvas, f"{pair[key + '_split']} | {pair[key + '_id']} | {Path(pair[key + '_path']).stem[:85]}", (15, y + 17), cv2.FONT_HERSHEY_SIMPLEX, .4, (55, 65, 75), 1, cv2.LINE_AA)
            for j, image in enumerate(thumbnails[pair[key + "_id"]]):
                canvas[y + 23:y + 143, 15 + j * 169:175 + j * 169] = image
        path = folder / "similarity" / f"pair_{k:02}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(path), canvas):
            raise RuntimeError("Similarity contact sheet write failed")
        pair["contact_sheet"] = path.relative_to(folder).as_posix()
    result = {"method": "Six chronological 63-bit perceptual hashes per clip. Compare all cross-split pairs; keep nearest 12 for visual triage.",
              "threshold": "Ordered mean <=10 with >=3 frames at distance <=6, or nearest-frame mean <=9 with >=2 frames at distance <=4. Fixed triage heuristic, not a calibrated duplicate detector.",
              "cross_split_pairs_compared": len(pairs), "flagged_pairs": sum(p["triage_flag"] for p in pairs),
              "nearest_pairs": nearest_pairs, "flagged_pair_details": [p for p in pairs if p["triage_flag"]],
              "limitation": "Similar scenes can share hashes, and cropping, shifted time, or brief overlap can evade hashes. No automatic split changes; human source review is still required."}
    source_pairs = source_overlap_candidates(rows)
    for k, pair in enumerate(source_pairs, 1):
        canvas = np.full((345, 1040, 3), 247, np.uint8)
        cv2.putText(canvas, f"Source-ID overlap candidate {k}: matching title/uploader, truncated ID", (15, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, .57, (35, 45, 55), 1, cv2.LINE_AA)
        for i, key in enumerate(("first", "second")):
            y = 42 + i * 147
            cv2.putText(canvas, f"{pair[key + '_split']} | {pair[key + '_id']} | {Path(pair[key + '_path']).stem[:85]}",
                        (15, y + 17), cv2.FONT_HERSHEY_SIMPLEX, .4, (55, 65, 75), 1, cv2.LINE_AA)
            for j, image in enumerate(thumbnails[pair[key + "_id"]]):
                canvas[y + 23:y + 143, 15 + j * 169:175 + j * 169] = image
        path = folder / "similarity" / f"source_pair_{k:02}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(path), canvas):
            raise RuntimeError("Source-overlap contact sheet write failed")
        pair["contact_sheet"] = path.relative_to(folder).as_posix()
    result["source_id_overlap_candidates"] = source_pairs
    result["source_id_overlap_candidate_count"] = len(source_pairs)
    result["source_independence_status"] = "review_required" if source_pairs else "no_known_id_overlap"
    write_json(folder / "similarity.json", result)
    return result


def analyze(root: Path, out: Path):
    folder = out / "failure_analysis"
    folder.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest(out / "manifest.csv")
    quality = {r["id"]: r for r in json.loads((out / "pose_quality.json").read_text(encoding="utf-8"))["clips"]}
    runs = json.loads((out / "training_summary.json").read_text(encoding="utf-8"))
    controls_path = out / "motion" / "summary.json"
    if not controls_path.exists():
        raise FileNotFoundError("Run the motion stage before failure analysis")
    controls = json.loads(controls_path.read_text(encoding="utf-8"))
    predictions = {r["variant"]: read_predictions(out / "runs" / f"{r['variant']}_seed{r['seed']}" / "predictions.csv") for r in runs}
    predictions.update({r["variant"]: read_predictions(out / "motion" / r["variant"] / "predictions.csv") for r in controls})
    thumbnails, hashes = {}, {}
    for number, row in enumerate(manifest, 1):
        images, _, _, _ = decode_sample(root / row["path"], 6)
        thumbnails[row["id"]] = [cv2.resize(image, (160, 120), interpolation=cv2.INTER_AREA) for image in images]
        hashes[row["id"]] = np.array([image_hash(image) for image in images])
        if number % 50 == 0 or number == len(manifest):
            print(f"Failure-review samples {number}/{len(manifest)}", flush=True)
    test_rows = []
    for row in manifest:
        if row["split"] != "test":
            continue
        q = quality[row["id"]]
        entry = {**row, **{k: q[k] for k in ("usable_pose_fraction", "mean_people", "total_tracks", "retained_tracks", "discarded_tracks", "valid_joint_fraction")}}
        entry["median_track_observations"] = 0.
        with np.load(out / "cache" / f"{row['id']}.npz", allow_pickle=False) as cached:
            lengths = cached["present"].sum(0)
            entry["median_track_observations"] = float(np.median(lengths[lengths > 0])) if (lengths > 0).any() else 0.
        for name, by_id in predictions.items():
            saved = by_id[row["id"]]
            if saved["label"] != row["label"]:
                raise ValueError("Prediction label mismatch")
            entry[name + "_score"] = saved["score"]
            entry[name + "_prediction"] = saved["prediction"]
            entry[name + "_correct"] = saved["prediction"] == row["label"]
        entry["all_skeleton_models_wrong"] = all(not entry[r["variant"] + "_correct"] for r in runs)
        entry["combined_error_type"] = "correct" if entry["combined_correct"] else "false_negative" if row["label"] else "false_positive"
        entry["low_pose_coverage"] = q["usable_pose_fraction"] < .25
        test_rows.append(entry)
    with (folder / "test_diagnostics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(test_rows[0]))
        writer.writeheader()
        writer.writerows(test_rows)
    metrics_by_variant = []
    strata_masks = {"all": lambda r: True, "pose_below_25_percent": lambda r: r["low_pose_coverage"],
                    "pose_at_least_25_percent": lambda r: not r["low_pose_coverage"],
                    "discarded_tracks": lambda r: r["discarded_tracks"] > 0,
                    "no_discarded_tracks": lambda r: r["discarded_tracks"] == 0,
                    "median_track_at_most_4_samples": lambda r: r["median_track_observations"] <= 4,
                    "median_track_above_4_samples": lambda r: r["median_track_observations"] > 4}
    for name in predictions:
        strata = {}
        for label, condition in strata_masks.items():
            chosen = [r for r in test_rows if condition(r)]
            strata[label] = {"n": len(chosen), "correct": sum(r[name + "_correct"] for r in chosen),
                            "accuracy": float(np.mean([r[name + "_correct"] for r in chosen])) if chosen else None}
        metrics_by_variant.append({"variant": name, "strata": strata})
    missed_with_good_poses = [r["id"] for r in test_rows if not r["combined_correct"] and not r["low_pose_coverage"]]
    sheets = []
    for start in range(0, len(test_rows), 4):
        path = folder / f"test_sheet_{start // 4 + 1:02}.jpg"
        review_sheet(test_rows[start:start + 4], thumbnails, path, f"Held-out review: clips {start + 1}-{min(start + 4, len(test_rows))} of {len(test_rows)}")
        sheets.append(path.name)
    similarity = similarity_audit(manifest, thumbnails, hashes, folder)
    errors = [r for r in test_rows if not r["combined_correct"]]
    paired = {}
    for name in ("baseline", "interactions", "combined"):
        paired[name] = {"motion_correct_skeleton_wrong": sum(r["motion_linear_correct"] and not r[name + "_correct"] for r in test_rows),
                        "skeleton_correct_motion_wrong": sum(r[name + "_correct"] and not r["motion_linear_correct"] for r in test_rows),
                        "both_wrong": sum(not r[name + "_correct"] and not r["motion_linear_correct"] for r in test_rows)}
    summary = {"test_clips": len(test_rows), "combined_errors": len(errors),
               "combined_false_positives": sum(r["combined_error_type"] == "false_positive" for r in test_rows),
               "combined_false_negatives": sum(r["combined_error_type"] == "false_negative" for r in test_rows),
               "combined_errors_with_pose_at_least_25_percent": len(missed_with_good_poses),
               "all_skeleton_models_wrong": sum(r["all_skeleton_models_wrong"] for r in test_rows),
               "metrics_by_variant": metrics_by_variant, "paired_motion_comparisons": paired,
               "visual_similarity_flagged_pairs": similarity["flagged_pairs"], "contact_sheets": sheets,
               "source_id_overlap_candidate_count": similarity["source_id_overlap_candidate_count"],
               "source_independence_status": similarity["source_independence_status"],
               "manifest_sha256": hashlib.sha256((out / "manifest.csv").read_bytes()).hexdigest(),
               "claim_boundary": "Descriptive associations on the previously inspected test split. Pose failures, track length and discarded tracks are proxies, not verified causes or measured identity switches. Sparse frame review does not verify full-clip labels."}
    write_json(folder / "summary.json", summary)
    all_results = [*runs, *controls]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    names = [r["variant"] for r in all_results]
    axes[0].bar(names, [r["test"]["accuracy"] for r in all_results], color=["#087F83"] * 4 + ["#af6837", "#65758c"])
    axes[0].axhline(24 / 47, ls="--", color="#65758c", label="Majority-class baseline")
    axes[0].set(ylim=(0, 1), ylabel="Accuracy", title="Same 47 test clips; all clips retained")
    axes[0].tick_params(axis="x", labelrotation=30)
    axes[0].legend(fontsize=8)
    for label, color in ((0, "#087F83"), (1, "#af6837")):
        chosen = [r for r in test_rows if r["label"] == label]
        axes[1].scatter([r["usable_pose_fraction"] for r in chosen], [r["combined_score"] for r in chosen],
                        label="Dataset nonviolent" if label == 0 else "Dataset violent", color=color, s=30, alpha=.8)
    combined = next(r for r in runs if r["variant"] == "combined")
    axes[1].axhline(combined["threshold"], ls="--", color="#65758c", label="Frozen combined threshold")
    axes[1].axvline(.25, ls=":", color="#65758c")
    axes[1].set(xlabel="Usable pose coverage", ylabel="Combined clip score", title="Errors also occur with high pose coverage")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(folder / "comparison.png", dpi=160)
    plt.close(fig)
    metric_rows = "".join(f"<tr><td>{r['variant']}</td><td>{r['test']['accuracy']:.1%}</td><td>{r['test']['macro_f1']:.3f}</td><td>{r['test']['roc_auc']:.3f}</td></tr>" for r in all_results)
    cards = []
    for row in test_rows:
        source_url = quote("../../../" + row["path"], safe="/")
        cards.append(f"<tr><td><a href='{source_url}'>{html.escape(row['id'])}</a></td><td>{row['label']}</td><td>{row['combined_error_type']}</td><td>{row['usable_pose_fraction']:.0%}</td><td>{row['total_tracks']}/{row['retained_tracks']}</td><td>{row['median_track_observations']:.0f}</td><td>{row['motion_linear_prediction']}</td></tr>")
    images_html = "".join(f"<img src='{s}' alt='Chronological samples of held-out clips'>" for s in sheets)
    similarities_html = "".join(f"<img src='{p['contact_sheet']}' alt='Cross-split visual similarity candidate'>" for p in similarity["nearest_pairs"])
    source_overlap_html = "".join(f"<img src='{p['contact_sheet']}' alt='Matching source IDs across training and validation'>" for p in similarity["source_id_overlap_candidates"])
    source_notice = (f"<p class='note'><strong>Source independence requires correction.</strong> Matching titles/uploaders with truncated source IDs identify {similarity['source_id_overlap_candidate_count']} cross-split candidate pairs. Zero image-hash flags do not clear this concern. Use corrected grouping and retrain before reporting source-independent results.</p>"
                     if similarity["source_id_overlap_candidate_count"] else
                     "<p>No exact or prefix-compatible source-ID overlaps remain across this split. Other related footage may escape filename and image-hash checks; manual source review remains necessary.</p>")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Failure analysis and motion controls</title>
<style>body{{font:16px/1.55 system-ui;background:#f6f7f9;color:#14243a;margin:0}}main{{max-width:1100px;padding:28px;margin:auto}}img{{max-width:100%;margin:12px 0}}table{{border-collapse:collapse;background:white;width:100%}}th,td{{padding:8px;text-align:left;border-bottom:1px solid #ccd6df}}.note{{padding:15px;background:#fff5dd}}a{{color:#087F83}}.table{{overflow:auto}}</style></head><body><main>
<p><a href="../index.html">Back to pilot</a></p><h1>Failure analysis and motion controls</h1>
<p class="note">This is exploratory follow-up on the existing pilot split. The four skeleton checkpoints remain unchanged. Motion descriptors and C grid were fixed for this run; scaling and model fitting use training data, C and threshold use validation data. Test observations do not establish generalization or a causal explanation.</p>
<h2>Same-split controls</h2><div class="table"><table><tr><th>Model</th><th>Accuracy</th><th>Macro-F1</th><th>ROC-AUC</th></tr>{metric_rows}</table></div>
<p>Motion control: 80 summaries of adjacent-frame differences and optical flow on a 2x2 grid, plus train-standardized logistic regression. It uses the same 32 time anchors as poses, with neighboring decoded frames for valid flow. Quality-only control: seven detection-count/quality descriptors and a fixed-C linear classifier, with no joint positions or motion.</p>
<p>These controls differ in architecture and feature count from the TCN. Motion examines adjacent pixels around each anchor rather than only the sampled pose frame. They diagnose useful signals and confounds; they are not published deep RGB/flow benchmarks.</p>
{source_notice}
<img src="comparison.png" alt="Same-split accuracy comparison and pose-coverage scatter">
<h2>Measured failures</h2><p>The combined model has {len(errors)} errors: {summary['combined_false_positives']} false positives and {summary['combined_false_negatives']} false negatives. {len(missed_with_good_poses)} errors occur above the 25% pose-coverage cutoff. {summary['all_skeleton_models_wrong']} clips are wrong in all four skeleton variants. Low pose coverage does not explain every failure.</p>
<p>Short tracks and discarded detections indicate possible information loss, but these numbers cannot identify actual identity switches. Labels remain the dataset labels until full-video review.</p>
<div class="table"><table><tr><th>Source video</th><th>Label</th><th>Combined outcome</th><th>Pose coverage</th><th>Tracks total/kept</th><th>Median track samples</th><th>Motion prediction</th></tr>{''.join(cards)}</table></div>
<h2>Review every held-out clip</h2><p>Each row contains six chronological frames. Use the source links for full-video inspection; short aggressive acts may fall between these samples.</p>{images_html}
<h2>Cross-split similarity triage</h2><p>{similarity['cross_split_pairs_compared']:,} pairs compared; {similarity['flagged_pairs']} flagged by the fixed hash heuristic. Below are the nearest twelve pairs. Similar stadiums or camera layouts are not proof of shared source. Hashes can miss cropping and short temporal overlap. No clips were moved or excluded.</p>{similarities_html}
<h2>Truncated source-ID overlaps</h2><p>These pairs match the title and uploader, with a short source ID that prefixes the longer ID. They should be grouped conservatively in future partitions. Contact sheets provide evidence for review, without changing the archived pilot.</p>{source_overlap_html}
<p><a href="summary.json">Summary JSON</a> | <a href="test_diagnostics.csv">Per-clip diagnostics</a> | <a href="similarity.json">Similarity details</a> | <a href="FINDINGS.md">Findings</a></p></main></body></html>"""
    (folder / "index.html").write_text(page, encoding="utf-8")
    lines = ["# Failure analysis and motion controls", "", "| Model | Test accuracy | Macro-F1 | ROC-AUC |", "|---|---:|---:|---:|"]
    lines += [f"| {r['variant']} | {r['test']['accuracy']:.1%} | {r['test']['macro_f1']:.3f} | {r['test']['roc_auc']:.3f} |" for r in all_results]
    lines += ["", f"Combined model: {len(errors)} errors, including {summary['combined_false_positives']} false positives and {summary['combined_false_negatives']} false negatives. {len(missed_with_good_poses)} errors occur with at least 25% usable pose coverage. All skeleton variants miss {summary['all_skeleton_models_wrong']} of the same clips.", "",
              "The 80-dimensional motion descriptor uses real adjacent decoded frames near the original 32 anchors, not flow between distant sampled frames. Train-only normalization and logistic fitting; validation log-loss selects regularization from C=0.01,0.1,1,10; validation macro-F1 selects threshold. The seven-feature quality-only control uses fixed C=1 and no joint positions or trajectories.", "",
              "This follow-up is exploratory because the original pilot test results were already inspected. The test set did not select these controls' coefficients, regularization or thresholds. No skeleton checkpoint or test partition was changed.", "",
              "| Skeleton model | Motion correct, skeleton wrong | Skeleton correct, motion wrong | Both wrong |", "|---|---:|---:|---:|"]
    lines += [f"| {name} | {p['motion_correct_skeleton_wrong']} | {p['skeleton_correct_motion_wrong']} | {p['both_wrong']} |" for name, p in paired.items()]
    lines += ["", f"Cross-split triage compared {similarity['cross_split_pairs_compared']} video pairs; {similarity['flagged_pairs']} passed its heuristic. Inspect similarity.json and the twelve candidate sheets before treating any pair as related source footage.", "",
              (f"Source-ID review finds {similarity['source_id_overlap_candidate_count']} cross-split candidate pairs with matching titles/uploaders and prefix-compatible IDs. Exact filename grouping missed them. Sampled frames show matching footage in the Preston crowd pair. Zero hash flags do not establish source independence. Regroup and retrain before claiming source-independent performance."
               if similarity["source_id_overlap_candidate_count"] else "No known exact or prefix-compatible source-ID overlaps remain across this split. Other shared source footage can escape filename and image-hash checks; manual source review remains necessary."), "",
              "Contact sheets cover all 47 test clips with six frames each. This is sparse visual triage; it cannot verify full-clip labels. No labels have been changed. Track observations and discarded detections are descriptive proxies, not measured tracking errors.", "",
              "Next: review complete videos for suspicious labels and source overlap; validate the signal comparison across seeds and source-separated folds. If aggregate pose quality predicts violence well, investigate scene and detection confounds. Compare a stronger motion/RGB baseline before making representation-superiority claims.", "",
              "![Motion comparison and pose coverage](comparison.png)", ""]
    (folder / "FINDINGS.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Failure analysis ready: {folder / 'index.html'}", flush=True)
    return summary
