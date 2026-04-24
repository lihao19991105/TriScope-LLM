#!/usr/bin/env python3
"""Validate expanded route-C bootstrap artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.expanded_route_c_bootstrap_checks import validate_expanded_route_c_bootstrap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate expanded route-C bootstrap artifacts.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--compare-run-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = validate_expanded_route_c_bootstrap(
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
        print(f"TriScope-LLM expanded route C validation failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    print("TriScope-LLM expanded route C validation complete")
    print(f"Acceptance: {result['output_paths']['acceptance']}")
    if result["output_paths"]["repeatability"] is not None:
        print(f"Repeatability: {result['output_paths']['repeatability']}")
    print(f"Log: {result['output_paths']['log']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
