#!/usr/bin/env python3
"""Validate fusion artifacts and optionally compare repeatability."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.fusion.fusion_artifact_checks import compare_fusion_runs, validate_fusion_artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the required artifact set for a TriScope-LLM fusion dataset and baseline run, "
            "and optionally compare it against a second run for repeatability."
        ),
    )
    parser.add_argument("--dataset-run-dir", type=Path, required=True, help="Primary fusion dataset run directory.")
    parser.add_argument("--baseline-run-dir", type=Path, required=True, help="Primary fusion baseline run directory.")
    parser.add_argument(
        "--compare-dataset-run-dir",
        type=Path,
        default=None,
        help="Optional second fusion dataset run directory used for repeatability comparison.",
    )
    parser.add_argument(
        "--compare-baseline-run-dir",
        type=Path,
        default=None,
        help="Optional second fusion baseline run directory used for repeatability comparison.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory where validation artifacts will be written.")
    return parser


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    acceptance = validate_fusion_artifacts(args.dataset_run_dir, args.baseline_run_dir)
    acceptance_path = args.output_dir / "artifact_acceptance.json"
    write_json(acceptance_path, acceptance)

    repeatability_payload = None
    if args.compare_dataset_run_dir is not None or args.compare_baseline_run_dir is not None:
        if args.compare_dataset_run_dir is None or args.compare_baseline_run_dir is None:
            raise SystemExit("Both --compare-dataset-run-dir and --compare-baseline-run-dir are required together.")
        repeatability_payload = compare_fusion_runs(
            reference_dataset_run_dir=args.dataset_run_dir,
            reference_baseline_run_dir=args.baseline_run_dir,
            candidate_dataset_run_dir=args.compare_dataset_run_dir,
            candidate_baseline_run_dir=args.compare_baseline_run_dir,
        )
        write_json(args.output_dir / "repeatability_summary.json", repeatability_payload)

    log_lines = [
        "TriScope-LLM fusion artifact validation",
        f"Dataset run dir: {args.dataset_run_dir.resolve()}",
        f"Baseline run dir: {args.baseline_run_dir.resolve()}",
        f"Acceptance status: {acceptance['summary_status']}",
        f"Acceptance artifact: {acceptance_path.resolve()}",
    ]
    if repeatability_payload is not None:
        log_lines.extend(
            [
                f"Compare dataset run dir: {args.compare_dataset_run_dir.resolve()}",
                f"Compare baseline run dir: {args.compare_baseline_run_dir.resolve()}",
                f"Repeatability status: {repeatability_payload['summary_status']}",
                f"All key metrics match: {repeatability_payload['all_key_metrics_match']}",
                f"Repeatability artifact: {(args.output_dir / 'repeatability_summary.json').resolve()}",
            ]
        )
    log_path = args.output_dir / "repeat_check.log"
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print("TriScope-LLM fusion artifact validation complete")
    print(f"Acceptance status: {acceptance['summary_status']}")
    print(f"Acceptance artifact: {acceptance_path.resolve()}")
    if repeatability_payload is not None:
        print(f"Repeatability status: {repeatability_payload['summary_status']}")
        print(f"Repeatability artifact: {(args.output_dir / 'repeatability_summary.json').resolve()}")
    print(f"Log: {log_path.resolve()}")
    return 0 if acceptance["summary_status"] == "PASS" and (repeatability_payload is None or repeatability_payload["summary_status"] == "PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
