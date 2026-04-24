#!/usr/bin/env python3
"""Build route_c stable baseline time-separated replay artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build route_c stable baseline time-separated replay artifacts."
    )
    parser.add_argument(
        "--route-c-anchor-followup-v2-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_anchor_followup_v2/default"),
    )
    parser.add_argument(
        "--route-c-anchor-execution-recheck-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_anchor_execution_recheck/default"),
    )
    parser.add_argument(
        "--stage-143-recheck-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_recheck/default"),
    )
    parser.add_argument(
        "--stage-143-analysis-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_analysis/default"),
    )
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--reasoning-config", type=Path, default=Path("configs/reasoning.yaml"))
    parser.add_argument("--confidence-config", type=Path, default=Path("configs/confidence.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument("--reasoning-prompt-dir", type=Path, default=Path("data/prompts/reasoning"))
    parser.add_argument("--confidence-prompt-dir", type=Path, default=Path("data/prompts/confidence"))
    parser.add_argument("--illumination-prompt-dir", type=Path, default=Path("data/prompts/illumination"))
    parser.add_argument("--replay-count", type=int, default=3)
    parser.add_argument("--min-time-separation-minutes", type=float, default=10.0)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.route_c_stable_baseline_time_separated_replay import (
        build_route_c_stable_baseline_time_separated_replay,
    )

    try:
        result = build_route_c_stable_baseline_time_separated_replay(
            route_c_anchor_followup_v2_dir=args.route_c_anchor_followup_v2_dir,
            route_c_anchor_execution_recheck_dir=args.route_c_anchor_execution_recheck_dir,
            stage_143_recheck_dir=args.stage_143_recheck_dir,
            stage_143_analysis_dir=args.stage_143_analysis_dir,
            models_config_path=args.models_config,
            reasoning_config_path=args.reasoning_config,
            confidence_config_path=args.confidence_config,
            illumination_config_path=args.illumination_config,
            reasoning_prompt_dir=args.reasoning_prompt_dir,
            confidence_prompt_dir=args.confidence_prompt_dir,
            illumination_prompt_dir=args.illumination_prompt_dir,
            output_dir=args.output_dir,
            replay_count=args.replay_count,
            min_time_separation_minutes=args.min_time_separation_minutes,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM route_c time-separated replay failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM route_c time-separated replay complete")
    print(f"Frozen settings: {result['output_paths']['frozen_settings']}")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Details: {result['output_paths']['details']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
