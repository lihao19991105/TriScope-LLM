#!/usr/bin/env python3
"""Build the first minimal real-experiment matrix execution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.first_minimal_real_experiment_matrix_execution import (
    build_first_minimal_real_experiment_matrix_execution,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the first minimal real-experiment matrix execution.")
    parser.add_argument(
        "--matrix-dry-run-summary-path",
        type=Path,
        default=Path("outputs/first_minimal_real_experiment_matrix_dry_run/default/first_matrix_dry_run_summary.json"),
    )
    parser.add_argument(
        "--matrix-cell-status-path",
        type=Path,
        default=Path("outputs/first_minimal_real_experiment_matrix_dry_run/default/first_matrix_cell_status.json"),
    )
    parser.add_argument(
        "--matrix-execution-contract-path",
        type=Path,
        default=Path("outputs/first_minimal_real_experiment_matrix_dry_run/default/first_matrix_execution_contract.json"),
    )
    parser.add_argument(
        "--matrix-definition-path",
        type=Path,
        default=Path("outputs/minimal_real_experiment_matrix_bootstrap/default/minimal_real_experiment_matrix_definition.json"),
    )
    parser.add_argument(
        "--v6-inputs-dir",
        type=Path,
        default=Path("outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs"),
    )
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--reasoning-config", type=Path, default=Path("configs/reasoning.yaml"))
    parser.add_argument("--confidence-config", type=Path, default=Path("configs/confidence.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument("--reasoning-prompt-dir", type=Path, default=Path("data/prompts/reasoning"))
    parser.add_argument("--confidence-prompt-dir", type=Path, default=Path("data/prompts/confidence"))
    parser.add_argument("--illumination-prompt-dir", type=Path, default=Path("data/prompts/illumination"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label-threshold", type=float, default=0.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_first_minimal_real_experiment_matrix_execution(
            matrix_dry_run_summary_path=args.matrix_dry_run_summary_path,
            matrix_cell_status_path=args.matrix_cell_status_path,
            matrix_execution_contract_path=args.matrix_execution_contract_path,
            matrix_definition_path=args.matrix_definition_path,
            v6_inputs_dir=args.v6_inputs_dir,
            models_config_path=args.models_config,
            reasoning_config_path=args.reasoning_config,
            confidence_config_path=args.confidence_config,
            illumination_config_path=args.illumination_config,
            reasoning_prompt_dir=args.reasoning_prompt_dir,
            confidence_prompt_dir=args.confidence_prompt_dir,
            illumination_prompt_dir=args.illumination_prompt_dir,
            output_dir=args.output_dir,
            seed=args.seed,
            label_threshold=args.label_threshold,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "build_failure.json").write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM first minimal real-experiment matrix execution failed: {exc}")
        return 1
    print("TriScope-LLM first minimal real-experiment matrix execution complete")
    print(f"Run summary: {result['output_paths']['run_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
