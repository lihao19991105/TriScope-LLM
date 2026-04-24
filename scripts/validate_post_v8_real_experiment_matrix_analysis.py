#!/usr/bin/env python3
"""CLI for validating post-v8 real-experiment matrix analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_v8_real_experiment_matrix_analysis_checks import validate_post_v8_real_experiment_matrix_analysis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the post-v8 real-experiment matrix analysis artifacts.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--compare-run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_post_v8_real_experiment_matrix_analysis(
        run_dir=args.run_dir,
        compare_run_dir=args.compare_run_dir,
        output_dir=args.output_dir,
    )
    print("TriScope-LLM post-v8 real-experiment matrix analysis validation complete")
    print(f"Acceptance: {args.output_dir / 'artifact_acceptance.json'}")
    return 0 if result["summary_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
