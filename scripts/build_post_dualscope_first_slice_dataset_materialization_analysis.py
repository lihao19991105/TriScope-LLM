#!/usr/bin/env python3
"""Analyze DualScope first-slice dataset materialization artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_first_slice_dataset_materialization_analysis import (
    post_dualscope_first_slice_dataset_materialization_analysis,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze DualScope first-slice dataset materialization.")
    parser.add_argument("--materialization-dir", type=Path, default=Path("outputs/dualscope_first_slice_dataset_materialization/default"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = post_dualscope_first_slice_dataset_materialization_analysis(args.materialization_dir, args.output_dir)
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure = args.output_dir / "analysis_failure.json"
        failure.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"Dataset materialization analysis failed: {exc}", file=sys.stderr)
        return 1
    print("DualScope first-slice dataset materialization analysis complete")
    print(f"Final verdict: {result['verdict']['final_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
