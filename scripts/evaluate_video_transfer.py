"""Fixed crowd-trained R3D-18 heads transferred to all 400 released RWF clips."""
from __future__ import annotations

import argparse
import csv
import html
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import torch
from torchvision.models.video import R3D_18_Weights, r3d_18

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from affective.cross_validation import digest
from affective.data import decode_sample, read_manifest, write_json
from affective.motion import score_linear
from affective.train import metrics

LIMITS = ("Exploratory transfer to previously evaluated RWF footage. No RWF fitting, normalization, "
          "threshold optimization or model selection. Primary head is crowd fold 1 by fixed convention, "
          "not selected for test performance. Other crowd fold heads and a predeclared equal-weight "
          "ensemble are supplementary. The ensemble threshold is the arithmetic mean of the five "
          "crowd-validation-selected thresholds. Scores are not calibrated probabilities. "
          "No supervised RWF or untouched benchmark claim is made; pretraining/source overlap is unaudited.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path, default=Path("output/video_baseline_v2_20261115"))
    parser.add_argument("--rwf", type=Path, default=Path("output/rwf_transfer_20261115"))
    parser.add_argument("--out", type=Path, default=Path("output/video_transfer_20261115"))
    args = parser.parse_args()
    root, source, rwf, out = args.root.resolve(), args.source.resolve(), args.rwf.resolve(), args.out.resolve()
    if (out / "completion.json").exists():
        for relative, expected in json.loads((out / "completion.json").read_text())["artifacts_sha256"].items():
            if digest(out / relative) != expected:
                raise ValueError("Completed video transfer changed")
        print((out / "RESULTS.md").read_text(), flush=True)
        return
    if out.exists():
        raise FileExistsError("Preserve a prior transfer plan; choose another directory")
    baseline = json.loads((source / "protocol.json").read_text())
    original = json.loads((rwf / "protocol.json").read_text())
    if digest(rwf / "manifest.csv") != original["manifest_sha256"]:
        raise ValueError("RWF evaluation manifest changed")
    out.mkdir(parents=True)
    (out / "weights").mkdir()
    weights = source / "weights" / baseline["weights_file"]
    if digest(weights) != baseline["weights_sha256"]:
        raise ValueError("Video baseline weights changed")
    shutil.copy2(weights, out / "weights" / weights.name)
    shutil.copy2(rwf / "manifest.csv", out / "manifest.csv")
    heads = []
    for fold in range(1, 6):
        path = source / f"fold_{fold}" / "motion" / "rgb_r3d18_frozen" / "model.json"
        frozen = json.loads(path.read_text())
        shutil.copy2(path, out / f"head_fold_{fold}.json")
        heads.append(frozen)
    plan = {"source_baseline_protocol_sha256": digest(source / "protocol.json"),
            "manifest_sha256": digest(out / "manifest.csv"), "weights_sha256": digest(weights),
            "head_sha256": {f"head_fold_{fold}.json": digest(out / f"head_fold_{fold}.json") for fold in range(1, 6)},
            "sampling": baseline["sampling"], "preprocessing": baseline["preprocessing"],
            "primary_head": 1, "thresholds": [head["threshold"] for head in heads],
            "ensemble": "Equal mean of five head scores; mean of fixed crowd-validation thresholds",
            "script_sha256": digest(Path(__file__)), "torch": torch.__version__,
            "known_prior_demo_ids": original["previously_inspected_ids"], "limitations": LIMITS}
    write_json(out / "protocol.json", plan)
    model = r3d_18(weights=None)
    model.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True))
    model.fc = torch.nn.Identity()
    model.eval().to("cuda")
    transform = R3D_18_Weights.KINETICS400_V1.transforms()
    torch.set_num_threads(4)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    rows = read_manifest(out / "manifest.csv")
    vectors = []
    for number, row in enumerate(rows, 1):
        path = root / row["path"]
        if digest(path) != row["sha256"]:
            raise ValueError("RWF source video changed")
        images, indices, _, decoded = decode_sample(path, 32)
        if decoded != row["frames"]:
            raise ValueError("RWF full decode differs from frozen header")
        with np.load(rwf / "cache" / f"{row['id']}.npz", allow_pickle=False) as saved:
            np.testing.assert_array_equal(indices, saved["frame_indices"])
        rgb = torch.from_numpy(np.stack([im[..., ::-1].copy() for im in images])).permute(0, 3, 1, 2)
        tensor = torch.stack([transform(rgb[:16]), transform(rgb[16:])]).to("cuda")
        with torch.inference_mode():
            vectors.append(model(tensor).mean(0).cpu().numpy().astype(np.float32))
        if number % 50 == 0:
            print(f"Video transfer encoded {number}/400", flush=True)
    features = np.array(vectors, dtype=np.float64)
    np.savez_compressed(out / "features.npz", features=features, ids=np.array([r["id"] for r in rows]))
    labels = np.array([r["label"] for r in rows])
    head_scores = np.stack([score_linear(features, head) for head in heads])
    ensemble = head_scores.mean(0)
    ensemble_threshold = float(np.mean(plan["thresholds"]))
    evaluations = [{"head": fold, "threshold": head["threshold"], "metrics": metrics(labels, scores, head["threshold"])}
                   for fold, (head, scores) in enumerate(zip(heads, head_scores), 1)]
    summary = {"status": "complete", "clips": len(rows), "primary_fold_1": evaluations[0],
               "supplementary_heads": evaluations[1:],
               "predeclared_ensemble": {"threshold": ensemble_threshold, "metrics": metrics(labels, ensemble, ensemble_threshold)},
               "full_decodes_and_frame_indices_verified": True, "limitations": LIMITS}
    predictions = [{"id": row["id"], "path": row["path"], "label": row["label"],
                    **{f"fold_{fold}_score": float(head_scores[fold - 1, index]) for fold in range(1, 6)},
                    "primary_prediction": int(head_scores[0, index] >= heads[0]["threshold"]),
                    "ensemble_score": float(ensemble[index]), "ensemble_prediction": int(ensemble[index] >= ensemble_threshold)}
                   for index, row in enumerate(rows)]
    with (out / "predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)
    # Rebuild scores and metrics from the saved feature corpus and frozen heads.
    with np.load(out / "features.npz", allow_pickle=False) as saved:
        for head, scores in zip(heads, head_scores):
            np.testing.assert_allclose(score_linear(saved["features"], head), scores, atol=1e-12, rtol=0)
    write_json(out / "metrics.json", summary)
    primary = summary["primary_fold_1"]["metrics"]
    averaged = summary["predeclared_ensemble"]["metrics"]
    notes = f"# Frozen video-model RWF transfer\n\nAll 400 released evaluation clips, including low-pose clips.\n\n| Frozen predictor | Accuracy | Macro-F1 | AUC |\n|---|---:|---:|---:|\n| Primary crowd fold 1 head | {primary['accuracy']:.1%} | {primary['macro_f1']:.3f} | {primary['roc_auc']:.3f} |\n| Predeclared five-head ensemble | {averaged['accuracy']:.1%} | {averaged['macro_f1']:.3f} | {averaged['roc_auc']:.3f} |\n\n" + LIMITS + "\n\nFull video decodes/frame indices verified. Saved features and heads reproduce all scores.\n"
    (out / "RESULTS.md").write_text(notes, encoding="utf-8")
    (out / "index.html").write_text('<!doctype html><meta charset="utf-8"><title>Video-model transfer</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;padding:20px;line-height:1.6}pre{white-space:pre-wrap}</style><h1>Frozen video-model RWF transfer</h1><pre>' + html.escape(notes) + '</pre><a href="metrics.json">Full metrics</a> | <a href="protocol.json">Protocol</a>', encoding="utf-8")
    files = [out / "protocol.json", out / "manifest.csv", out / "features.npz", out / "metrics.json", out / "predictions.csv",
             *out.glob("head_fold_*.json"), out / "weights" / weights.name]
    write_json(out / "completion.json", {"status": "complete", "artifacts_sha256": {p.relative_to(out).as_posix(): digest(p) for p in files}})
    print(notes, flush=True)


if __name__ == "__main__":
    main()
