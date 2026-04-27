#!/usr/bin/env python3
"""Build post-analysis artifacts for AdvBench small-slice materialization."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_advbench_small_slice_materialization_analysis import (  # noqa: E402
    build_post_advbench_small_slice_materialization_analysis,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build AdvBench small-slice post-analysis artifacts.")
    parser.add_argument(
        "--materialization-dir",
        type=Path,
        default=Path("outputs/dualscope_advbench_small_slice_materialization/default"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_advbench_small_slice_materialization_analysis/default"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    analysis = build_post_advbench_small_slice_materialization_analysis(
        materialization_dir=args.materialization_dir,
        output_dir=args.output_dir,
    )
    print(f"Final verdict: {analysis['final_verdict']}")
    print(f"Rows: {analysis['row_count']}")
    print(f"Artifacts: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
