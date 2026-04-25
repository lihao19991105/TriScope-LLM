#!/usr/bin/env python3
"""Build repair/compression artifacts for the labeled first-slice rerun."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_minimal_first_slice_real_run_rerun_with_labels_repair import (  # noqa: E402
    build_labeled_rerun_repair,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compress source-level labeled rerun blockers into condition-level rerun inputs."
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for repair artifacts.")
    parser.add_argument(
        "--labeled-rerun-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default"),
        help="Input labeled-rerun artifact directory.",
    )
    parser.add_argument(
        "--label-file",
        type=Path,
        default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"),
        help="Clean/poisoned labeled-pairs JSONL.",
    )
    parser.add_argument("--max-sources", type=int, default=12, help="Maximum source examples to include.")
    parser.add_argument("--seed", type=int, default=42, help="Compatibility seed argument recorded by callers.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    _ = args.seed
    summary = build_labeled_rerun_repair(
        output_dir=args.output_dir,
        labeled_rerun_dir=args.labeled_rerun_dir,
        label_file=args.label_file,
        max_sources=args.max_sources,
    )
    print(f"Verdict: {summary['final_verdict']}")
    print(f"Recommendation: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
