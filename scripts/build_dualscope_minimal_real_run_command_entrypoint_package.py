#!/usr/bin/env python3
"""Build and validate the DualScope minimal real-run command entrypoint package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_minimal_real_run_command_entrypoint_package import (
    build_dualscope_minimal_real_run_command_entrypoint_package,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate DualScope minimal real-run command entrypoints.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = build_dualscope_minimal_real_run_command_entrypoint_package(args.output_dir, seed=args.seed)
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"DualScope real-run entrypoint package failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1
    print("DualScope real-run entrypoint package complete")
    print(f"Verdict: {result['verdict']['final_verdict']}")
    print(f"Recommendation: {result['recommendation']['recommended_next_step']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

