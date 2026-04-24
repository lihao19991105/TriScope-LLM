#!/usr/bin/env python3
"""CLI for next-axis-after-v10 matrix execution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.next_axis_after_v10_matrix_execution import build_next_axis_after_v10_matrix_execution


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the refined-fusion-support-floor-stress-sweep-aware next-axis-after-v10 matrix execution."
    )
    parser.add_argument(
        "--matrix-dry-run-summary-path",
        type=Path,
        default=Path("outputs/next_axis_after_v10_matrix_dry_run/default/next_axis_after_v10_matrix_dry_run_summary.json"),
    )
    parser.add_argument(
        "--matrix-cell-status-path",
        type=Path,
        default=Path("outputs/next_axis_after_v10_matrix_dry_run/default/next_axis_after_v10_matrix_cell_status.json"),
    )
    parser.add_argument(
        "--matrix-execution-contract-path",
        type=Path,
        default=Path("outputs/next_axis_after_v10_matrix_dry_run/default/next_axis_after_v10_matrix_execution_contract.json"),
    )
    parser.add_argument(
        "--matrix-definition-path",
        type=Path,
        default=Path("outputs/next_axis_after_v10_matrix_bootstrap/default/next_axis_after_v10_matrix_definition.json"),
    )
    parser.add_argument(
        "--v10-execution-dir",
        type=Path,
        default=Path("outputs/next_axis_after_v9_matrix_execution/default"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_next_axis_after_v10_matrix_execution(
            matrix_dry_run_summary_path=args.matrix_dry_run_summary_path,
            matrix_cell_status_path=args.matrix_cell_status_path,
            matrix_execution_contract_path=args.matrix_execution_contract_path,
            matrix_definition_path=args.matrix_definition_path,
            v10_execution_dir=args.v10_execution_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "build_failure.json").write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM next-axis-after-v10 matrix execution failed: {exc}")
        return 1
    print("TriScope-LLM next-axis-after-v10 matrix execution complete")
    print(f"Summary: {result['output_paths']['run_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
