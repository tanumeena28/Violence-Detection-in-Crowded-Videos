"""Render diagnostic demonstrations and verify preservation of completed experiments."""
from __future__ import annotations

import csv
import html
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import digest
from affective.data import write_json
from affective.inference import VideoPredictor, count_frames, iter_video_windows
from scripts.predict_video_model import render
from scripts.score_final_evaluations import check_hashes

OUT = ROOT / 'output/final_delivery_20261115'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def demos():
    out = OUT / 'demos'
    out.mkdir(exist_ok=True)
    with (OUT / 'rwf_evaluation/predictions.csv').open(newline='', encoding='utf-8') as stream:
        rows = [r for r in csv.DictReader(stream) if r['model'] == 'rwf_finetuned_video']
    selected = []
    # Explicit diagnostic selection after scoring; no independent performance claim.
    for label, prediction, name in [(1, 1, 'true_positive'), (0, 0, 'true_negative'),
                                     (0, 1, 'false_positive'), (1, 0, 'false_negative')]:
        candidates = [r for r in rows if int(r['label']) == label and int(r['prediction']) == prediction]
        if candidates:
            key = lambda r: (float(r['score']), r['id'])
            row = (max if prediction else min)(candidates, key=key)
            selected.append((name, row))
    predictor = VideoPredictor(ROOT / 'output/rwf_finetune_v2_20261115')
    records = []
    for name, row in selected:
        source = ROOT / row['path']
        result = predictor.predict(source)
        drift = abs(result['score'] - float(row['score']))
        if drift > 3e-4 or result['prediction'] != int(row['prediction']):
            raise ValueError('Diagnostic raw-video score does not reproduce')
        target = out / f'{name}.mp4'
        if target.exists():
            raise FileExistsError('Preserve existing demos rather than overwrite them')
        encoded = render(source, result, target, int(row['label']))
        decoded, fps = count_frames(target)
        if encoded != result['decoded_frames'] or decoded != encoded:
            raise ValueError('Diagnostic MP4 failed complete decode')
        if cv2.imread(str(target.with_suffix('.jpg'))) is None:
            raise ValueError('Diagnostic poster is unreadable')
        records.append({'case': name, 'source': row['path'], 'source_sha256': digest(source),
                        'score_drift': drift, 'dataset_label': int(row['label']), 'result': result,
                        'encoded_frames': encoded, 'verified_decoded_frames': decoded,
                        'video': target.relative_to(OUT).as_posix(),
                        'poster': target.with_suffix('.jpg').relative_to(OUT).as_posix()})
        print(f'Diagnostic demo verified: {name}, {decoded} frames', flush=True)
    # Exercise the window interface on a released clip with a short window size,
    # including its residual window. This is an implementation test, not new data.
    source = ROOT / selected[0][1]['path']
    total, fps = count_frames(source)
    windows = []
    for images, indices, rate, decoded, start in iter_video_windows(source, 2.):
        result = predictor.process(images, indices, rate, decoded) if images is not None else {'score': None, 'abstain': True}
        windows.append({'start_seconds': start, 'frames': decoded, 'result': result})
    if sum(w['frames'] for w in windows) != total:
        raise ValueError('Window demonstration does not cover every frame')
    write_json(OUT / 'window_smoke_check.json', {'status': 'pass', 'source': str(source),
        'decoded_frames': total, 'windows': windows, 'window_seconds': 2.,
        'scope': 'Frame coverage and sealed GPU window inference only; no streaming accuracy claim'})
    write_json(OUT / 'demo_audit.json', {'status': 'pass', 'checks': records,
        'selection': 'Most confident example of each confusion-matrix category, selected after scoring for diagnosis',
        'labels_independently_verified': False})
    return records


def preserve():
    old = read_json(OUT / 'previous_artifacts_before.json')
    checks = {}
    for experiment, hashes in old.items():
        folder = ROOT / 'output' / experiment
        check_hashes(folder, hashes)
        actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
        extra = sorted(actual - set(hashes))
        checks[experiment] = {'original_files_verified': len(hashes), 'additional_files': extra}
        print(f'Preserved experiment: {experiment} ({len(hashes)} files)', flush=True)
    write_json(OUT / 'preservation_audit.json', {'status': 'pass', 'experiments': checks,
        'original_files_verified': sum(len(h) for h in old.values()), 'all_original_files_byte_exact': True})


def plot(rwf, external):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, title, result in zip(axes, ['RWF released evaluation (400 clips)', 'Hockey Fight external set (1,000 clips)'], [rwf, external]):
        names = list(result['models'])
        labels = [n.replace('rwf_frozen_video', 'Frozen video').replace('rwf_finetuned_video', 'Fine-tuned video')
                  .replace('crowd_pose_interactions', 'Crowd pose') for n in names]
        values = [result['models'][n]['all_clips']['accuracy'] * 100 for n in names]
        bars = ax.bar(labels, values, color=['#3684a4', '#237d60', '#ac7b39'][:len(names)])
        ax.set(title=title, ylim=(0, 100), ylabel='Accuracy (%)')
        ax.spines[['top', 'right']].set_visible(False)
        for bar, value, name in zip(bars, values, names):
            cm = result['models'][name]['all_clips']['confusion_matrix']
            ax.text(bar.get_x()+bar.get_width()/2, value+2, f'{value:.2f}%\nFP {cm[0][1]}, FN {cm[1][0]}', ha='center', fontsize=9)
    fig.suptitle('Fixed-model evaluations: supplied labels, no evaluation tuning')
    fig.tight_layout()
    fig.savefig(OUT / 'evaluation_comparison.png', dpi=170)
    plt.close(fig)


def page(rwf, external, records):
    table = '<table><tr><th>Evaluation</th><th>Model</th><th>Accuracy</th><th>Macro-F1</th><th>AUC</th><th>FP / FN</th></tr>'
    for dataset, result in [('RWF (400)', rwf), ('Hockey Fight (1,000)', external)]:
        for name, r in result['models'].items():
            m = r['all_clips']; cm = m['confusion_matrix']
            table += f'<tr><td>{dataset}</td><td>{html.escape(name)}</td><td>{m["accuracy"]:.2%}</td><td>{m["macro_f1"]:.3f}</td><td>{m["roc_auc"]:.3f}</td><td>{cm[0][1]} / {cm[1][0]}</td></tr>'
    cards = ''.join(f'<article><h3>{r["case"].replace("_", " ").title()}</h3><video controls preload="none" poster="{r["poster"]}" src="{r["video"]}"></video><p>Supplied label: {r["dataset_label"]}. Score: {r["result"]["score"]:.3f}; threshold: 0.23.</p></article>' for r in records)
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Technical delivery | Affective project</title><style>body{{font:16px system-ui;background:#edf2f5;color:#172c39;margin:0}}main{{max-width:1150px;margin:auto;padding:32px}}p{{line-height:1.65}}table{{border-collapse:collapse;width:100%;background:white}}td,th{{padding:13px;text-align:left;border-bottom:1px solid #ddd}}.scroll{{overflow:auto}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}}article{{background:white;border-radius:10px;padding:18px}}video,img{{width:100%}}a{{color:#126d8b}}.note{{padding:18px;background:#fff1d3}}</style></head><body><main><p>15 November 2026 | Local RTX 3050 GPU</p><h1>Affective project: technical delivery</h1><p>The fine-tuned video model is retained by its validation promotion rule: epoch 2 and threshold 0.23. Both evaluation sets use frozen choices. The original frozen-video reference remains the primary model in the predeclared external protocol.</p><div class="scroll">{table}</table></div><img src="evaluation_comparison.png" alt="Accuracy and errors for fixed models on both evaluation sets"><p class="note">Independent human label review is pending because no reviewer is currently available. RWF evaluation clips were already inspected. Hockey Fight is a sports-broadcast mirror with 997 unique byte hashes across 1,000 clips, supplied unreviewed labels and unaudited source/pretraining overlap. These results do not establish surveillance deployment reliability.</p><p><a href="rwf_evaluation/index.html">RWF evaluation</a> | <a href="../external_validation_20261115/index.html">External evaluation</a> | <a href="RUNBOOK.md">Runbook and commands</a> | <a href="demo_audit.json">Demo verification</a> | <a href="preservation_audit.json">Preservation audit</a> | <a href="../blind_review_20261115/index.html">Neutral review pack</a></p><h2>Diagnostic raw-video examples</h2><p>Examples were selected after evaluation from each outcome category for explanation. They are not an independent performance sample. All MP4 files decode completely and reproduce their saved model scores.</p><div class="cards">{cards}</div><p>Whole-clip scores do not attribute violence to individual people. Closed-window inference is available for longer videos; streaming and event-localization accuracy are unvalidated. Paper drafting remains deferred.</p></main></body></html>'''
    (OUT / 'index.html').write_text(doc, encoding='utf-8')


def update_project_docs(rwf, external):
    validation = read_json(ROOT / 'output/rwf_finetune_v2_20261115/promotion.json')['candidate_validation']['validation']
    test = rwf['models']['rwf_finetuned_video']['all_clips']
    backup = ROOT / 'tmp/final_delivery_20261115'
    for name in ['README.md', 'PROJECT_STATUS.md', 'NEXT_STEPS.md']:
        target = backup / f'before_final_{name}'
        if not target.exists():
            target.write_bytes((ROOT / name).read_bytes())
    rows = []
    for dataset, result in [('RWF released evaluation', rwf), ('Hockey Fight external', external)]:
        for name, r in result['models'].items():
            m = r['all_clips']; cm = m['confusion_matrix']
            rows.append(f'| {dataset} | {name} | {m["n"]} | {m["accuracy"]:.2%} | {m["macro_f1"]:.3f} | {m["roc_auc"]:.3f} | {cm[0][1]} | {cm[1][0]} |')
    summary = f'''The local GPU evaluation and delivery work is complete. Independent human
label/difficulty review remains pending because no reviewer is available.
Paper drafting remains deferred. Completion describes work delivered and does
not imply reliable deployment.

The retained video model is the layer-4 fine-tuned R3D-18 candidate. Validation
alone selected epoch 2 and threshold 0.23 before either evaluation was scored.
Validation accuracy is {validation['accuracy']:.1%}, macro-F1 {validation['macro_f1']:.3f}, and AUC
{validation['roc_auc']:.3f}. Validation Fight misses fell from 42 to 13 and false alarms
increased from 15 to 30. The original frozen-video reference is preserved and
remains the predeclared primary model for the external experiment.

| Evaluation | Model | Clips | Accuracy | Macro-F1 | AUC | False alarms | Misses |
|---|---|---:|---:|---:|---:|---:|---:|
''' + '\n'.join(rows) + '''

The RWF evaluation clips were previously inspected, so their scores remain
exploratory supervised development evidence. Hockey Fight was pinned and its
protocol frozen before external scoring. All 1,000 mirror clips were retained,
including three duplicate files, with 997 unique byte hashes. No byte-identical
overlap was found with the compared 2,245-file crowd/RWF inventory. Byte hashes
do not establish independent source games or rule out near-duplicates and
Kinetics pretraining overlap. Sports broadcasts differ from surveillance.
Supplied labels remain unchanged and independently unreviewed.

Four diagnostic raw-video MP4s cover correct positive/negative decisions,
a false alarm and a miss. They reproduce saved scores and decode completely.
The bounded decoder reproduces the original uniform 32-frame samples. Single
video calls preserve the validation batch shape to match CUDA score rounding.
A closed-window interface accounts for every frame in a longer-video smoke
check; event localization and real-time streaming accuracy are unvalidated.
All 8,474 files in ten previous completed experiments are preserved byte-exact.
All 60 project tests pass, including exact bounded sampling, window-tail
accounting, sealed-protocol rejection and the validation batch-shape check.

[Final results and demos](output/final_delivery_20261115/index.html) |
[Runbook](output/final_delivery_20261115/RUNBOOK.md) |
[RWF evaluation](output/final_delivery_20261115/rwf_evaluation/index.html) |
[External evaluation](output/external_validation_20261115/index.html) |
[Preservation audit](output/final_delivery_20261115/preservation_audit.json) |
[Independent review pack](output/blind_review_20261115/index.html)
'''
    status = '''# Project status

Updated 15 November 2026 after the sealed fine-tuned evaluations and final
technical delivery. Earlier percentage estimates were rough planning judgments.
The current checklist records completed outputs and the remaining review task.

''' + summary + '''
The core clip-level implementation, controlled experiments, bounded fine-tuning,
external scoring and demo/runbook delivery are complete. Independent full-video
label/difficulty review is still required for the broader technical completion
claim. No review has been fabricated or replaced by assistant inspection.
The full manuscript is outside the active scope and remains deferred.
'''
    (ROOT / 'PROJECT_STATUS.md').write_text(status, encoding='utf-8')
    readme_path = ROOT / 'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    marker = '## Technical progress: 15 November 2026'
    readme = readme.replace(marker, '## Earlier technical progress: 15 November 2026', 1)
    position = readme.index('## Earlier technical progress: 15 November 2026')
    readme = readme[:position] + '## Final technical delivery: 15 November 2026\n\n' + summary + '\n' + readme[position:]
    readme_path.write_text(readme, encoding='utf-8')
    next_path = ROOT / 'NEXT_STEPS.md'
    old_next = next_path.read_text(encoding='utf-8')
    prior = old_next[old_next.index('## Previous work order (paper drafting deferred)'):]
    active = '''# Technical project priorities

Updated 15 November 2026 after fixed-model scoring and verified technical
delivery. Paper drafting remains deferred. Local GPU work has completed all
currently authorized computation and demonstration tasks.

''' + summary + '''
## Remaining required work

An independent person must review the existing neutral 40-clip full-video pack
and export labels/difficulty notes before seeing predictions or the coordinator
mapping. No reviewer is available at present. Preserve the experiment labels;
later corrections require a versioned dataset. This diagnostic subset does not
establish dataset-wide label accuracy.

## Optional later research

New surveillance sources, longer videos, occlusion and difficult lighting would
support a more relevant transfer study. Freeze any new protocol before scoring.
Do not tune the retained epoch, threshold or model against these completed
evaluation sets. Source independence, pretraining overlap, calibrated scores,
person-level attribution and streaming evaluation require separate work.

Resume paper drafting when Vishal brings it back into scope. The previous
requirement was a complete manuscript of at least 12 pages before 20 November,
with an internal target of 19 November. The final group date remains unconfirmed.

''' + prior
    next_path.write_text(active, encoding='utf-8')


def main():
    rwf = read_json(OUT / 'rwf_evaluation/metrics.json')
    external_folder = ROOT / 'output/external_validation_20261115'
    external = read_json(external_folder / 'metrics.json')
    for folder in [OUT / 'rwf_evaluation', external_folder]:
        check_hashes(folder, read_json(folder / 'completion.json')['artifacts_sha256'])
    records = demos()
    preserve()
    plot(rwf, external)
    page(rwf, external, records)
    update_project_docs(rwf, external)
    checklist = read_json(OUT / 'completion_checklist.json')
    checklist['tasks'].update({'fresh_source_evaluation': 'complete', 'bounded_fine_tuning': 'complete',
        'independent_human_review': 'deferred_no_reviewer_available', 'final_demo_and_runbook': 'complete',
        'final_preservation_and_checks': 'complete'})
    checklist.update({'automatable_technical_work_complete': True, 'overall_complete': False,
        'remaining_required_work': ['Independent full-video label/difficulty review'], 'paper': 'Deferred by user'})
    write_json(OUT / 'completion_checklist.json', checklist)
    print('Technical outputs complete; independent review remains pending', flush=True)


if __name__ == '__main__':
    main()
