#!/usr/bin/env python3
"""Build the real-pilot fusion readiness layer for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.real_pilot_fusion_readiness import build_real_pilot_fusion_readiness


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build updated 3/3 cross-pilot reporting and a real-pilot fusion readiness dataset "
            "from the current real reasoning, confidence, and illumination pilot artifacts."
        ),
    )
    parser.add_argument("--reasoning-run-summary", type=Path, default=Path("outputs/pilot_runs/pilot_csqa_reasoning_local_ready/pilot_run_summary.json"))
    parser.add_argument("--reasoning-feature-jsonl", type=Path, default=Path("outputs/pilot_runs/pilot_csqa_reasoning_local_ready/reasoning_probe/features/reasoning_prompt_level_features.jsonl"))
    parser.add_argument("--reasoning-feature-summary", type=Path, default=Path("outputs/pilot_runs/pilot_csqa_reasoning_local_ready/reasoning_probe/features/feature_summary.json"))
    parser.add_argument("--reasoning-validation-dir", type=Path, default=Path("outputs/pilot_runs/repeatability_pilot_csqa_reasoning_local"))
    parser.add_argument("--confidence-run-summary", type=Path, default=Path("outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/pilot_extension_run_summary.json"))
    parser.add_argument("--confidence-feature-jsonl", type=Path, default=Path("outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/confidence_probe/features/confidence_prompt_level_features.jsonl"))
    parser.add_argument("--confidence-feature-summary", type=Path, default=Path("outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/confidence_probe/features/feature_summary.json"))
    parser.add_argument("--confidence-validation-dir", type=Path, default=Path("outputs/pilot_extension_runs/repeatability_pilot_csqa_confidence_local"))
    parser.add_argument("--illumination-run-summary", type=Path, default=Path("outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready/pilot_illumination_run_summary.json"))
    parser.add_argument("--illumination-feature-jsonl", type=Path, default=Path("outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready/illumination_probe/features/prompt_level_features.jsonl"))
    parser.add_argument("--illumination-feature-summary", type=Path, default=Path("outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready/illumination_probe/features/feature_summary.json"))
    parser.add_argument("--illumination-validation-dir", type=Path, default=Path("outputs/pilot_illumination_runs/repeatability_pilot_csqa_illumination_local"))
    parser.add_argument("--smoke-report-summary", type=Path, default=Path("outputs/analysis_reports/smoke_report/smoke_report_summary.json"))
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory where real-pilot fusion readiness artifacts will be written.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_real_pilot_fusion_readiness(
            reasoning_run_summary_path=args.reasoning_run_summary,
            reasoning_feature_jsonl_path=args.reasoning_feature_jsonl,
            reasoning_feature_summary_path=args.reasoning_feature_summary,
            reasoning_validation_dir=args.reasoning_validation_dir,
            confidence_run_summary_path=args.confidence_run_summary,
            confidence_feature_jsonl_path=args.confidence_feature_jsonl,
            confidence_feature_summary_path=args.confidence_feature_summary,
            confidence_validation_dir=args.confidence_validation_dir,
            illumination_run_summary_path=args.illumination_run_summary,
            illumination_feature_jsonl_path=args.illumination_feature_jsonl,
            illumination_feature_summary_path=args.illumination_feature_summary,
            illumination_validation_dir=args.illumination_validation_dir,
            smoke_report_summary_path=args.smoke_report_summary,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "real_pilot_fusion_readiness_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "output_dir": str(args.output_dir),
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM real-pilot fusion readiness failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    summary = result["real_pilot_fusion_readiness_summary"]
    print("TriScope-LLM real-pilot fusion readiness complete")
    print(f"Real pilot modules: {', '.join(summary['real_pilot_modules'])}")
    print(f"Aligned rows: {summary['num_aligned_rows']}")
    print(f"Join strategy: {summary['join_strategy_used']}")
    print(f"Fusion readiness summary: {result['output_paths']['real_pilot_fusion_readiness_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
