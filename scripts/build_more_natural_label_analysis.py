#!/usr/bin/env python3
"""Build the route-A-vs-route-B decision layer after controlled supervision expansion."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.more_natural_label_analysis import build_more_natural_label_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build more-natural-label bootstrap decision artifacts.")
    parser.add_argument(
        "--labeled-fusion-analysis-dir",
        type=Path,
        default=Path("outputs/labeled_fusion_analysis/default"),
    )
    parser.add_argument(
        "--controlled-supervision-expansion-dir",
        type=Path,
        default=Path("outputs/controlled_supervision_expansion/default"),
    )
    parser.add_argument(
        "--first-labeled-fusion-dir",
        type=Path,
        default=Path("outputs/labeled_real_pilot_fusion/default"),
    )
    parser.add_argument(
        "--first-labeled-fusion-run-dir",
        type=Path,
        default=Path("outputs/labeled_real_pilot_fusion_runs/default"),
    )
    parser.add_argument(
        "--real-pilot-fusion-readiness-dir",
        type=Path,
        default=Path("outputs/real_pilot_fusion_readiness/default"),
    )
    parser.add_argument(
        "--real-pilot-fusion-run-dir",
        type=Path,
        default=Path("outputs/real_pilot_fusion_runs/default"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_more_natural_label_analysis(
            labeled_fusion_analysis_dir=args.labeled_fusion_analysis_dir,
            controlled_supervision_expansion_dir=args.controlled_supervision_expansion_dir,
            first_labeled_fusion_dir=args.first_labeled_fusion_dir,
            first_labeled_fusion_run_dir=args.first_labeled_fusion_run_dir,
            real_pilot_fusion_readiness_dir=args.real_pilot_fusion_readiness_dir,
            real_pilot_fusion_run_dir=args.real_pilot_fusion_run_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM more-natural-label analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM more-natural-label analysis complete")
    print(f"Recommendation: {result['recommendation']['recommended_route_name']}")
    print(f"Output dir: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
