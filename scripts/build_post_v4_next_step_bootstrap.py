#!/usr/bin/env python3
"""Build the post-v4 next-step bootstrap."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_v4_next_step_bootstrap import build_post_v4_next_step_bootstrap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the post-v4 next-step bootstrap.")
    parser.add_argument(
        "--current-v4-inputs-dir",
        type=Path,
        default=Path("outputs/post_v3_next_step_bootstrap/default/materialized_post_v3_inputs"),
    )
    parser.add_argument(
        "--recommendation-path",
        type=Path,
        default=Path("outputs/post_v4_symmetric_comparison/default/v4_symmetric_next_step_recommendation.json"),
    )
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--reasoning-config", type=Path, default=Path("configs/reasoning.yaml"))
    parser.add_argument("--confidence-config", type=Path, default=Path("configs/confidence.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_post_v4_next_step_bootstrap(
            current_v4_inputs_dir=args.current_v4_inputs_dir,
            recommendation_path=args.recommendation_path,
            output_dir=args.output_dir,
            models_config_path=args.models_config,
            reasoning_config_path=args.reasoning_config,
            confidence_config_path=args.confidence_config,
            illumination_config_path=args.illumination_config,
            seed=args.seed,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM post-v4 next-step bootstrap failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM post-v4 next-step bootstrap complete")
    print(f"Plan: {result['output_paths']['plan']}")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Bridge summary: {result['output_paths']['bridge_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
