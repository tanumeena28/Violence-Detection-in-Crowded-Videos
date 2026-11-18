"""Freeze and test one global/local temporal RWF development candidate."""
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
from affective.cross_validation import digest
from affective.data import read_manifest, write_json
from affective.motion import score_linear
from affective.rwf_supervised import fit_development_head
from affective.temporal_video import SETTINGS, combine_embeddings, decode_windows, encode_indices, window_indices
from affective.train import choose_threshold, metrics

LIMITS = ('Exploratory supervised RWF development on the same source-grouped split. '
          'The released evaluation clips have already been inspected in previous experiments. '
          'This is not an untouched test or an independent confirmation of generalization. '
          'No supplied labels changed. Independent human label review, near-duplicate and pretraining overlap audits remain pending. '
          'Whole-clip scores are not calibrated probabilities or person-level attribution.')


def write_rows(path, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def development_gate(selection, baseline):
    """Only validation evidence is accepted by the predeclared promotion rule."""
    loss = min(r['validation_log_loss'] for r in selection['candidates'])
    baseline_loss = min(r['validation_log_loss'] for r in baseline['candidates'])
    candidate, reference = selection['validation'], baseline['validation']
    criteria = {
        'log_loss_improved': loss < baseline_loss,
        'macro_f1_improved': candidate['macro_f1'] > reference['macro_f1'],
        'fight_recall_not_reduced': candidate['recall_violent'] >= reference['recall_violent'],
    }
    return {'eligible_for_evaluation': all(criteria.values()), 'criteria': criteria,
            'baseline_validation_log_loss': baseline_loss, 'candidate_validation_log_loss': loss,
            'baseline_validation': reference, 'candidate_validation': candidate,
            'decision_inputs': 'Validation only; no evaluation metrics accepted'}


def prepare(source, review, out):
    if out.exists():
        raise FileExistsError('Frozen experiments are never overwritten')
    baseline = json.loads((source / 'protocol.json').read_text())
    selection = json.loads((source / 'selection.json').read_text())
    audit = json.loads((source / 'development_feature_audit.json').read_text())
    for relative, expected in json.loads((source / 'completion.json').read_text())['artifacts_sha256'].items():
        if digest(source / relative) != expected:
            raise ValueError('Original supervised artifact changed')
    out.mkdir(parents=True)
    shutil.copy2(source / 'manifest.csv', out / 'manifest.csv')
    (out / 'weights').mkdir()
    shutil.copy2(source / 'weights' / baseline['encoder']['weights_file'], out / 'weights' / baseline['encoder']['weights_file'])
    feature_settings = {**SETTINGS, 'encoder': baseline['encoder'],
                        'global_encoder_signature': baseline['encoder_signature']}
    signature = hashlib.sha256(json.dumps(feature_settings, sort_keys=True).encode()).hexdigest()
    plan = {
        'schema': SETTINGS['schema'], 'date': '2026-11-15', 'encoder': baseline['encoder'],
        'feature_settings': feature_settings, 'encoder_signature': signature,
        'feature_dimensions': SETTINGS['feature_dimensions'], 'manifest_sha256': digest(out / 'manifest.csv'),
        'source_experiment': str(source), 'source_protocol_sha256': digest(source / 'protocol.json'),
        'source_development_audit_sha256': digest(source / 'development_feature_audit.json'),
        'source_development_cache_sha256': audit['cache_sha256'],
        'baseline_selection': selection, 'baseline_selection_sha256': digest(source / 'selection.json'),
        'diagnosis_file': str(review / 'DIAGNOSIS.md'), 'diagnosis_sha256': digest(review / 'DIAGNOSIS.md'),
        'evaluation_global_cache': baseline['evaluation_cache'], 'split': baseline['split'],
        'regularization': baseline['regularization'], 'maximum_iterations': 2000,
        'head_solver': 'lbfgs', 'C_selection': baseline['C_selection'],
        'threshold_selection': baseline['threshold_selection'],
        'promotion_rule': 'Strictly lower validation log loss and strictly higher validation macro-F1, with Fight recall at least the baseline; otherwise stop at development results',
        'selection_boundary': 'Seal development caches, fitted head and promotion decision before loading evaluation global arrays or extracting evaluation local features',
        'candidate_count': 1, 'device': 'cuda', 'precision': 'float32 encoder; float64 logistic head',
        'cpu_threads': 4, 'packages': baseline['packages'],
        'script_sha256': digest(Path(__file__)),
        'implementation_sha256': {p.name: digest(p) for p in (ROOT / 'affective').glob('*.py')},
        'limitations': LIMITS,
    }
    write_json(out / 'protocol.json', plan)
    snapshot = out / 'implementation_snapshot'
    shutil.copytree(ROOT / 'affective', snapshot / 'affective', ignore=shutil.ignore_patterns('__pycache__'))
    (snapshot / 'scripts').mkdir()
    shutil.copy2(Path(__file__), snapshot / 'scripts' / Path(__file__).name)
    shutil.copy2(ROOT / 'scripts/predict_video_model.py', snapshot / 'scripts/predict_video_model.py')
    (out / 'run_snapshot.py').write_text('import sys\nfrom pathlib import Path\ne=Path(__file__).resolve().parent\n'
        'sys.path.insert(0,str(e/"implementation_snapshot"))\nfrom scripts.run_rwf_temporal import main\n'
        'sys.argv=[sys.argv[0],"--out",str(e),*sys.argv[1:]]\nmain()\n', encoding='utf-8')
    return plan


def validate(out, plan):
    if digest(Path(__file__)) != plan['script_sha256']:
        raise ValueError('Use the frozen temporal runner')
    for name, expected in plan['implementation_sha256'].items():
        if digest(Path(__file__).resolve().parents[1] / 'affective' / name) != expected:
            raise ValueError('Use the frozen temporal implementation')
    if digest(out / 'manifest.csv') != plan['manifest_sha256']:
        raise ValueError('Source split changed')
    if digest(out / 'weights' / plan['encoder']['weights_file']) != plan['encoder']['weights_sha256']:
        raise ValueError('Encoder weights changed')
    source = Path(plan['source_experiment'])
    for name, key in [('protocol.json', 'source_protocol_sha256'), ('selection.json', 'baseline_selection_sha256'),
                      ('development_feature_audit.json', 'source_development_audit_sha256')]:
        if digest(source / name) != plan[key]:
            raise ValueError('Frozen reference evidence changed')
    if digest(Path(plan['diagnosis_file'])) != plan['diagnosis_sha256']:
        raise ValueError('Pre-fit diagnosis changed')
    if any(version(name) != expected for name, expected in plan['packages'].items()):
        raise ValueError('Use the recorded package versions')


def validate_head(out):
    seal = json.loads((out / 'head_frozen.json').read_text())
    if digest(out / 'protocol.json') != seal['protocol_sha256']:
        raise ValueError('Selected protocol changed')
    for name, expected in seal['artifacts_sha256'].items():
        if digest(out / name) != expected:
            raise ValueError('Selected development artifact changed')
    return json.loads((out / 'promotion.json').read_text())


def evaluation_globals(out, plan):
    if not validate_head(out)['eligible_for_evaluation']:
        raise ValueError('Candidate failed development gate; evaluation is not permitted')
    settings = plan['evaluation_global_cache']
    source = Path(settings['path'])
    for name, key in [('features.npz', 'features_sha256'), ('manifest.csv', 'manifest_sha256'), ('protocol.json', 'protocol_sha256')]:
        if digest(source / name) != settings[key]:
            raise ValueError('Frozen global evaluation cache changed')
    rows = [r for r in read_manifest(out / 'manifest.csv') if r['split'] == 'test']
    cached = read_manifest(source / 'manifest.csv')
    if sorted((r['id'], r['sha256'], r['label']) for r in rows) != sorted((r['id'], r['sha256'], r['label']) for r in cached):
        raise ValueError('Global evaluation cache refers to different sources')
    with np.load(source / 'features.npz', allow_pickle=False) as saved:
        return dict(zip(saved['ids'].tolist(), saved['features']))


def extract(root, out, plan, partition):
    global_test = evaluation_globals(out, plan) if partition == 'evaluation' else None
    rows = [r for r in read_manifest(out / 'manifest.csv') if (r['split'] == 'test') == (partition == 'evaluation')]
    torch.set_num_threads(4)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    model = r3d_18(weights=None)
    model.load_state_dict(torch.load(out / 'weights' / plan['encoder']['weights_file'], map_location='cpu', weights_only=True))
    model.fc = torch.nn.Identity()
    model.eval().to('cuda')
    transform = R3D_18_Weights.KINETICS400_V1.transforms()
    cache = out / f'{partition}_cache'
    cache.mkdir(exist_ok=True)
    started, records = time.perf_counter(), []
    torch.cuda.reset_peak_memory_stats()
    for number, row in enumerate(rows, 1):
        target = cache / f"{row['id']}.npz"
        if target.exists():
            with np.load(target, allow_pickle=False) as saved:
                if str(saved['source_sha256']) != row['sha256'] or str(saved['encoder_signature']) != plan['encoder_signature']:
                    raise ValueError('Temporal cache provenance changed')
                records.append(json.loads(str(saved['record'])))
            continue
        if global_test is None:
            global_path = Path(plan['source_experiment']) / 'development_cache' / f"{row['id']}.npz"
            if digest(global_path) != plan['source_development_cache_sha256'][row['id']]:
                raise ValueError('Reference global development cache changed')
            with np.load(global_path, allow_pickle=False) as saved:
                if (str(saved['source_sha256']) != row['sha256'] or
                        str(saved['encoder_signature']) != plan['feature_settings']['global_encoder_signature']):
                    raise ValueError('Reference development cache provenance changed')
                global_vector = saved['features'].copy()
        else:
            global_vector = global_test[row['id']]
        path = root / row['path']
        if digest(path) != row['sha256']:
            raise ValueError('Raw video changed')
        frames, indices, global_indices, fps = decode_windows(path)
        local = encode_indices(model, transform, frames, indices, 'cuda')
        features = combine_embeddings(global_vector, local)
        record = {'id': row['id'], 'split': row['split'], 'decoded_frames': len(frames), 'fps': fps,
                  'duration_seconds': len(frames)/fps, 'local_indices': indices.tolist()}
        temporary = target.with_suffix('.tmp.npz')
        np.savez_compressed(temporary, features=features, local_embeddings=local, frame_indices=indices,
                            global_indices=global_indices, source_sha256=np.array(row['sha256']),
                            encoder_signature=np.array(plan['encoder_signature']), record=np.array(json.dumps(record)))
        temporary.replace(target)
        records.append(record)
        if number == 1 or number % 50 == 0 or number == len(rows):
            elapsed = time.perf_counter()-started
            print(f'{partition} temporal features {number}/{len(rows)} | elapsed {elapsed:.0f}s', flush=True)
    write_json(out / f'{partition}_feature_audit.json', {'clips': records, 'clips_encoded': len(records),
        'wall_seconds': time.perf_counter()-started, 'gpu': torch.cuda.get_device_name(0),
        'peak_allocated_gpu_bytes': torch.cuda.max_memory_allocated(),
        'cache_sha256': {p.stem: digest(p) for p in sorted(cache.glob('*.npz'))}})


def arrays(out, plan, partition):
    rows = [r for r in read_manifest(out / 'manifest.csv') if (r['split'] == 'test') == (partition == 'evaluation')]
    audit = json.loads((out / f'{partition}_feature_audit.json').read_text())
    if set(audit['cache_sha256']) != {r['id'] for r in rows}:
        raise ValueError('Incomplete temporal features')
    vectors = []
    for row in rows:
        path = out / f'{partition}_cache' / f"{row['id']}.npz"
        if digest(path) != audit['cache_sha256'][row['id']]:
            raise ValueError('Temporal feature bytes changed')
        with np.load(path, allow_pickle=False) as saved:
            if str(saved['source_sha256']) != row['sha256'] or str(saved['encoder_signature']) != plan['encoder_signature']:
                raise ValueError('Temporal feature provenance changed')
            record = json.loads(str(saved['record']))
            np.testing.assert_array_equal(saved['frame_indices'], window_indices(record['decoded_frames'], record['fps']))
            np.testing.assert_array_equal(saved['features'], combine_embeddings(saved['features'][:512], saved['local_embeddings']))
            vectors.append(saved['features'])
    return rows, np.asarray(vectors, np.float64)


def freeze_head(out, plan):
    rows, features = arrays(out, plan, 'development')
    train = np.array([r['split'] == 'train' for r in rows])
    labels = np.array([r['label'] for r in rows])
    checkpoint, selection = fit_development_head(features[train], labels[train], features[~train], labels[~train], plan['regularization'])
    if any(c['iterations'] >= 2000 for c in selection['candidates']):
        raise ValueError('Unconverged head')
    checkpoint.update({'name': 'rwf_r3d18_global_local', 'feature_signature': plan['encoder_signature'],
                       'protocol_sha256': digest(out / 'protocol.json')})
    write_json(out / 'model.json', checkpoint)
    write_json(out / 'selection.json', selection)
    write_json(out / 'promotion.json', development_gate(selection, plan['baseline_selection']))
    scores = score_linear(features, checkpoint)
    write_rows(out / 'development_predictions.csv', [{**{key: r[key] for key in ('id', 'path', 'split', 'label')},
        'score': float(score), 'prediction': int(score >= checkpoint['threshold'])} for r, score in zip(rows, scores)])
    write_json(out / 'head_frozen.json', {'status': 'selected_before_evaluation', 'protocol_sha256': digest(out / 'protocol.json'),
        'artifacts_sha256': {name: digest(out / name) for name in ('model.json', 'selection.json', 'promotion.json',
            'development_predictions.csv', 'development_feature_audit.json')}, 'boundary': plan['selection_boundary']})
    print(json.dumps({'selected_C': checkpoint['selected_C'], 'threshold': checkpoint['threshold'],
        'validation': selection['validation'], 'promotion': validate_head(out)}, indent=2), flush=True)


def evaluate(out, plan):
    if not validate_head(out)['eligible_for_evaluation']:
        raise ValueError('Candidate failed the development gate')
    rows, features = arrays(out, plan, 'evaluation')
    if len(rows) != 400 or len({r['id'] for r in rows}) != 400:
        raise ValueError('All 400 released evaluation clips must be retained')
    checkpoint = json.loads((out / 'model.json').read_text())
    scores = score_linear(features, checkpoint)
    write_rows(out / 'evaluation_predictions.csv', [{**{key: r[key] for key in ('id', 'path', 'split', 'label')},
        'score': float(score), 'prediction': int(score >= checkpoint['threshold'])} for r, score in zip(rows, scores)])
    selection = json.loads((out / 'selection.json').read_text())
    result = {**{key: selection[key] for key in ('train', 'validation', 'selected_C', 'threshold')},
              'test': metrics([r['label'] for r in rows], scores, checkpoint['threshold']),
              'head_frozen_before_evaluation': True, 'limitations': LIMITS}
    write_json(out / 'metrics.json', result)
    return result


def verify(out, plan):
    promotion = validate_head(out)
    rows, features = arrays(out, plan, 'development')
    checkpoint = json.loads((out / 'model.json').read_text())
    train = np.array([r['split'] == 'train' for r in rows])
    labels = np.array([r['label'] for r in rows])
    np.testing.assert_array_equal(checkpoint['mean'], features[train].mean(0))
    np.testing.assert_array_equal(checkpoint['std'], np.maximum(features[train].std(0), .01))
    selection = json.loads((out / 'selection.json').read_text())
    assert promotion == development_gate(selection, plan['baseline_selection'])
    result = None
    partitions = [('development', rows, features)]
    if (out / 'metrics.json').exists():
        if not promotion['eligible_for_evaluation']:
            raise ValueError('Rejected candidate was evaluated')
        test_rows, test_features = arrays(out, plan, 'evaluation')
        global_test = evaluation_globals(out, plan)
        np.testing.assert_array_equal(test_features[:, :512], np.asarray([global_test[r['id']] for r in test_rows]))
        partitions.append(('evaluation', test_rows, test_features))
        result = json.loads((out / 'metrics.json').read_text())
    for partition, subset, vectors in partitions:
        scores = score_linear(vectors, checkpoint)
        with (out / f'{partition}_predictions.csv').open(newline='') as stream:
            saved = list(csv.DictReader(stream))
        assert [(r['id'], int(r['label'])) for r in saved] == [(r['id'], r['label']) for r in subset]
        np.testing.assert_allclose(scores, [float(r['score']) for r in saved], atol=1e-12, rtol=0)
        np.testing.assert_array_equal(scores >= checkpoint['threshold'], [int(r['prediction']) for r in saved])
        if partition == 'evaluation':
            assert len(subset) == 400
            assert metrics([r['label'] for r in subset], scores, checkpoint['threshold']) == result['test']
    scores = score_linear(features, checkpoint)
    assert checkpoint['threshold'] == choose_threshold(labels[~train], scores[~train])
    for key, mask in [('train', train), ('validation', ~train)]:
        assert metrics(labels[mask], scores[mask], checkpoint['threshold']) == selection[key]
    selected_loss = next(c['validation_log_loss'] for c in selection['candidates'] if c['C'] == checkpoint['selected_C'])
    assert abs(float(log_loss(labels[~train], scores[~train])) - selected_loss) < 1e-12
    assert checkpoint['selected_C'] == min(selection['candidates'], key=lambda c: c['validation_log_loss'])['C']
    sets = [{r['source_group'] for r in read_manifest(out / 'manifest.csv') if r['split'] == split} for split in ('train', 'val', 'test')]
    assert not (sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2])
    write_json(out / 'audit.json', {'status': 'pass', 'development_caches_verified': len(rows),
        'evaluation_caches_verified': 400 if result else 0, 'train_only_scaling_verified': True,
        'source_groups_disjoint': True, 'sampling_and_pooling_reproduced': True,
        'promotion_and_selection_reproduced': True, 'scores_and_metrics_reproduced': True,
        'head_seal_unchanged': True})
    return result or {**selection, 'limitations': LIMITS}


def report(out, result):
    promoted = json.loads((out / 'promotion.json').read_text())['eligible_for_evaluation']
    table = '\n'.join(f"| {key} | {result[key]['n']} | {result[key]['accuracy']:.2%} | {result[key]['macro_f1']:.3f} | {result[key]['recall_violent']:.3f} | {result[key]['roc_auc']:.3f} |"
        for key in ('train', 'validation', 'test') if key in result)
    text = '# RWF global and local temporal video study\n\nOne frozen R3D-18 candidate: original whole-clip mean plus four local 16-frame windows, pooled by mean and maximum. Same source split and development-only selection.\n\n| Partition | Clips | Accuracy | Macro-F1 | Fight recall | AUC |\n|---|---:|---:|---:|---:|---:|\n' + table
    text += f"\n\nC={result['selected_C']}; threshold={result['threshold']:.2f}. Predeclared development promotion rule passed: {promoted}.\n\n"
    if not promoted:
        text += 'The candidate was retained as a negative development finding. Released evaluation arrays were not loaded and no evaluation features were extracted.\n\n'
    text += LIMITS + '\n\n[Protocol](protocol.json) | [Development decision](promotion.json) | [Verification](audit.json)\n'
    (out / 'RESULTS.md').write_text(text, encoding='utf-8')
    (out / 'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RWF temporal study</title><style>body{font:17px system-ui;max-width:1050px;margin:35px auto;padding:20px;line-height:1.6}pre{white-space:pre-wrap}</style><h1>RWF temporal video study</h1><pre>' + html.escape(text) + '</pre>', encoding='utf-8')
    print(text, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--source', type=Path, default=Path('output/rwf_supervised_20261115'))
    parser.add_argument('--review', type=Path, default=Path('output/rwf_validation_review_20261115'))
    parser.add_argument('--out', type=Path, default=Path('output/rwf_temporal_20261115'))
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--development-only', action='store_true')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    out = args.out.resolve()
    plan = json.loads((out / 'protocol.json').read_text()) if out.exists() else prepare(args.source.resolve(), args.review.resolve(), out)
    validate(out, plan)
    if args.prepare_only:
        print('Temporal protocol frozen before extraction or fitting', flush=True)
        return
    if (out / 'completion.json').exists():
        for name, expected in json.loads((out / 'completion.json').read_text())['artifacts_sha256'].items():
            if digest(out / name) != expected:
                raise ValueError('Completed temporal artifact changed')
    elif not args.verify_only:
        if not (out / 'head_frozen.json').exists():
            extract(args.root.resolve(), out, plan, 'development')
            freeze_head(out, plan)
        if args.development_only:
            report(out, verify(out, plan))
            return
        if validate_head(out)['eligible_for_evaluation'] and not (out / 'metrics.json').exists():
            extract(args.root.resolve(), out, plan, 'evaluation')
            evaluate(out, plan)
    result = verify(out, plan)
    report(out, result)
    if not (out / 'completion.json').exists():
        names = ['protocol.json', 'manifest.csv', 'model.json', 'selection.json', 'promotion.json',
                 'head_frozen.json', 'development_predictions.csv', 'development_feature_audit.json']
        names += [name for name in ('metrics.json', 'evaluation_predictions.csv', 'evaluation_feature_audit.json') if (out / name).exists()]
        write_json(out / 'completion.json', {'status': 'complete', 'evaluation_performed': 'test' in result,
            'artifacts_sha256': {name: digest(out / name) for name in names}})


if __name__ == '__main__':
    main()
