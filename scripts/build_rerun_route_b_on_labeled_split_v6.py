#!/usr/bin/env python3
"""Build route B rerun on labeled split v6."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.rerun_route_b_on_labeled_split_v6 import materialize_route_b_v6, run_route_b_v6


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rerun route B on labeled split v6.")
    parser.add_argument(
        "--v6-inputs-dir",
        type=Path,
        default=Path("outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs"),
    )
    parser.add_argument(
        "--route-c-v6-run-summary-path",
        type=Path,
        default=Path("outputs/rerun_route_c_on_labeled_split_v6/default/route_c_v6_run_summary.json"),
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
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        materialized = materialize_route_b_v6(
            v6_inputs_dir=args.v6_inputs_dir,
            route_c_v6_run_summary_path=args.route_c_v6_run_summary_path,
            output_dir=args.output_dir,
        )
        executed = run_route_b_v6(
            models_config_path=args.models_config,
            reasoning_config_path=args.reasoning_config,
            confidence_config_path=args.confidence_config,
            illumination_config_path=args.illumination_config,
            reasoning_prompt_dir=args.reasoning_prompt_dir,
            confidence_prompt_dir=args.confidence_prompt_dir,
            illumination_prompt_dir=args.illumination_prompt_dir,
            v6_inputs_dir=Path(materialized["output_paths"]["materialized_inputs_dir"]),
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
        print(f"TriScope-LLM route B on labeled split v6 failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM route B on labeled split v6 complete")
    print(f"Plan: {materialized['output_paths']['plan']}")
    print(f"Summary: {executed['output_paths']['summary']}")
    print(f"Logistic summary: {executed['output_paths']['logistic_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
