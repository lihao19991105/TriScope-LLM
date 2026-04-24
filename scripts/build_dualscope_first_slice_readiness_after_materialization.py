#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_readiness_after_materialization import build_dualscope_first_slice_readiness_after_materialization


def main() -> int:
    parser = argparse.ArgumentParser(description="Build readiness package after first-slice materialization.")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = build_dualscope_first_slice_readiness_after_materialization(args.output_dir)
    print("DualScope readiness-after-materialization complete")
    print(f"Final verdict: {result['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
