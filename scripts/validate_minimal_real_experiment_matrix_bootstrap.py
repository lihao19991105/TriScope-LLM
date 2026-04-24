#!/usr/bin/env python3
"""Validate minimal real-experiment matrix bootstrap artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.minimal_real_experiment_matrix_bootstrap_checks import validate_minimal_real_experiment_matrix_bootstrap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate minimal real-experiment matrix bootstrap artifacts.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--compare-run-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = validate_minimal_real_experiment_matrix_bootstrap(args.run_dir, args.compare_run_dir, args.output_dir)
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "validation_failure.json").write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"TriScope-LLM minimal real matrix bootstrap validation failed: {exc}")
        return 1
    print("TriScope-LLM minimal real matrix bootstrap validation complete")
    print(f"Acceptance status: {result['acceptance']['summary_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
