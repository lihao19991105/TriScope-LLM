#!/usr/bin/env python3
"""Build DualScope minimal first-slice real-run compression artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_minimal_first_slice_real_run_compression import build_dualscope_minimal_first_slice_real_run_compression


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = build_dualscope_minimal_first_slice_real_run_compression(args.output_dir)
    print(f"Verdict: {result['verdict']}")
    print(f"Recommendation: {result['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

