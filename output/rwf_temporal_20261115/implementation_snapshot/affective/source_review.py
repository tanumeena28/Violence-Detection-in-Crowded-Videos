"""Full-video decoding and dense, label-independent source-overlap triage."""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

import cv2
import numpy as np

from .data import canonicalize_source_groups, read_manifest, write_json

SETTINGS = {"sample_fps": 4, "hash": "63-bit DCT median hash",
            "views": ["full", "central 80 percent"], "maximum_hamming": 6,
            "minimum_gray_correlation": .94, "minimum_gray_std": 8.,
            "offset_tolerance_seconds": .3, "minimum_matches": 3,
            "minimum_span_seconds": .5, "maximum_median_hamming": 4.}
BIT_COUNTS = np.array([int(i).bit_count() for i in range(256)], dtype=np.uint8)


def hash_gray(gray):
    small = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
    coefficients = cv2.dct(small.astype(np.float32))[:8, :8].ravel()[1:]
    return np.packbits(coefficients > np.median(coefficients), bitorder="little").view("<u8")[0]


def decode_clip(path, expected_digest):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_digest:
        raise ValueError(f"Source changed: {path}")
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not np.isfinite(fps) or fps <= 0:
        cap.release()
        raise ValueError(f"Invalid FPS: {path}")
    stride = max(1, round(fps / SETTINGS["sample_fps"]))
    thumbnails, views, times = [], [], []
    count = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if count % stride == 0:
            h, w = frame.shape[:2]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            crop = gray[int(h * .1):max(int(h * .9), 1), int(w * .1):max(int(w * .9), 1)]
            views.append([cv2.resize(g, (64, 48), interpolation=cv2.INTER_AREA) for g in (gray, crop)])
            thumbnails.append(cv2.resize(frame, (240, 180), interpolation=cv2.INTER_AREA))
            times.append(count / fps)
        count += 1
    cap.release()
    if count < 2:
        raise ValueError(f"Cannot decode usable video: {path}")
    grays = np.asarray(views)
    hashes = np.array([[hash_gray(g) for g in sample] for sample in grays], dtype=np.uint64)
    flat = grays.astype(np.float32).reshape(len(grays), 2, -1)
    flat -= flat.mean(-1, keepdims=True)
    norms = np.linalg.norm(flat, axis=-1)
    normalized = flat / np.maximum(norms[..., None], 1e-6)
    textured = grays.std((2, 3)) >= SETTINGS["minimum_gray_std"]
    return {"times": np.array(times), "hashes": hashes, "normalized": normalized,
            "textured": textured, "thumbnails": thumbnails, "decoded_frames": count, "fps": fps}


def aligned_matches(first, second, matches):
    """Require several chronological matches at a consistent time offset."""
    best = []
    offsets = [second["times"][j] - first["times"][i] for i, j, _, _ in matches]
    for offset in offsets:
        candidates = [m for m, delta in zip(matches, offsets)
                      if abs(delta - offset) <= SETTINGS["offset_tolerance_seconds"]]
        chosen, last_i, last_j = [], -1, -1
        for match in sorted(candidates, key=lambda m: (m[0], m[2], -m[3], m[1])):
            if match[0] > last_i and match[1] > last_j:
                chosen.append(match)
                last_i, last_j = match[:2]
        if len(chosen) > len(best) or (len(chosen) == len(best) and chosen
                                     and np.mean([m[2] for m in chosen]) < np.mean([m[2] for m in best])):
            best = chosen
    return best


def compare_clips(first, second):
    best = {"view": "full", "matches": [], "minimum_hamming": 63,
            "matched_frames": 0, "span_seconds": 0., "flagged": False}
    for view, name in enumerate(SETTINGS["views"]):
        xor = first["hashes"][:, view, None] ^ second["hashes"][None, :, view]
        distances = BIT_COUNTS[xor.view(np.uint8).reshape(*xor.shape, 8)].sum(-1)
        best["minimum_hamming"] = min(best["minimum_hamming"], int(distances.min()))
        eligible = ((distances <= SETTINGS["maximum_hamming"])
                    & first["textured"][:, view, None] & second["textured"][None, :, view])
        matches = []
        for i, j in zip(*np.where(eligible)):
            correlation = float(first["normalized"][i, view] @ second["normalized"][j, view])
            if correlation >= SETTINGS["minimum_gray_correlation"]:
                matches.append((int(i), int(j), int(distances[i, j]), correlation))
        aligned = aligned_matches(first, second, matches)
        span = float(min(first["times"][aligned[-1][0]] - first["times"][aligned[0][0]],
                         second["times"][aligned[-1][1]] - second["times"][aligned[0][1]])) if aligned else 0.
        median = float(np.median([m[2] for m in aligned])) if aligned else 63.
        flagged = (len(aligned) >= SETTINGS["minimum_matches"] and span >= SETTINGS["minimum_span_seconds"]
                   and median <= SETTINGS["maximum_median_hamming"])
        if (flagged, len(aligned), span) > (best["flagged"], best["matched_frames"], best["span_seconds"]):
            best.update(view=name, matches=aligned, matched_frames=len(aligned), span_seconds=span,
                        median_hamming=median, flagged=bool(flagged))
    return best


def pair_sheet(pair, clips, path):
    first, second = clips[pair["first_id"]], clips[pair["second_id"]]
    matches = pair["matches"]
    if matches:
        selected = [matches[i] for i in np.rint(np.linspace(0, len(matches) - 1, 4)).astype(int)]
    else:
        a = np.rint(np.linspace(0, len(first["times"]) - 1, 4)).astype(int)
        b = np.rint(np.linspace(0, len(second["times"]) - 1, 4)).astype(int)
        selected = [(int(i), int(j), 63, 0.) for i, j in zip(a, b)]
    canvas = np.full((520, 1000, 3), 247, np.uint8)
    cv2.putText(canvas, f"Candidate: {pair['first_id']} / {pair['second_id']} | matches={pair['matched_frames']} | {pair['view']}",
                (12, 25), cv2.FONT_HERSHEY_SIMPLEX, .5, (35, 45, 55), 1, cv2.LINE_AA)
    for row, (key, clip) in enumerate((("first", first), ("second", second))):
        top = 48 + row * 232
        cv2.putText(canvas, Path(pair[key + "_path"]).name[:116], (12, top),
                    cv2.FONT_HERSHEY_SIMPLEX, .36, (35, 45, 55), 1, cv2.LINE_AA)
        for column, match in enumerate(selected):
            index = match[row]
            left = 12 + column * 246
            canvas[top + 12:top + 192, left:left + 240] = clip["thumbnails"][index]
            cv2.putText(canvas, f"{clip['times'][index]:.2f}s", (left, top + 210),
                        cv2.FONT_HERSHEY_SIMPLEX, .43, (35, 45, 55), 1, cv2.LINE_AA)
    cv2.putText(canvas, "Full clips decoded; frames sampled near 4 FPS. Content matching does not validate violence labels.",
                (12, 508), cv2.FONT_HERSHEY_SIMPLEX, .4, (35, 45, 55), 1, cv2.LINE_AA)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), canvas):
        raise RuntimeError("Source-review sheet write failed")


def audit_sources(root, source, out):
    root, source, out = Path(root), Path(source), Path(out)
    if out.exists():
        raise FileExistsError("Use a new source-review directory")
    rows, aliases = canonicalize_source_groups(read_manifest(source / "manifest.csv"))
    out.mkdir(parents=True)
    clips = {}
    for number, row in enumerate(rows, 1):
        clips[row["id"]] = decode_clip(root / row["path"], row["sha256"])
        if number % 25 == 0 or number == len(rows):
            print(f"Source decode and dense sampling: {number}/{len(rows)}", flush=True)
    pairs = []
    compared = 0
    for i, first in enumerate(rows):
        for second in rows[i + 1:]:
            if first["source_group"] == second["source_group"]:
                continue
            comparison = compare_clips(clips[first["id"]], clips[second["id"]])
            pairs.append({"first_id": first["id"], "second_id": second["id"],
                          "first_path": first["path"], "second_path": second["path"], **comparison})
            compared += 1
    pairs.sort(key=lambda p: (not p["flagged"], -p["matched_frames"], -p["span_seconds"], p["minimum_hamming"], p["first_id"], p["second_id"]))
    selected = [p for i, p in enumerate(pairs) if p["flagged"] or i < 20]
    for number, pair in enumerate(selected, 1):
        sheet = Path("pairs") / f"pair_{number:03}.jpg"
        pair_sheet(pair, clips, out / sheet)
        pair["contact_sheet"] = sheet.as_posix()
    report = {"source_manifest_sha256": hashlib.sha256((source / "manifest.csv").read_bytes()).hexdigest(),
              "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "settings": SETTINGS, "clips": len(rows), "decoded_frames": sum(c["decoded_frames"] for c in clips.values()),
              "sampled_frames": sum(len(c["times"]) for c in clips.values()), "pairs_compared": compared,
              "canonical_source_groups": len({r["source_group"] for r in rows}), "source_group_aliases": aliases,
              "flagged_pairs": sum(p["flagged"] for p in pairs), "candidate_pairs": selected,
              "review_scope": "Full decoding and dense content-overlap triage. Candidate images require review; labels are unchanged.",
              "limitations": "Sampling and hashes can miss brief, cropped, edited or re-encoded shared footage. "
                             "Matching views can resemble each other. This does not certify source independence or full-video labels."}
    write_json(out / "triage.json", report)
    cards = "".join(f"<article><h2>Pair {i}: {'flagged' if p['flagged'] else 'nearest candidate'}</h2>"
                    f"<p>{html.escape(p['first_path'])}<br>{html.escape(p['second_path'])}</p>"
                    f"<img src='{p['contact_sheet']}' alt='Aligned source-review frames'></article>"
                    for i, p in enumerate(selected, 1))
    (out / "index.html").write_text("<!doctype html><meta charset='utf-8'><title>Source-overlap review</title>"
                                  "<style>body{font:16px system-ui;max-width:1100px;margin:30px auto;padding:20px}"
                                  "img{max-width:100%}article{border-top:1px solid #ddd;padding:20px 0}</style>"
                                  f"<h1>Source-overlap review</h1><p>{len(rows)} videos fully decoded, "
                                  f"{report['sampled_frames']} sampled frames, {compared} pairs compared. "
                                  f"{report['flagged_pairs']} pairs flagged. This is source triage, not label validation.</p>{cards}",
                                  encoding="utf-8")
    print(f"Source review ready: {report['flagged_pairs']} flagged pairs; {out / 'index.html'}", flush=True)
    return report
