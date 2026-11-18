"""Fit on training clips, select on validation clips, evaluate held-out clips once."""
from __future__ import annotations

import csv
import hashlib
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from torch.utils.data import DataLoader, TensorDataset

from .data import read_manifest, write_json
from .features import FEATURE_SCHEMA, build_features, feature_dim
from .input_controls import control_inputs
from .model import CrowdTCN

VARIANTS = {"baseline": (False, False), "reliability": (True, False),
            "interactions": (False, True), "combined": (True, True)}


def metrics(labels, scores, threshold):
    prediction = scores >= threshold
    return {"n": len(labels), "accuracy": float(accuracy_score(labels, prediction)),
            "macro_f1": float(f1_score(labels, prediction, average="macro", zero_division=0)),
            "precision_violent": float(precision_score(labels, prediction, zero_division=0)),
            "recall_violent": float(recall_score(labels, prediction, zero_division=0)),
            "roc_auc": float(roc_auc_score(labels, scores)) if len(np.unique(labels)) == 2 else None,
            "confusion_matrix": confusion_matrix(labels, prediction, labels=[0, 1]).tolist()}


def choose_threshold(labels, scores):
    # Threshold choice uses validation data only; nearest to 0.5 wins ties.
    candidates = np.linspace(0.1, 0.9, 81)
    return float(max(candidates, key=lambda x: (f1_score(labels, scores >= x, average="macro", zero_division=0), -abs(x - 0.5))))


def load_features(out, variant, cache_dir=None, feature_schema=FEATURE_SCHEMA, input_control="full"):
    reliability, interactions = VARIANTS[variant]
    rows = read_manifest(out / "manifest.csv")
    parts = {split: {"x": [], "mask": [], "y": [], "rows": [], "quality": []} for split in ("train", "val", "test")}
    signature = None
    for row in rows:
        p = (Path(cache_dir) if cache_dir is not None else out / "cache") / f"{row['id']}.npz"
        if not p.exists():
            raise FileNotFoundError(f"Missing pose cache {p}. Run extract for the complete manifest.")
        with np.load(p, allow_pickle=False) as d:
            if str(d["source_sha256"]) != row["sha256"]:
                raise ValueError(f"Source digest mismatch: {p}")
            current = str(d["signature"])
            if signature is None:
                signature = current
            if current != signature:
                raise ValueError("Mixed extraction settings in cache; re-extract the manifest")
            x, mask = build_features(d["keypoints"], d["boxes"], d["present"], d["times"], reliability, interactions,
                                     feature_schema=feature_schema)
            x, mask = control_inputs(x, mask, row["id"], input_control)
            group = parts[row["split"]]
            group["x"].append(x)
            group["mask"].append(mask)
            group["y"].append(row["label"])
            group["rows"].append(row)
            group["quality"].append(json.loads(str(d["quality"])))
    for group in parts.values():
        for key in ("x", "mask", "y"):
            group[key] = np.array(group[key], np.float32)
    return parts, signature


def normalize_training(parts):
    observed = parts["train"]["mask"].astype(bool)
    values = parts["train"]["x"][observed]
    if not len(values):
        raise ValueError("Training clips contain no detected people")
    mu = values.mean(0)
    sd = np.maximum(values.std(0), 0.01)
    for group in parts.values():
        group["x"] = np.clip((group["x"] - mu) / sd, -10, 10) * group["mask"][..., None]
    return mu.astype(np.float32), sd.astype(np.float32)


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def predict(model, group, device):
    model.eval()
    scores = []
    with torch.inference_mode():
        for start in range(0, len(group["y"]), 32):
            x = torch.from_numpy(group["x"][start:start + 32]).to(device)
            mask = torch.from_numpy(group["mask"][start:start + 32]).to(device)
            scores.extend(model(x, mask).sigmoid().cpu().numpy().tolist())
    return np.array(scores)


def train_one(out: Path, variant, seed=42, epochs=180, patience=30, hidden=48, device="auto",
              cache_dir=None, protocol=None, use_coverage=True, feature_schema=FEATURE_SCHEMA, input_control="full"):
    if min(epochs, patience, hidden) < 1:
        raise ValueError("Epochs, patience and hidden size must be positive")
    seed_everything(seed)
    torch.set_num_threads(4)
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    parts, signature = load_features(out, variant, cache_dir, feature_schema, input_control)
    mu, sd = normalize_training(parts)
    reliability, interactions = VARIANTS[variant]
    model = CrowdTCN(feature_dim(reliability, interactions), hidden, use_coverage=use_coverage).to(device)
    parameter_count = sum(p.numel() for p in model.parameters())
    train = parts["train"]
    dataset = TensorDataset(torch.from_numpy(train["x"]), torch.from_numpy(train["mask"]), torch.from_numpy(train["y"]))
    loader = DataLoader(dataset, batch_size=16, shuffle=True, num_workers=0,
                        generator=torch.Generator().manual_seed(seed))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
    positive = train["y"].sum()
    loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor((len(train["y"]) - positive) / positive, device=device))
    run = out / "runs" / f"{variant}_seed{seed}"
    run.mkdir(parents=True, exist_ok=True)
    best_loss, best_epoch, best_state = float("inf"), 0, None
    history = []
    started = time.perf_counter()
    for epoch in range(1, epochs + 1):
        model.train()
        total = 0
        for x, mask, labels in loader:
            x, mask, labels = x.to(device), mask.to(device), labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_fn(model(x, mask), labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total += float(loss.item()) * len(labels)
        val_scores = predict(model, parts["val"], device)
        with torch.no_grad():
            s = np.clip(val_scores, 1e-7, 1 - 1e-7)
            y = parts["val"]["y"]
            val_loss = float(-np.mean(y * np.log(s) + (1 - y) * np.log(1 - s)))
        history.append({"epoch": epoch, "train_loss": total / len(dataset), "val_loss": val_loss,
                        "val_macro_f1_at_05": float(f1_score(y, val_scores >= 0.5, average="macro", zero_division=0))})
        if val_loss < best_loss - 1e-4:
            best_loss, best_epoch = val_loss, epoch
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        if epoch == 1 or epoch % 10 == 0:
            print(f"{variant} seed={seed} epoch={epoch} train_loss={history[-1]['train_loss']:.4f} val_loss={val_loss:.4f}", flush=True)
        if epoch - best_epoch >= patience:
            break
    model.load_state_dict(best_state)
    val_scores = predict(model, parts["val"], device)
    threshold = choose_threshold(parts["val"]["y"], val_scores)
    # All model/threshold decisions are finalized before this test prediction.
    test_scores = predict(model, parts["test"], device)
    test_metrics = metrics(parts["test"]["y"], test_scores, threshold)
    checkpoint = {"state_dict": best_state, "variant": variant, "seed": seed,
                  "input_dim": len(mu), "hidden": hidden, "threshold": threshold,
                  "use_coverage": use_coverage,
                  "input_control": input_control,
                  "mean": torch.from_numpy(mu), "std": torch.from_numpy(sd),
                  "pose_signature": signature, "feature_schema": feature_schema,
                  "manifest_sha256": hashlib.sha256((out / "manifest.csv").read_bytes()).hexdigest()}
    torch.save(checkpoint, run / "model.pt")
    result = {"variant": variant, "seed": seed, "parameters": parameter_count, "device": device,
              "use_coverage": use_coverage, "feature_schema": feature_schema,
              "input_control": input_control,
              "epochs_executed": len(history), "selected_epoch": best_epoch, "threshold": threshold,
              "training_seconds": time.perf_counter() - started,
              "train_clips": len(train["y"]), "val_clips": len(parts["val"]["y"]), "test_clips": len(parts["test"]["y"]),
              "validation": metrics(parts["val"]["y"], val_scores, threshold), "test": test_metrics,
              "majority_baseline_test_accuracy": float(max(np.mean(parts["test"]["y"]), 1 - np.mean(parts["test"]["y"]))),
              "feature_shape": list(train["x"].shape[1:]), "pose_signature": signature,
              "protocol": protocol or "Single pilot holdout, validation-selected checkpoint and threshold. Test metrics are exploratory, not a completed benchmark."}
    prediction_rows = []
    for split, scores in (("val", val_scores), ("test", test_scores)):
        for row, quality, score in zip(parts[split]["rows"], parts[split]["quality"], scores):
            prediction_rows.append({"id": row["id"], "path": row["path"], "split": split,
                                    "label": row["label"], "score": float(score), "prediction": int(score >= threshold),
                                    "usable_pose_fraction": quality["usable_pose_fraction"],
                                    "demo_abstain": quality["usable_pose_fraction"] < 0.25})
    with (run / "predictions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(prediction_rows[0]))
        writer.writeheader()
        writer.writerows(prediction_rows)
    write_json(run / "metrics.json", result)
    write_json(run / "history.json", history)
    print(json.dumps(result, indent=2), flush=True)
    return result


def train_variants(out, variants, seeds, **kwargs):
    results = []
    for seed in seeds:
        for variant in variants:
            results.append(train_one(out, variant, seed=seed, **kwargs))
    write_json(out / "training_summary.json", results)
    return results
