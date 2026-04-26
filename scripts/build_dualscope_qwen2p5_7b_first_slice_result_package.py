#!/usr/bin/env python3
"""Build the Qwen2.5-7B first-slice result package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_first_slice_result_package import (  # noqa: E402
    FINAL_NOT_VALIDATED,
    build_qwen2p5_7b_first_slice_result_package,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package Qwen2.5-7B first-slice response and metric artifacts without full-paper claims."
    )
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"),
        help="Qwen2.5-7B first-slice response-generation artifact directory.",
    )
    parser.add_argument(
        "--metric-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default"),
        help="Qwen2.5-7B label-aligned metric-computation artifact directory.",
    )
    parser.add_argument(
        "--repair-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_metric_computation_repair/default"),
        help="Optional Qwen2.5-7B metric repair artifact directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_first_slice_result_package/default"),
        help="Output directory for the packaged result artifacts.",
    )
    parser.add_argument("--seed", type=int, default=2025, help="Recorded seed for reproducibility.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_qwen2p5_7b_first_slice_result_package(
        response_dir=args.response_dir,
        metric_dir=args.metric_dir,
        repair_dir=args.repair_dir,
        output_dir=args.output_dir,
        seed=args.seed,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Artifacts: {args.output_dir}")
    return 2 if summary["final_verdict"] == FINAL_NOT_VALIDATED else 0


if __name__ == "__main__":
    raise SystemExit(main())
