#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_dry_run_config_validator import build_dualscope_first_slice_dry_run_config_validator


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DualScope first-slice dry-run config validator artifacts.")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = build_dualscope_first_slice_dry_run_config_validator(args.output_dir)
    print("DualScope dry-run config validator complete")
    print(f"Final verdict: {result['verdict']['final_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
