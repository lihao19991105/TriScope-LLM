#!/usr/bin/env python3
"""Build route_c label-path consistency recheck artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build route_c label-path consistency recheck artifacts.")
    parser.add_argument(
        "--route-c-anchor-followup-v2-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_anchor_followup_v2/default"),
    )
    parser.add_argument(
        "--route-c-anchor-execution-recheck-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_anchor_execution_recheck/default"),
    )
    parser.add_argument(
        "--route-c-label-health-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_health/default"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.route_c_label_path_consistency_recheck import build_route_c_label_path_consistency_recheck

    try:
        result = build_route_c_label_path_consistency_recheck(
            route_c_anchor_followup_v2_dir=args.route_c_anchor_followup_v2_dir,
            route_c_anchor_execution_recheck_dir=args.route_c_anchor_execution_recheck_dir,
            route_c_label_health_dir=args.route_c_label_health_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM route_c label-path consistency recheck failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM route_c label-path consistency recheck complete")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Comparison: {result['output_paths']['comparison']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
