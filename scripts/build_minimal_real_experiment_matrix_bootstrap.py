#!/usr/bin/env python3
"""Build the minimal real-experiment matrix bootstrap."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.minimal_real_experiment_matrix_bootstrap import build_minimal_real_experiment_matrix_bootstrap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the minimal real-experiment matrix bootstrap.")
    parser.add_argument("--recommendation-path", type=Path, default=Path("outputs/post_first_real_experiment_analysis/default/first_real_experiment_next_step_recommendation.json"))
    parser.add_argument("--first-real-selection-path", type=Path, default=Path("outputs/first_real_experiment_execution/default/first_real_execution_selection.json"))
    parser.add_argument("--cutover-contract-path", type=Path, default=Path("outputs/real_experiment_cutover_bootstrap/default/real_experiment_input_contract.json"))
    parser.add_argument("--cutover-inputs-dir", type=Path, default=Path("outputs/real_experiment_cutover_bootstrap/default/materialized_real_experiment_inputs"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_minimal_real_experiment_matrix_bootstrap(
            recommendation_path=args.recommendation_path,
            first_real_selection_path=args.first_real_selection_path,
            cutover_contract_path=args.cutover_contract_path,
            cutover_inputs_dir=args.cutover_inputs_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "build_failure.json").write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"TriScope-LLM minimal real matrix bootstrap failed: {exc}")
        return 1
    print("TriScope-LLM minimal real matrix bootstrap complete")
    print(f"Summary: {result['output_paths']['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
