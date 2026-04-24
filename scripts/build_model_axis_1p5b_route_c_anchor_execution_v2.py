#!/usr/bin/env python3
"""Build anchor-aware baseline-preserving route_c execution v2 artifacts for model-axis 1.5B."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build model-axis 1.5B anchor-aware baseline-preserving execution v2.")
    parser.add_argument(
        "--route-c-anchor-followup-v2-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_anchor_followup_v2/default"),
    )
    parser.add_argument(
        "--route-c-anchor-execution-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_anchor_execution/default"),
    )
    parser.add_argument(
        "--route-c-deepened-execution-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_deepened_execution/default"),
    )
    parser.add_argument(
        "--route-c-refined-execution-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_refined_execution/default"),
    )
    parser.add_argument(
        "--route-c-stable-portability-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_stable_portability/default"),
    )
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--reasoning-config", type=Path, default=Path("configs/reasoning.yaml"))
    parser.add_argument("--confidence-config", type=Path, default=Path("configs/confidence.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument("--reasoning-prompt-dir", type=Path, default=Path("data/prompts/reasoning"))
    parser.add_argument("--confidence-prompt-dir", type=Path, default=Path("data/prompts/confidence"))
    parser.add_argument("--illumination-prompt-dir", type=Path, default=Path("data/prompts/illumination"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label-threshold", type=float, default=0.5)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.model_axis_1p5b_route_c_anchor_execution_v2 import build_model_axis_1p5b_route_c_anchor_execution_v2

    try:
        result = build_model_axis_1p5b_route_c_anchor_execution_v2(
            route_c_anchor_followup_v2_dir=args.route_c_anchor_followup_v2_dir,
            route_c_anchor_execution_dir=args.route_c_anchor_execution_dir,
            route_c_deepened_execution_dir=args.route_c_deepened_execution_dir,
            route_c_refined_execution_dir=args.route_c_refined_execution_dir,
            route_c_stable_portability_dir=args.route_c_stable_portability_dir,
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
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM model-axis 1.5B route_c anchor execution v2 failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM model-axis 1.5B route_c anchor execution v2 complete")
    print(f"Run summary: {result['output_paths']['run_summary']}")
    print(f"Metrics: {result['output_paths']['metrics']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
