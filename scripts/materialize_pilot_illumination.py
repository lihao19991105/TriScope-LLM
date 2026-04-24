#!/usr/bin/env python3
"""Materialize the third pilot illumination route for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.pilot_illumination import materialize_pilot_illumination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize the minimal third pilot route for illumination by reusing the local "
            "CSQA-style slice and building targeted-ICL-style query contracts."
        ),
    )
    parser.add_argument(
        "--datasets-config",
        type=Path,
        default=Path("configs/datasets.yaml"),
        help="Path to the datasets configuration YAML file.",
    )
    parser.add_argument(
        "--models-config",
        type=Path,
        default=Path("configs/models.yaml"),
        help="Path to the models configuration YAML file.",
    )
    parser.add_argument(
        "--experiments-config",
        type=Path,
        default=Path("configs/experiments.yaml"),
        help="Path to the experiments configuration YAML file.",
    )
    parser.add_argument(
        "--pilot-materialized-dir",
        type=Path,
        default=Path("outputs/pilot_materialization/pilot_csqa_reasoning_local"),
        help="Directory containing the existing local CSQA-style pilot slice.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory where illumination materialization artifacts will be written.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = materialize_pilot_illumination(
            datasets_config_path=args.datasets_config,
            models_config_path=args.models_config,
            experiments_config_path=args.experiments_config,
            pilot_materialized_dir=args.pilot_materialized_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "pilot_illumination_materialization_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "datasets_config": str(args.datasets_config),
                    "models_config": str(args.models_config),
                    "experiments_config": str(args.experiments_config),
                    "pilot_materialized_dir": str(args.pilot_materialized_dir),
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM pilot illumination materialization failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    readiness = result["readiness_summary"]
    print("TriScope-LLM pilot illumination materialization complete")
    print(f"Selected route: {readiness['selected_illumination_route']}")
    print(f"Ready to run: {readiness['ready_to_run']}")
    print(f"Selection: {result['output_paths']['selection']}")
    print(f"Registry: {result['output_paths']['registry']}")
    print(f"Readiness summary: {result['output_paths']['readiness_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
