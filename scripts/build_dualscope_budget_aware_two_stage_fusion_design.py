#!/usr/bin/env python3
"""Build the DualScope Stage 3 budget-aware fusion design artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_budget_aware_two_stage_fusion import (
    build_dualscope_budget_aware_two_stage_fusion,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Freeze DualScope Stage 3 budget-aware two-stage fusion into executable protocol artifacts.",
    )
    parser.add_argument(
        "--stage1-freeze-dir",
        type=Path,
        default=Path("outputs/dualscope_illumination_screening_freeze/default"),
        help="Directory containing the Stage 1 illumination screening freeze artifacts.",
    )
    parser.add_argument(
        "--stage2-freeze-dir",
        type=Path,
        default=Path("outputs/dualscope_confidence_verification_with_without_logprobs/default"),
        help="Directory containing the Stage 2 confidence verification freeze artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where DualScope Stage 3 fusion design artifacts will be written.",
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
        result = build_dualscope_budget_aware_two_stage_fusion(
            stage1_freeze_dir=args.stage1_freeze_dir,
            stage2_freeze_dir=args.stage2_freeze_dir,
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
                    "task_name": "dualscope-budget-aware-two-stage-fusion-design",
                    "seed": args.seed,
                    "stage1_freeze_dir": str(args.stage1_freeze_dir),
                    "stage2_freeze_dir": str(args.stage2_freeze_dir),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"DualScope Stage 3 fusion design failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("DualScope budget-aware two-stage fusion design complete")
    print(f"Summary status: {result['summary']['summary_status']}")
    print(f"Problem definition: {result['output_paths']['problem_definition']}")
    print(f"Dependency contract: {result['output_paths']['dependency_contract']}")
    print(f"Budget policy: {result['output_paths']['budget_policy']}")
    print(f"Final decision contract: {result['output_paths']['final_decision_contract']}")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Report: {result['output_paths']['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
