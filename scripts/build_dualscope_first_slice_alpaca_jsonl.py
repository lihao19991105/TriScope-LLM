#!/usr/bin/env python3
"""Build the real DualScope first-slice Alpaca JSONL from a user-provided source."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_preflight_repair_common import (
    normalize_records,
    read_json_or_jsonl,
    write_json,
    write_jsonl,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize a real Alpaca-style source file into DualScope first-slice JSONL.")
    parser.add_argument("--source-file", type=Path, required=True, help="Real Alpaca-style JSON or JSONL source file.")
    parser.add_argument("--output-file", type=Path, required=True, help="Target first-slice JSONL file.")
    parser.add_argument("--max-examples", type=int, default=72, help="Maximum examples to write.")
    parser.add_argument("--seed", type=int, default=2025, help="Stable shuffle seed.")
    parser.add_argument("--split-name", default="first_slice", help="Split name to record in output rows.")
    parser.add_argument("--dataset-id", default="stanford_alpaca", help="Dataset id to record in output rows.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest_path = args.output_file.with_suffix(args.output_file.suffix + ".manifest.json")
    if not args.source_file.exists():
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(
            manifest_path,
            {
                "summary_status": "FAIL",
                "error": "source_file_missing",
                "source_file": str(args.source_file),
                "output_file": str(args.output_file),
                "real_data_required": True,
                "synthetic_data_generated": False,
            },
        )
        print(f"Source file missing: {args.source_file}", file=sys.stderr)
        print(f"Failure manifest: {manifest_path}", file=sys.stderr)
        return 2
    try:
        rows = read_json_or_jsonl(args.source_file)
        normalized, manifest = normalize_records(
            rows,
            dataset_id=args.dataset_id,
            split_name=args.split_name,
            source_file=args.source_file,
            max_examples=args.max_examples,
            seed=args.seed,
        )
        manifest.update({"output_file": str(args.output_file)})
        write_jsonl(args.output_file, normalized)
        write_json(manifest_path, manifest)
    except Exception as exc:
        write_json(
            manifest_path,
            {
                "summary_status": "FAIL",
                "error": str(exc),
                "source_file": str(args.source_file),
                "output_file": str(args.output_file),
                "real_data_required": True,
                "synthetic_data_generated": False,
            },
        )
        print(f"Failed to build first-slice JSONL: {exc}", file=sys.stderr)
        print(f"Failure manifest: {manifest_path}", file=sys.stderr)
        return 1
    print(f"Wrote {len(normalized)} rows to {args.output_file}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
