#!/usr/bin/env python3
"""Validate route C rerun on labeled split v3 artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.rerun_route_c_on_labeled_split_v3_checks import validate_rerun_route_c_on_labeled_split_v3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate route C rerun on labeled split v3 artifacts.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--compare-run-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = validate_rerun_route_c_on_labeled_split_v3(
            run_dir=args.run_dir,
            compare_run_dir=args.compare_run_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "validation_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM route C on labeled split v3 validation failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM route C on labeled split v3 validation complete")
    print(f"Acceptance status: {result['acceptance']['summary_status']}")
    if result["repeatability"] is not None:
        print(f"Repeatability status: {result['repeatability']['summary_status']}")
    print(f"Log: {result['output_paths']['log']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
