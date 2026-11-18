"""Plot fixed-threshold supervised RWF evaluation diagnostics from saved scores."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("output/rwf_supervised_20261115"))
    args = parser.parse_args()
    out = args.out.resolve()
    result = json.loads((out / "metrics.json").read_text())
    with (out / "evaluation_predictions.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    labels = np.array([int(r["label"]) for r in rows])
    scores = np.array([float(r["score"]) for r in rows])
    matrix = confusion_matrix(labels, scores >= result["threshold"], labels=[0, 1])
    if matrix.tolist() != result["test"]["confusion_matrix"] or abs(roc_auc_score(labels, scores) - result["test"]["roc_auc"]) > 1e-12:
        raise ValueError("Plot inputs do not reproduce recorded metrics")
    false_positive, true_positive, _ = roc_curve(labels, scores)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
    axes[0].imshow(matrix, cmap="Blues")
    for i in range(2):
        for j in range(2):
            axes[0].text(j, i, str(matrix[i, j]), ha="center", va="center", fontsize=20,
                         color="white" if matrix[i, j] > matrix.max() / 2 else "black")
    axes[0].set_xticks([0, 1], ["NonFight", "Fight"])
    axes[0].set_yticks([0, 1], ["NonFight", "Fight"])
    axes[0].set(xlabel="Predicted", ylabel="Supplied label", title=f"Validation-selected threshold {result['threshold']:.2f}")
    axes[1].plot(false_positive, true_positive, color="#087f8c", label=f"AUC {result['test']['roc_auc']:.3f}")
    axes[1].plot([0, 1], [0, 1], "--", color="#64748b", linewidth=1)
    axes[1].scatter(matrix[0, 1] / matrix[0].sum(), matrix[1, 1] / matrix[1].sum(), color="#d97706", label="Fixed threshold")
    axes[1].set(xlabel="False-positive rate", ylabel="True-positive rate", title="All 400 released evaluation clips", xlim=(0, 1), ylim=(0, 1.02))
    axes[1].legend(loc="lower right")
    axes[1].grid(alpha=.2)
    fig.text(.5, .015, "Exploratory supervised development: evaluation footage was inspected previously; supplied labels remain unchanged.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .05, 1, 1))
    (out / "figures").mkdir(exist_ok=True)
    fig.savefig(out / "figures" / "evaluation_diagnostics.png", dpi=200)
    plt.close(fig)
    print("Saved fixed-threshold ROC and confusion diagnostics.")


if __name__ == "__main__":
    main()
