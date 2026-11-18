"""Deterministic local video windows for the frozen RWF temporal study."""
from __future__ import annotations

import cv2
import numpy as np

SETTINGS = {
    'schema': 'r3d18-global-local-mean-max-v1',
    'local_windows': 4, 'frames_per_window': 16, 'target_sample_fps': 15.,
    'start_rule': 'Rounded evenly spaced starts from zero to last legal start',
    'stride_rule': 'Round source FPS / 15, clamp to at least one and fit within decoded length',
    'short_clip_rule': 'Below 16 decoded frames, repeat uniformly sampled indices in each window',
    'pooling': 'Concatenate original global mean embedding, local mean embedding, local componentwise maximum embedding',
    'feature_dimensions': 1536, 'encoder_batch_size': 2,
}


def window_indices(decoded_frames, fps):
    if decoded_frames < 2 or not np.isfinite(fps) or fps <= 0:
        raise ValueError('At least two frames and positive finite FPS required')
    if decoded_frames < 16:
        return np.tile(np.linspace(0, decoded_frames-1, 16).round().astype(np.int32), (4, 1))
    stride = max(1, min(round(fps/15.), (decoded_frames-1)//15))
    span = 15*stride+1
    starts = np.linspace(0, decoded_frames-span, 4).round().astype(np.int32)
    return starts[:, None] + stride*np.arange(16, dtype=np.int32)[None, :]


def decode_windows(path):
    cap = cv2.VideoCapture(str(path))
    fps, frames = float(cap.get(cv2.CAP_PROP_FPS)), []
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frames.append(frame)
    finally:
        cap.release()
    local = window_indices(len(frames), fps)
    global_indices = np.linspace(0, len(frames)-1, 32).round().astype(np.int32)
    return frames, local, global_indices, fps


def encode_indices(model, transform, frames, indices, device):
    import torch
    embeddings = []
    for start in range(0, len(indices), 2):
        tensors = []
        for window in indices[start:start+2]:
            rgb = np.stack([frames[int(i)][..., ::-1].copy() for i in window])
            tensors.append(transform(torch.from_numpy(rgb).permute(0, 3, 1, 2)))
        with torch.inference_mode():
            embeddings.append(model(torch.stack(tensors).to(device)).cpu().numpy().astype(np.float32))
    result = np.concatenate(embeddings)
    if result.shape != (len(indices), 512) or not np.isfinite(result).all():
        raise ValueError('Invalid frozen encoder output')
    return result


def combine_embeddings(global_embedding, local_embeddings):
    global_embedding = np.asarray(global_embedding, dtype=np.float32)
    local_embeddings = np.asarray(local_embeddings, dtype=np.float32)
    if (global_embedding.shape != (512,) or local_embeddings.shape != (4, 512)
            or not np.isfinite(global_embedding).all() or not np.isfinite(local_embeddings).all()):
        raise ValueError('Invalid global or local embeddings')
    return np.concatenate([global_embedding, local_embeddings.mean(0), local_embeddings.max(0)])
