#!/usr/bin/env python3
"""Build route_c label output normalization artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build route_c label output normalization artifacts.")
    parser.add_argument(
        "--execution-root-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_anchor_execution_recheck/default"),
    )
    parser.add_argument(
        "--route-c-run-subdir",
        type=str,
        default="route_c_anchor_execution_run",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.route_c_label_output_normalization import build_route_c_label_output_normalization

    try:
        result = build_route_c_label_output_normalization(
            execution_root_dir=args.execution_root_dir,
            route_c_run_subdir=args.route_c_run_subdir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM route_c label output normalization build failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM route_c label output normalization build complete")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Compare: {result['output_paths']['compare']}")
    print(f"Report: {result['output_paths']['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
