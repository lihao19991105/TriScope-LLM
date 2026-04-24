#!/usr/bin/env python3
"""Build DualScope first-slice preflight repair artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_preflight_repair import build_dualscope_first_slice_preflight_repair


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build DualScope first-slice preflight repair package.")
    parser.add_argument(
        "--preflight-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_real_run_preflight/default"),
        help="Directory containing preflight artifacts.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for repair artifacts.")
    parser.add_argument("--seed", type=int, default=42, help="Seed recorded in repair artifacts.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = build_dualscope_first_slice_preflight_repair(args.preflight_dir, args.output_dir, args.seed)
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"DualScope first-slice preflight repair failed: {exc}", file=sys.stderr)
        print(f"Failure summary: {failure_path}", file=sys.stderr)
        return 1
    print("DualScope first-slice preflight repair complete")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Report: {result['output_paths']['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
