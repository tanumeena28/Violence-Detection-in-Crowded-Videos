import numpy as np
import pytest

from affective.input_controls import control_inputs


def test_detection_control_removes_all_kinematics_and_preserves_detection_channels():
    x = np.arange(4 * 2 * 110, dtype=np.float32).reshape(4, 2, 110)
    mask = np.array([[1, 0], [1, 1], [0, 1], [1, 1]], dtype=np.float32)
    controlled, observed = control_inputs(x, mask, "clip", "detection_only")
    np.testing.assert_array_equal(controlled[..., :68], 0)
    np.testing.assert_array_equal(controlled[..., 102:108], 0)
    np.testing.assert_array_equal(controlled[..., 68:102], x[..., 68:102])
    np.testing.assert_array_equal(controlled[..., 108:], x[..., 108:])
    np.testing.assert_array_equal(mask, observed)
    assert x[0, 0, 1] == 1


def test_time_shuffle_preserves_frame_mask_pairs_and_is_stable_per_clip():
    x = np.broadcast_to(np.arange(32)[:, None, None], (32, 2, 110)).astype(np.float32)
    mask = np.stack([np.arange(32), np.arange(32) + 100], axis=1)
    changed, observed = control_inputs(x, mask, "clip-a", "shuffled_time")
    repeated, repeated_mask = control_inputs(x, mask, "clip-a", "shuffled_time")
    np.testing.assert_array_equal(changed, repeated)
    np.testing.assert_array_equal(observed, repeated_mask)
    np.testing.assert_array_equal(np.sort(changed[:, 0, 0]), np.arange(32))
    np.testing.assert_array_equal(changed[:, 0, 0], observed[:, 0])
    assert not np.array_equal(changed, x)
    with pytest.raises(ValueError, match="Unsupported input control"):
        control_inputs(x, mask, "clip", "unknown")
    with pytest.raises(ValueError, match="110-channel"):
        control_inputs(x[..., :68], mask, "clip", "detection_only")
