#!/usr/bin/env python3
"""Build post-analysis for first-slice real-run artifact validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_first_slice_real_run_artifact_validation_analysis import build_post_real_run_artifact_validation_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build artifact validation post-analysis.")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    analysis = build_post_real_run_artifact_validation_analysis(args.output_dir)
    print(f"Final verdict: {analysis['final_verdict']}")
    print(f"Recommendation: {analysis['recommended_next_step']}")
    return 0 if analysis["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
