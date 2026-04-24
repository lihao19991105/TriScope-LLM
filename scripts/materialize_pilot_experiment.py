#!/usr/bin/env python3
"""Materialize a minimal real pilot experiment for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.pilot_execution import materialize_pilot_experiment, rebuild_bootstrap_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize a minimal real pilot experiment by selecting a blocked/config-only route, "
            "creating a local pilot dataset slice, and writing pilot readiness artifacts."
        ),
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
        "--validated-registry",
        type=Path,
        default=Path("outputs/experiment_bootstrap/default/validated_experiment_registry.json"),
        help="Validated experiment registry used to choose the pilot route.",
    )
    parser.add_argument(
        "--bootstrap-output-dir",
        type=Path,
        default=Path("outputs/experiment_bootstrap/pilot_refresh"),
        help="Directory where a refreshed bootstrap snapshot should be written after materialization.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where pilot materialization artifacts will be written.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        materialized = materialize_pilot_experiment(
            datasets_config_path=args.datasets_config,
            models_config_path=args.models_config,
            experiments_config_path=args.experiments_config,
            validated_registry_path=args.validated_registry,
            output_dir=args.output_dir,
        )
        bootstrap_refresh = rebuild_bootstrap_snapshot(
            datasets_config_path=args.datasets_config,
            models_config_path=args.models_config,
            experiments_config_path=args.experiments_config,
            output_dir=args.bootstrap_output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "materialization_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "datasets_config": str(args.datasets_config),
                    "models_config": str(args.models_config),
                    "experiments_config": str(args.experiments_config),
                    "validated_registry": str(args.validated_registry),
                    "bootstrap_output_dir": str(args.bootstrap_output_dir),
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM pilot materialization failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    readiness = materialized["readiness_summary"]
    bootstrap_summary = bootstrap_refresh["experiment_bootstrap_summary"]
    print("TriScope-LLM pilot materialization complete")
    print(f"Selected experiment: {readiness['selected_experiment_profile']}")
    print(f"Ready to run: {readiness['ready_to_run']}")
    print(f"Pilot dataset summary: {materialized['output_paths']['dataset_summary']}")
    print(f"Pilot readiness summary: {materialized['output_paths']['readiness_summary']}")
    print(f"Refreshed experiment bootstrap summary: {bootstrap_summary['num_experiments']} experiments")
    print(f"Refreshed bootstrap dir: {args.bootstrap_output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
