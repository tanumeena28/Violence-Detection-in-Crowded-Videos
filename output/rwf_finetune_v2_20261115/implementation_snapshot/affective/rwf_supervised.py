"""Source grouping and validation-only head fitting for supervised RWF work."""
from __future__ import annotations

from collections import Counter, defaultdict

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedGroupKFold

from .motion import score_linear
from .train import choose_threshold, metrics


def partition_rows(rows, split_seed=42, folds=5):
    """Keep source IDs and byte-identical clips together, including mixed labels.

    Released evaluation clips are retained. Development clips related to an
    evaluation source or identical bytes are excluded before validation split.
    Same-label duplicate development bytes are collapsed deterministically.
    """
    rows = sorted((dict(row) for row in rows), key=lambda row: row["path"])
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Clip IDs must be unique")
    if any(r["released_partition"] not in ("train", "val") or r["label"] not in (0, 1) for r in rows):
        raise ValueError("Invalid released partition or class")
    parent = {r["source_group"]: r["source_group"] for r in rows}

    def find(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    hashes = defaultdict(list)
    for row in rows:
        hashes[row["sha256"]].append(row)
    for duplicates in hashes.values():
        if len({r["label"] for r in duplicates}) > 1:
            raise ValueError("Byte-identical clips have conflicting supplied labels; review before training")
        keys = sorted({find(r["source_group"]) for r in duplicates})
        for key in keys[1:]:
            parent[find(key)] = find(keys[0])
    grouped = [{**r, "source_group": find(r["source_group"])} for r in rows]
    evaluation = [r for r in grouped if r["released_partition"] == "val"]
    evaluation_groups = {r["source_group"] for r in evaluation}
    excluded, development, seen = [], [], {}
    for row in grouped:
        if row["released_partition"] != "train":
            continue
        if row["source_group"] in evaluation_groups:
            excluded.append({**row, "reason": "Source group linked to released evaluation"})
        elif row["sha256"] in seen:
            excluded.append({**row, "reason": "Same-label byte duplicate in development", "retained_id": seen[row["sha256"]]})
        else:
            development.append(row)
            seen[row["sha256"]] = row["id"]
    if len({r["source_group"] for r in development}) < folds:
        raise ValueError("Not enough development source groups")
    labels = np.array([r["label"] for r in development])
    groups = np.array([r["source_group"] for r in development])
    splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=split_seed)
    _, val_indices = next(splitter.split(np.zeros(len(development)), labels, groups))
    val_ids = {development[index]["id"] for index in val_indices}
    assigned = [{**r, "split": "val" if r["id"] in val_ids else "train"} for r in development]
    assigned.extend({**r, "split": "test"} for r in evaluation)
    assigned.sort(key=lambda row: (row["split"], row["path"]))
    sets = {split: {r["source_group"] for r in assigned if r["split"] == split} for split in ("train", "val", "test")}
    if any(sets[a] & sets[b] for a, b in (("train", "val"), ("train", "test"), ("val", "test"))):
        raise ValueError("Source groups cross experiment partitions")
    if any({r["label"] for r in assigned if r["split"] == split} != {0, 1} for split in sets):
        raise ValueError("Every partition must contain both classes")
    group_labels = defaultdict(set)
    for row in grouped:
        group_labels[row["source_group"]].add(row["label"])
    audit = {"released_clips": len(rows), "included_clips": len(assigned), "excluded_clips": excluded,
             "byte_duplicate_sets": [[r["id"] for r in values] for values in hashes.values() if len(values) > 1],
             "mixed_label_source_groups": sum(len(values) > 1 for values in group_labels.values()),
             "split_counts": {split: dict(Counter(str(r["label"]) for r in assigned if r["split"] == split)) for split in sets},
             "source_group_counts": {split: len(keys) for split, keys in sets.items()},
             "source_groups_disjoint": True, "evaluation_clips_retained": len(evaluation),
             "split_seed": split_seed, "group_folds": folds, "validation_fold": 0,
             "source_policy": "Filename source ID after stripping final numeric segment suffix; union all source IDs linked by identical video SHA256, ignoring class folder. Mixed-label sources remain whole.",
             "limitation": "Source IDs and identical bytes do not rule out renamed or visually similar footage. Supplied labels are not independently verified."}
    return assigned, audit


def fit_development_head(train_features, train_labels, val_features, val_labels,
                         regularization=(.001, .01, .1, 1., 10.)):
    """No test inputs are accepted by model, scaling, C or threshold selection."""
    train_features, val_features = np.asarray(train_features, np.float64), np.asarray(val_features, np.float64)
    train_labels, val_labels = np.asarray(train_labels), np.asarray(val_labels)
    if (train_features.ndim != 2 or val_features.ndim != 2 or train_features.shape[1] != val_features.shape[1]
            or len(train_features) != len(train_labels) or len(val_features) != len(val_labels)
            or not np.isfinite(train_features).all() or not np.isfinite(val_features).all()
            or set(train_labels) != {0, 1} or set(val_labels) != {0, 1}
            or not regularization or any(c <= 0 for c in regularization)):
        raise ValueError("Invalid development inputs")
    mean, std = train_features.mean(0), np.maximum(train_features.std(0), .01)
    x_train, x_val = (train_features - mean) / std, (val_features - mean) / std
    candidates, best, best_loss, best_c = [], None, float("inf"), None
    for c in regularization:
        model = LogisticRegression(C=c, solver="lbfgs", max_iter=2000, random_state=42)
        model.fit(x_train, train_labels)
        scores = model.predict_proba(x_val)[:, 1]
        loss = float(log_loss(val_labels, scores))
        candidates.append({"C": float(c), "validation_log_loss": loss, "iterations": int(model.n_iter_[0])})
        if loss < best_loss:
            best, best_loss, best_c = model, loss, float(c)
    val_scores = best.predict_proba(x_val)[:, 1]
    threshold = choose_threshold(val_labels, val_scores)
    checkpoint = {"schema": "standardized-logistic-v1", "name": "rwf_r3d18_frozen",
                  "mean": mean.tolist(), "std": std.tolist(), "coefficients": best.coef_[0].tolist(),
                  "intercept": float(best.intercept_[0]), "threshold": threshold, "selected_C": best_c}
    np.testing.assert_allclose(score_linear(val_features, checkpoint), val_scores, atol=1e-10, rtol=0)
    selection = {"candidates": candidates, "selected_C": best_c, "threshold": threshold,
                 "train": metrics(train_labels, score_linear(train_features, checkpoint), threshold),
                 "validation": metrics(val_labels, val_scores, threshold),
                 "selection_boundary": "Scaling and logistic coefficients fitted on train only; C selected by validation log loss, threshold by validation macro-F1. No test inputs accepted."}
    return checkpoint, selection
