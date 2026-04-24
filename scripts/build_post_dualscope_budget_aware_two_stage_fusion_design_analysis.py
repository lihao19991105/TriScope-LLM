#!/usr/bin/env python3
"""Post-analysis CLI for the DualScope Stage 3 budget-aware fusion design."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_budget_aware_two_stage_fusion_analysis import (
    post_dualscope_budget_aware_two_stage_fusion_analysis,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run post-analysis for DualScope Stage 3 budget-aware fusion design artifacts.",
    )
    parser.add_argument(
        "--freeze-dir",
        type=Path,
        default=Path("outputs/dualscope_budget_aware_two_stage_fusion_design/default"),
        help="Directory containing the Stage 3 fusion design artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where post-analysis artifacts will be written.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = post_dualscope_budget_aware_two_stage_fusion_analysis(
            freeze_dir=args.freeze_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "error": str(exc),
                    "freeze_dir": str(args.freeze_dir),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"DualScope Stage 3 fusion design post-analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("DualScope budget-aware two-stage fusion design post-analysis complete")
    print(f"Final verdict: {result['verdict']['final_verdict']}")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
