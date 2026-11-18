"""Body motion, confidence masks, and interactions in shared image coordinates."""
from __future__ import annotations

import numpy as np

LEGACY_FEATURE_SCHEMA = "coco17-hip-box-center-v1"
FEATURE_SCHEMA = "coco17-continuous-hip-offset-v2"
FEATURE_SCHEMAS = (LEGACY_FEATURE_SCHEMA, FEATURE_SCHEMA)
# Raw pose tensors are unchanged by the derived-feature correction. Retain the
# recorded extraction descriptor so existing poses and fresh inference agree.
POSE_SCHEMA = LEGACY_FEATURE_SCHEMA


def track_centers(xy, boxes, present, hips_ok, times):
    """Estimate a continuous hip origin inside each observed track segment.

    Reliable frames use the measured hip midpoint exactly. Missing-hip frames
    use an interpolated hip-to-box offset, with nearest-anchor extension at
    segment boundaries. Segments with no reliable hips use their box center.
    This is offline full-clip interpolation; absent observations are not filled.
    """
    box_center = (boxes[..., :2] + boxes[..., 2:]) / 2
    hip_center = (xy[..., 11, :] + xy[..., 12, :]) / 2
    center = np.where(hips_ok[..., None], hip_center, box_center)
    for person in range(present.shape[1]):
        observed = present[:, person].astype(bool)
        edges = np.diff(np.r_[False, observed, False].astype(np.int8))
        for start, end in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)):
            segment = np.arange(start, end)
            anchors = segment[hips_ok[segment, person]]
            missing = segment[~hips_ok[segment, person]]
            if not len(anchors) or not len(missing):
                continue
            offsets = hip_center[anchors, person] - box_center[anchors, person]
            interpolated = np.stack([np.interp(times[missing], times[anchors], offsets[:, axis])
                                     for axis in range(2)], axis=-1).astype(np.float32)
            center[missing, person] = box_center[missing, person] + interpolated
    return center


def build_features(keypoints, boxes, present, times, reliability=False, interactions=False,
                   joint_threshold=0.25, feature_schema=FEATURE_SCHEMA):
    """Return (T,P,F) features and (T,P) observation mask.

    Both baseline and variants share the same missing-data policy. Reliability
    adds confidence weighting and explicit per-joint validity channels. Distances
    are calculated BEFORE individual body centering.
    """
    if feature_schema not in FEATURE_SCHEMAS:
        raise ValueError(f"Unsupported feature schema: {feature_schema}")
    xy = keypoints[..., :2].astype(np.float32)
    confidence = keypoints[..., 2].astype(np.float32)
    valid = (confidence >= joint_threshold) & present[..., None]
    hips_ok = valid[..., 11] & valid[..., 12]
    if feature_schema == LEGACY_FEATURE_SCHEMA:
        box_center = (boxes[..., :2] + boxes[..., 2:]) / 2
        center = np.where(hips_ok[..., None], (xy[..., 11, :] + xy[..., 12, :]) / 2, box_center)
    else:
        center = track_centers(xy, boxes, present, hips_ok, times)
    # A box-size fallback is defined even when both shoulders are missing.
    scale = np.maximum(np.linalg.norm(boxes[..., 2:] - boxes[..., :2], axis=-1), 0.03)
    centered = (xy - center[..., None, :]) / scale[..., None, None]
    centered = np.clip(centered, -3, 3) * valid[..., None]
    velocity = np.zeros_like(centered)
    dt = np.maximum(np.diff(times), 1e-3).astype(np.float32)
    paired = valid[1:] & valid[:-1]
    velocity[1:] = np.clip((centered[1:] - centered[:-1]) / dt[:, None, None, None], -10, 10) * paired[..., None]
    if reliability:
        centered = centered * confidence[..., None]
        velocity = velocity * confidence[..., None]
    t, p = present.shape
    channels = [centered.reshape(t, p, -1), velocity.reshape(t, p, -1)]
    if reliability:
        channels += [confidence * valid, valid.astype(np.float32)]
    if interactions:
        scene_velocity = np.zeros_like(center)
        adjacent = present[1:] & present[:-1]
        scene_velocity[1:] = np.clip((center[1:] - center[:-1]) / dt[:, None, None], -10, 10) * adjacent[..., None]
        interaction = np.zeros((t, p, 8), np.float32)
        for ti in range(t):
            people = np.flatnonzero(present[ti])
            for person in people:
                others = people[people != person]
                if not len(others):
                    continue
                offsets = center[ti, others] - center[ti, person]
                distances = np.linalg.norm(offsets, axis=1)
                k = int(distances.argmin())
                nearest = others[k]
                relative_velocity = scene_velocity[ti, nearest] - scene_velocity[ti, person]
                approach = np.dot(offsets[k], relative_velocity) / max(distances[k], 1e-4)
                interaction[ti, person] = [distances[k], *offsets[k], *relative_velocity,
                                          np.clip(approach, -10, 10), min(len(others), p) / max(p - 1, 1), 1]
        channels.append(interaction)
    features = np.concatenate(channels, axis=-1).astype(np.float32)
    features *= present[..., None]
    if not np.isfinite(features).all():
        raise ValueError("Non-finite feature values")
    return features, present.astype(np.float32)


def feature_dim(reliability, interactions):
    return 68 + 34 * int(reliability) + 8 * int(interactions)
