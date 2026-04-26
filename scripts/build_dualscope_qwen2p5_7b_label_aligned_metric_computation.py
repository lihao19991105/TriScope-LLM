#!/usr/bin/env python3
"""Build Qwen2.5-7B label-aligned metric artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_label_aligned_metric_computation import (  # noqa: E402
    build_qwen2p5_7b_label_aligned_metric_computation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute Qwen2.5-7B first-slice metrics only from aligned labels, scores, and real responses."
    )
    parser.add_argument(
        "--labeled-pairs",
        type=Path,
        default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"),
        help="Stanford Alpaca first-slice labeled pairs JSONL.",
    )
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"),
        help="Qwen2.5-7B first-slice response-generation output directory.",
    )
    parser.add_argument(
        "--condition-level-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_condition_level_rerun/default"),
        help="Condition-level score artifact directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default"),
        help="Output directory for metric artifacts.",
    )
    parser.add_argument("--threshold", type=float, default=0.55, help="Final risk score threshold for F1/Accuracy.")
    parser.add_argument("--seed", type=int, default=2025, help="Recorded seed for reproducibility.")
    parser.add_argument("--no-full-matrix", action="store_true", default=True, help="Required first-slice scope guard.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_qwen2p5_7b_label_aligned_metric_computation(
        labeled_pairs=args.labeled_pairs,
        response_dir=args.response_dir,
        condition_level_dir=args.condition_level_dir,
        output_dir=args.output_dir,
        threshold=args.threshold,
        seed=args.seed,
        no_full_matrix=args.no_full_matrix,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Aligned rows: {summary['aligned_metric_row_count']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
