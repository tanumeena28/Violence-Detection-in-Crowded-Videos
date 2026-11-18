import json
from pathlib import Path

import numpy as np
import pytest

from affective.data import write_json
from affective.cross_validation import digest
from affective.temporal_video import window_indices, combine_embeddings
from scripts.run_rwf_temporal import development_gate, evaluation_globals


def test_five_second_windows_preserve_local_speed_and_cover_endpoints():
    indices = window_indices(150, 30.)
    assert indices.shape == (4, 16)
    np.testing.assert_array_equal(np.diff(indices, axis=1), np.full((4, 15), 2))
    assert indices[0, 0] == 0 and indices[-1, -1] == 149
    assert np.all(indices[:-1, 0] < indices[1:, 0])
    # The encoder sees about one second per local window rather than 2.5 seconds.
    np.testing.assert_allclose((indices[:, -1] - indices[:, 0])/30., 1.)


def test_short_and_high_fps_clips_stay_within_fully_decoded_frames():
    for length, fps in [(2, 30.), (15, 30.), (16, 30.), (18, 120.), (80, 60.), (300, 60.)]:
        indices = window_indices(length, fps)
        assert indices.shape == (4, 16)
        assert indices.min() == 0 and indices.max() == length-1
        assert np.all(np.diff(indices, axis=1) >= 0)
    for length, fps in [(1, 30.), (150, 0), (150, np.nan)]:
        with pytest.raises(ValueError):
            window_indices(length, fps)


def test_pooling_retains_a_localized_response_and_the_original_global_branch():
    global_vector = np.full(512, 2., dtype=np.float32)
    local = np.zeros((4, 512), np.float32)
    local[2, 0] = 8.
    combined = combine_embeddings(global_vector, local)
    np.testing.assert_array_equal(combined[:512], global_vector)
    assert combined[512] == 2. and combined[1024] == 8.
    assert combined.shape == (1536,) and combined.dtype == np.float32
    with pytest.raises(ValueError):
        combine_embeddings(global_vector, local[:3])


def selection(loss, f1, recall):
    return {'candidates': [{'validation_log_loss': loss}],
            'validation': {'macro_f1': f1, 'recall_violent': recall}}


def test_promotion_requires_every_predeclared_validation_criterion():
    reference = selection(.4, .82, .74)
    assert development_gate(selection(.39, .83, .74), reference)['eligible_for_evaluation']
    for rejected in [selection(.4, .83, .74), selection(.39, .82, .74), selection(.39, .83, .73)]:
        assert not development_gate(rejected, reference)['eligible_for_evaluation']


def test_evaluation_arrays_cannot_load_before_sealing_or_after_rejection(tmp_path, monkeypatch):
    loaded = []
    monkeypatch.setattr(np, 'load', lambda *args, **kwargs: loaded.append(args))
    with pytest.raises(FileNotFoundError):
        evaluation_globals(tmp_path, {})
    write_json(tmp_path/'protocol.json', {'frozen': True})
    write_json(tmp_path/'promotion.json', {'eligible_for_evaluation': False})
    write_json(tmp_path/'head_frozen.json', {
        'protocol_sha256': digest(tmp_path/'protocol.json'),
        'artifacts_sha256': {'promotion.json': digest(tmp_path/'promotion.json')}})
    with pytest.raises(ValueError, match='failed development gate'):
        evaluation_globals(tmp_path, {})
    assert not loaded
    write_json(tmp_path/'promotion.json', {'eligible_for_evaluation': True})
    with pytest.raises(ValueError, match='Selected development artifact changed'):
        evaluation_globals(tmp_path, {})
    assert not loaded
