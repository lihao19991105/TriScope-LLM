#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_first_slice_dry_run_config_validator_analysis import (
    post_dualscope_first_slice_dry_run_config_validator_analysis,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze DualScope first-slice dry-run config validator artifacts.")
    parser.add_argument("--validator-dir", type=Path, default=Path("outputs/dualscope_first_slice_dry_run_config_validator/default"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = post_dualscope_first_slice_dry_run_config_validator_analysis(args.validator_dir, args.output_dir)
    print("DualScope dry-run config validator analysis complete")
    print(f"Final verdict: {result['verdict']['final_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
