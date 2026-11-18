"""Meeting notes and self-contained local results page, grounded in actual outputs."""
from __future__ import annotations

import html
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def write_report(root: Path, out: Path, date=None):
    report_date = (datetime.strptime(date, "%Y-%m-%d") if date else datetime.now(timezone(timedelta(hours=5, minutes=30)))).strftime("%d %B %Y")
    inventory = json.loads((out / "inventory.json").read_text())
    pose = json.loads((out / "pose_quality.json").read_text())
    runs = json.loads((out / "training_summary.json").read_text())
    demos = json.loads((out / "demos.json").read_text())
    audit_path = out / "audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else None
    controls_path = out / "motion" / "summary.json"
    controls = json.loads(controls_path.read_text(encoding="utf-8")) if controls_path.exists() else []
    failure_path = out / "failure_analysis" / "summary.json"
    failure = json.loads(failure_path.read_text(encoding="utf-8")) if failure_path.exists() else None
    manifest_digest = hashlib.sha256((out / "manifest.csv").read_bytes()).hexdigest()
    for artifact in (audit, failure):
        if artifact and artifact["manifest_sha256"] != manifest_digest:
            raise ValueError("Report diagnostics belong to a different manifest")
    controls_section = ""
    controls_notes = ""
    source_warning = ""
    source_warning_notes = ""
    corrected = (out / "correction.json").exists()
    overlap_count = len(audit.get("source_id_overlap_candidates", [])) if audit else 0
    split_description = ("Known source overlaps were removed using matching crowd titles/uploaders and prefix-compatible IDs. Filename checks still cannot rule out other related footage."
                         if "source_group_policy" in inventory else "Source review found related training/validation footage missed by the original filename grouping."
                         if overlap_count else "Source grouping uses filenames; other related footage still requires manual review.")
    next_step = ("First regroup related source footage and retrain on the corrected split. Then compare the skeleton and quality/motion signals across source-separated folds and seeds."
                 if overlap_count else "Compare the skeleton and quality/motion signals across source-separated folds and seeds.")
    related_report = ("<p><a href='../pilot/index.html'>Archived pilot and overlap review</a></p>" if corrected else
                      "<p><a href='../source_corrected/index.html'>Pilot retrained after removing known source overlaps</a></p>" if (out.parent / "source_corrected" / "training_summary.json").exists() else "")
    if corrected:
        source_warning = """<p class="note"><strong>Known source overlaps removed.</strong> This rerun excludes three related training clips and keeps the same validation and test clips. It was performed after inspecting the original test results, so it remains exploratory. Filename and image-hash checks do not establish that every shared source has been found. <a href="correction.json">Correction details</a>.</p>"""
        source_warning_notes = """## Corrected source grouping

This rerun conservatively excludes three related training clips while retaining all original validation and test clips. All models and training normalization were recomputed. The original test results had already been inspected, so this remains an exploratory rerun rather than fresh benchmark evaluation. No known exact or prefix-compatible source-ID overlaps remain, but other shared footage may escape the checks.

"""
    if overlap_count:
        source_warning = f"""<p class="note"><strong>Source overlap found.</strong> Source-ID review identifies {overlap_count} training/validation candidate pairs missed by exact filename grouping. Sampled Preston footage matches visually. Current scores describe the archived pilot; source-independent performance requires corrected grouping and retraining. <a href="failure_analysis/index.html">Inspect the source review</a>.</p>"""
        source_warning_notes = f"""## Source overlap found

The original filename keys missed {overlap_count} training/validation candidate pairs with matching titles/uploaders and truncated source IDs. Sampled Preston footage matches visually. All current scores describe the archived pilot and do not establish source-independent performance. The grouping rule now links these IDs for future runs. Regroup and retrain before reporting corrected results.

"""
    if controls:
        control_rows = "".join(f"<tr><td>{html.escape(r['variant'])}</td><td>{r['classifier_parameters']}</td><td>{r['test']['accuracy']:.1%}</td><td>{r['test']['macro_f1']:.3f}</td><td>{r['test']['roc_auc']:.3f}</td></tr>" for r in controls)
        quality_control = next(r for r in controls if r["variant"] == "pose_quality_only")
        controls_section = f"""<h2>Motion baseline and pose-quality control</h2>
<table><thead><tr><th>Control</th><th>Classifier parameters</th><th>Accuracy</th><th>Macro-F1</th><th>ROC-AUC</th></tr></thead><tbody>{control_rows}</tbody></table>
<p>The motion control uses 80 summaries of adjacent-frame differences and optical flow with a linear classifier. The quality-only control uses seven aggregate detection descriptors, without joint positions or trajectories. Normalization and fitting use training clips; regularization and thresholds use validation clips.</p>
<p class="note">Quality-only accuracy is {quality_control['test']['accuracy']:.1%}. Scene, crowd density or detection behavior may explain part of the signal. These exploratory controls were added after the original test results were inspected; they do not establish that one representation is superior. Check the source review before interpreting this comparison.</p>"""
        control_lines = "\n".join(f"| {r['variant']} | {r['test']['accuracy']:.1%} | {r['test']['macro_f1']:.3f} | {r['test']['roc_auc']:.3f} |" for r in controls)
        controls_notes = f"""## Follow-up controls

| Control | Accuracy | Macro-F1 | ROC-AUC |
|---|---:|---:|---:|
{control_lines}

Motion uses adjacent-frame differences and optical flow summarized into 80 features. Quality-only uses seven detection descriptors and no joint positions or trajectories. Training clips define scaling and coefficients; validation clips select regularization and thresholds. These are exploratory results after prior test inspection. Check the source review before interpreting the comparison.

Investigate scene and detection confounds before claiming the model learned violent body motion. The saved-control audit reproduces scores and decisions and checks training normalization and validation thresholds.

"""
    if failure:
        controls_section += f"""<h2>Failure review</h2><p>The combined model makes {failure['combined_errors']} errors on {failure['test_clips']} test clips: {failure['combined_false_positives']} false positives and {failure['combined_false_negatives']} false negatives. {failure['combined_errors_with_pose_at_least_25_percent']} errors occur at or above 25% pose coverage; missing poses do not explain every failure.</p>
<img src="failure_analysis/comparison.png" alt="Comparison of skeleton models and controls, with pose-coverage scatter">
<p><a href="failure_analysis/index.html">Open all test contact sheets and source-overlap candidates</a> · <a href="motion/audit.json">Saved-control audit</a></p>"""
        controls_notes += f"The combined model has {failure['combined_false_positives']} false positives and {failure['combined_false_negatives']} false negatives; {failure['combined_errors_with_pose_at_least_25_percent']} errors occur with at least 25% pose coverage. Review [every test clip and source candidate](failure_analysis/index.html).\n\n"
    diagnostics = ""
    external_section = ""
    new_video_section = ""
    external_path = out / "external_smoke.json"
    if external_path.exists():
        external = json.loads(external_path.read_text(encoding="utf-8"))
        expected = "violent" if external.get("dataset_label") == 1 else "non-fight"
        outcome = ("The model abstained because pose evidence was insufficient." if external["abstain"] else
                   "The clip-level prediction matched its supplied dataset label." if external.get("is_correct") else
                   "The clip-level prediction disagreed with its supplied dataset label.")
        external_section = f"""<h2>New-video path: external example</h2>
<p>A locally available RWF-2000 clip, labelled {expected}, was passed through fresh pose extraction and the saved combined classifier. Its output was <strong>{html.escape(external['decision'])}</strong> at score {external['score']:.3f}. {outcome} This single example checks the inference path; it is not external benchmark evaluation.</p>
<video controls preload="metadata" poster="{html.escape(external['snapshot'])}" src="{html.escape(external['video'])}"></video>
<p class="small">{html.escape(Path(external['source']).name)}. No threshold or model was changed after inspecting this example.</p>"""
    new_video_path = out / "new_video_demo.json"
    if new_video_path.exists():
        fresh = json.loads(new_video_path.read_text(encoding="utf-8"))
        external_sources = {external["source"]} if external_path.exists() else set()
        for demo in fresh:
            if demo["source"] in external_sources:
                continue
            new_video_section += f"""<h2>Selected raw-video output</h2>
<p>{html.escape(Path(demo['source']).name)} was processed through pose extraction and the saved classifier. Output: <strong>{html.escape(demo['decision'])}</strong>, score {demo['score']:.3f}, usable pose coverage {demo['usable_pose_fraction']:.0%}. No benchmark label is assigned by this inference path.</p>
<video controls preload="metadata" poster="{html.escape(demo['snapshot'])}" src="{html.escape(demo['video'])}"></video>"""
    if audit:
        diagnostic_rows = "".join(
            f"<tr><td>{html.escape(r['variant'])}</td><td>{r['accuracy_95_percent_bootstrap_ci'][0]:.1%} to {r['accuracy_95_percent_bootstrap_ci'][1]:.1%}</td>"
            f"<td>{r['pose_quality_strata']['below_25_percent']['accuracy']:.1%} (n={r['pose_quality_strata']['below_25_percent']['n']})</td>"
            f"<td>{r['pose_quality_strata']['at_least_25_percent']['accuracy']:.1%} (n={r['pose_quality_strata']['at_least_25_percent']['n']})</td></tr>"
            for r in audit["runs"])
        diagnostics = f"""<h2>Verification and uncertainty</h2>
<p>All {audit['source_videos_verified']} source hashes match. Four saved checkpoints reproduce recorded scores on CPU with unchanged decisions, and all {len(audit['demos'])} demo videos decode fully.</p>
<table><thead><tr><th>Variant</th><th>95% accuracy interval</th><th>Pose coverage below 25%</th><th>Pose coverage at least 25%</th></tr></thead><tbody>{diagnostic_rows}</tbody></table>
<p class="small">{html.escape(audit['uncertainty_method'])} The strata describe failures; overall results above include every test clip. Small differences between variants are not established as significant.</p>
<img src="figures/confusion_matrices.png" alt="Confusion matrices for all four models, dataset labels against predicted labels">
<p>The models overfit quickly. Validation loss selects early checkpoints before the loss increases. Track selection discards detected tracks in {audit['clips_with_discarded_tracks']} clips; {len(audit['decode_header_mismatches'])} clip has a frame-header discrepancy, so extraction uses the fully decoded length.</p>"""
    figures = out / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    coverage = np.array([r["usable_pose_fraction"] for r in pose["clips"]])
    axes[0].hist(coverage, bins=np.linspace(0, 1, 11), color="#087F83", edgecolor="white")
    axes[0].set(xlabel="Fraction of sampled frames with at least 5 valid joints", ylabel="Clips", title="Measured pose coverage")
    axes[1].bar([r["variant"] for r in runs], [r["test"]["macro_f1"] for r in runs], color="#087F83")
    axes[1].set(ylim=(0, 1), ylabel="Macro-F1", title="Exploratory held-out pilot results")
    axes[1].tick_params(axis="x", labelrotation=18)
    fig.tight_layout()
    fig.savefig(figures / "pilot_results.png", dpi=160)
    plt.close(fig)
    combined = next((r for r in runs if r["variant"] == "combined"), runs[0])
    history = json.loads((out / "runs" / f"{combined['variant']}_seed{combined['seed']}" / "history.json").read_text())
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot([h["epoch"] for h in history], [h["train_loss"] for h in history], label="Training")
    ax.plot([h["epoch"] for h in history], [h["val_loss"] for h in history], label="Validation")
    ax.axvline(combined["selected_epoch"], color="#526173", ls="--", label="Selected checkpoint")
    ax.set(xlabel="Epoch", ylabel="Binary cross-entropy", title="Combined model: actual training history")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures / "training_curve.png", dpi=160)
    plt.close(fig)
    counts = inventory["split_counts"]
    training_n = sum(counts["train"].values())
    validation_n = sum(counts["val"].values())
    test_n = sum(counts["test"].values())
    table = "".join(f"<tr><td>{html.escape(r['variant'])}</td><td>{r['parameters']:,}</td><td>{r['selected_epoch']}</td><td>{r['threshold']:.2f}</td><td>{r['test']['accuracy']:.1%}</td><td>{r['test']['macro_f1']:.3f}</td><td>{r['test']['roc_auc']:.3f}</td></tr>" for r in runs)
    videos = "".join(f"<article><h3>Held-out dataset label: {'violent' if d['label'] else 'nonviolent'}</h3><video controls preload='metadata' poster='{html.escape(d['snapshot'])}' src='{html.escape(d['video'])}'></video><p>Prediction: <strong>{html.escape(d['decision'])}</strong>. Score {d['score']:.3f}; pose coverage {d['usable_pose_fraction']:.0%}.</p><p class='small'>{html.escape(Path(d['source']).name)}</p></article>" for d in demos)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Crowd violence implementation pilot</title>
<style>body{{font:16px/1.55 system-ui,sans-serif;color:#14243a;background:#f6f7f9;margin:0}}main{{max-width:1120px;margin:auto;padding:32px}}h1{{font-size:36px;line-height:1.15}}h2{{margin-top:38px}}.lead{{font-size:20px}}.note{{background:#fff5dd;border-left:4px solid #a76c00;padding:16px}}table{{border-collapse:collapse;background:white;width:100%}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #ccd6df}}video{{width:100%;max-width:920px;background:#14243a}}img{{max-width:100%}}article{{margin-bottom:30px}}.small{{font-size:13px;overflow-wrap:anywhere;color:#526173}}a{{color:#087f83}}code{{background:#eaf2f2;padding:3px 6px}}@media(max-width:700px){{main{{padding:18px}}table{{font-size:12px}}th,td{{padding:5px}}}}</style></head>
<body><main><p>Vishal Gautam | SVNIT Surat | Pilot results, {report_date}</p>
{related_report}
<h1>Violence detection in crowded videos</h1><p class="lead">A working pilot from raw video to a trained temporal model and annotated predictions.</p>
<p class="note"><strong>Implementation pilot.</strong> These are actual results from one held-out split and one training seed per variant. They do not establish benchmark performance, reliable person attribution, or precise event timestamps.</p>
{source_warning}
<h2>What runs</h2><p>Video decoding → YOLO11n COCO-17 pose extraction → within-clip tracking → body motion and relative interaction features → shared per-person TCN → masked pooling → clip score.</p>
<p>Four configurations use the same pose caches and splits: baseline, confidence/mask handling, interaction features, and their combination. Training normalization uses only the training split. Checkpoints and thresholds use validation data.</p>
<h2>Data and measured feasibility</h2><p>{training_n} training clips, {validation_n} validation clips, {test_n} held-out test clips. {len(inventory['exact_duplicates'])} byte-identical duplicate removed; {len(inventory['source_overlap_exclusions'])} source overlaps excluded. Average usable pose coverage: {coverage.mean():.1%}. {int((coverage < 0.25).sum())} clips have usable poses in fewer than 25% of sampled frames.</p>
<p>Crowd folds 1-3 for training, fold 4 for validation, fold 5 for testing. Exact byte duplicates were removed. {split_description}</p><p class="small">Filename and byte-hash grouping cannot establish that all near-duplicates have been removed. Pose extraction can lose small or occluded people and fragment tracks. The model score is not a calibrated probability.</p>
<h2>Held-out pilot results</h2><table><thead><tr><th>Variant</th><th>Parameters</th><th>Best epoch</th><th>Threshold</th><th>Accuracy</th><th>Macro-F1</th><th>ROC-AUC</th></tr></thead><tbody>{table}</tbody></table>
<p>Test majority-class accuracy: {combined['majority_baseline_test_accuracy']:.1%}. All clips, including poor-pose clips, remain in the evaluation. The demo abstains when pose coverage is below 25%; this operational cutoff is an initial safeguard, not a validated decision rule.</p>
<img src="figures/pilot_results.png" alt="Measured pose coverage and pilot results"><img src="figures/training_curve.png" alt="Training and validation loss curves">
{diagnostics}
{controls_section}
<h2>Video demonstrations</h2><p>The first {len(demos) // 2} filenames in each held-out class were selected without filtering by model correctness. Examples include insufficient pose evidence and incorrect predictions. Scores use the entire clip. Track overlays use the nearest sampled pose frame and do not identify violent participants.</p>{videos}
{external_section}
{new_video_section}
<h2>Next experiments</h2><p>{next_step} Review full videos for labels and tracking failures, compare a stronger RGB/motion model, and evaluate an external surveillance split using RWF-2000.</p>
<h2>Reproduce and inspect</h2><p>Run <code>.\\scripts\\run_pilot.ps1</code> from the project folder. For a new video, use the command in README.md. The pose model is pretrained; the temporal classifier is trained locally from the crowd dataset labels.</p>
<p><a href="MEETING_NOTES.md">Meeting notes</a> · <a href="AUDIT.md">Verification and limitations</a> · <a href="audit.json">Artifact audit</a> · <a href="inventory.json">Inventory and split audit</a> · <a href="pose_quality.json">Pose quality by clip</a> · <a href="training_summary.json">Full training results</a> · <a href="manifest.csv">Clip manifest</a></p>
</main></body></html>"""
    (out / "index.html").write_text(page, encoding="utf-8")
    metric_lines = "\n".join(f"| {r['variant']} | {r['parameters']:,} | {r['test']['accuracy']:.1%} | {r['test']['macro_f1']:.3f} | {r['test']['roc_auc']:.3f} |" for r in runs)
    notes = f"""# Implementation discussion: pilot run {report_date}

## Opening explanation

My pipeline now runs from raw crowd videos to pose extraction, tracking, motion and interaction features, a trained temporal model, and video predictions. I have implemented the four variants in the presentation on identical inputs and splits. This is a feasibility pilot; I am showing actual outputs and failure cases rather than claiming completed benchmark performance.

{source_warning_notes}
## Demonstration order

1. Open `index.html` and explain the pipeline.
2. Show a held-out nonviolent and violent video. Explain that the IDs are clip-local tracks, not person-level violence labels.
3. Show the results table and actual loss curves.
4. Explain pose misses, track fragmentation, and the small single-split evaluation.
5. Discuss the next validation experiments and scope with the professor.

## What was implemented

- Video inventory, exact duplicate removal, and source-group split checks.
- Pretrained YOLO11n-pose, {pose['settings']['frames']} uniformly sampled frames per clip, COCO-17 joints.
- Hungarian matching using box overlap and center distance, reset for every clip.
- Up to {pose['settings']['max_people']} tracks, chosen by observed keypoint signal. Report discarded tracks.
- Body-centered positions, temporal changes, confidence weighting and validity masks.
- Nearest-person distances, offsets, relative velocities, and approach rate in shared scene coordinates.
- Shared per-person TCN, masked temporal and person pooling, binary clip classifier.
- Real training on {training_n} clips, validation on {validation_n}, final pilot test on {test_n}.
- Validation-selected checkpoint and threshold; saved model, manifest, feature statistics, and extraction signature.
- Offline video demos and new-video inference. No person labels or timestamp annotations were available.

## Actual pilot results

| Variant | Parameters | Accuracy | Macro-F1 | ROC-AUC |
|---|---:|---:|---:|---:|
{metric_lines}

These results use one seed and one holdout, not five-fold/three-seed evaluation. Mean usable pose coverage is {coverage.mean():.1%}; {int((coverage < 0.25).sum())} clips fall below 25%. The original dataset labels are used as supplied. A pose model failing to see people is not evidence of a nonviolent event.

{controls_notes}
## Important technical details

The combined feature tensor per clip is {combined['feature_shape']}: time, track slots, feature channels. Only training observations define normalization statistics. The same temporal encoder size and tuning budget are used for the four variants; extra input channels change parameter count, which is reported. Demo scores are offline full-clip scores and are not calibrated probabilities. The sampled skeleton overlay is held until the nearest next sampled frame, so it is a visualization of sampled inputs rather than full-frame pose tracking.

The pose confidence threshold is 0.25. A frame is called usable when at least five joints pass this threshold anywhere among retained people. Demo abstention below 25% usable frames is an initial quality rule, not a tuned or validated rejection system. Test metrics include every selected clip regardless of pose quality.

## Questions to discuss

- Is clip-level violence detection with reliability/interaction ablations the agreed final scope?
- Should the next stage prioritize an RGB reference, external RWF-2000 validation, or full crowd cross-validation?
- What date applies to this group's final presentation?
- What paper format should be used for the required draft before 20 November?

## Next stage

{next_step} Review full videos and labels; compare a stronger RGB/motion model and external RWF-2000 performance. Write methods now and expand the results after those experiments.
"""
    (out / "MEETING_NOTES.md").write_text(notes, encoding="utf-8")
    print(f"Results page: {out / 'index.html'}", flush=True)
