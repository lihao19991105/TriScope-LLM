#!/usr/bin/env python3
"""Run stabilized 1.5B route_b execution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run model-axis 1.5B stabilized route_b execution.")
    parser.add_argument(
        "--dry-run-summary-path",
        type=Path,
        default=Path("outputs/model_axis_1p5b_dry_run/default/model_axis_1p5b_dry_run_summary.json"),
    )
    parser.add_argument(
        "--execution-gate-path",
        type=Path,
        default=Path("outputs/model_axis_1p5b_dry_run/default/model_axis_1p5b_execution_gate.json"),
    )
    parser.add_argument(
        "--stabilization-precheck-path",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_b_stabilization/default/route_b_label_balance_precheck.json"),
    )
    parser.add_argument(
        "--bootstrap-materialized-inputs-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_bootstrap/default/materialized_model_axis_1p5b_inputs"),
    )
    parser.add_argument(
        "--dry-run-materialized-inputs-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_dry_run/default/materialized_model_axis_1p5b_dry_run_inputs"),
    )
    parser.add_argument(
        "--reference-route-b-dataset-path",
        type=Path,
        default=Path("outputs/rerun_route_b_on_labeled_split_v6/default/route_b_v6_dataset.jsonl"),
    )
    parser.add_argument(
        "--reference-route-b-slice-path",
        type=Path,
        default=Path("outputs/rerun_route_b_on_labeled_split_v6/default/materialized_route_b_v6_inputs/csqa_reasoning_pilot_slice.jsonl"),
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
    parser.add_argument("--target-budget", type=int, default=32)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.model_axis_1p5b_route_b_stable_execution import build_model_axis_1p5b_route_b_stable_execution

    try:
        result = build_model_axis_1p5b_route_b_stable_execution(
            dry_run_summary_path=args.dry_run_summary_path,
            execution_gate_path=args.execution_gate_path,
            stabilization_precheck_path=args.stabilization_precheck_path,
            bootstrap_materialized_inputs_dir=args.bootstrap_materialized_inputs_dir,
            dry_run_materialized_inputs_dir=args.dry_run_materialized_inputs_dir,
            reference_route_b_dataset_path=args.reference_route_b_dataset_path,
            reference_route_b_slice_path=args.reference_route_b_slice_path,
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
            target_budget=args.target_budget,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM model-axis 1.5B route_b stable execution failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM model-axis 1.5B route_b stable execution complete")
    print(f"Run summary: {result['output_paths']['run_summary']}")
    print(f"Metrics: {result['output_paths']['metrics']}")
    print(f"Route_b summary: {result['output_paths']['route_b_summary']}")
    print(f"Route_b logistic summary: {result['output_paths']['route_b_logistic_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
