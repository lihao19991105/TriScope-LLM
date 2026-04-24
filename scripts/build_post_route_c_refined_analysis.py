#!/usr/bin/env python3
"""Build post route_c refined analysis artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build post route_c refined analysis artifacts.")
    parser.add_argument(
        "--route-c-execution-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_execution/default"),
    )
    parser.add_argument(
        "--route-c-stability-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_stability/default"),
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
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.post_route_c_refined_analysis import build_post_route_c_refined_analysis

    try:
        result = build_post_route_c_refined_analysis(
            route_c_execution_dir=args.route_c_execution_dir,
            route_c_stability_dir=args.route_c_stability_dir,
            route_c_refined_execution_dir=args.route_c_refined_execution_dir,
            route_c_refined_stability_dir=args.route_c_refined_stability_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM post route_c refined analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM post route_c refined analysis complete")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
