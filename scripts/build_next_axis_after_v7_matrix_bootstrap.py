#!/usr/bin/env python3
"""CLI for bootstrapping the next-axis-after-v7 matrix."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.next_axis_after_v7_matrix_bootstrap import build_next_axis_after_v7_matrix_bootstrap


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the next-axis-after-v7 matrix bootstrap.")
    parser.add_argument(
        "--recommendation-path",
        type=Path,
        default=Path("outputs/post_v7_real_experiment_matrix_analysis/default/next_axis_after_v6_matrix_next_step_recommendation.json"),
    )
    parser.add_argument(
        "--current-matrix-definition-path",
        type=Path,
        default=Path("outputs/next_axis_after_v6_matrix_bootstrap/default/next_axis_after_v6_matrix_definition.json"),
    )
    parser.add_argument(
        "--current-matrix-contract-path",
        type=Path,
        default=Path("outputs/next_axis_after_v6_matrix_bootstrap/default/next_axis_after_v6_input_contract.json"),
    )
    parser.add_argument(
        "--current-matrix-inputs-dir",
        type=Path,
        default=Path("outputs/next_axis_after_v6_matrix_bootstrap/default/materialized_next_axis_after_v6_matrix"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_next_axis_after_v7_matrix_bootstrap(
            recommendation_path=args.recommendation_path,
            current_matrix_definition_path=args.current_matrix_definition_path,
            current_matrix_contract_path=args.current_matrix_contract_path,
            current_matrix_inputs_dir=args.current_matrix_inputs_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "build_failure.json").write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM next-axis-after-v7 matrix bootstrap failed: {exc}")
        return 1
    print("TriScope-LLM next-axis-after-v7 matrix bootstrap complete")
    print(f"Summary: {result['output_paths']['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
