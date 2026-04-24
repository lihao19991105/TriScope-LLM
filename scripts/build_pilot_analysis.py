#!/usr/bin/env python3
"""Build a compact pilot-vs-smoke analysis artifact set for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.pilot_analysis import build_pilot_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a compact pilot analysis layer that registers the current real pilot run "
            "and compares it against the existing smoke reasoning artifacts."
        ),
    )
    parser.add_argument(
        "--pilot-run-summary",
        type=Path,
        default=Path("outputs/pilot_runs/pilot_csqa_reasoning_local_ready/pilot_run_summary.json"),
        help="Path to the pilot_run_summary.json artifact.",
    )
    parser.add_argument(
        "--pilot-feature-summary",
        type=Path,
        default=Path("outputs/pilot_runs/pilot_csqa_reasoning_local_ready/reasoning_probe/features/feature_summary.json"),
        help="Path to the pilot reasoning feature summary artifact.",
    )
    parser.add_argument(
        "--smoke-reasoning-summary",
        type=Path,
        default=Path("outputs/reasoning_runs/smoke_local_run/summary.json"),
        help="Path to the smoke reasoning summary artifact.",
    )
    parser.add_argument(
        "--smoke-reasoning-feature-summary",
        type=Path,
        default=Path("outputs/reasoning_runs/smoke_local_run/features/feature_summary.json"),
        help="Path to the smoke reasoning feature summary artifact.",
    )
    parser.add_argument(
        "--smoke-report-summary",
        type=Path,
        default=Path("outputs/analysis_reports/smoke_report/smoke_report_summary.json"),
        help="Path to the smoke report summary artifact.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory where pilot analysis artifacts will be written.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_pilot_analysis(
            pilot_run_summary_path=args.pilot_run_summary,
            pilot_feature_summary_path=args.pilot_feature_summary,
            smoke_reasoning_summary_path=args.smoke_reasoning_summary,
            smoke_reasoning_feature_summary_path=args.smoke_reasoning_feature_summary,
            smoke_report_summary_path=args.smoke_report_summary,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "pilot_analysis_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "pilot_run_summary": str(args.pilot_run_summary),
                    "pilot_feature_summary": str(args.pilot_feature_summary),
                    "smoke_reasoning_summary": str(args.smoke_reasoning_summary),
                    "smoke_reasoning_feature_summary": str(args.smoke_reasoning_feature_summary),
                    "smoke_report_summary": str(args.smoke_report_summary),
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM pilot analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    summary = result["pilot_analysis_summary"]
    print("TriScope-LLM pilot analysis complete")
    print(f"Pilot run ID: {summary['pilot_run_id']}")
    print(f"Pilot run registry: {result['output_paths']['pilot_run_registry']}")
    print(f"Pilot vs smoke summary: {result['output_paths']['pilot_vs_smoke_summary']}")
    print(f"Pilot analysis summary: {result['output_paths']['pilot_analysis_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
