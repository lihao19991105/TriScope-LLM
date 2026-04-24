#!/usr/bin/env python3
"""Build real-experiment registries and readiness summaries for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.experiment_bootstrap import build_experiment_bootstrap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build dataset, model, and experiment registries for real-experiment bootstrap "
            "and validate their local/remote readiness."
        ),
    )
    parser.add_argument(
        "--datasets-config",
        type=Path,
        default=Path("configs/datasets.yaml"),
        help="Path to the dataset source registry YAML file.",
    )
    parser.add_argument(
        "--models-config",
        type=Path,
        default=Path("configs/models.yaml"),
        help="Path to the model profile matrix YAML file.",
    )
    parser.add_argument(
        "--experiments-config",
        type=Path,
        default=Path("configs/experiments.yaml"),
        help="Path to the experiment matrix YAML file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where registry and readiness artifacts will be written.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_experiment_bootstrap(
            datasets_config_path=args.datasets_config,
            models_config_path=args.models_config,
            experiments_config_path=args.experiments_config,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "bootstrap_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "datasets_config": str(args.datasets_config),
                    "models_config": str(args.models_config),
                    "experiments_config": str(args.experiments_config),
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM experiment bootstrap failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    summary = result["experiment_bootstrap_summary"]
    output_paths = result["output_paths"]
    print("TriScope-LLM experiment bootstrap complete")
    print(f"Dataset profiles: {summary['num_dataset_profiles']}")
    print(f"Model profiles: {summary['num_model_profiles']}")
    print(f"Experiments: {summary['num_experiments']}")
    print(f"Ready local experiments: {summary['num_ready_local_experiments']}")
    print(f"Config-ready remote experiments: {summary['num_config_ready_remote_experiments']}")
    print(f"Dataset registry: {output_paths['dataset_registry']}")
    print(f"Model registry: {output_paths['model_registry']}")
    print(f"Experiment matrix: {output_paths['experiment_matrix']}")
    print(f"Readiness summary: {output_paths['experiment_readiness_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
