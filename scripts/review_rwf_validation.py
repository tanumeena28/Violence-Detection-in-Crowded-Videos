"""Build development-only evidence, without changing labels or model choices."""
from pathlib import Path
import csv
import json
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import digest
from affective.data import write_json


def main():
    source = ROOT / 'output/rwf_supervised_20261115'
    out = ROOT / 'output/rwf_validation_review_20261115'
    out.mkdir(exist_ok=False)
    previous = json.loads((ROOT / 'output/rwf_preparation_review_20261115/previous_artifacts_before.json').read_text())
    write_json(out / 'earlier_preservation_inventory.json', previous)
    write_json(out / 'supervised_preservation_inventory.json', {
        p.relative_to(source).as_posix(): digest(p) for p in sorted(source.rglob('*')) if p.is_file()
    })
    with (source / 'development_predictions.csv').open(newline='') as stream:
        rows = [r for r in csv.DictReader(stream) if r['split'] == 'val']
    errors = [r for r in rows if r['label'] != r['prediction']]
    # Deterministic score-stratified correct controls, six from each label.
    correct = []
    for label in ('0', '1'):
        candidates = sorted([r for r in rows if r['label'] == r['prediction'] == label], key=lambda r: float(r['score']))
        correct.extend(candidates[i] for i in np.linspace(0, len(candidates)-1, 6).round().astype(int))
    selected = sorted(errors, key=lambda r: (r['label'], float(r['score']))) + correct
    selected_ids = {r['id'] for r in selected}
    strips, records = {}, []
    for number, row in enumerate(rows, 1):
        cap = cv2.VideoCapture(str(ROOT / row['path']))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        mini, evidence = [], []
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            mini.append(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (128, 72)))
            if row['id'] in selected_ids:
                evidence.append(cv2.resize(frame, (256, 144)))
        cap.release()
        if len(mini) < 2 or fps <= 0:
            raise ValueError('Invalid validation decode')
        differences = np.abs(np.diff(np.asarray(mini, dtype=np.float32), axis=0))
        records.append({**row, 'decoded_frames': len(mini), 'fps': fps,
                        'duration_seconds': len(mini)/fps,
                        'consecutive_gray_difference': float(differences.mean()),
                        'motion_pixel_fraction_over_12': float((differences > 12).mean())})
        if row['id'] in selected_ids:
            indices = np.linspace(0, len(evidence)-1, 8).round().astype(int)
            strip = Image.new('RGB', (2048, 184), '#18222c')
            draw = ImageDraw.Draw(strip)
            outcome = 'FN' if row['label'] == '1' and row['prediction'] == '0' else 'FP' if row['label'] == '0' and row['prediction'] == '1' else 'correct control'
            draw.text((5, 5), f"{row['id']} | {outcome} | label={row['label']} score={float(row['score']):.3f} | {Path(row['path']).name}", fill='white')
            for k, index in enumerate(indices):
                strip.paste(Image.fromarray(evidence[index][..., ::-1]), (256*k, 24))
                draw.text((256*k+5, 168), f'{index/fps:.2f}s', fill='white')
            strips[row['id']] = strip
        if number % 100 == 0:
            print(f'Validation evidence {number}/{len(rows)}', flush=True)
    for page, start in enumerate(range(0, len(selected), 6), 1):
        sheet = Image.new('RGB', (2048, 1104), '#18222c')
        for k, row in enumerate(selected[start:start+6]):
            sheet.paste(strips[row['id']], (0, 184*k))
        sheet.save(out / f'validation_sheet_{page:02d}.jpg', quality=93)
    with (out / 'validation_decode_motion.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    write_json(out / 'evidence.json', {
        'partition': 'validation only', 'clips_fully_decoded': len(rows),
        'false_negatives': sum(r['label'] == '1' for r in errors),
        'false_positives': sum(r['label'] == '0' for r in errors),
        'correct_controls': len(correct), 'dense_evidence_frames_per_clip': 8,
        'evidence_order': [r['id'] for r in selected],
        'review_status': 'Prepared for assistant-assisted visual diagnosis; no independent human review',
        'limits': 'Eight sampled images do not establish full action timing or independently verify a video label. Gray difference includes camera motion and is only a descriptive diagnostic.'
    })
    print(json.dumps({'validation_clips': len(rows), 'errors': len(errors), 'sheets': (len(selected)+5)//6}), flush=True)


if __name__ == '__main__':
    main()
