#!/usr/bin/env python3
"""Build post-analysis for DualScope artifact-validation repair artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_first_slice_real_run_artifact_validation_repair_analysis import (  # noqa: E402
    build_post_real_run_artifact_validation_repair_analysis,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze first-slice real-run artifact-validation repair artifacts.")
    parser.add_argument(
        "--repair-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_real_run_artifact_validation_repair/default"),
        help="Repair artifact directory.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for post-analysis artifacts.")
    parser.add_argument("--seed", type=int, default=42, help="Seed recorded in analysis artifacts.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    analysis = build_post_real_run_artifact_validation_repair_analysis(
        repair_dir=args.repair_dir,
        output_dir=args.output_dir,
        seed=args.seed,
    )
    print(f"Verdict: {analysis['final_verdict']}")
    print(f"Recommendation: {analysis['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if analysis["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
