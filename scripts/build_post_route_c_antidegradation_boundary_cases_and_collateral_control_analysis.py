#!/usr/bin/env python3
"""CLI for post-analysis of route_c anti-degradation boundary control."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build post-analysis artifacts for route_c anti-degradation boundary control."
    )
    parser.add_argument(
        "--boundary-control-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_antidegradation_boundary_control/default"),
        help="Directory containing primary boundary-control artifacts.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write post-analysis artifacts.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.post_route_c_antidegradation_boundary_cases_and_collateral_control_analysis import (
        post_route_c_antidegradation_boundary_cases_and_collateral_control_analysis,
    )

    try:
        result = post_route_c_antidegradation_boundary_cases_and_collateral_control_analysis(
            boundary_control_dir=args.boundary_control_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM route_c anti-degradation boundary post-analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("route_c anti-degradation boundary post-analysis artifacts written to:")
    for key, value in result["output_paths"].items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
