#!/usr/bin/env python3
"""Build route_c label-balance stabilization artifacts for model-axis 1.5B."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build model-axis 1.5B route_c label-balance stabilization artifacts.")
    parser.add_argument(
        "--route-c-portability-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_portability/default"),
    )
    parser.add_argument(
        "--dry-run-materialized-inputs-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_dry_run/default/materialized_model_axis_1p5b_dry_run_inputs"),
    )
    parser.add_argument(
        "--reference-route-c-dataset-path",
        type=Path,
        default=Path("outputs/rerun_route_c_on_labeled_split_v6/default/route_c_v6_dataset.jsonl"),
    )
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument("--illumination-prompt-dir", type=Path, default=Path("data/prompts/illumination"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--target-base-budget", type=int, default=12)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.model_axis_1p5b_route_c_stabilization import build_model_axis_1p5b_route_c_stabilization

    try:
        result = build_model_axis_1p5b_route_c_stabilization(
            route_c_portability_dir=args.route_c_portability_dir,
            dry_run_materialized_inputs_dir=args.dry_run_materialized_inputs_dir,
            reference_route_c_dataset_path=args.reference_route_c_dataset_path,
            models_config_path=args.models_config,
            illumination_config_path=args.illumination_config,
            illumination_prompt_dir=args.illumination_prompt_dir,
            output_dir=args.output_dir,
            seed=args.seed,
            target_base_budget=args.target_base_budget,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM model-axis 1.5B route_c stabilization failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM model-axis 1.5B route_c stabilization complete")
    print(f"Diagnosis: {result['output_paths']['diagnosis']}")
    print(f"Balanced candidate summary: {result['output_paths']['balanced_candidate_summary']}")
    print(f"Precheck: {result['output_paths']['precheck']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
