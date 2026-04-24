#!/usr/bin/env python3
"""Build a compact cross-pilot report for the current real pilot coverage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.cross_pilot_reporting import build_cross_pilot_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a compact cross-pilot registry and comparison layer for the current "
            "real reasoning and confidence pilot runs."
        ),
    )
    parser.add_argument(
        "--reasoning-run-summary",
        type=Path,
        default=Path("outputs/pilot_runs/pilot_csqa_reasoning_local_ready/pilot_run_summary.json"),
        help="Path to the reasoning pilot run summary.",
    )
    parser.add_argument(
        "--reasoning-feature-summary",
        type=Path,
        default=Path("outputs/pilot_runs/pilot_csqa_reasoning_local_ready/reasoning_probe/features/feature_summary.json"),
        help="Path to the reasoning pilot feature summary.",
    )
    parser.add_argument(
        "--reasoning-validation-dir",
        type=Path,
        default=Path("outputs/pilot_runs/repeatability_pilot_csqa_reasoning_local"),
        help="Directory containing reasoning pilot acceptance / repeatability artifacts.",
    )
    parser.add_argument(
        "--reasoning-analysis-summary",
        type=Path,
        default=Path("outputs/pilot_analysis/pilot_csqa_reasoning_local/pilot_analysis_summary.json"),
        help="Path to the reasoning pilot analysis summary.",
    )
    parser.add_argument(
        "--confidence-run-summary",
        type=Path,
        default=Path("outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/pilot_extension_run_summary.json"),
        help="Path to the confidence pilot run summary.",
    )
    parser.add_argument(
        "--confidence-feature-summary",
        type=Path,
        default=Path("outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/confidence_probe/features/feature_summary.json"),
        help="Path to the confidence pilot feature summary.",
    )
    parser.add_argument(
        "--confidence-validation-dir",
        type=Path,
        default=Path("outputs/pilot_extension_runs/repeatability_pilot_csqa_confidence_local"),
        help="Directory containing confidence pilot acceptance / repeatability artifacts.",
    )
    parser.add_argument(
        "--smoke-report-summary",
        type=Path,
        default=Path("outputs/analysis_reports/smoke_report/smoke_report_summary.json"),
        help="Path to the smoke report summary artifact.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory where cross-pilot report artifacts will be written.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_cross_pilot_report(
            reasoning_run_summary_path=args.reasoning_run_summary,
            reasoning_feature_summary_path=args.reasoning_feature_summary,
            reasoning_validation_dir=args.reasoning_validation_dir,
            reasoning_analysis_summary_path=args.reasoning_analysis_summary,
            confidence_run_summary_path=args.confidence_run_summary,
            confidence_feature_summary_path=args.confidence_feature_summary,
            confidence_validation_dir=args.confidence_validation_dir,
            smoke_report_summary_path=args.smoke_report_summary,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "cross_pilot_report_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "reasoning_run_summary": str(args.reasoning_run_summary),
                    "confidence_run_summary": str(args.confidence_run_summary),
                    "smoke_report_summary": str(args.smoke_report_summary),
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM cross-pilot report failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    summary = result["cross_pilot_summary"]
    print("TriScope-LLM cross-pilot report complete")
    print(f"Real pilot modules: {', '.join(summary['real_pilot_modules'])}")
    print(f"Smoke-only modules: {', '.join(summary['smoke_only_modules'])}")
    print(f"Cross-pilot registry: {result['output_paths']['cross_pilot_registry']}")
    print(f"Comparison CSV: {result['output_paths']['pilot_comparison_csv']}")
    print(f"Coverage summary: {result['output_paths']['pilot_coverage_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
