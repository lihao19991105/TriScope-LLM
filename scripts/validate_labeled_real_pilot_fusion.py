#!/usr/bin/env python3
"""Validate labeled real-pilot fusion bootstrap artifacts and optionally compare repeatability."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.fusion.labeled_real_pilot_fusion_checks import compare_labeled_real_pilot_fusion, validate_labeled_real_pilot_fusion


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate labeled real-pilot fusion artifacts and optionally compare repeatability.")
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--compare-dataset-dir", type=Path, default=None)
    parser.add_argument("--compare-run-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    acceptance = validate_labeled_real_pilot_fusion(args.dataset_dir, args.run_dir)
    acceptance_path = args.output_dir / "artifact_acceptance.json"
    write_json(acceptance_path, acceptance)
    repeatability = None
    if args.compare_dataset_dir is not None and args.compare_run_dir is not None:
        repeatability = compare_labeled_real_pilot_fusion(
            reference_dataset_dir=args.dataset_dir,
            reference_run_dir=args.run_dir,
            candidate_dataset_dir=args.compare_dataset_dir,
            candidate_run_dir=args.compare_run_dir,
        )
        write_json(args.output_dir / "repeatability_summary.json", repeatability)
    log_lines = [
        "TriScope-LLM labeled real-pilot fusion validation",
        f"Dataset dir: {args.dataset_dir.resolve()}",
        f"Run dir: {args.run_dir.resolve()}",
        f"Acceptance status: {acceptance['summary_status']}",
        f"Acceptance artifact: {acceptance_path.resolve()}",
    ]
    if repeatability is not None:
        log_lines.extend(
            [
                f"Compare dataset dir: {args.compare_dataset_dir.resolve()}",
                f"Compare run dir: {args.compare_run_dir.resolve()}",
                f"Repeatability status: {repeatability['summary_status']}",
                f"Repeatability artifact: {(args.output_dir / 'repeatability_summary.json').resolve()}",
            ]
        )
    log_path = args.output_dir / "repeat_check.log"
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print("TriScope-LLM labeled real-pilot fusion validation complete")
    print(f"Acceptance status: {acceptance['summary_status']}")
    if repeatability is not None:
        print(f"Repeatability status: {repeatability['summary_status']}")
    print(f"Log: {log_path.resolve()}")
    return 0 if acceptance["summary_status"] == "PASS" and (repeatability is None or repeatability["summary_status"] == "PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
