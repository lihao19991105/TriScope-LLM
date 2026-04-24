#!/usr/bin/env python3
"""Build the DualScope illumination screening freeze artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_illumination_screening_freeze import build_dualscope_illumination_screening_freeze


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Freeze DualScope Stage 1 illumination screening into executable protocol artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where DualScope illumination screening freeze artifacts will be written.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed recorded in the run manifest for reproducibility.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_dualscope_illumination_screening_freeze(
            output_dir=args.output_dir,
            seed=args.seed,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "error": str(exc),
                    "task_name": "dualscope-illumination-screening-freeze",
                    "seed": args.seed,
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"DualScope illumination screening freeze failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("DualScope illumination screening freeze complete")
    print(f"Summary status: {result['summary']['summary_status']}")
    print(f"Problem definition: {result['output_paths']['problem_definition']}")
    print(f"Feature schema: {result['output_paths']['feature_schema']}")
    print(f"Budget contract: {result['output_paths']['budget_contract']}")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Report: {result['output_paths']['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
