#!/usr/bin/env python3
"""Validate real-pilot analysis artifacts and optionally compare repeatability."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.real_pilot_analysis_checks import compare_real_pilot_analysis_runs, validate_real_pilot_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate real-pilot analysis artifacts and optionally compare repeatability.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--compare-run-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    acceptance = validate_real_pilot_analysis(args.run_dir)
    acceptance_path = args.output_dir / "artifact_acceptance.json"
    write_json(acceptance_path, acceptance)

    repeatability = None
    if args.compare_run_dir is not None:
        repeatability = compare_real_pilot_analysis_runs(args.run_dir, args.compare_run_dir)
        write_json(args.output_dir / "repeatability_summary.json", repeatability)

    log_lines = [
        "TriScope-LLM real-pilot analysis validation",
        f"Run dir: {args.run_dir.resolve()}",
        f"Acceptance status: {acceptance['summary_status']}",
        f"Acceptance artifact: {acceptance_path.resolve()}",
    ]
    if repeatability is not None:
        log_lines.extend(
            [
                f"Compare run dir: {args.compare_run_dir.resolve()}",
                f"Repeatability status: {repeatability['summary_status']}",
                f"All key metrics match: {repeatability['all_key_metrics_match']}",
                f"Repeatability artifact: {(args.output_dir / 'repeatability_summary.json').resolve()}",
            ]
        )
    log_path = args.output_dir / "repeat_check.log"
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print("TriScope-LLM real-pilot analysis validation complete")
    print(f"Acceptance status: {acceptance['summary_status']}")
    print(f"Acceptance artifact: {acceptance_path.resolve()}")
    if repeatability is not None:
        print(f"Repeatability status: {repeatability['summary_status']}")
        print(f"Repeatability artifact: {(args.output_dir / 'repeatability_summary.json').resolve()}")
    print(f"Log: {log_path.resolve()}")
    return 0 if acceptance["summary_status"] == "PASS" and (repeatability is None or repeatability["summary_status"] == "PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
