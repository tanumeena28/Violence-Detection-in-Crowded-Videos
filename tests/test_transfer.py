import hashlib
import json

import cv2
import numpy as np
import pytest
import torch

from affective.cross_validation import write_manifest
from affective.data import write_json
from affective.features import FEATURE_SCHEMA
from affective.model import CrowdTCN
from scripts import evaluate_rwf_transfer as transfer


def test_saved_normalization_is_independent_of_other_evaluation_observations():
    checkpoint = {"mean": torch.tensor([2., -1.]), "std": torch.tensor([2., .5])}
    features = np.array([[[4., 0.], [999., 999.]]], dtype=np.float32)
    mask = np.array([[1., 0.]], dtype=np.float32)
    normalized = transfer.normalize_saved(features, mask, checkpoint)
    np.testing.assert_array_equal(normalized, [[[1., 2.], [0., 0.]]])
    shifted = np.concatenate([features, features + 1000], axis=0)
    both = transfer.normalize_saved(shifted, np.concatenate([mask, mask]), checkpoint)
    np.testing.assert_array_equal(both[:1], normalized)


def test_transfer_keeps_saved_model_and_threshold_and_does_not_repeat_completed_evaluation(tmp_path, monkeypatch):
    root = tmp_path / "project"
    source = root / "output" / "source"
    run = source / "runs" / "combined_seed42"
    run.mkdir(parents=True)
    torch.manual_seed(7)
    model = CrowdTCN(110, hidden=8)
    checkpoint = {"state_dict": model.state_dict(), "input_dim": 110, "hidden": 8,
                  "variant": "combined", "seed": 42, "feature_schema": FEATURE_SCHEMA,
                  "pose_signature": "synthetic-transfer", "threshold": .54,
                  "mean": torch.linspace(-.4, .3, 110), "std": torch.linspace(.2, 1., 110)}
    torch.save(checkpoint, run / "model.pt")
    weights = root / "models" / "yolo11n-pose.pt"
    weights.parent.mkdir()
    weights.write_bytes(b"synthetic-pose-weights")
    settings = {"signature": "synthetic-transfer", "weights": weights.name,
                "weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
                "frames": 4, "max_people": 2, "image_size": 32, "batch_size": 2, "device": "cpu"}
    write_json(source / "pose_settings.json", settings)
    write_manifest(source / "manifest.csv", [{"id": "crowd", "path": "crowd.avi", "sha256": "0" * 64,
                                               "source_group": "crowd", "label": 0, "fold": 1, "split": "train",
                                               "fps": 8, "frames": 4, "width": 24, "height": 24}])
    for class_name in ("NonFight", "Fight"):
        folder = root / "data" / "RWF-2000" / "val" / class_name
        folder.mkdir(parents=True)
        for index in range(2):
            writer = cv2.VideoWriter(str(folder / f"{class_name}_{index}.avi"), cv2.VideoWriter_fourcc(*"MJPG"), 8, (24, 24))
            assert writer.isOpened()
            for frame in range(4):
                writer.write(np.full((24, 24, 3), 20 + index * 30 + frame, dtype=np.uint8))
            writer.release()
    calls = []

    def fake_extract(project_root, out, *args, **kwargs):
        calls.append(True)
        (out / "cache").mkdir()
        write_json(out / "pose_settings.json", settings)
        for row in transfer.read_manifest(out / "manifest.csv"):
            keypoints = np.full((4, 2, 17, 3), .4, dtype=np.float32)
            keypoints[..., 2] = .9
            report = {"usable_pose_fraction": 1., "decoded_frames": 4, "full_decode_matches_header": True}
            np.savez_compressed(out / "cache" / f"{row['id']}.npz", keypoints=keypoints,
                                boxes=np.tile(np.array([.1, .1, .8, .8], dtype=np.float32), (4, 2, 1)),
                                present=np.ones((4, 2), dtype=bool), times=np.arange(4, dtype=np.float32)/8,
                                signature=np.array(settings["signature"]), source_sha256=np.array(row["sha256"]),
                                quality=np.array(json.dumps(report)))
        write_json(out / "pose_quality.json", {"failures": []})

    monkeypatch.setattr(transfer, "extract", fake_extract)
    out = root / "output" / "transfer"
    transfer.prepare_transfer(root, source, out, "2026-11-14", expected_per_class=2)
    original = (run / "model.pt").read_bytes()
    result = transfer.run_transfer(root, out, device="cpu")
    assert result["primary_all_released_clips"]["n"] == 4
    assert result["threshold"] == checkpoint["threshold"] == .54
    assert (out / "model.pt").read_bytes() == original == (run / "model.pt").read_bytes()
    assert transfer.run_transfer(root, out, device="cpu") == result
    assert len(calls) == 1
    with (out / "predictions.csv").open("a") as stream:
        stream.write("changed\n")
    with pytest.raises(ValueError, match="Completed transfer evaluation changed"):
        transfer.run_transfer(root, out, device="cpu")
