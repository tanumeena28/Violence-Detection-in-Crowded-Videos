import csv
import hashlib
import json

import numpy as np
import pytest
import torch

from affective.cross_validation import grouped_folds, prepare_cv, run_cv, validate_plan, write_manifest
from affective.data import read_manifest, write_json
from affective.train import load_features, train_one, normalize_training
from affective.motion import SETTINGS, load_cached_motion, quality_features
from affective.cv_report import write_cv_report
from affective.demo import load_model, infer_cache
from affective.ablation import check_coverage_pair, compare_coverage, check_centering_pair, compare_centering
from affective.features import FEATURE_SCHEMA, FEATURE_SCHEMAS, LEGACY_FEATURE_SCHEMA


def rows():
    return [{"id": f"{index:016x}", "path": f"video_{index}.avi", "sha256": f"{index:064x}",
             "source_group": f"source_{index // 2}", "label": (index // 2) % 2,
             "fold": index % 5 + 1, "split": "train", "fps": 10., "frames": 6,
             "width": 100, "height": 100} for index in range(40)]


def make_source(path):
    path.mkdir()
    (path / "cache").mkdir()
    (path / "motion" / "cache").mkdir(parents=True)
    corpus = rows()
    write_manifest(path / "manifest.csv", corpus)
    write_json(path / "pose_settings.json", {"signature": "synthetic-test", "frames": 6})
    rng = np.random.default_rng(5)
    settings = {**SETTINGS, "opencv": "recorded-extraction-version"}
    motion_signature = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()
    write_json(path / "motion" / "feature_settings.json", {**settings, "signature": motion_signature, "clips": len(corpus)})
    quality = []
    for row in corpus:
        points = rng.uniform(.2, .7, (6, 2, 17, 3)).astype(np.float32)
        points[..., 2] = .9
        points[2, 0, [11, 12], 2] = 0
        report = {"id": row["id"], "label": row["label"], "usable_pose_fraction": float(rng.uniform(.2, 1.)),
                  "mean_people": float(rng.uniform(1., 3.)), "valid_joint_fraction": float(rng.uniform(.4, 1.)),
                  "total_tracks": row["fold"] + 2, "max_people_detected": row["fold"],
                  "discarded_tracks": row["fold"] - 1, "frames_with_people": float(rng.uniform(.2, 1.))}
        quality.append(report)
        np.savez_compressed(path / "cache" / f"{row['id']}.npz", keypoints=points,
                            boxes=np.tile(np.array([.1, .1, .8, .8], np.float32), (6, 2, 1)),
                            present=np.ones((6, 2), bool), times=np.arange(6, dtype=np.float32) / 10,
                            frame_indices=np.arange(6),
                            signature=np.array("synthetic-test"), source_sha256=np.array(row["sha256"]),
                            quality=np.array(json.dumps(report)))
        np.savez_compressed(path / "motion" / "cache" / f"{row['id']}.npz",
                            features=rng.normal(size=80).astype(np.float32) + row["fold"],
                            frame_indices=np.arange(6), signature=np.array(motion_signature),
                            source_sha256=np.array(row["sha256"]))
    write_json(path / "pose_quality.json", {"clips": quality, "signature": "synthetic-test"})
    return path


def test_folds_keep_sources_together_and_cover_every_clip_once():
    corpus = rows()
    assigned, partitions, _ = grouped_folds(corpus)
    repeated, _, _ = grouped_folds(list(reversed(corpus)))
    assert assigned == repeated
    assert all(row["split"] == "train" for row in corpus)
    test_ids = []
    for partition in partitions:
        groups = {split: {row["source_group"] for row in partition if row["split"] == split}
                  for split in ("train", "val", "test")}
        assert not (groups["train"] & groups["val"] or groups["train"] & groups["test"] or groups["val"] & groups["test"])
        test_ids.extend(row["id"] for row in partition if row["split"] == "test")
    assert sorted(test_ids) == sorted(row["id"] for row in corpus)


def test_review_merges_are_transitive_and_preserve_existing_source_groups():
    corpus = rows()
    assigned, _, _ = grouped_folds(corpus, source_merges=[[corpus[0]["id"], corpus[2]["id"]],
                                                        [corpus[2]["id"], corpus[4]["id"]]])
    assert len({row["evaluation_fold"] for row in assigned[:6]}) == 1
    with pytest.raises(ValueError, match="known clip IDs"):
        grouped_folds(corpus, source_merges=[["unknown", corpus[0]["id"]]])


@pytest.mark.parametrize("use_coverage", [True, False])
@pytest.mark.parametrize("feature_schema", FEATURE_SCHEMAS)
def test_cv_trains_resumes_and_uses_only_training_normalization(tmp_path, use_coverage, feature_schema):
    source = make_source(tmp_path / "source")
    out = tmp_path / "cv"
    plan = prepare_cv(source, out, folds=3, seeds=[7, 11], variants=["baseline"], epochs=1,
                      hidden=8, use_coverage=use_coverage, feature_schema=feature_schema)
    assert plan["settings"]["use_coverage"] is use_coverage
    validate_plan(out, out / "implementation_snapshot" / "affective")
    partial = run_cv(out, device="cpu", folds=[1])
    assert partial["status"] == "incomplete"
    run = out / "fold_1" / "runs" / "baseline_seed7"
    checkpoint = torch.load(run / "model.pt", map_location="cpu", weights_only=True)
    assert checkpoint["use_coverage"] is use_coverage
    assert checkpoint["feature_schema"] == feature_schema
    model, _ = load_model(run / "model.pt")
    assert model.use_coverage is use_coverage
    if use_coverage:
        legacy = dict(checkpoint)
        del legacy["use_coverage"]
        torch.save(legacy, tmp_path / "legacy.pt")
        legacy_model, _ = load_model(tmp_path / "legacy.pt")
        features, mask = torch.randn(2, 6, 2, 68), torch.ones(2, 6, 2)
        with torch.inference_mode():
            torch.testing.assert_close(model(features, mask), legacy_model(features, mask), rtol=0, atol=0)
    parts, _ = load_features(out / "fold_1", "baseline", out / "cache", feature_schema)
    expected = parts["train"]["x"][parts["train"]["mask"].astype(bool)].mean(0)
    np.testing.assert_allclose(checkpoint["mean"].numpy(), expected, atol=1e-6)
    modified = (run / "model.pt").stat().st_mtime_ns
    control_files = [out / "fold_1" / "motion" / name / "model.json" for name in ("motion_linear", "pose_quality_only")]
    control_times = [p.stat().st_mtime_ns for p in control_files]
    assert run_cv(out, device="cpu", folds=[1])["status"] == "incomplete"
    assert (run / "model.pt").stat().st_mtime_ns == modified
    assert [p.stat().st_mtime_ns for p in control_files] == control_times
    result = run_cv(out, device="cpu", folds=[2, 3])
    assert result["status"] == "complete"
    assert result["models"][0]["completed_runs"] == 6
    assert all(r["completed_runs"] == r["expected_runs"] == 3 for r in result["models"][1:])
    assert all(r["seed"] is None for model in result["models"][1:] for r in model["runs"])
    partition = read_manifest(out / "fold_1" / "manifest.csv")
    train = np.array([r["split"] == "train" for r in partition])
    for name in ("motion_linear", "pose_quality_only"):
        features = load_cached_motion(out, partition)[0] if name == "motion_linear" else quality_features(out, partition)
        control = json.loads((out / "fold_1" / "motion" / name / "model.json").read_text(encoding="utf-8"))
        np.testing.assert_allclose(control["mean"], features.astype(np.float64)[train].mean(0), atol=1e-12)
    with (run / "predictions.csv").open(newline="") as stream:
        predicted = list(csv.DictReader(stream))
    assert {row["id"] for row in predicted if row["split"] == "test"} == {
        row["id"] for row in read_manifest(out / "fold_1" / "manifest.csv") if row["split"] == "test"}
    write_cv_report(out, "2026-11-07")
    audit = json.loads((out / "audit.json").read_text(encoding="utf-8"))
    pooled = json.loads((out / "pooled_metrics.json").read_text(encoding="utf-8"))["models"]
    assert audit["runs_verified"] == 12
    assert all(r["use_coverage"] is use_coverage for r in audit["runs"] if r["seed"] is not None)
    assert len(pooled) == 4 and all(r["n"] == 40 for r in pooled)
    with pytest.raises(FileExistsError):
        prepare_cv(source, out)
    with (run / "predictions.csv").open("a") as stream:
        stream.write("changed\n")
    with pytest.raises(ValueError, match="Completed run changed"):
        run_cv(out, device="cpu", folds=[1])


def test_coverage_comparison_pairs_frozen_runs_without_changing_reference(tmp_path):
    source = make_source(tmp_path / "source")
    before, after = tmp_path / "enabled", tmp_path / "disabled"
    plans = []
    for folder, use_coverage in ((before, True), (after, False)):
        plans.append(prepare_cv(source, folder, folds=3, seeds=[7], variants=["baseline"],
                                controls=[], epochs=1, hidden=8, use_coverage=use_coverage))
        run_cv(folder, device="cpu")
    original = {str(path.relative_to(before)): path.read_bytes() for path in before.rglob("*") if path.is_file()}
    comparison = compare_coverage(after, before, "2026-11-14")
    assert comparison["verification"]["reference_runs_verified"] == 3
    assert comparison["models"][0]["paired_runs"] == 3
    assert comparison["models"][0]["per_seed_decision_changes"][0]["clips"] == 40
    assert original == {str(path.relative_to(before)): path.read_bytes() for path in before.rglob("*") if path.is_file()}
    mismatched = {**plans[1], "settings": {**plans[1]["settings"], "seeds": [11]}}
    with pytest.raises(ValueError, match="identical folds, seeds"):
        check_coverage_pair(plans[0], mismatched)
    with pytest.raises(ValueError, match="inputs differ: assignments_sha256"):
        check_coverage_pair(plans[0], {**plans[1], "assignments_sha256": "changed"})
    with pytest.raises(ValueError, match="coverage-enabled reference"):
        check_coverage_pair(plans[1], plans[0])


def test_motion_anchor_mismatch_is_rejected_before_creating_a_plan(tmp_path):
    source = make_source(tmp_path / "source")
    cache = next((source / "motion" / "cache").glob("*.npz"))
    with np.load(cache, allow_pickle=False) as saved:
        data = {key: saved[key].copy() for key in saved.files}
    data["frame_indices"][0] += 1
    np.savez_compressed(cache, **data)
    out = tmp_path / "cv"
    with pytest.raises(ValueError, match="Motion cache provenance"):
        prepare_cv(source, out)
    assert not out.exists()


def test_centering_comparison_changes_only_the_declared_feature_schema(tmp_path):
    source = make_source(tmp_path / "source")
    before, after = tmp_path / "original", tmp_path / "corrected"
    plans = []
    for folder, schema in ((before, LEGACY_FEATURE_SCHEMA), (after, FEATURE_SCHEMA)):
        plans.append(prepare_cv(source, folder, folds=3, seeds=[7], variants=["baseline"],
                                controls=[], epochs=1, hidden=8, feature_schema=schema))
        run_cv(folder, device="cpu")
    original = {str(path.relative_to(before)): path.read_bytes() for path in before.rglob("*") if path.is_file()}
    comparison = compare_centering(after, before, "2026-11-15")
    assert comparison["comparison_kind"] == "centering"
    assert comparison["models"][0]["paired_runs"] == 3
    assert "original" in comparison["models"][0] and "corrected" in comparison["models"][0]
    assert original == {str(path.relative_to(before)): path.read_bytes() for path in before.rglob("*") if path.is_file()}
    with pytest.raises(ValueError, match="identical folds, seeds"):
        check_centering_pair(plans[0], {**plans[1], "settings": {**plans[1]["settings"], "use_coverage": False}})
    with pytest.raises(ValueError, match="inputs differ: assignments_sha256"):
        check_centering_pair(plans[0], {**plans[1], "assignments_sha256": "changed"})
    with pytest.raises(ValueError, match="original v1"):
        check_centering_pair(plans[1], plans[0])


@pytest.mark.parametrize("control", ["detection_only", "shuffled_time"])
def test_control_checkpoint_inference_preserves_training_inputs(tmp_path, control):
    source = make_source(tmp_path / "source")
    out = tmp_path / "cv"
    prepare_cv(source, out, folds=3, seeds=[7], variants=["combined"], controls=[], epochs=1, hidden=8)
    folder = out / "fold_1"
    result = train_one(folder, "combined", seed=7, epochs=1, hidden=8, device="cpu",
                       cache_dir=out / "cache", input_control=control)
    model, checkpoint = load_model(folder / "runs" / "combined_seed7" / "model.pt")
    groups, _ = load_features(folder, "combined", out / "cache", input_control=control)
    normalize_training(groups)
    row = groups["test"]["rows"][0]
    path = out / "cache" / f"{row['id']}.npz"
    with np.load(path, allow_pickle=False) as saved:
        data = {key: saved[key].copy() for key in saved.files}
    data["track_ids"] = np.array([1, 2])
    quality = json.loads(str(data["quality"]))
    quality["seconds_including_decode"] = .1
    data["quality"] = np.array(json.dumps(quality))
    # Inference cache metadata adds only fields used by the demonstration.
    np.savez_compressed(path, **data)
    inferred, _ = infer_cache(model, checkpoint, path)
    with torch.inference_mode():
        expected = model(torch.from_numpy(groups["test"]["x"][:1]),
                         torch.from_numpy(groups["test"]["mask"][:1])).sigmoid().item()
    assert checkpoint["input_control"] == control and result["input_control"] == control
    assert inferred["score"] == expected


@pytest.mark.parametrize("relative,message", [("pose_quality.json", "Pose-quality features changed"),
                                               ("motion/feature_settings.json", "Motion settings changed")])
def test_frozen_control_inputs_are_protected(tmp_path, relative, message):
    source = make_source(tmp_path / "source")
    out = tmp_path / "cv"
    prepare_cv(source, out)
    with (out / relative).open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValueError, match=message):
        validate_plan(out)


def test_source_review_and_prepared_links_must_agree(tmp_path):
    source = make_source(tmp_path / "source")
    review = tmp_path / "review.json"
    corpus = read_manifest(source / "manifest.csv")
    write_json(review, {"source_manifest_sha256": hashlib.sha256((source / "manifest.csv").read_bytes()).hexdigest(),
                        "manual_source_merges": [[corpus[0]["id"], corpus[2]["id"]]]})
    out = tmp_path / "cv"
    with pytest.raises(ValueError, match="Source merges differ"):
        prepare_cv(source, out, source_review=review)
    assert not out.exists()


def test_frozen_cache_and_manifest_changes_are_rejected(tmp_path):
    source = make_source(tmp_path / "source")
    out = tmp_path / "cv"
    prepare_cv(source, out)
    manifest = out / "fold_1" / "manifest.csv"
    original = manifest.read_bytes()
    manifest.write_bytes(original + b"\n")
    with pytest.raises(ValueError, match="manifest changed"):
        validate_plan(out)
    manifest.write_bytes(original)
    cache = next((out / "cache").glob("*.npz"))
    with cache.open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="cache changed"):
        validate_plan(out)
