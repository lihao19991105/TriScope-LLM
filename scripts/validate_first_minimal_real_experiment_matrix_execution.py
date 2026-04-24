#!/usr/bin/env python3
"""Validate the first minimal real-experiment matrix execution."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.first_minimal_real_experiment_matrix_execution_checks import (
    validate_first_minimal_real_experiment_matrix_execution,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the first minimal real-experiment matrix execution.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--compare-run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_first_minimal_real_experiment_matrix_execution(
        run_dir=args.run_dir,
        compare_run_dir=args.compare_run_dir,
        output_dir=args.output_dir,
    )
    print("TriScope-LLM first minimal real-experiment matrix execution validation complete")
    print(f"Acceptance status: {result['summary_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
