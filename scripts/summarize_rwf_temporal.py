"""Report paired temporal-study results after development selection is sealed."""
from pathlib import Path
import csv
import html
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.data import write_json
from scripts.run_rwf_temporal import validate_head


def read(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def main():
    out = ROOT / 'output/rwf_temporal_20261115'
    source = ROOT / 'output/rwf_supervised_20261115'
    promotion = validate_head(out)
    if not (out / 'completion.json').exists():
        raise ValueError('Finish and verify the frozen study before reporting comparisons')
    manifest = {r['id']: r for r in read(out/'manifest.csv')}
    partitions = ['validation']
    if (out/'metrics.json').exists():
        if not promotion['eligible_for_evaluation']:
            raise ValueError('Evaluation comparison is not permitted for a rejected candidate')
        partitions.append('evaluation')
    changes, summary = [], {}
    fig, axes = plt.subplots(len(partitions), 3, figsize=(13, 4.6*len(partitions)), squeeze=False)
    for number, partition in enumerate(partitions):
        name = 'development_predictions.csv' if partition == 'validation' else 'evaluation_predictions.csv'
        previous = {r['id']: r for r in read(source/name) if partition != 'validation' or r['split'] == 'val'}
        current = [r for r in read(out/name) if partition != 'validation' or r['split'] == 'val']
        if set(previous) != {r['id'] for r in current}:
            raise ValueError('Paired clips differ')
        labels = np.array([int(r['label']) for r in current])
        baseline_scores = np.array([float(previous[r['id']]['score']) for r in current])
        scores = np.array([float(r['score']) for r in current])
        old_predictions = np.array([int(previous[r['id']]['prediction']) for r in current])
        predictions = np.array([int(r['prediction']) for r in current])
        old_ok, new_ok = old_predictions == labels, predictions == labels
        group_delta = {}
        for i, row in enumerate(current):
            group = manifest[row['id']]['source_group']
            group_delta[group] = group_delta.get(group, 0) + int(new_ok[i])-int(old_ok[i])
            if old_predictions[i] != predictions[i]:
                changes.append({'partition': partition, 'id': row['id'], 'source_group': group, 'path': row['path'],
                    'label': int(labels[i]), 'previous_score': float(baseline_scores[i]), 'new_score': float(scores[i]),
                    'previous_prediction': int(old_predictions[i]), 'new_prediction': int(predictions[i]),
                    'transition': 'recovered' if new_ok[i] else 'regressed'})
        summary[partition] = {
            'n': len(current), 'both_correct': int((old_ok & new_ok).sum()),
            'both_wrong': int((~old_ok & ~new_ok).sum()), 'recovered': int((~old_ok & new_ok).sum()),
            'regressed': int((old_ok & ~new_ok).sum()),
            'baseline_accuracy': float(old_ok.mean()), 'new_accuracy': float(new_ok.mean()),
            'accuracy_difference_percentage_points': float((new_ok.mean()-old_ok.mean())*100),
            'source_groups_with_positive_net_change': sum(value > 0 for value in group_delta.values()),
            'source_groups_with_negative_net_change': sum(value < 0 for value in group_delta.values()),
            'source_groups_with_zero_net_change': sum(value == 0 for value in group_delta.values()),
            'source_group_net_correct_clip_changes': group_delta,
            'limits': 'Descriptive paired comparison. Sources and clips are dependent; repeated validation selection and previously inspected evaluation footage prevent independent confirmation.'}
        for col, (model_name, predicted) in enumerate([('Original global video', old_predictions), ('Global and local video', predictions)]):
            matrix = confusion_matrix(labels, predicted, labels=[0, 1])
            axes[number, col].imshow(matrix, cmap='Blues')
            for i in range(2):
                for j in range(2):
                    axes[number, col].text(j, i, str(matrix[i, j]), ha='center', va='center', fontsize=20,
                        color='white' if matrix[i, j] > matrix.max()/2 else 'black')
            axes[number, col].set_xticks([0, 1], ['NonFight', 'Fight'])
            axes[number, col].set_yticks([0, 1], ['NonFight', 'Fight'])
            axes[number, col].set(title=f'{partition.title()}: {model_name}', xlabel='Prediction', ylabel='Supplied label')
        for values, title, color in [(baseline_scores, 'Original', '#64748b'), (scores, 'Temporal', '#087f8c')]:
            fpr, tpr, _ = roc_curve(labels, values)
            axes[number, 2].plot(fpr, tpr, label=f'{title} AUC {roc_auc_score(labels, values):.3f}', color=color)
        axes[number, 2].plot([0, 1], [0, 1], '--', color='#aaaaaa', lw=1)
        axes[number, 2].set(title=f'{partition.title()} ROC', xlabel='False-positive rate', ylabel='True-positive rate', xlim=(0, 1), ylim=(0, 1.02))
        axes[number, 2].legend(loc='lower right')
        axes[number, 2].grid(alpha=.2)
    (out/'figures').mkdir(exist_ok=True)
    fig.text(.5, .012, 'Exploratory development; unchanged supplied labels. Thresholds selected on validation. Evaluation footage inspected previously.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(out/'figures/paired_diagnostics.png', dpi=180)
    plt.close(fig)
    write_json(out/'paired_comparison.json', summary)
    if changes:
        with (out/'changed_predictions.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(changes[0]))
            writer.writeheader()
            writer.writerows(changes)
    lines = ['# Paired temporal video comparison', '', '| Partition | Previous accuracy | Temporal accuracy | Old errors fixed | New errors introduced |', '|---|---:|---:|---:|---:|']
    for partition, result in summary.items():
        lines.append(f"| {partition} | {result['baseline_accuracy']:.2%} | {result['new_accuracy']:.2%} | {result['recovered']} | {result['regressed']} |")
    lines += ['', 'This comparison uses identical clips and source groups with unchanged labels. Each head has its own validation-selected threshold. The temporal candidate and evaluation eligibility were frozen before evaluation features were read. These are exploratory development results, not an independent generalization claim.', '', '[Changed predictions](changed_predictions.csv) | [Per-source changes](paired_comparison.json) | [Development decision](promotion.json)', '', '![Paired diagnostics](figures/paired_diagnostics.png)']
    (out/'COMPARISON.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    notes = (out/'RESULTS.md').read_text()+'\n'+'\n'.join(lines)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RWF temporal results</title><style>body{font:17px system-ui;max-width:1200px;margin:35px auto;padding:20px;line-height:1.6}pre{white-space:pre-wrap}img{max-width:100%}a{color:#087f8c}</style><h1>RWF temporal video results</h1><pre>'+html.escape(notes)+'</pre><p><a href="protocol.json">Frozen protocol</a> | <a href="audit.json">Verification</a> | <a href="COMPARISON.md">Paired comparison</a> | <a href="demos/index.html">Raw-video demonstrations</a></p><img src="figures/paired_diagnostics.png" alt="Paired confusion matrices and ROC curves">', encoding='utf-8')
    review = ROOT/'output/rwf_validation_review_20261115'
    images = ''.join(f'<h2>Sheet {i}</h2><img src="validation_sheet_{i:02d}.jpg" alt="Validation evidence sheet {i}">' for i in range(1, 13))
    diagnosis = (review/'DIAGNOSIS.md').read_text()
    (review/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Validation evidence</title><style>body{font:16px system-ui;margin:30px;line-height:1.6}pre{white-space:pre-wrap;max-width:1000px}img{max-width:100%}</style><h1>Assistant-assisted validation evidence</h1><pre>'+html.escape(diagnosis)+'</pre>'+images, encoding='utf-8')
    print(json.dumps({k: {field: value for field, value in v.items() if field != 'source_group_net_correct_clip_changes'} for k, v in summary.items()}, indent=2))


if __name__ == '__main__':
    main()
