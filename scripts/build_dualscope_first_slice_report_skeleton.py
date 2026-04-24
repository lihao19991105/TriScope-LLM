#!/usr/bin/env python3
"""Build the DualScope first-slice report skeleton."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_report_skeleton import build_dualscope_first_slice_report_skeleton


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a paper-facing DualScope first-slice report skeleton.")
    parser.add_argument("--plan-dir", type=Path, default=Path("outputs/dualscope_minimal_first_slice_execution_plan/default"))
    parser.add_argument("--smoke-dir", type=Path, default=Path("outputs/dualscope_minimal_first_slice_smoke_run/default"))
    parser.add_argument("--validation-dir", type=Path, default=Path("outputs/dualscope_first_slice_artifact_validation/default"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = build_dualscope_first_slice_report_skeleton(
            plan_dir=args.plan_dir,
            smoke_dir=args.smoke_dir,
            validation_dir=args.validation_dir,
            output_dir=args.output_dir,
            docs_dir=args.docs_dir,
            seed=args.seed,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"DualScope first-slice report skeleton failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1
    print("DualScope first-slice report skeleton complete")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Report: {result['output_paths']['report']}")
    print(f"Docs report: {result['output_paths']['docs_report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
