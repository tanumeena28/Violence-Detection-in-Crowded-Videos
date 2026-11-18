"""Video inventory and clip/source-disjoint pilot partitions."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def source_key(path: Path, dataset: str) -> str:
    if dataset == "crowd":
        # Search keywords can differ for the same source clip. Remove that prefix.
        return "__".join(path.stem.split("__")[1:]).casefold()
    return re.sub(r"_\d+$", "", path.stem).casefold()


def canonicalize_source_groups(rows, dataset="crowd"):
    """Link truncated IDs only when the crowd title and uploader also match.

    Conservative grouping keeps potentially related clips out of separate
    partitions. It does not establish that their frames are duplicates.
    """
    if dataset != "crowd":
        return [dict(row) for row in rows], {}
    keys = sorted({row["source_group"] for row in rows}, key=lambda key: (len(key), key))
    aliases = {}
    for key in keys:
        parts = key.rsplit("__", 1)
        if len(parts) != 2 or len(parts[1]) < 2:
            aliases[key] = key
            continue
        prefix, identifier = parts
        candidates = [old for old in aliases if old.rsplit("__", 1)[0] == prefix
                      and len(old.rsplit("__", 1)[-1]) >= 2
                      and identifier.startswith(old.rsplit("__", 1)[-1])]
        aliases[key] = aliases[candidates[0]] if candidates else key
    resolved = [{**row, "source_group": aliases[row["source_group"]]} for row in rows]
    return resolved, {key: value for key, value in aliases.items() if key != value}


def source_overlap_candidates(rows, dataset="crowd"):
    resolved, _ = canonicalize_source_groups(rows, dataset)
    pairs = []
    for i, first in enumerate(resolved):
        for second in resolved[i + 1:]:
            if first["split"] != second["split"] and first["source_group"] == second["source_group"]:
                pairs.append({"first_id": first["id"], "second_id": second["id"],
                              "first_path": first["path"], "second_path": second["path"],
                              "first_split": first["split"], "second_split": second["split"],
                              "source_group": first["source_group"],
                              "evidence": "Matching title/uploader and exact or prefix-compatible source ID; frames require review."})
    return pairs


def prepare(root: Path, out: Path, dataset="crowd", limit_per_class=0, seed=42):
    folder = root / "data" / ("movies" if dataset == "crowd" else "RWF-2000")
    files = sorted(folder.rglob("*.avi"))
    if not files:
        raise FileNotFoundError(f"No AVI videos in {folder}")
    rows, failures, duplicates = [], [], []
    seen_hash = {}
    for p in files:
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        cap = cv2.VideoCapture(str(p))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        ok, frame = cap.read()
        cap.release()
        if not ok or fps <= 0 or frames < 2:
            failures.append(str(p.relative_to(root)))
            continue
        label = int(p.parent.name in ("Violence", "Fight"))
        if digest in seen_hash:
            old = seen_hash[digest]
            if old["label"] != label:
                raise ValueError(f"Conflicting labels for identical videos: {p}, {old['path']}")
            duplicates.append({"kept": old["path"], "removed": p.relative_to(root).as_posix()})
            continue
        if dataset == "crowd":
            fold = int(p.parent.parent.name)
            split = "test" if fold == 5 else "val" if fold == 4 else "train"
        else:
            fold = 0
            split = "test" if p.parent.parent.name == "val" else "train"
        row = {"id": digest[:16], "path": p.relative_to(root).as_posix(),
               "sha256": digest, "source_group": source_key(p, dataset),
               "label": label, "fold": fold, "split": split, "fps": fps,
               "frames": frames, "width": frame.shape[1], "height": frame.shape[0]}
        rows.append(row)
        seen_hash[digest] = row

    if dataset == "rwf":
        # Validation groups come only from the released training partition.
        rng = np.random.default_rng(seed)
        for label in (0, 1):
            groups = sorted({r["source_group"] for r in rows if r["split"] == "train" and r["label"] == label})
            rng.shuffle(groups)
            val_groups = set(groups[:max(1, int(len(groups) * 0.2))])
            for row in rows:
                if row["split"] == "train" and row["source_group"] in val_groups:
                    row["split"] = "val"

    rows, aliases = canonicalize_source_groups(rows, dataset)
    # Holdout priority: test > validation > train. Remove overlapping source groups
    # from earlier partitions; never move test clips into training.
    priority = {"train": 0, "val": 1, "test": 2}
    group_priority = {}
    for row in rows:
        key = row["source_group"]
        group_priority[key] = max(group_priority.get(key, 0), priority[row["split"]])
    excluded = [r for r in rows if priority[r["split"]] != group_priority[r["source_group"]]]
    rows = [r for r in rows if priority[r["split"]] == group_priority[r["source_group"]]]
    if limit_per_class:
        rng = np.random.default_rng(seed)
        selected = []
        for split in ("train", "val", "test"):
            for label in (0, 1):
                subset = [r for r in rows if r["split"] == split and r["label"] == label]
                rng.shuffle(subset)
                selected.extend(subset[:limit_per_class])
        rows = selected
    rows.sort(key=lambda r: (r["split"], r["path"]))
    counts = {s: dict(Counter(str(r["label"]) for r in rows if r["split"] == s)) for s in ("train", "val", "test")}
    for split, count in counts.items():
        if set(count) != {"0", "1"}:
            raise ValueError(f"Both classes required in {split}: {count}")
    group_sets = {s: {r["source_group"] for r in rows if r["split"] == s} for s in counts}
    assert not (group_sets["train"] & group_sets["val"] or group_sets["train"] & group_sets["test"] or group_sets["val"] & group_sets["test"])
    report = {"dataset": dataset, "seed": seed, "video_count": len(files), "usable_count": len(rows),
              "split_counts": counts, "decode_header_failures": failures, "exact_duplicates": duplicates,
              "source_overlap_exclusions": [r["path"] for r in excluded],
              "source_group_aliases": aliases,
              "source_group_policy": "Exact keys plus matching crowd title/uploader with prefix-compatible IDs of at least two characters.",
              "protocol": "Pilot holdout: crowd folds 1-3 train, 4 validation, 5 test; source overlaps removed. Not full five-fold evaluation." if dataset == "crowd" else "Released RWF validation partition used as test; training-source groups supply validation.",
              "limitation": "Source grouping uses filenames and byte hashes; near-duplicates and truncated source names still need manual review."}
    out.mkdir(parents=True, exist_ok=True)
    with (out / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_json(out / "inventory.json", report)
    print(json.dumps(report, indent=2), flush=True)
    return rows


def read_manifest(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in ("label", "fold", "frames", "width", "height"):
            row[key] = int(row[key])
        row["fps"] = float(row["fps"])
    return rows


def decode_sample(path: Path, count: int):
    """Decode every frame once, then sample the clip uniformly without seeking artifacts."""
    cap = cv2.VideoCapture(str(path))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()
    if len(frames) < 2 or fps <= 0:
        raise ValueError(f"Cannot decode usable video: {path}")
    indices = np.rint(np.linspace(0, len(frames) - 1, count)).astype(np.int32)
    return [frames[i] for i in indices], indices, fps, len(frames)
