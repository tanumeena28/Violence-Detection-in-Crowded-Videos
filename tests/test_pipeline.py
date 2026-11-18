import numpy as np
import pytest
import torch

from affective.features import build_features, feature_dim
from affective.model import CrowdTCN
from affective.tracking import ClipTracker
from affective.train import choose_threshold
from affective.data import canonicalize_source_groups, source_overlap_candidates


def example():
    points = np.zeros((4, 2, 17, 3), np.float32)
    points[..., :2] = np.array([0.4, 0.5])
    points[:, 1, :, 0] += 0.2
    points[..., 2] = 0.9
    boxes = np.tile(np.array([0.3, 0.2, 0.5, 0.8], np.float32), (4, 2, 1))
    boxes[:, 1, [0, 2]] += 0.2
    return points, boxes, np.ones((4, 2), bool), np.arange(4, dtype=np.float32)


def test_interactions_preserve_spacing_before_body_centering():
    points, boxes, present, times = example()
    x, _ = build_features(points, boxes, present, times, interactions=True)
    assert x.shape[-1] == feature_dim(False, True)
    np.testing.assert_allclose(x[:, :, :34], 0, atol=1e-6)
    np.testing.assert_allclose(x[:, :, -8], 0.2, atol=1e-6)
    points[:, 1, :, 0] += 0.1
    boxes[:, 1, [0, 2]] += 0.1
    shifted, _ = build_features(points, boxes, present, times, interactions=True)
    np.testing.assert_allclose(shifted[:, :, -8], 0.3, atol=1e-6)


def test_missing_joint_cannot_create_velocity_spike():
    points, boxes, present, times = example()
    points[1, 0, 9, 2] = 0
    points[1, 0, 9, :2] = 0
    x, _ = build_features(points, boxes, present, times, reliability=True)
    np.testing.assert_array_equal(x[1:3, 0, 34 + 9 * 2:34 + 9 * 2 + 2], 0)
    assert np.isfinite(x).all()


def test_tracking_survives_detection_order_change_and_resets():
    tracker = ClipTracker()
    boxes = np.array([[0.1, 0.1, 0.2, 0.3], [0.7, 0.1, 0.8, 0.3]], np.float32)
    ids = tracker.update(boxes, 0)
    new_ids = tracker.update(boxes[::-1] + 0.01, 1)
    np.testing.assert_array_equal(new_ids, ids[::-1])
    np.testing.assert_array_equal(ClipTracker().update(boxes, 0), [1, 2])


@pytest.mark.parametrize("use_coverage", [True, False])
def test_set_pooling_is_permutation_invariant_and_masks_empty_tracks(use_coverage):
    torch.manual_seed(1)
    model = CrowdTCN(68, hidden=12, use_coverage=use_coverage).eval()
    x = torch.randn(2, 6, 3, 68)
    mask = torch.ones(2, 6, 3)
    mask[:, :, 2] = 0
    with torch.inference_mode():
        expected = model(x, mask)
        shuffled = model(x[:, :, [2, 0, 1]], mask[:, :, [2, 0, 1]])
        corrupted = x.clone()
        corrupted[:, :, 2] = 1e6
        ignored = model(corrupted, mask)
        empty = model(x, torch.zeros_like(mask))
    torch.testing.assert_close(expected, shuffled)
    torch.testing.assert_close(expected, ignored)
    assert torch.isfinite(empty).all()


def test_disabling_coverage_removes_padding_cue_with_identical_initialization():
    torch.manual_seed(13)
    enabled = CrowdTCN(68, hidden=12).eval()
    torch.manual_seed(13)
    disabled = CrowdTCN(68, hidden=12, use_coverage=False).eval()
    for name, value in enabled.state_dict().items():
        torch.testing.assert_close(value, disabled.state_dict()[name], rtol=0, atol=0)
    # The retained person's features are identical. Empty padding changes only
    # explicit coverage, and must have no effect when that scalar is disabled.
    features = torch.randn(2, 6, 1, 68)
    mask = torch.ones(2, 6, 1)
    padded = torch.cat([features, torch.randn(2, 6, 3, 68)], dim=2)
    padded_mask = torch.cat([mask, torch.zeros(2, 6, 3)], dim=2)
    with torch.inference_mode():
        torch.testing.assert_close(disabled(features, mask), disabled(padded, padded_mask))
        assert not torch.allclose(enabled(features, mask), enabled(padded, padded_mask))


def test_threshold_uses_supplied_validation_scores():
    y = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.2, 0.3, 0.4])
    threshold = choose_threshold(y, scores)
    assert 0.2 < threshold <= 0.3


def test_truncated_source_ids_link_without_merging_other_uploaders_or_ids():
    keys = ["same_title__uploader__abc123", "same_title__uploader__ab",
            "same_title__other_uploader__ab", "same_title__uploader__xyz123"]
    rows = [{"id": str(i), "path": str(i) + ".avi", "source_group": key,
             "split": "val" if i == 1 else "train"} for i, key in enumerate(keys)]
    resolved, aliases = canonicalize_source_groups(rows)
    assert resolved[0]["source_group"] == resolved[1]["source_group"]
    assert resolved[2]["source_group"] != resolved[0]["source_group"]
    assert resolved[3]["source_group"] != resolved[0]["source_group"]
    assert aliases == {keys[0]: keys[1]}
    pairs = source_overlap_candidates(rows)
    assert len(pairs) == 1 and pairs[0]["first_id"] == "0" and pairs[0]["second_id"] == "1"
    assert rows[0]["source_group"] == keys[0]
