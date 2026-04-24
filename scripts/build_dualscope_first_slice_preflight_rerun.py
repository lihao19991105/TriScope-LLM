#!/usr/bin/env python3
"""Build DualScope first-slice preflight rerun artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_preflight_rerun import build_dualscope_first_slice_preflight_rerun


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run DualScope first-slice preflight rerun.")
    parser.add_argument(
        "--real-run-plan-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_real_run_plan/default"),
        help="Directory containing first-slice real-run plan artifacts.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for rerun artifacts.")
    parser.add_argument("--seed", type=int, default=42, help="Seed recorded in rerun scope.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = build_dualscope_first_slice_preflight_rerun(
            real_run_plan_dir=args.real_run_plan_dir,
            output_dir=args.output_dir,
            seed=args.seed,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"DualScope first-slice preflight rerun failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1
    print("DualScope first-slice preflight rerun complete")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Report: {result['output_paths']['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

