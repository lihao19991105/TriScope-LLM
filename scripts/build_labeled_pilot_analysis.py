#!/usr/bin/env python3
"""Build labeled-pilot analysis and fusion-integration recommendation artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.labeled_pilot_analysis import build_labeled_pilot_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a compact analysis layer describing how the labeled pilot can be integrated back into real-pilot fusion.",
    )
    parser.add_argument("--real-pilot-analysis-summary", type=Path, default=Path("outputs/real_pilot_analysis/default/real_pilot_analysis_summary.json"))
    parser.add_argument("--real-pilot-next-step-recommendation", type=Path, default=Path("outputs/real_pilot_analysis/default/next_step_recommendation.json"))
    parser.add_argument("--real-pilot-readiness-summary", type=Path, default=Path("outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_readiness_summary.json"))
    parser.add_argument("--real-pilot-fusion-dataset", type=Path, default=Path("outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_dataset.jsonl"))
    parser.add_argument("--real-pilot-logistic-summary", type=Path, default=Path("outputs/real_pilot_fusion_runs/default/real_pilot_logistic_summary.json"))
    parser.add_argument("--labeled-pilot-summary", type=Path, default=Path("outputs/labeled_pilot_runs/default/labeled_pilot_summary.json"))
    parser.add_argument("--labeled-supervised-readiness-summary", type=Path, default=Path("outputs/labeled_pilot_runs/default/labeled_supervised_readiness_summary.json"))
    parser.add_argument("--labeled-logistic-summary", type=Path, default=Path("outputs/labeled_pilot_runs/default/labeled_logistic_summary.json"))
    parser.add_argument("--labeled-pilot-dataset", type=Path, default=Path("outputs/labeled_pilot_runs/default/labeled_pilot_dataset.jsonl"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_labeled_pilot_analysis(
            real_pilot_analysis_summary_path=args.real_pilot_analysis_summary,
            real_pilot_next_step_recommendation_path=args.real_pilot_next_step_recommendation,
            real_pilot_readiness_summary_path=args.real_pilot_readiness_summary,
            real_pilot_fusion_dataset_path=args.real_pilot_fusion_dataset,
            real_pilot_logistic_summary_path=args.real_pilot_logistic_summary,
            labeled_pilot_summary_path=args.labeled_pilot_summary,
            labeled_supervised_readiness_summary_path=args.labeled_supervised_readiness_summary,
            labeled_logistic_summary_path=args.labeled_logistic_summary,
            labeled_pilot_dataset_path=args.labeled_pilot_dataset,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "labeled_pilot_analysis_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"TriScope-LLM labeled pilot analysis failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    summary = result["labeled_pilot_analysis_summary"]
    print("TriScope-LLM labeled pilot analysis complete")
    print(f"Labeled rows: {summary['num_labeled_rows']}")
    print(f"Natural aligned base ids: {result['labeled_vs_real_pilot_alignment_summary']['num_naturally_aligned_base_ids']}")
    print(f"Recommendation: {result['fusion_integration_recommendation']['recommended_route']}")
    print(f"Analysis summary: {result['output_paths']['labeled_pilot_analysis_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
