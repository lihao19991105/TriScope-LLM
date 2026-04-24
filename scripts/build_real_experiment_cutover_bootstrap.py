#!/usr/bin/env python3
"""Build the real-experiment cutover bootstrap."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.real_experiment_cutover_bootstrap import build_real_experiment_cutover_bootstrap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the real-experiment cutover bootstrap.")
    parser.add_argument(
        "--recommendation-path",
        type=Path,
        default=Path("outputs/post_v6_symmetric_comparison/default/v6_symmetric_next_step_recommendation.json"),
    )
    parser.add_argument(
        "--validated-experiment-registry",
        type=Path,
        default=Path("outputs/experiment_bootstrap/pilot_refresh/validated_experiment_registry.json"),
    )
    parser.add_argument(
        "--experiment-readiness-summary",
        type=Path,
        default=Path("outputs/experiment_bootstrap/pilot_refresh/experiment_readiness_summary.json"),
    )
    parser.add_argument(
        "--dataset-registry",
        type=Path,
        default=Path("outputs/experiment_bootstrap/pilot_refresh/dataset_registry.json"),
    )
    parser.add_argument(
        "--model-registry",
        type=Path,
        default=Path("outputs/experiment_bootstrap/pilot_refresh/model_registry.json"),
    )
    parser.add_argument(
        "--v6-split-path",
        type=Path,
        default=Path("outputs/post_v5_next_step_bootstrap/default/larger_labeled_split_v6.jsonl"),
    )
    parser.add_argument(
        "--v6-split-summary-path",
        type=Path,
        default=Path("outputs/post_v5_next_step_bootstrap/default/larger_labeled_split_v6_summary.json"),
    )
    parser.add_argument(
        "--route-b-v6-summary-path",
        type=Path,
        default=Path("outputs/rerun_route_b_on_labeled_split_v6/default/route_b_v6_summary.json"),
    )
    parser.add_argument(
        "--route-c-v6-summary-path",
        type=Path,
        default=Path("outputs/rerun_route_c_on_labeled_split_v6/default/route_c_v6_summary.json"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_real_experiment_cutover_bootstrap(
            recommendation_path=args.recommendation_path,
            validated_experiment_registry_path=args.validated_experiment_registry,
            experiment_readiness_summary_path=args.experiment_readiness_summary,
            dataset_registry_path=args.dataset_registry,
            model_registry_path=args.model_registry,
            v6_split_path=args.v6_split_path,
            v6_split_summary_path=args.v6_split_summary_path,
            route_b_v6_summary_path=args.route_b_v6_summary_path,
            route_c_v6_summary_path=args.route_c_v6_summary_path,
            output_dir=args.output_dir,
            seed=args.seed,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM real experiment cutover bootstrap failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM real experiment cutover bootstrap complete")
    print(f"Plan: {result['output_paths']['plan']}")
    print(f"Bootstrap summary: {result['output_paths']['bootstrap_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
