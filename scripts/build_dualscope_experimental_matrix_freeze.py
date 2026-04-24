#!/usr/bin/env python3
"""Build DualScope experimental matrix freeze artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_experimental_matrix_freeze import build_dualscope_experimental_matrix_freeze


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Freeze the DualScope experimental matrix contracts.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for freeze artifacts.")
    parser.add_argument("--seed", type=int, default=42, help="Seed recorded in the run manifest.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = build_dualscope_experimental_matrix_freeze(output_dir=args.output_dir, seed=args.seed)
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc), "seed": args.seed}, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"DualScope experimental matrix freeze failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1
    print("DualScope experimental matrix freeze complete")
    print(f"Summary status: {result['summary']['summary_status']}")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Report: {result['output_paths']['report']}")
    print(f"Minimal first slice: {result['output_paths']['first_slice']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
