#!/usr/bin/env python3
"""Build compact analysis artifacts for the current real-pilot stack."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.real_pilot_analysis import build_real_pilot_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a compact, machine-readable real-pilot analysis layer and next-step recommendation.",
    )
    parser.add_argument(
        "--real-pilot-readiness-summary",
        type=Path,
        default=Path("outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_readiness_summary.json"),
    )
    parser.add_argument(
        "--real-pilot-alignment-summary",
        type=Path,
        default=Path("outputs/real_pilot_fusion_readiness/default/real_pilot_alignment_summary.json"),
    )
    parser.add_argument(
        "--real-pilot-rule-summary",
        type=Path,
        default=Path("outputs/real_pilot_fusion_runs/default/real_pilot_rule_summary.json"),
    )
    parser.add_argument(
        "--real-pilot-logistic-summary",
        type=Path,
        default=Path("outputs/real_pilot_fusion_runs/default/real_pilot_logistic_summary.json"),
    )
    parser.add_argument(
        "--reasoning-run-summary",
        type=Path,
        default=Path("outputs/pilot_runs/pilot_csqa_reasoning_local_ready/pilot_run_summary.json"),
    )
    parser.add_argument(
        "--reasoning-feature-summary",
        type=Path,
        default=Path("outputs/pilot_runs/pilot_csqa_reasoning_local_ready/reasoning_probe/features/feature_summary.json"),
    )
    parser.add_argument(
        "--confidence-run-summary",
        type=Path,
        default=Path("outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/pilot_extension_run_summary.json"),
    )
    parser.add_argument(
        "--confidence-feature-summary",
        type=Path,
        default=Path("outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/confidence_probe/features/feature_summary.json"),
    )
    parser.add_argument(
        "--illumination-run-summary",
        type=Path,
        default=Path("outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready/pilot_illumination_run_summary.json"),
    )
    parser.add_argument(
        "--illumination-feature-summary",
        type=Path,
        default=Path("outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready/illumination_probe/features/feature_summary.json"),
    )
    parser.add_argument(
        "--smoke-report-summary",
        type=Path,
        default=Path("outputs/analysis_reports/smoke_report/smoke_report_summary.json"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_real_pilot_analysis(
            real_pilot_readiness_summary_path=args.real_pilot_readiness_summary,
            real_pilot_alignment_summary_path=args.real_pilot_alignment_summary,
            real_pilot_rule_summary_path=args.real_pilot_rule_summary,
            real_pilot_logistic_summary_path=args.real_pilot_logistic_summary,
            reasoning_run_summary_path=args.reasoning_run_summary,
            reasoning_feature_summary_path=args.reasoning_feature_summary,
            confidence_run_summary_path=args.confidence_run_summary,
            confidence_feature_summary_path=args.confidence_feature_summary,
            illumination_run_summary_path=args.illumination_run_summary,
            illumination_feature_summary_path=args.illumination_feature_summary,
            smoke_report_summary_path=args.smoke_report_summary,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "real_pilot_analysis_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM real-pilot analysis failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    summary = result["real_pilot_analysis_summary"]
    print("TriScope-LLM real-pilot analysis complete")
    print(f"Real-pilot modules: {summary['num_real_pilot_modules']}")
    print(f"Full intersection available: {summary['full_intersection_available']}")
    print(f"Primary blocker: {result['next_step_recommendation']['recommended_route']}")
    print(f"Analysis summary: {result['output_paths']['real_pilot_analysis_summary']}")
    print(f"Recommendation: {result['output_paths']['next_step_recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
