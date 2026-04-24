#!/usr/bin/env python3
"""Build DualScope first-slice dataset materialization artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_dataset_materialization import build_dualscope_first_slice_dataset_materialization


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Materialize DualScope first-slice dataset from a real Alpaca source.")
    parser.add_argument("--source-file", type=Path, required=True)
    parser.add_argument("--output-file", type=Path, default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--schema-check-output-dir", type=Path, default=Path("outputs/dualscope_first_slice_dataset_schema_check/default"))
    parser.add_argument("--max-examples", type=int, default=72)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--split-name", default="first_slice")
    parser.add_argument("--dataset-id", default="stanford_alpaca")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = build_dualscope_first_slice_dataset_materialization(
            source_file=args.source_file,
            output_file=args.output_file,
            output_dir=args.output_dir,
            schema_check_output_dir=args.schema_check_output_dir,
            max_examples=args.max_examples,
            seed=args.seed,
            split_name=args.split_name,
            dataset_id=args.dataset_id,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure = args.output_dir / "build_failure.json"
        failure.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"Dataset materialization failed: {exc}", file=sys.stderr)
        return 1
    print("DualScope first-slice dataset materialization complete")
    print(f"Summary: {result['output_paths']['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
