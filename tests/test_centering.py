import json

import numpy as np
import pytest
import torch

from affective.demo import infer_cache, load_model
from affective.features import FEATURE_SCHEMA, LEGACY_FEATURE_SCHEMA, build_features, track_centers
from affective.model import CrowdTCN


def stationary(frames=5, people=2):
    points = np.zeros((frames, people, 17, 3), dtype=np.float32)
    points[..., :2] = [.4, .45]
    points[..., 2] = .9
    points[:, :, 11, :2] = [.35, .65]
    points[:, :, 12, :2] = [.45, .65]
    boxes = np.tile(np.array([.2, .1, .8, .9], dtype=np.float32), (frames, people, 1))
    for person in range(people):
        points[:, person, :, 0] += person * .1
        boxes[:, person, [0, 2]] += person * .1
    return points, boxes, np.ones((frames, people), dtype=bool), np.arange(frames, dtype=np.float32) / 10


@pytest.mark.parametrize("reliability", [False, True])
def test_static_hip_dropout_cannot_create_body_or_interaction_motion(reliability):
    points, boxes, present, times = stationary()
    points[1:4, 0, [11, 12], 2] = 0
    points[2, 1, [11, 12], 2] = 0
    corrected, mask = build_features(points, boxes, present, times, reliability, True)
    original, _ = build_features(points, boxes, present, times, reliability, True,
                                 feature_schema=LEGACY_FEATURE_SCHEMA)
    shoulder_velocity = slice(34 + 5 * 2, 34 + 5 * 2 + 2)
    assert np.abs(original[:, :, shoulder_velocity]).max() > .5
    np.testing.assert_allclose(corrected[:, :, shoulder_velocity], 0, atol=1e-6)
    np.testing.assert_allclose(corrected[:, :, -5:-2], 0, atol=1e-6)
    np.testing.assert_allclose(corrected[:, :, -8], .1, atol=1e-6)
    np.testing.assert_array_equal(mask, present)


def test_actual_wrist_motion_is_preserved_during_hip_dropout():
    points, boxes, present, times = stationary(people=1)
    points[1:4, 0, [11, 12], 2] = 0
    points[:, 0, 9, 0] += np.arange(5, dtype=np.float32) * .02
    features, _ = build_features(points, boxes, present, times)
    np.testing.assert_allclose(features[1:, 0, 34 + 9 * 2], .2, atol=1e-6)
    np.testing.assert_allclose(features[:, 0, 34 + 5 * 2:34 + 5 * 2 + 2], 0, atol=1e-6)


def test_real_relative_translation_is_preserved_during_hip_dropout():
    points, boxes, present, times = stationary()
    for frame in range(5):
        points[frame, 0, :, 0] += .015 * frame
        boxes[frame, 0, [0, 2]] += .015 * frame
    points[1:4, 0, [11, 12], 2] = 0
    features, _ = build_features(points, boxes, present, times, interactions=True)
    np.testing.assert_allclose(features[1:, 0, -5], -.15, atol=1e-6)
    np.testing.assert_allclose(features[1:, 1, -5], .15, atol=1e-6)
    np.testing.assert_allclose(features[1:, :, -3], -.15, atol=1e-6)


@pytest.mark.parametrize("hips_reliable", [False, True])
def test_correction_is_identical_when_reference_does_not_change(hips_reliable):
    points, boxes, present, times = stationary()
    if not hips_reliable:
        points[:, :, [11, 12], 2] = 0
    for reliability, interactions in ((False, False), (True, False), (False, True), (True, True)):
        corrected, _ = build_features(points, boxes, present, times, reliability, interactions)
        original, _ = build_features(points, boxes, present, times, reliability, interactions,
                                     feature_schema=LEGACY_FEATURE_SCHEMA)
        np.testing.assert_array_equal(corrected, original)


def test_missing_track_segment_does_not_borrow_root_from_a_later_segment():
    points, boxes, present, times = stationary(people=1)
    points[:2, 0, [11, 12], 2] = 0
    present[2, 0] = False
    corrected, _ = build_features(points, boxes, present, times, interactions=True)
    original, _ = build_features(points, boxes, present, times, interactions=True,
                                 feature_schema=LEGACY_FEATURE_SCHEMA)
    np.testing.assert_array_equal(corrected[:2], original[:2])
    np.testing.assert_array_equal(corrected[2], 0)
    np.testing.assert_array_equal(corrected[3, :, 34:68], 0)


def test_single_anchor_extends_to_segment_edges_and_body_scaling_is_invariant():
    points, boxes, present, times = stationary(people=1)
    points[[0, 1, 3, 4], 0, [11], 2] = 0
    points[[0, 1, 3, 4], 0, [12], 2] = 0
    features, _ = build_features(points, boxes, present, times, reliability=True)
    np.testing.assert_allclose(features[:, 0, 34 + 5 * 2:34 + 5 * 2 + 2], 0, atol=1e-6)
    shifted = points.copy()
    shifted[..., :2] = shifted[..., :2] * .6 + .1
    transformed, _ = build_features(shifted, boxes * .6 + .1, present, times, reliability=True)
    np.testing.assert_allclose(features, transformed, atol=2e-6)


def test_interpolation_uses_sample_times_and_repeated_timestamps_remain_finite():
    points, boxes, present, times = stationary(people=1)
    times = np.array([0., .1, .1, .4, 1.], dtype=np.float32)
    points[1:4, 0, [11, 12], 2] = 0
    points[4, 0, [11, 12], 0] += .2
    xy = points[..., :2]
    hips_ok = (points[..., 2] >= .25)[..., 11] & (points[..., 2] >= .25)[..., 12]
    centers = track_centers(xy, boxes, present, hips_ok, times)
    np.testing.assert_allclose(centers[:, 0, 0], .4 + times * .2, atol=1e-6)
    features, _ = build_features(points, boxes, present, times)
    assert np.isfinite(features).all()
    with pytest.raises(ValueError, match="Unsupported feature schema"):
        build_features(points, boxes, present, times, feature_schema="unknown")


def test_legacy_checkpoint_inference_keeps_original_feature_semantics(tmp_path):
    points, boxes, present, times = stationary(frames=3, people=1)
    points[1, 0, [11, 12], 2] = 0
    model = CrowdTCN(68, hidden=8).eval()
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.zero_()
        model.project.weight[0, 34 + 5 * 2, 0] = 1
        model.temporal[0].net[0].weight[0, 0, 1] = 1
        model.temporal[0].net[3].weight[0, 0, 0] = 1
        model.classifier[0].weight[0, 0] = 1
        model.classifier[3].weight[0, 0] = 1
    checkpoint = {"feature_schema": LEGACY_FEATURE_SCHEMA, "state_dict": model.state_dict(),
                  "input_dim": 68, "hidden": 8, "variant": "baseline", "seed": 42,
                  "pose_signature": "test", "threshold": .54, "mean": torch.zeros(68), "std": torch.ones(68)}
    torch.save(checkpoint, tmp_path / "legacy.pt")
    np.savez_compressed(tmp_path / "poses.npz", keypoints=points, boxes=boxes, present=present, times=times,
                        signature=np.array("test"), track_ids=np.array([1]), frame_indices=np.arange(3),
                        quality=np.array(json.dumps({"usable_pose_fraction": 1., "seconds_including_decode": .1})))
    loaded, saved = load_model(tmp_path / "legacy.pt")
    inferred, _ = infer_cache(loaded, saved, tmp_path / "poses.npz")
    original, mask = build_features(points, boxes, present, times, feature_schema=LEGACY_FEATURE_SCHEMA)
    corrected, _ = build_features(points, boxes, present, times)
    with torch.inference_mode():
        expected = loaded(torch.from_numpy(original[None]), torch.from_numpy(mask[None])).sigmoid().item()
        changed = loaded(torch.from_numpy(corrected[None]), torch.from_numpy(mask[None])).sigmoid().item()
    assert inferred["score"] == expected
    assert expected > changed
    assert changed == .5
