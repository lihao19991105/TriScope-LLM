#!/usr/bin/env python3
"""Validate that a poisoned dataset can be consumed by the future training stage."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.models.training_dataset import (
    validate_training_dataset,
    write_preview_samples,
    write_validation_log,
    write_validation_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a poisoned dataset or dataset manifest against the TriScope-LLM training contract.",
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--dataset-manifest",
        type=Path,
        help="Path to a poison pipeline dataset manifest JSON file.",
    )
    source_group.add_argument(
        "--dataset-path",
        type=Path,
        help="Path to a poisoned dataset JSONL file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/train_validation"),
        help="Directory where validation artifacts will be written.",
    )
    parser.add_argument(
        "--preview-count",
        type=int,
        default=3,
        help="Number of training samples to preview in the validation output.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed used for deterministic preview sample selection.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    manifest_path = args.dataset_manifest
    dataset_path = args.dataset_path

    report = validate_training_dataset(
        dataset_path=dataset_path,
        manifest_path=manifest_path,
        preview_count=args.preview_count,
        seed=args.seed,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.output_dir / "validation_report.json"
    preview_path = args.output_dir / "preview_samples.jsonl"
    log_path = args.output_dir / "validation.log"

    write_validation_report(report, report_path)
    write_preview_samples(report.preview_samples, preview_path)
    write_validation_log(report, log_path)

    print("TriScope-LLM training dataset validation complete")
    print(f"Summary status: {report.summary_status}")
    print(f"Dataset path: {report.dataset_path}")
    print(f"Train-ready samples: {report.dataset_stats['num_train_ready']}/{report.dataset_stats['num_records']}")
    print(f"Validation report: {report_path}")
    print(f"Preview samples: {preview_path}")
    print(f"Validation log: {log_path}")

    if report.issues:
        print("Issues:")
        for issue in report.issues:
            print(f"- [{issue['level']}] {issue['code']}: {issue['message']}")

    return 0 if report.summary_status in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
