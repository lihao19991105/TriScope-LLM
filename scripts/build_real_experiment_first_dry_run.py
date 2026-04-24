#!/usr/bin/env python3
"""Build the first real-experiment dry-run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.real_experiment_first_dry_run import build_real_experiment_first_dry_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the first real-experiment dry-run.")
    parser.add_argument("--candidate-selection-path", type=Path, default=Path("outputs/real_experiment_cutover_bootstrap/default/real_experiment_candidate_selection.json"))
    parser.add_argument("--input-contract-path", type=Path, default=Path("outputs/real_experiment_cutover_bootstrap/default/real_experiment_input_contract.json"))
    parser.add_argument("--bootstrap-summary-path", type=Path, default=Path("outputs/real_experiment_cutover_bootstrap/default/real_experiment_bootstrap_summary.json"))
    parser.add_argument("--materialized-inputs-dir", type=Path, default=Path("outputs/real_experiment_cutover_bootstrap/default/materialized_real_experiment_inputs"))
    parser.add_argument("--v6-inputs-dir", type=Path, default=Path("outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs"))
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--reasoning-config", type=Path, default=Path("configs/reasoning.yaml"))
    parser.add_argument("--confidence-config", type=Path, default=Path("configs/confidence.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument("--reasoning-prompt-dir", type=Path, default=Path("data/prompts/reasoning"))
    parser.add_argument("--confidence-prompt-dir", type=Path, default=Path("data/prompts/confidence"))
    parser.add_argument("--illumination-prompt-dir", type=Path, default=Path("data/prompts/illumination"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_real_experiment_first_dry_run(
            candidate_selection_path=args.candidate_selection_path,
            input_contract_path=args.input_contract_path,
            bootstrap_summary_path=args.bootstrap_summary_path,
            materialized_inputs_dir=args.materialized_inputs_dir,
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
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "build_failure.json").write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"TriScope-LLM first real-experiment dry-run failed: {exc}")
        return 1
    print("TriScope-LLM first real-experiment dry-run complete")
    print(f"Summary: {result['output_paths']['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
