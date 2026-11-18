import numpy as np

from affective.source_review import compare_clips, hash_gray


def clip(grays, offset=0.):
    flat = grays.astype(np.float32).reshape(len(grays), -1)
    flat -= flat.mean(-1, keepdims=True)
    flat /= np.maximum(np.linalg.norm(flat, axis=-1, keepdims=True), 1e-6)
    hashes = np.array([hash_gray(g) for g in grays], dtype=np.uint64)
    return {"times": np.arange(len(grays)) / 4 + offset,
            "hashes": np.repeat(hashes[:, None], 2, axis=1),
            "normalized": np.repeat(flat[:, None], 2, axis=1),
            "textured": np.repeat((grays.std((1, 2)) >= 8)[:, None], 2, axis=1)}


def test_shared_sequence_is_found_at_a_different_time_offset():
    rng = np.random.default_rng(80)
    grays = rng.integers(0, 250, (8, 48, 64), dtype=np.uint8)
    original = clip(grays)
    altered = clip(grays + 3, offset=2.)
    matching = compare_clips(original, altered)
    assert matching["flagged"]
    assert matching["matched_frames"] >= 6
    assert matching["span_seconds"] >= 1.
    unrelated = clip(rng.integers(0, 250, grays.shape, dtype=np.uint8))
    assert not compare_clips(original, unrelated)["flagged"]


def test_black_transition_frames_do_not_merge_sources():
    black = clip(np.zeros((8, 48, 64), dtype=np.uint8))
    assert not compare_clips(black, black)["flagged"]
