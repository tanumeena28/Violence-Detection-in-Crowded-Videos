"""Check committed evaluation CSVs and included artifact hashes without datasets."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import digest
from affective.train import metrics


def main():
    folders = [ROOT / 'output/final_delivery_20261115/rwf_evaluation',
               ROOT / 'output/external_validation_20261115']
    total = 0
    for folder in folders:
        expected = json.loads((folder / 'metrics.json').read_text(encoding='utf-8'))
        with (folder / 'predictions.csv').open(newline='', encoding='utf-8') as stream:
            rows = list(csv.DictReader(stream))
        for name, record in expected['models'].items():
            part = [r for r in rows if r['model'] == name]
            if len({r['id'] for r in part}) != len(part):
                raise ValueError('Duplicate prediction IDs')
            labels = np.asarray([int(r['label']) for r in part])
            scores = np.asarray([float(r['score']) for r in part])
            threshold = record['threshold']
            if any(float(r['threshold']) != threshold or int(r['prediction']) != int(float(r['score']) >= threshold) for r in part):
                raise ValueError('Saved threshold or decision differs')
            if metrics(labels, scores, threshold) != record['all_clips']:
                raise ValueError('Saved scores do not reproduce published metrics')
            total += len(part)
        completion = json.loads((folder / 'completion.json').read_text(encoding='utf-8'))
        for name, expected_hash in completion['artifacts_sha256'].items():
            path = folder / name
            if path.is_file() and digest(path) != expected_hash:
                raise ValueError(f'Committed sealed artifact changed: {path}')
        print(f'Verified {folder.name}: CSV metrics and included sealed artifacts', flush=True)
    print(f'Verified {total} model predictions across both evaluation sets. Raw-source/model verification requires the local archive.', flush=True)


if __name__ == '__main__':
    main()
