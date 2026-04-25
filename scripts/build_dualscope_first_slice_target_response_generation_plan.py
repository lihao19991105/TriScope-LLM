#!/usr/bin/env python3
"""Build the DualScope first-slice target response generation plan."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_target_response_generation_plan import (  # noqa: E402
    build_target_response_generation_plan,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan first-slice target response generation artifacts.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for plan artifacts.")
    parser.add_argument(
        "--labeled-rerun-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default"),
        help="Labeled rerun artifact directory containing joined label rows.",
    )
    parser.add_argument(
        "--labeled-slice-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default"),
        help="Clean/poisoned labeled slice artifact directory.",
    )
    parser.add_argument("--seed", type=int, default=2025, help="Seed to record in planned generation config.")
    parser.add_argument("--max-new-tokens", type=int, default=128, help="Planned max_new_tokens for target responses.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Planned generation temperature.")
    parser.add_argument("--top-p", type=float, default=1.0, help="Planned nucleus sampling value.")
    parser.add_argument(
        "--no-full-matrix",
        action="store_true",
        default=True,
        help="Required guard against full-matrix expansion.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_target_response_generation_plan(
        output_dir=args.output_dir,
        labeled_rerun_dir=args.labeled_rerun_dir,
        labeled_slice_dir=args.labeled_slice_dir,
        seed=args.seed,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        no_full_matrix=args.no_full_matrix,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Recommended next step: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
