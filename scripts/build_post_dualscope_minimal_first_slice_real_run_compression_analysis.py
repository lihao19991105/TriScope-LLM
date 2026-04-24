#!/usr/bin/env python3
"""Build post-analysis for first-slice real-run compression."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_minimal_first_slice_real_run_compression_analysis import post_dualscope_minimal_first_slice_real_run_compression_analysis


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compression-dir", type=Path, default=Path("outputs/dualscope_minimal_first_slice_real_run_compression/default"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = post_dualscope_minimal_first_slice_real_run_compression_analysis(args.compression_dir, args.output_dir)
    print(f"Final verdict: {result['verdict']}")
    print(f"Recommendation: {result['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

