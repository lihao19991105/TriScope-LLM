#!/usr/bin/env python3
"""Build DualScope first-slice model execution enablement artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_model_execution_enablement import build_model_execution_enablement


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build model execution enablement artifacts.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-samples", type=int, default=3)
    parser.add_argument("--max-new-tokens", type=int, default=8)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_model_execution_enablement(args.output_dir, args.max_samples, args.max_new_tokens)
    print(f"Verdict: {summary['final_verdict']}")
    print(f"Recommendation: {summary['recommended_next_step']}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
