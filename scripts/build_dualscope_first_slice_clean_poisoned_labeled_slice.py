#!/usr/bin/env python3
"""Build DualScope first-slice clean / poisoned labeled pairs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_clean_poisoned_labeled_slice import (  # noqa: E402
    build_clean_poisoned_labeled_slice,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build DualScope first-slice clean/poisoned labeled pairs.")
    parser.add_argument("--source-file", type=Path, required=True, help="Input first-slice source JSONL.")
    parser.add_argument("--output-file", type=Path, required=True, help="Output labeled-pairs JSONL.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output artifact directory.")
    parser.add_argument("--trigger-text", required=True, help="Frozen lexical trigger text.")
    parser.add_argument("--target-text", required=True, help="Frozen fixed response target text.")
    parser.add_argument("--seed", type=int, required=True, help="Seed recorded in label metadata.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = build_clean_poisoned_labeled_slice(
        source_file=args.source_file,
        output_file=args.output_file,
        output_dir=args.output_dir,
        trigger_text=args.trigger_text,
        target_text=args.target_text,
        seed=args.seed,
    )
    print(f"Final verdict: {result['final_verdict']}")
    print(f"Recommendation: {result['recommended_next_step']}")
    print(f"Label file: {args.output_file}")
    print(f"Output dir: {args.output_dir}")
    return 0 if result["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
