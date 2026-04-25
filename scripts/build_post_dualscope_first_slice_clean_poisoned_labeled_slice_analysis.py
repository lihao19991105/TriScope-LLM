#!/usr/bin/env python3
"""Build post-analysis for DualScope first-slice clean / poisoned labels."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_first_slice_clean_poisoned_labeled_slice_analysis import (  # noqa: E402
    post_clean_poisoned_labeled_slice_analysis,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze DualScope first-slice clean/poisoned labeled pairs.")
    parser.add_argument(
        "--label-file",
        type=Path,
        default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"),
        help="Labeled-pairs JSONL to validate.",
    )
    parser.add_argument(
        "--build-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default"),
        help="Directory containing build artifacts.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Output analysis artifact directory.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = post_clean_poisoned_labeled_slice_analysis(
        label_file=args.label_file,
        build_dir=args.build_dir,
        output_dir=args.output_dir,
    )
    print(f"Final verdict: {result['final_verdict']}")
    print(f"Recommendation: {result['recommended_next_step']}")
    print(f"Output dir: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
