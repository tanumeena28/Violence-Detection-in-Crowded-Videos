"""Controlled removal of kinematics and permutation of derived time slices."""
from __future__ import annotations

import hashlib

import numpy as np

INPUT_CONTROLS = ("full", "detection_only", "shuffled_time")


def control_inputs(features, mask, clip_id, control="full"):
    if control not in INPUT_CONTROLS:
        raise ValueError(f"Unsupported input control: {control}")
    if control == "full":
        return features, mask
    if features.shape[-1] != 110:
        raise ValueError("Input controls require the 110-channel combined variant")
    if control == "detection_only":
        result = features.copy()
        result[..., :68] = 0  # Joint coordinates and velocities.
        result[..., 102:108] = 0  # Interaction geometry, velocity and approach.
        return result, mask
    # Velocities are already derived before permutation. This tests the order
    # of feature slices, not the removal of all motion evidence.
    seed = int.from_bytes(hashlib.sha256(("time-control-v1:" + str(clip_id)).encode()).digest()[:8], "little")
    permutation = np.random.default_rng(seed).permutation(len(features))
    return features[permutation], mask[permutation]
