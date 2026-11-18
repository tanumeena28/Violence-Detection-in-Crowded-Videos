import json

import cv2
import numpy as np
import pytest
import torch

from affective.data import decode_sample
from affective.inference import VideoPredictor, decode_sample_bounded, iter_video_windows


def make_video(path, frames):
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'MJPG'), 10, (48, 32))
    assert writer.isOpened()
    for i in range(frames):
        writer.write(np.full((32, 48, 3), i * 3, dtype=np.uint8))
    writer.release()


@pytest.mark.parametrize('frames', [3, 37])
def test_bounded_decode_preserves_exact_training_samples(tmp_path, frames):
    video = tmp_path / 'sample.avi'
    make_video(video, frames)
    expected, expected_indices, expected_fps, expected_count = decode_sample(video, 32)
    actual, indices, fps, count = decode_sample_bounded(video)
    assert count == expected_count == frames
    assert fps == expected_fps
    np.testing.assert_array_equal(indices, expected_indices)
    for first, second in zip(actual, expected):
        np.testing.assert_array_equal(first, second)


def test_windows_account_for_unscorable_single_frame_tail(tmp_path):
    video = tmp_path / 'windows.avi'
    make_video(video, 21)
    windows = list(iter_video_windows(video, seconds=1))
    assert [w[3] for w in windows] == [10, 10, 1]
    assert [w[4] for w in windows] == [0, 1, 2]
    assert windows[-1][0] is None
    assert windows[-1][1] is None
    assert sum(w[3] for w in windows) == 21


def test_model_protocol_tampering_fails_before_model_initialization(tmp_path):
    (tmp_path / 'protocol.json').write_text(json.dumps({'schema': 'rwf-r3d18-layer4-finetune-v1'}))
    (tmp_path / 'head_frozen.json').write_text(json.dumps({'protocol_sha256': 'incorrect'}))
    with pytest.raises(ValueError, match='Sealed video protocol changed'):
        VideoPredictor(tmp_path, device='cpu')


def test_single_video_preserves_validation_batch_shape():
    predictor = VideoPredictor.__new__(VideoPredictor)
    predictor.device = 'cpu'
    predictor.finetuned = True
    predictor.plan = {'batch_size_clips': 2}
    predictor.threshold = .23
    predictor.model_hash = 'test'
    predictor.transform = lambda frames: frames.float().permute(1, 0, 2, 3)

    def score(batch):
        assert batch.shape[:3] == (2, 2, 3)
        torch.testing.assert_close(batch[0], batch[1], rtol=0, atol=0)
        return torch.tensor([0., 1.])

    predictor.model = score
    images = [np.zeros((4, 4, 3), dtype=np.uint8) for _ in range(32)]
    result = predictor.process(images, np.arange(32), 10, 32)
    assert result['score'] == .5
    assert result['prediction'] == 1
