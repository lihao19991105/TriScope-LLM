#!/usr/bin/env python3
"""Build DualScope minimal first-slice real-run rerun artifacts with labels attached."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_minimal_first_slice_real_run_rerun_with_labels import (  # noqa: E402
    build_labeled_real_run_rerun,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rerun minimal first-slice and attach clean/poisoned label contracts.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for labeled rerun artifacts.")
    parser.add_argument(
        "--rerun-output-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_real_run_rerun/default"),
        help="Existing base rerun output directory used for context.",
    )
    parser.add_argument(
        "--label-output-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default"),
        help="Clean/poisoned labeled slice artifact directory.",
    )
    parser.add_argument(
        "--label-analysis-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_clean_poisoned_labeled_slice_analysis/default"),
        help="Clean/poisoned labeled slice analysis artifact directory.",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "model_with_logprobs", "model_without_logprobs_fallback", "model_generation_only", "protocol_fallback_only"],
        default="auto",
        help="Base rerun capability mode.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed recorded in the labeled rerun scope.")
    parser.add_argument("--no-full-matrix", action="store_true", default=True, help="Required guard against full-matrix execution.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_labeled_real_run_rerun(
        output_dir=args.output_dir,
        rerun_output_dir=args.rerun_output_dir,
        label_output_dir=args.label_output_dir,
        label_analysis_dir=args.label_analysis_dir,
        mode=args.mode,
        seed=args.seed,
        no_full_matrix=args.no_full_matrix,
    )
    print(f"Verdict: {summary['final_verdict']}")
    print(f"Recommendation: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
