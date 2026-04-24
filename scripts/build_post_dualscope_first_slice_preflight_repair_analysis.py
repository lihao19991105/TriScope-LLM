#!/usr/bin/env python3
"""Run post-analysis for DualScope first-slice preflight repair."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_first_slice_preflight_repair_analysis import (
    post_dualscope_first_slice_preflight_repair_analysis,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze DualScope first-slice preflight repair artifacts.")
    parser.add_argument(
        "--repair-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_preflight_repair/default"),
        help="Directory containing repair artifacts.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for analysis artifacts.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = post_dualscope_first_slice_preflight_repair_analysis(args.repair_dir, args.output_dir)
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "analysis_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"DualScope first-slice preflight repair analysis failed: {exc}", file=sys.stderr)
        print(f"Failure summary: {failure_path}", file=sys.stderr)
        return 1
    print("DualScope first-slice preflight repair analysis complete")
    print(f"Final verdict: {result['verdict']['final_verdict']}")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
