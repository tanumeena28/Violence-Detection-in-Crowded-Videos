import cv2
import numpy as np
import pytest

from affective.motion import fit_control, motion_features, score_linear
from affective.cross_validation import write_manifest
import json


def test_static_video_has_zero_motion_and_translation_has_signal():
    rng = np.random.default_rng(8)
    image = rng.integers(0, 256, (120, 160), dtype=np.uint8)
    static = motion_features([image] * 4, np.array([0, 1, 2, 3]), 25.)
    shifted = [cv2.warpAffine(image, np.float32([[1, 0, 2 * t], [0, 1, 0]]), (160, 120), borderMode=cv2.BORDER_REFLECT) for t in range(4)]
    moving = motion_features(shifted, np.array([0, 1, 2, 3]), 25.)
    np.testing.assert_allclose(static.reshape(4, 4, 5)[..., 0], 0)
    assert static.max() < .005
    mean_channels = moving[:20].reshape(4, 5).mean(0)
    assert mean_channels[0] > .1
    assert mean_channels[1] > .1
    assert mean_channels[3] > .1
    assert mean_channels[2] < mean_channels[1]
    assert np.isfinite(moving).all()


def test_motion_rejects_invalid_timing_and_anchors():
    images = [np.zeros((120, 160), np.uint8)] * 2
    with pytest.raises(ValueError):
        motion_features(images, np.array([0]), 0)
    with pytest.raises(ValueError):
        motion_features(images, np.array([2]), 25)


def test_linear_checkpoint_uses_saved_training_scaling():
    checkpoint = {"mean": [2., 4.], "std": [2., 1.], "coefficients": [1., -1.], "intercept": 0.}
    np.testing.assert_allclose(score_linear(np.array([[2., 4.], [4., 4.]]), checkpoint), [0.5, 1 / (1 + np.exp(-1))])


def test_outer_test_changes_do_not_select_control_parameters(tmp_path):
    rows = [{"id": str(i), "path": f"{i}.avi", "split": ["train", "val", "test"][i // 4],
             "label": i % 2} for i in range(12)]
    rng = np.random.default_rng(30)
    features = rng.normal(size=(12, 3))
    features[:, 0] += np.array([r["label"] for r in rows]) * 2
    checkpoints = []
    for name in ("original", "changed_test"):
        out = tmp_path / name
        out.mkdir()
        current_rows = [dict(r) for r in rows]
        current_features = features.copy()
        if name == "changed_test":
            for r in current_rows[8:]:
                r["label"] = 1 - r["label"]
            current_features[8:] += 100
        write_manifest(out / "manifest.csv", current_rows)
        fit_control(out, current_rows, current_features, "motion_linear", "test", [.01, .1, 1., 10.], protocol="CV test")
        checkpoints.append(json.loads((out / "motion" / "motion_linear" / "model.json").read_text(encoding="utf-8")))
    for key in ("mean", "std", "coefficients", "intercept", "threshold", "selected_C"):
        assert checkpoints[0][key] == checkpoints[1][key]
