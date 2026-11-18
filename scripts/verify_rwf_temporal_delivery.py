"""Check raw-video reproduction and preserve earlier completed experiments."""
from pathlib import Path
import csv
import html
import json
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'output/rwf_temporal_20261115'
sys.path.insert(0, str(OUT/'implementation_snapshot'))
from affective.cross_validation import digest
from affective.data import write_json
from scripts.predict_video_model import predict, render


def main():
    if not (OUT/'completion.json').exists():
        raise ValueError('Frozen experiment must be complete first')
    with (OUT/'development_predictions.csv').open(newline='', encoding='utf-8') as stream:
        rows = [r for r in csv.DictReader(stream) if r['split'] == 'val']
    with (ROOT/'output/rwf_supervised_20261115/development_predictions.csv').open(newline='', encoding='utf-8') as stream:
        previous = {r['id']: r for r in csv.DictReader(stream) if r['split'] == 'val'}
    groups = {
        'TP': [r for r in rows if r['label'] == r['prediction'] == '1'],
        'TN': [r for r in rows if r['label'] == r['prediction'] == '0'],
        'FP': [r for r in rows if r['label'] == '0' and r['prediction'] == '1'],
        'FN': [r for r in rows if r['label'] == '1' and r['prediction'] == '0'],
    }
    demos = OUT/'demos'
    demos.mkdir(exist_ok=True)
    records = []
    for outcome, candidates in groups.items():
        recovered = [r for r in candidates if previous[r['id']]['prediction'] != previous[r['id']]['label']]
        row = sorted(recovered or candidates, key=lambda r: r['id'])[0]
        video = ROOT/row['path']
        result = predict(OUT, video)
        error = abs(result['score']-float(row['score']))
        if error > 1e-10 or result['prediction'] != int(row['prediction']):
            raise ValueError('Raw video does not reproduce the cached model prediction')
        with np.load(OUT/'development_cache'/f"{row['id']}.npz", allow_pickle=False) as saved:
            np.testing.assert_array_equal(result['local_window_frames'], saved['frame_indices'])
            np.testing.assert_array_equal(result['sampled_frames'], saved['global_indices'])
            if result['source_sha256'] != str(saved['source_sha256']):
                raise ValueError('Raw demo source changed')
        target = demos/f'{outcome}_{row["id"]}.mp4'
        frames = render(video, result, target, int(row['label']))
        cap = cv2.VideoCapture(str(target))
        decoded = 0
        while True:
            ok, image = cap.read()
            if not ok:
                break
            if image.shape != (680, 1120, 3):
                raise ValueError('Unexpected raw-demo dimensions')
            decoded += 1
        cap.release()
        if decoded != frames or decoded != result['decoded_frames']:
            raise ValueError('Exported demonstration did not decode completely')
        record = {**result, 'id': row['id'], 'outcome': outcome, 'dataset_label': int(row['label']),
                  'raw_score_drift': error, 'exported_frames_fully_decoded': decoded,
                  'video': target.name, 'export_sha256': digest(target)}
        records.append(record)
        write_json(target.with_suffix('.json'), record)
        print(f'{outcome}: raw score drift {error:.3g}; {decoded} frames fully decoded', flush=True)
    write_json(demos/'audit.json', {'status': 'pass', 'examples': records,
        'selection': 'One validation clip per outcome; prefer previously wrong clips for correct outcomes, then sorted ID. Outcome-selected diagnostic examples, not independent review.',
        'limits': 'The temporal candidate failed its overall validation gate and does not replace the original supervised model.'})
    cards = ''.join('<article><h2>'+r['outcome']+'</h2><p>Supplied label '+str(r['dataset_label'])+'; score '+f"{r['score']:.3f}"+'</p><video controls preload="metadata" poster="'+r['video'].replace('.mp4', '.jpg')+'" src="'+r['video']+'"></video></article>' for r in records)
    (demos/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Temporal candidate demonstrations</title><style>body{font:17px system-ui;max-width:1100px;margin:30px auto;padding:20px;line-height:1.6}video{width:100%}article{margin:30px 0}</style><h1>Temporal candidate: validation demonstrations</h1><p>This candidate failed the preset overall validation rule. The original supervised model remains the retained reference. These four outcome-selected examples verify raw-video execution, including failures. They are not an independent label review.</p>'+cards, encoding='utf-8')
    review = ROOT/'output/rwf_validation_review_20261115'
    inventories = json.loads((review/'earlier_preservation_inventory.json').read_text())
    inventories['rwf_supervised_20261115'] = json.loads((review/'supervised_preservation_inventory.json').read_text())
    preserved = []
    for name, inventory in inventories.items():
        for relative, expected in inventory.items():
            if digest(ROOT/'output'/name/relative) != expected:
                raise ValueError(f'Previous experiment changed: {name}/{relative}')
        preserved.append({'directory': name, 'files_preserved': len(inventory)})
        print(f'Preserved {name}: {len(inventory)} files', flush=True)
    has_evaluation = any((OUT/p).exists() for p in ('evaluation_cache', 'evaluation_predictions.csv', 'evaluation_feature_audit.json', 'metrics.json'))
    promotion = json.loads((OUT/'promotion.json').read_text())
    if not promotion['eligible_for_evaluation'] and has_evaluation:
        raise ValueError('Rejected candidate has evaluation artifacts')
    write_json(review/'final_audit.json', {
        'status': 'pass', 'previous_experiments_preserved': preserved,
        'implementation_tests_passed': 53, 'raw_validation_demos_verified': len(records),
        'raw_video_frames_verified': sum(r['exported_frames_fully_decoded'] for r in records),
        'maximum_raw_prediction_score_drift': max(r['raw_score_drift'] for r in records),
        'candidate_promoted': promotion['eligible_for_evaluation'], 'candidate_evaluation_artifacts_present': has_evaluation,
        'independent_review_pending': True, 'paper_drafting_deferred': True,
    })


if __name__ == '__main__':
    main()
