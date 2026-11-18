"""Score sealed models without changing development or external selection choices."""
from __future__ import annotations

import argparse
import csv
import html
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import digest
from affective.data import read_manifest, write_json
from affective.inference import VideoPredictor, PosePredictor, decode_sample_bounded
from affective.train import metrics

FINE = ROOT / 'output/rwf_finetune_v2_20261115'
BASE = ROOT / 'output/rwf_supervised_20261115'
DELIVERY = ROOT / 'output/final_delivery_20261115'
EXTERNAL = ROOT / 'output/external_validation_20261115'
TOLERANCE = 3e-4


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check_hashes(folder, hashes):
    for name, expected in hashes.items():
        if digest(folder / name) != expected:
            raise ValueError(f'Frozen artifact changed: {folder / name}')


def implementation_hashes():
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in
            [Path(__file__), *sorted((ROOT / 'affective').glob('*.py')), ROOT / 'scripts/run_rwf_finetune.py']}


def verify_selection():
    for experiment in (FINE, BASE):
        seal = read_json(experiment / 'head_frozen.json')
        if digest(experiment / 'protocol.json') != seal['protocol_sha256']:
            raise ValueError('Development protocol changed')
        check_hashes(experiment, seal['artifacts_sha256'])
    if not read_json(FINE / 'promotion.json')['eligible_for_evaluation']:
        raise ValueError('Fine-tuning candidate failed its validation promotion rule')
    plan = read_json(EXTERNAL / 'protocol.json')
    if digest(EXTERNAL / 'manifest.csv') != plan['manifest_sha256']:
        raise ValueError('External manifest changed')
    for record in plan['models'].values():
        if digest(Path(record['path'])) != record['sha256']:
            raise ValueError('External model changed')
    for name, expected in plan['archives_sha256'].items():
        if digest(ROOT / 'data/external/HockeyFight' / name) != expected:
            raise ValueError('External archive changed')


def freeze_execution():
    out = DELIVERY / 'rwf_evaluation'
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'protocol.json'
    plan = {
        'date': '2026-11-15', 'schema': 'sealed-final-evaluation-v1',
        'selection': 'All 400 released evaluation clips, previously inspected; exploratory evaluation',
        'manifest_path': str(FINE / 'manifest.csv'), 'manifest_sha256': digest(FINE / 'manifest.csv'),
        'fine_model_sha256': digest(FINE / 'model.pt'), 'baseline_model_sha256': digest(BASE / 'model.json'),
        'fine_seal_sha256': digest(FINE / 'head_frozen.json'),
        'external_protocol_sha256': digest(EXTERNAL / 'protocol.json'),
        'implementation_sha256': implementation_hashes(),
        'choices': {'epoch': 2, 'fine_threshold': .23, 'baseline_threshold': .5},
        'precision': 'Original float32 frozen encoder; fine-tuned CUDA float16 inputs/autocast, float32 parameters',
        'decode': 'Two full sequential passes, retaining only the exact 32 uniform samples',
        'score_reproduction_tolerance': TOLERANCE,
        'preflight': 'Two validation clips per class nearest the sealed threshold; verify saved scores and decisions',
        'selection_after_scoring': False, 'device': 'cuda',
        'external_rule': 'Existing external protocol remains authoritative, including its primary frozen-video model',
    }
    if path.exists():
        if read_json(path) != plan:
            raise ValueError('Execution protocol or implementation changed; preserve this run')
    else:
        write_json(path, plan)
    return out, plan


def preflight(fine, frozen, out):
    with (FINE / 'validation_predictions.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    with (BASE / 'development_predictions.csv').open(newline='', encoding='utf-8') as stream:
        baseline = {r['id']: r for r in csv.DictReader(stream)}
    selected = []
    for label in (0, 1):
        selected.extend(sorted((r for r in rows if int(r['label']) == label),
                               key=lambda r: (abs(float(r['score']) - fine.threshold), r['id']))[:2])
    checks = []
    for row in selected:
        images, indices, fps, decoded = decode_sample_bounded(ROOT / row['path'])
        for name, predictor, reference in [('fine', fine, row), ('frozen', frozen, baseline[row['id']])]:
            result = predictor.process(images, indices, fps, decoded)
            drift = abs(result['score'] - float(reference['score']))
            if drift > TOLERANCE or result['prediction'] != int(reference['prediction']):
                raise ValueError(f'Raw-video preflight failed: {row["id"]} {name}, drift={drift}')
            checks.append({'id': row['id'], 'model': name, 'score_drift': drift, 'decision_reproduced': True})
    write_json(out / 'raw_video_preflight.json', {'status': 'pass', 'checks': checks, 'tolerance': TOLERANCE})
    print('Raw-video preflight passed for both models on four validation clips', flush=True)


def score_set(out, rows, predictors, frozen_plan):
    folder = out / 'records'
    folder.mkdir(exist_ok=True)
    protocol_hash = digest(out / 'protocol.json')
    implementation = frozen_plan['implementation_sha256']
    records = []
    started = time.perf_counter()
    for i, row in enumerate(rows, 1):
        path = ROOT / row['path']
        if digest(path) != row['sha256']:
            raise ValueError('Raw evaluation video changed')
        target = folder / f'{row["id"]}.json'
        if target.exists():
            record = read_json(target)
            if (record['source_sha256'] != row['sha256'] or record['protocol_sha256'] != protocol_hash
                    or record['implementation_sha256'] != implementation
                    or set(record['models']) != set(predictors)):
                raise ValueError('Resumed record provenance differs')
        else:
            clip_started = time.perf_counter()
            images, indices, fps, decoded = decode_sample_bounded(path)
            record = {'id': row['id'], 'path': row['path'], 'label': int(row['label']),
                      'source_sha256': row['sha256'], 'protocol_sha256': protocol_hash,
                      'implementation_sha256': implementation, 'decoded_frames': decoded,
                      'header_frames': int(row['frames']), 'fps': fps,
                      'models': {name: predictor.process(images, indices, fps, decoded)
                                 for name, predictor in predictors.items()},
                      'seconds_including_decode_and_all_models': time.perf_counter() - clip_started}
            write_json(target, record)
        for name, result in record['models'].items():
            if (not np.isfinite(result['score']) or not 0 <= result['score'] <= 1
                    or result['threshold'] != predictors[name].threshold
                    or result['prediction'] != int(result['score'] >= result['threshold'])
                    or result['model_sha256'] != predictors[name].model_hash):
                raise ValueError('Invalid saved model score or threshold')
        records.append(record)
        if i == 1 or i % 100 == 0 or i == len(rows):
            print(f'{out.name}: {i}/{len(rows)} clips | {time.perf_counter()-started:.0f}s', flush=True)
    check_hashes(ROOT, implementation)
    labels = np.asarray([r['label'] for r in records])
    result = {'date': '2026-11-15', 'models': {}, 'device': 'cuda', 'gpu': torch.cuda.get_device_name(0),
              'all_clips': len(rows), 'labels': 'Unchanged supplied dataset labels, independently unreviewed',
              'scoring_record_seconds': sum(r['seconds_including_decode_and_all_models'] for r in records),
              'runtime_boundary': 'Shared full decode and all declared GPU models per clip; initialization/reporting excluded. Offline, not streaming.'}
    prediction_rows = []
    for name, predictor in predictors.items():
        scores = np.asarray([r['models'][name]['score'] for r in records])
        result['models'][name] = {'threshold': predictor.threshold, 'all_clips': metrics(labels, scores, predictor.threshold)}
        if name == 'crowd_pose_interactions':
            supported = np.asarray([not r['models'][name]['abstain'] for r in records])
            result['models'][name].update({'pose_supported_clips': int(supported.sum()),
                'pose_supported_subset': metrics(labels[supported], scores[supported], predictor.threshold) if supported.any() else None})
        prediction_rows.extend({'id': r['id'], 'path': r['path'], 'sha256': r['source_sha256'], 'label': r['label'],
            'model': name, 'score': r['models'][name]['score'], 'threshold': predictor.threshold,
            'prediction': r['models'][name]['prediction'], 'abstain': r['models'][name]['abstain'],
            'decoded_frames': r['decoded_frames']} for r in records)
    with (out / 'predictions.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(prediction_rows[0]))
        writer.writeheader(); writer.writerows(prediction_rows)
    write_json(out / 'metrics.json', result)
    groups = defaultdict(list)
    for row in rows:
        groups[row['sha256']].append({'id': row['id'], 'label': int(row['label']), 'path': row['path']})
    duplicates = [values for values in groups.values() if len(values) > 1]
    write_json(out / 'audit.json', {'status': 'pass', 'fully_decoded_clips': len(records),
        'header_decode_mismatches': [r['id'] for r in records if r['decoded_frames'] != r['header_frames']],
        'source_hashes_verified': True, 'frozen_models_and_thresholds_verified': True,
        'unique_byte_hashes': len(groups), 'duplicate_groups': duplicates,
        'metrics_reproduced_from_saved_scores': True, 'evaluation_fitting_or_selection': False})
    # Reproduce aggregate metrics from the actual CSV delivery artifact.
    with (out / 'predictions.csv').open(newline='', encoding='utf-8') as stream:
        saved = list(csv.DictReader(stream))
    for name in predictors:
        part = [r for r in saved if r['model'] == name]
        if metrics(np.asarray([int(r['label']) for r in part]), np.asarray([float(r['score']) for r in part]),
                   predictors[name].threshold) != result['models'][name]['all_clips']:
            raise ValueError('Saved CSV does not reproduce metrics')
    return result


def report(out, title, result, limitation):
    lines = [f'# {title}', '', limitation, '', '| Model | Clips | Accuracy | Macro-F1 | AUC | Fight recall | False alarms | Misses |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for name, record in result['models'].items():
        m = record['all_clips']; cm = m['confusion_matrix']
        lines.append(f'| {name} (threshold {record["threshold"]:.2f}) | {m["n"]} | {m["accuracy"]:.2%} | '
                     f'{m["macro_f1"]:.3f} | {m["roc_auc"]:.3f} | {m["recall_violent"]:.1%} | {cm[0][1]} | {cm[1][0]} |')
    lines.extend(['', 'Every model retains its development threshold and normalization. All supplied labels are unchanged.', '',
                  '[Predictions](predictions.csv) | [Metrics](metrics.json) | [Audit](audit.json) | [Protocol](protocol.json)', ''])
    (out / 'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    table = '<table><tr><th>Model</th><th>Accuracy</th><th>Macro-F1</th><th>AUC</th><th>False alarms</th><th>Misses</th></tr>'
    for name, r in result['models'].items():
        m = r['all_clips']; cm = m['confusion_matrix']
        table += f'<tr><td>{html.escape(name)}</td><td>{m["accuracy"]:.2%}</td><td>{m["macro_f1"]:.3f}</td><td>{m["roc_auc"]:.3f}</td><td>{cm[0][1]}</td><td>{cm[1][0]}</td></tr>'
    page = f'<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>body{{font:16px system-ui;margin:40px auto;max-width:1100px;padding:20px;color:#17232d}}td,th{{padding:14px;border-bottom:1px solid #ddd;text-align:left}}table{{border-collapse:collapse}}p{{line-height:1.6}}</style><h1>{title}</h1><p>{html.escape(limitation)}</p>{table}</table><p>All supplied labels and sealed thresholds retained. Scores are not calibrated probabilities.</p><p><a href="RESULTS.md">Results notes</a> | <a href="predictions.csv">Per-clip scores</a> | <a href="audit.json">Audit</a> | <a href="protocol.json">Protocol</a></p></html>'
    (out / 'index.html').write_text(page, encoding='utf-8')
    names = ['protocol.json', 'predictions.csv', 'metrics.json', 'audit.json', 'RESULTS.md', 'index.html']
    write_json(out / 'completion.json', {'status': 'complete', 'artifacts_sha256':
        {**{name: digest(out / name) for name in names},
         **{p.relative_to(out).as_posix(): digest(p) for p in (out / 'records').glob('*.json')}}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    verify_selection()
    rwf_out, execution = freeze_execution()
    if args.verify_only:
        for out in (rwf_out, EXTERNAL):
            check_hashes(out, read_json(out / 'completion.json')['artifacts_sha256'])
        print('Both final evaluation artifact sets verified', flush=True)
        return
    if not torch.cuda.is_available():
        raise RuntimeError('These evaluations require the authorized local CUDA GPU')
    fine, frozen = VideoPredictor(FINE), VideoPredictor(BASE)
    preflight(fine, frozen, rwf_out)
    # Expose the same sealed threshold check for the pose diagnostic.
    pose = PosePredictor()
    pose.threshold = pose.saved['threshold']
    rwf_rows = [r for r in read_manifest(FINE / 'manifest.csv') if r['split'] == 'test']
    if len(rwf_rows) != 400:
        raise ValueError('Expected all 400 RWF released evaluation clips')
    result = score_set(rwf_out, rwf_rows, {'rwf_frozen_video': frozen, 'rwf_finetuned_video': fine}, execution)
    with (BASE / 'evaluation_predictions.csv').open(newline='', encoding='utf-8') as stream:
        old = {r['id']: r for r in csv.DictReader(stream)}
    with (rwf_out / 'predictions.csv').open(newline='', encoding='utf-8') as stream:
        saved = [r for r in csv.DictReader(stream) if r['model'] == 'rwf_frozen_video']
    drift = max(abs(float(r['score']) - float(old[r['id']]['score'])) for r in saved)
    if drift > TOLERANCE or any(int(r['prediction']) != int(old[r['id']]['prediction']) for r in saved):
        raise ValueError('Original frozen RWF scores do not reproduce')
    write_json(rwf_out / 'baseline_reproduction.json', {'status': 'pass', 'clips': 400, 'max_score_drift': drift})
    report(rwf_out, 'Sealed fine-tuned RWF evaluation', result, 'Exploratory supervised evaluation on 400 previously inspected RWF clips. Epoch 2 and threshold 0.23 were selected solely on validation and sealed before evaluation.')
    external_rows = read_manifest(EXTERNAL / 'manifest.csv')
    if len(external_rows) != 1000:
        raise ValueError('Expected the full 1,000-clip Hockey Fight mirror')
    result = score_set(EXTERNAL, external_rows, {'rwf_frozen_video': frozen, 'rwf_finetuned_video': fine,
                                               'crowd_pose_interactions': pose}, execution)
    report(EXTERNAL, 'Fixed-model Hockey Fight external evaluation', result, read_json(EXTERNAL / 'protocol.json')['limits'] + ' Primary: fixed frozen-video reference. All 1,000 released clips retained, including three duplicate files; 997 unique byte hashes. No byte overlap with the compared prior inventory, which does not establish source independence.')
    verify_selection()
    print(json.dumps(result['models'], indent=2), flush=True)


if __name__ == '__main__':
    main()
