#!/usr/bin/env python3
"""Build the DualScope confidence verification freeze artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_confidence_verification import build_dualscope_confidence_verification


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Freeze DualScope Stage 2 confidence verification into executable protocol artifacts.",
    )
    parser.add_argument(
        "--stage1-freeze-dir",
        type=Path,
        default=Path("outputs/dualscope_illumination_screening_freeze/default"),
        help="Directory containing the Stage 1 illumination screening freeze artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where DualScope confidence verification freeze artifacts will be written.",
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
        result = build_dualscope_confidence_verification(
            stage1_freeze_dir=args.stage1_freeze_dir,
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
                    "task_name": "dualscope-confidence-verification-with-without-logprobs",
                    "seed": args.seed,
                    "stage1_freeze_dir": str(args.stage1_freeze_dir),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"DualScope confidence verification freeze failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("DualScope confidence verification freeze complete")
    print(f"Summary status: {result['summary']['summary_status']}")
    print(f"Problem definition: {result['output_paths']['problem_definition']}")
    print(f"Capability contract: {result['output_paths']['capability_contract']}")
    print(f"With-logprobs schema: {result['output_paths']['feature_schema_with_logprobs']}")
    print(f"Without-logprobs schema: {result['output_paths']['feature_schema_without_logprobs']}")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Report: {result['output_paths']['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
