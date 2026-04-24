#!/usr/bin/env python3
"""Build the chosen-route rerun on the larger labeled split."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.chosen_route_rerun_on_larger_split import (
    materialize_chosen_route_rerun,
    run_chosen_route_rerun,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rerun the chosen route on the larger labeled split.")
    parser.add_argument(
        "--larger-inputs-dir",
        type=Path,
        default=Path("outputs/larger_labeled_split_bootstrap/default/materialized_larger_labeled_inputs"),
    )
    parser.add_argument(
        "--recommendation-path",
        type=Path,
        default=Path("outputs/larger_split_route_rerun_decision/default/larger_split_route_next_step_recommendation.json"),
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
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        materialized = materialize_chosen_route_rerun(
            larger_inputs_dir=args.larger_inputs_dir,
            recommendation_path=args.recommendation_path,
            output_dir=args.output_dir,
        )
        executed = run_chosen_route_rerun(
            models_config_path=args.models_config,
            reasoning_config_path=args.reasoning_config,
            confidence_config_path=args.confidence_config,
            illumination_config_path=args.illumination_config,
            reasoning_prompt_dir=args.reasoning_prompt_dir,
            confidence_prompt_dir=args.confidence_prompt_dir,
            illumination_prompt_dir=args.illumination_prompt_dir,
            larger_inputs_dir=Path(materialized["output_paths"]["materialized_inputs_dir"]),
            output_dir=args.output_dir,
            seed=args.seed,
            label_threshold=args.label_threshold,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM chosen route rerun failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM chosen route rerun on larger split complete")
    print(f"Rerun plan: {materialized['output_paths']['rerun_plan']}")
    print(f"Expanded summary: {executed['output_paths']['expanded_summary']}")
    print(f"Expanded logistic summary: {executed['output_paths']['expanded_logistic_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
