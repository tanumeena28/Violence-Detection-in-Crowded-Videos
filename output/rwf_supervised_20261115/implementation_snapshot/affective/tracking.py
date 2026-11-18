"""Short-lived, within-video tracking by box overlap and normalized center distance."""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment


def box_iou(a, b):
    lo, hi = np.maximum(a[:2], b[:2]), np.minimum(a[2:], b[2:])
    inter = np.maximum(hi - lo, 0).prod()
    area_a = np.maximum(a[2:] - a[:2], 0).prod()
    area_b = np.maximum(b[2:] - b[:2], 0).prod()
    return float(inter / max(area_a + area_b - inter, 1e-8))


class ClipTracker:
    """IDs reset on each clip. Occlusion and fast motion can still break tracks."""
    def __init__(self, max_gap=2, distance_gate=0.18):
        self.max_gap = max_gap
        self.distance_gate = distance_gate
        self.tracks = {}
        self.next_id = 1

    def update(self, boxes, frame_index):
        active = [i for i, t in self.tracks.items() if frame_index - t["last"] <= self.max_gap + 1]
        ids = np.full(len(boxes), -1, dtype=np.int32)
        if active and len(boxes):
            cost = np.full((len(active), len(boxes)), 1e6, dtype=np.float32)
            for i, tid in enumerate(active):
                old = self.tracks[tid]["box"]
                center = (old[:2] + old[2:]) / 2
                for j, box in enumerate(boxes):
                    distance = float(np.linalg.norm(center - (box[:2] + box[2:]) / 2))
                    iou = box_iou(old, box)
                    if iou >= 0.1 or distance <= self.distance_gate:
                        cost[i, j] = (1 - iou) + 2 * distance
            ri, ci = linear_sum_assignment(cost)
            for i, j in zip(ri, ci):
                if cost[i, j] < 1e5:
                    ids[j] = active[i]
        for j, box in enumerate(boxes):
            if ids[j] < 0:
                ids[j] = self.next_id
                self.next_id += 1
            self.tracks[int(ids[j])] = {"box": box.copy(), "last": frame_index}
        return ids


def pack_tracks(detections, max_people):
    """Keep the tracks with most observed joint signal; retain stable slots over time."""
    scores = {}
    for frame in detections:
        for tid, points in zip(frame["ids"], frame["keypoints"]):
            scores[int(tid)] = scores.get(int(tid), 0) + float(points[:, 2].sum())
    selected = sorted(scores, key=lambda i: (-scores[i], i))[:max_people]
    slot = {tid: i for i, tid in enumerate(selected)}
    points = np.zeros((len(detections), max_people, 17, 3), np.float32)
    boxes = np.zeros((len(detections), max_people, 4), np.float32)
    present = np.zeros((len(detections), max_people), bool)
    for t, frame in enumerate(detections):
        for tid, pose, box in zip(frame["ids"], frame["keypoints"], frame["boxes"]):
            if int(tid) in slot:
                p = slot[int(tid)]
                points[t, p], boxes[t, p], present[t, p] = pose, box, True
    return points, boxes, present, np.array(selected + [-1] * (max_people - len(selected)), dtype=np.int32), len(scores)
