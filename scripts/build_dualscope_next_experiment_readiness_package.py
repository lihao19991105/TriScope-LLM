#!/usr/bin/env python3
"""Build DualScope next experiment readiness package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_next_experiment_readiness_package import build_next_experiment_readiness_package


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build next experiment readiness package.")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_next_experiment_readiness_package(args.output_dir)
    print(f"Verdict: {summary['final_verdict']}")
    print(f"Recommendation: {summary['recommended_next_step']}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
