#!/usr/bin/env python3
"""Build anchor-aware route_c follow-up artifacts for model-axis 1.5B."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build model-axis 1.5B anchor-aware route_c follow-up artifacts.")
    parser.add_argument(
        "--route-c-execution-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_execution/default"),
    )
    parser.add_argument(
        "--route-c-refined-execution-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_refined_execution/default"),
    )
    parser.add_argument(
        "--route-c-refined-stability-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_refined_stability/default"),
    )
    parser.add_argument(
        "--route-c-refined-analysis-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_refined_analysis/default"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.model_axis_1p5b_route_c_anchor_followup import build_model_axis_1p5b_route_c_anchor_followup

    try:
        result = build_model_axis_1p5b_route_c_anchor_followup(
            route_c_execution_dir=args.route_c_execution_dir,
            route_c_refined_execution_dir=args.route_c_refined_execution_dir,
            route_c_refined_stability_dir=args.route_c_refined_stability_dir,
            route_c_refined_analysis_dir=args.route_c_refined_analysis_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM model-axis 1.5B route_c anchor follow-up failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM model-axis 1.5B route_c anchor follow-up complete")
    print(f"Candidate summary: {result['output_paths']['candidate_summary']}")
    print(f"Precheck: {result['output_paths']['precheck']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
