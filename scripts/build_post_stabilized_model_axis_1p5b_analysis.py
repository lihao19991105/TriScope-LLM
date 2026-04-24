#!/usr/bin/env python3
"""Build post-stabilized 1.5B model-axis analysis artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build post-stabilized model-axis 1.5B analysis artifacts.")
    parser.add_argument(
        "--original-execution-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_execution/default"),
    )
    parser.add_argument(
        "--stable-execution-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_b_stable_execution/default"),
    )
    parser.add_argument(
        "--lightweight-route-b-dir",
        type=Path,
        default=Path("outputs/rerun_route_b_on_labeled_split_v6/default"),
    )
    parser.add_argument(
        "--previous-analysis-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_analysis/default"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.post_stabilized_model_axis_1p5b_analysis import build_post_stabilized_model_axis_1p5b_analysis

    try:
        result = build_post_stabilized_model_axis_1p5b_analysis(
            original_execution_dir=args.original_execution_dir,
            stable_execution_dir=args.stable_execution_dir,
            lightweight_route_b_dir=args.lightweight_route_b_dir,
            previous_analysis_dir=args.previous_analysis_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM post-stabilized model-axis 1.5B analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM post-stabilized model-axis 1.5B analysis complete")
    print(f"Analysis summary: {result['output_paths']['analysis_summary']}")
    print(f"Comparison: {result['output_paths']['comparison']}")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
