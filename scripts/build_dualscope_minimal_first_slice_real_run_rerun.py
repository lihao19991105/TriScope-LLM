#!/usr/bin/env python3
"""Build DualScope minimal first-slice real-run rerun artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_minimal_first_slice_real_run_rerun import build_real_run_rerun


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rerun minimal first-slice with model/fallback capability evidence.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["auto", "model_with_logprobs", "model_without_logprobs_fallback", "model_generation_only", "protocol_fallback_only"], default="auto")
    parser.add_argument("--no-full-matrix", action="store_true", default=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_real_run_rerun(args.output_dir, args.mode, args.no_full_matrix)
    print(f"Verdict: {summary['final_verdict']}")
    print(f"Recommendation: {summary['recommended_next_step']}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
