#!/usr/bin/env python3
"""Build post route_c label-path repair analysis artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build post route_c label-path repair analysis artifacts.")
    parser.add_argument(
        "--collapse-diagnosis-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis/default"),
    )
    parser.add_argument(
        "--micro-analysis-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_micro_analysis/default"),
    )
    parser.add_argument(
        "--label-health-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_health/default"),
    )
    parser.add_argument(
        "--label-recheck-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_recheck/default"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.post_route_c_label_path_repair_analysis import build_post_route_c_label_path_repair_analysis

    try:
        result = build_post_route_c_label_path_repair_analysis(
            collapse_diagnosis_dir=args.collapse_diagnosis_dir,
            micro_analysis_dir=args.micro_analysis_dir,
            label_health_dir=args.label_health_dir,
            label_recheck_dir=args.label_recheck_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM post route_c label-path repair analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM post route_c label-path repair analysis complete")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
