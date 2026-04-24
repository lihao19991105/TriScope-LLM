#!/usr/bin/env python3
"""Build compact scaling analysis for the labeled real-pilot fusion path."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.labeled_fusion_analysis import build_labeled_fusion_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build compact analysis and route recommendation for labeled real-pilot fusion scaling.")
    parser.add_argument("--labeled-pilot-analysis-dir", type=Path, default=Path("outputs/labeled_pilot_analysis/default"))
    parser.add_argument("--labeled-real-pilot-fusion-dir", type=Path, default=Path("outputs/labeled_real_pilot_fusion/default"))
    parser.add_argument("--labeled-real-pilot-fusion-run-dir", type=Path, default=Path("outputs/labeled_real_pilot_fusion_runs/default"))
    parser.add_argument("--real-pilot-fusion-readiness-dir", type=Path, default=Path("outputs/real_pilot_fusion_readiness/default"))
    parser.add_argument("--real-pilot-fusion-run-dir", type=Path, default=Path("outputs/real_pilot_fusion_runs/default"))
    parser.add_argument("--reasoning-run-summary", type=Path, default=Path("outputs/pilot_runs/pilot_csqa_reasoning_local_ready/pilot_run_summary.json"))
    parser.add_argument("--confidence-run-summary", type=Path, default=Path("outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/pilot_extension_run_summary.json"))
    parser.add_argument("--illumination-run-summary", type=Path, default=Path("outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready/pilot_illumination_run_summary.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_labeled_fusion_analysis(
            labeled_pilot_analysis_dir=args.labeled_pilot_analysis_dir,
            labeled_real_pilot_fusion_dir=args.labeled_real_pilot_fusion_dir,
            labeled_real_pilot_fusion_run_dir=args.labeled_real_pilot_fusion_run_dir,
            real_pilot_fusion_readiness_dir=args.real_pilot_fusion_readiness_dir,
            real_pilot_fusion_run_dir=args.real_pilot_fusion_run_dir,
            reasoning_pilot_run_summary_path=args.reasoning_run_summary,
            confidence_pilot_run_summary_path=args.confidence_run_summary,
            illumination_pilot_run_summary_path=args.illumination_run_summary,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "labeled_fusion_analysis_failure.json"
        failure_path.write_text(
            json.dumps(
                {"summary_status": "FAIL", "output_dir": str(args.output_dir), "error": str(exc)},
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM labeled fusion analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM labeled fusion analysis complete")
    print(f"Recommendation: {result['recommendation']['chosen_route_name']}")
    print(f"Analysis summary: {result['output_paths']['analysis_summary']}")
    print(f"Recommendation file: {result['output_paths']['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
