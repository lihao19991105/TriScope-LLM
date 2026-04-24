#!/usr/bin/env python3
"""Validate DualScope first-slice smoke artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_artifact_validation import build_dualscope_first_slice_artifact_validation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate DualScope first-slice smoke artifacts.")
    parser.add_argument(
        "--smoke-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_smoke_run/default"),
        help="Directory containing smoke artifacts.",
    )
    parser.add_argument(
        "--plan-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_execution_plan/default"),
        help="Directory containing first-slice plan artifacts.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory.")
    parser.add_argument("--seed", type=int, default=42, help="Seed recorded in the manifest.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = build_dualscope_first_slice_artifact_validation(args.smoke_dir, args.plan_dir, args.output_dir, args.seed)
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"DualScope first-slice artifact validation failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1
    print("DualScope first-slice artifact validation complete")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Report: {result['output_paths']['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
