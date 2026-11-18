import numpy as np
import pytest
import json

from affective.rwf_supervised import fit_development_head, partition_rows
from affective.motion import score_linear
from affective.train import choose_threshold
from affective.cross_validation import digest, write_manifest
from affective.data import write_json
from scripts import run_rwf_supervised as runner


def corpus():
    result = []
    for group in range(20):
        for label in (0, 1):
            result.append({"id": f"d{group}-{label}", "path": f"train/{group}/{label}.avi",
                           "sha256": f"bytes-{group}-{label}", "source_group": f"source-{group}",
                           "released_partition": "train", "label": label})
    for label in (0, 1):
        result.append({"id": f"test-{label}", "path": f"val/{label}.avi", "sha256": f"test-{label}",
                       "source_group": f"test-source-{label}", "released_partition": "val", "label": label})
    return result


def test_mixed_label_sources_stay_whole_and_split_is_order_independent():
    rows = corpus()
    assigned, audit = partition_rows(rows)
    reverse, _ = partition_rows(list(reversed(rows)))
    assert assigned == reverse
    assert audit["source_groups_disjoint"] and audit["mixed_label_source_groups"] == 20
    assert audit["evaluation_clips_retained"] == 2
    for group in {r["source_group"] for r in assigned}:
        assert len({r["split"] for r in assigned if r["source_group"] == group}) == 1
    assert all(r["split"] == "test" for r in assigned if r["released_partition"] == "val")


def test_identical_bytes_union_sources_and_exclude_related_training_clips():
    rows = corpus()
    rows[-2]["sha256"] = rows[0]["sha256"]
    assigned, audit = partition_rows(rows)
    assert {r["id"] for r in audit["excluded_clips"]} == {"d0-0", "d0-1"}
    assert audit["evaluation_clips_retained"] == 2
    duplicate = {**rows[2], "id": "duplicate", "path": "train/duplicate.avi", "source_group": "renamed"}
    assigned, audit = partition_rows(rows + [duplicate])
    assert sum(r["sha256"] == duplicate["sha256"] for r in assigned) == 1
    assert any(r["reason"] == "Same-label byte duplicate in development" for r in audit["excluded_clips"])


def test_conflicting_identical_video_labels_require_review():
    rows = corpus()
    rows[1]["sha256"] = rows[0]["sha256"]
    with pytest.raises(ValueError, match="conflicting supplied labels"):
        partition_rows(rows)


def test_head_scaling_and_choices_use_only_development_data():
    rng = np.random.default_rng(12)
    train = rng.normal(size=(50, 6))
    val = rng.normal(size=(20, 6))
    y_train = (train[:, 0] > 0).astype(int)
    y_val = (val[:, 0] > 0).astype(int)
    model, selection = fit_development_head(train, y_train, val, y_val)
    np.testing.assert_allclose(model["mean"], train.mean(0), atol=0, rtol=0)
    np.testing.assert_allclose(model["std"], np.maximum(train.std(0), .01), atol=0, rtol=0)
    assert model["selected_C"] == min(selection["candidates"], key=lambda c: c["validation_log_loss"])["C"]
    assert model["threshold"] == choose_threshold(y_val, score_linear(val, model))
    # Scoring arbitrary evaluation observations cannot modify the frozen model.
    original = {k: list(v) if isinstance(v, list) else v for k, v in model.items()}
    score_linear(rng.normal(size=(100, 6)) * 1000, model)
    assert model == original
    repeated, _ = fit_development_head(train, y_train, val, y_val)
    assert model == repeated


def test_evaluation_requires_sealed_head_and_cannot_change_development_choices(tmp_path):
    out = tmp_path / "experiment"
    cache = tmp_path / "evaluation"
    out.mkdir()
    cache.mkdir()
    (out / "development_cache").mkdir()
    rng = np.random.default_rng(17)
    rows, audit = [], {}
    for index in range(460):
        vector = rng.normal(size=6).astype(np.float32)
        split = "train" if index < 40 else "val" if index < 60 else "test"
        row = {"id": str(index), "path": f"clip_{index}.avi", "sha256": f"raw-{index}",
               "source_group": f"source-{index}", "label": int(vector[0] > 0), "fold": 0,
               "split": split, "fps": 10., "frames": 32, "width": 24, "height": 24}
        rows.append(row)
        if split != "test":
            path = out / "development_cache" / f"{index}.npz"
            np.savez_compressed(path, features=vector, source_sha256=np.array(row["sha256"]), encoder_signature=np.array("synthetic"))
            audit[str(index)] = digest(path)
    write_manifest(out / "manifest.csv", rows)
    write_manifest(cache / "manifest.csv", rows[60:])
    write_json(out / "development_feature_audit.json", {"cache_sha256": audit})
    write_json(cache / "protocol.json", {"frozen": True})
    # Deliberately uninformative evaluation vectors cannot participate in selection.
    np.savez_compressed(cache / "features.npz", features=np.zeros((400, 6)), ids=np.array([r["id"] for r in rows[60:]]))
    plan = {"encoder_signature": "synthetic", "manifest_sha256": digest(out / "manifest.csv"),
            "regularization": [.1, 1.], "maximum_iterations": 2000,
            "selection_boundary": "Development head sealed before test arrays",
            "evaluation_cache": {"path": str(cache), "features_sha256": digest(cache / "features.npz"),
                "manifest_sha256": digest(cache / "manifest.csv"), "protocol_sha256": digest(cache / "protocol.json")}}
    write_json(out / "protocol.json", plan)
    with pytest.raises(FileNotFoundError):
        runner.evaluate(out, plan)
    runner.freeze_head(out, plan)
    original = (out / "model.json").read_bytes()
    result = runner.evaluate(out, plan)
    assert result["head_frozen_before_evaluation"] and result["test_clips"] == 400
    assert runner.verify(out, plan) == result
    assert (out / "model.json").read_bytes() == original
    model = json.loads(original)
    model["threshold"] = .1
    write_json(out / "model.json", model)
    with pytest.raises(ValueError, match="Selected development artifact changed"):
        runner.evaluate(out, plan)
