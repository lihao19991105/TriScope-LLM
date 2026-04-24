#!/usr/bin/env python3
"""Run a minimal pilot coverage extension for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.pilot_extension import run_confidence_extension


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a minimal second pilot route by consuming materialized extension inputs "
            "and delegating execution to the existing confidence probe chain."
        ),
    )
    parser.add_argument(
        "--experiment-profile",
        default="pilot_csqa_confidence_local",
        help="Experiment profile name to execute.",
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
        "--confidence-config",
        type=Path,
        default=Path("configs/confidence.yaml"),
        help="Path to the confidence configuration YAML file.",
    )
    parser.add_argument(
        "--prompt-dir",
        type=Path,
        default=Path("data/prompts/confidence"),
        help="Directory containing confidence prompt templates.",
    )
    parser.add_argument(
        "--materialized-dir",
        type=Path,
        required=True,
        help="Directory containing the pilot extension materialization outputs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where pilot extension artifacts will be written.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic pilot extension execution.",
    )
    parser.add_argument(
        "--skip-feature-extraction",
        action="store_true",
        help="Run the confidence extension without the follow-up feature extraction stage.",
    )
    parser.add_argument(
        "--smoke-mode",
        action="store_true",
        help="Clamp query budget and generation lengths for a faster extension run.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_confidence_extension(
            experiment_profile_name=args.experiment_profile,
            models_config_path=args.models_config,
            experiments_config_path=args.experiments_config,
            confidence_config_path=args.confidence_config,
            prompt_dir=args.prompt_dir,
            materialized_dir=args.materialized_dir,
            output_dir=args.output_dir,
            seed=args.seed,
            extract_features=not args.skip_feature_extraction,
            smoke_mode=args.smoke_mode,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "pilot_extension_run_failure.json"
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
        print(f"TriScope-LLM pilot extension execution failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    summary = result["run_summary"]
    print("TriScope-LLM pilot extension execution complete")
    print(f"Experiment profile: {summary['experiment_profile']}")
    print(f"Model profile: {summary['model_profile']}")
    print(f"Feature extraction completed: {summary['feature_extraction_completed']}")
    print(f"Pilot extension summary: {result['output_paths']['pilot_extension_run_summary']}")
    print(f"Pilot extension config snapshot: {result['output_paths']['pilot_extension_config_snapshot']}")
    print(f"Pilot extension log: {result['output_paths']['pilot_extension_execution_log']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
