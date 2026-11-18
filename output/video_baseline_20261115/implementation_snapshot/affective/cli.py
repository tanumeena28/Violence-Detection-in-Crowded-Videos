"""Command-line entry point: python -m affective.cli --help."""
from __future__ import annotations

import argparse
from pathlib import Path


def main():
    from .features import FEATURE_SCHEMA, FEATURE_SCHEMAS
    parser = argparse.ArgumentParser(description="Crowd violence implementation pilot")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare", help="Audit clips and create source-disjoint splits")
    p.add_argument("--dataset", choices=["crowd", "rwf"], default="crowd")
    p.add_argument("--limit-per-class", type=int, default=0)
    p.add_argument("--seed", type=int, default=42)
    p = sub.add_parser("extract", help="Extract pretrained COCO-17 poses and clip tracks")
    p.add_argument("--weights", type=Path, default=Path("models/yolo11n-pose.pt"))
    p.add_argument("--device", default="auto")
    p.add_argument("--frames", type=int, default=32)
    p.add_argument("--max-people", type=int, default=8)
    p.add_argument("--image-size", type=int, default=640)
    p.add_argument("--batch", type=int, default=12)
    p.add_argument("--limit", type=int, default=0)
    p = sub.add_parser("train", help="Train and evaluate the four controlled variants")
    p.add_argument("--variants", nargs="+", choices=["baseline", "reliability", "interactions", "combined"], default=["baseline", "reliability", "interactions", "combined"])
    p.add_argument("--seeds", nargs="+", type=int, default=[42])
    p.add_argument("--epochs", type=int, default=180)
    p.add_argument("--patience", type=int, default=30)
    p.add_argument("--hidden", type=int, default=48)
    p.add_argument("--device", default="auto")
    p.add_argument("--no-coverage", dest="use_coverage", action="store_false",
                   help="Replace the explicit TCN coverage input with zero; masks remain")
    p.add_argument("--feature-schema", choices=FEATURE_SCHEMAS, default=FEATURE_SCHEMA)
    p = sub.add_parser("demo", help="Generate annotated held-out video demonstrations")
    p.add_argument("--run", default="combined_seed42")
    p.add_argument("--count", type=int, default=2)
    p.add_argument("--video", type=Path, default=None)
    p = sub.add_parser("report", help="Write a local HTML results page and meeting notes")
    p.add_argument("--date", default=None, help="Report date as YYYY-MM-DD; defaults to current India date")
    sub.add_parser("motion", help="Extract adjacent-frame motion and fit fixed-split linear controls")
    sub.add_parser("analyze", help="Audit failures, pose quality and cross-split visual similarity")
    p = sub.add_parser("review-sources", help="Decode full videos and triage dense content overlap")
    p.add_argument("--source", type=Path, default=Path("output/pilot"))
    p = sub.add_parser("prepare-cv", help="Freeze custom source-grouped folds from existing pose caches")
    p.add_argument("--source", type=Path, default=Path("output/pilot"))
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--split-seed", type=int, default=42)
    p.add_argument("--seeds", nargs="+", type=int, default=[42, 123, 2026])
    p.add_argument("--variants", nargs="+", choices=["baseline", "reliability", "interactions", "combined"],
                   default=["baseline", "reliability", "interactions", "combined"])
    p.add_argument("--epochs", type=int, default=180)
    p.add_argument("--patience", type=int, default=30)
    p.add_argument("--hidden", type=int, default=48)
    p.add_argument("--source-merges", type=Path, help="JSON list of clip-ID lists to merge after manual source review")
    p.add_argument("--controls", nargs="*", choices=["motion_linear", "pose_quality_only"],
                   default=["motion_linear", "pose_quality_only"],
                   help="Deterministic controls fitted once per fold; pass --controls alone to disable")
    p.add_argument("--source-review", type=Path, help="Source-review JSON tied to the source manifest")
    p.add_argument("--no-coverage", dest="use_coverage", action="store_false",
                   help="Freeze the explicit-coverage ablation with the same network size")
    p.add_argument("--feature-schema", choices=FEATURE_SCHEMAS, default=FEATURE_SCHEMA)
    p = sub.add_parser("run-cv", help="Run/resume frozen fold/seed experiments")
    p.add_argument("--device", default="auto")
    p.add_argument("--folds", nargs="+", type=int, help="Optional fold subset for server jobs")
    sub.add_parser("summarize-cv", help="Verify and aggregate completed cross-validation runs")
    p = sub.add_parser("report-cv", help="Reproduce completed experiments and write the results report")
    p.add_argument("--date", required=True, help="Report date as YYYY-MM-DD")
    p.add_argument("--verification-device", choices=["cpu", "cuda"], default="cpu")
    p.add_argument("--implementation-dir", type=Path,
                   help="Validate frozen training code from this directory when using a newer verifier")
    p = sub.add_parser("compare-coverage", help="Verify and compare matching coverage-on/off experiments")
    p.add_argument("--reference", type=Path, required=True, help="Completed coverage-enabled experiment")
    p.add_argument("--date", required=True, help="Comparison date as YYYY-MM-DD")
    p.add_argument("--verification-device", choices=["cpu", "cuda"], default="cpu")
    p.add_argument("--implementation-dir", type=Path, help="Frozen training implementation for the ablation")
    p = sub.add_parser("compare-centering", help="Verify a matched original/continuous-centering experiment")
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--verification-device", choices=["cpu", "cuda"], default="cpu")
    p.add_argument("--implementation-dir", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    default_folder = ("cross_validation_v1" if args.command in ("prepare-cv", "run-cv", "summarize-cv", "report-cv", "compare-coverage", "compare-centering")
                      else "source_review" if args.command == "review-sources" else "pilot")
    out = args.out.resolve() if args.out else root / "output" / default_folder
    if args.command == "prepare":
        from .data import prepare
        prepare(root, out, args.dataset, args.limit_per_class, args.seed)
    elif args.command == "extract":
        from .pose import extract
        weights = args.weights if args.weights.is_absolute() else root / args.weights
        weights.parent.mkdir(parents=True, exist_ok=True)
        extract(root, out, weights, args.device, args.frames, args.max_people, args.image_size, args.batch, args.limit)
    elif args.command == "train":
        from .train import train_variants
        train_variants(out, args.variants, args.seeds, epochs=args.epochs, patience=args.patience,
                       hidden=args.hidden, device=args.device, use_coverage=args.use_coverage,
                       feature_schema=args.feature_schema)
    elif args.command == "demo":
        from .demo import make_demos
        make_demos(root, out, args.run, args.count, args.video)
    elif args.command == "report":
        from .report import write_report
        write_report(root, out, args.date)
    elif args.command == "motion":
        from .motion import run_motion
        run_motion(root, out)
    elif args.command == "analyze":
        from .analysis import analyze
        analyze(root, out)
    elif args.command == "review-sources":
        from .source_review import audit_sources
        source = args.source if args.source.is_absolute() else root / args.source
        audit_sources(root, source, out)
    elif args.command == "prepare-cv":
        from .cross_validation import prepare_cv
        source = args.source if args.source.is_absolute() else root / args.source
        prepare_cv(source, out, args.folds, args.split_seed, args.seeds, args.variants,
                   args.epochs, args.patience, args.hidden, args.source_merges, args.controls,
                   args.source_review, use_coverage=args.use_coverage, feature_schema=args.feature_schema)
    elif args.command == "run-cv":
        from .cross_validation import run_cv
        run_cv(out, args.device, args.folds)
    elif args.command == "summarize-cv":
        import json
        from .cross_validation import summarize_cv
        print(json.dumps(summarize_cv(out), indent=2))
    elif args.command == "report-cv":
        from .cv_report import write_cv_report
        write_cv_report(out, args.date, args.verification_device, args.implementation_dir)
    elif args.command == "compare-coverage":
        from .ablation import compare_coverage
        compare_coverage(out, args.reference.resolve(), args.date, args.verification_device, args.implementation_dir)
    elif args.command == "compare-centering":
        from .ablation import compare_centering
        compare_centering(out, args.reference.resolve(), args.date, args.verification_device, args.implementation_dir)


if __name__ == "__main__":
    main()
