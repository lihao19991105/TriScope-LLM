#!/usr/bin/env python3
"""Run a minimal real pilot experiment for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.pilot_execution import run_pilot_reasoning_experiment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a minimal real pilot experiment by consuming a materialized pilot dataset and "
            "delegating execution to the existing reasoning probe chain."
        ),
    )
    parser.add_argument(
        "--experiment-profile",
        default="pilot_csqa_reasoning_local",
        help="Experiment profile name to execute.",
    )
    parser.add_argument(
        "--datasets-config",
        type=Path,
        default=Path("configs/datasets.yaml"),
        help="Path to the dataset registry YAML file.",
    )
    parser.add_argument(
        "--models-config",
        type=Path,
        default=Path("configs/models.yaml"),
        help="Path to the model profile YAML file.",
    )
    parser.add_argument(
        "--experiments-config",
        type=Path,
        default=Path("configs/experiments.yaml"),
        help="Path to the experiment matrix YAML file.",
    )
    parser.add_argument(
        "--reasoning-config",
        type=Path,
        default=Path("configs/reasoning.yaml"),
        help="Path to the reasoning configuration YAML file.",
    )
    parser.add_argument(
        "--prompt-dir",
        type=Path,
        default=Path("data/prompts/reasoning"),
        help="Directory containing reasoning prompt templates.",
    )
    parser.add_argument(
        "--materialized-dir",
        type=Path,
        required=True,
        help="Directory containing the pilot materialization outputs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where pilot run artifacts will be written.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic pilot execution.",
    )
    parser.add_argument(
        "--skip-feature-extraction",
        action="store_true",
        help="Run the pilot probe without the follow-up reasoning feature extraction stage.",
    )
    parser.add_argument(
        "--smoke-mode",
        action="store_true",
        help="Clamp query budget and generation lengths for a faster pilot slice run.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_pilot_reasoning_experiment(
            experiment_profile_name=args.experiment_profile,
            datasets_config_path=args.datasets_config,
            models_config_path=args.models_config,
            experiments_config_path=args.experiments_config,
            reasoning_config_path=args.reasoning_config,
            prompt_dir=args.prompt_dir,
            materialized_dir=args.materialized_dir,
            output_dir=args.output_dir,
            seed=args.seed,
            extract_features=not args.skip_feature_extraction,
            smoke_mode=args.smoke_mode,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "pilot_run_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "experiment_profile": args.experiment_profile,
                    "materialized_dir": str(args.materialized_dir),
                    "output_dir": str(args.output_dir),
                    "seed": args.seed,
                    "smoke_mode": args.smoke_mode,
                    "skip_feature_extraction": args.skip_feature_extraction,
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM pilot execution failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    summary = result["run_summary"]
    print("TriScope-LLM pilot execution complete")
    print(f"Experiment profile: {summary['experiment_profile']}")
    print(f"Model profile: {summary['model_profile']}")
    print(f"Feature extraction completed: {summary['feature_extraction_completed']}")
    print(f"Pilot run summary: {result['output_paths']['pilot_run_summary']}")
    print(f"Pilot config snapshot: {result['output_paths']['pilot_run_config_snapshot']}")
    print(f"Pilot log: {result['output_paths']['pilot_execution_log']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
