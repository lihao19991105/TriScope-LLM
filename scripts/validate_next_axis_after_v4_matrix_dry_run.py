#!/usr/bin/env python3
"""CLI for validating the next-axis-after-v4 matrix v5 dry-run."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.next_axis_after_v4_matrix_dry_run_checks import validate_next_axis_after_v4_matrix_dry_run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the refined-fusion-ablation-aware next-axis-after-v4 matrix dry-run."
    )
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--compare-run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_next_axis_after_v4_matrix_dry_run(
        run_dir=args.run_dir,
        compare_run_dir=args.compare_run_dir,
        output_dir=args.output_dir,
    )
    print("TriScope-LLM next-axis-after-v4 matrix dry-run validation complete")
    print(f"Acceptance: {args.output_dir / 'artifact_acceptance.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
