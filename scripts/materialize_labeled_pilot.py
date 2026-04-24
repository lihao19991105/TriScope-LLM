#!/usr/bin/env python3
"""Materialize the first labeled pilot route for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.labeled_pilot_bootstrap import materialize_labeled_pilot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Materialize the first labeled pilot route from the local CSQA-style pilot slice.")
    parser.add_argument("--datasets-config", type=Path, default=Path("configs/datasets.yaml"))
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--experiments-config", type=Path, default=Path("configs/experiments.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument(
        "--pilot-materialized-dir",
        type=Path,
        default=Path("outputs/pilot_materialization/pilot_csqa_reasoning_local"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = materialize_labeled_pilot(
            datasets_config_path=args.datasets_config,
            models_config_path=args.models_config,
            experiments_config_path=args.experiments_config,
            illumination_config_path=args.illumination_config,
            pilot_materialized_dir=args.pilot_materialized_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "labeled_pilot_materialization_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM labeled pilot materialization failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    print("TriScope-LLM labeled pilot materialization complete")
    print(f"Selection: {result['output_paths']['selection']}")
    print(f"Label definition: {result['output_paths']['label_definition']}")
    print(f"Readiness summary: {result['output_paths']['readiness_summary']}")
    print(f"Contracts: {result['output_paths']['query_contracts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
