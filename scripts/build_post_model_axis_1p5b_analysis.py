#!/usr/bin/env python3
"""CLI for post-model-axis 1.5B analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the post-model-axis 1.5B analysis artifacts.")
    parser.add_argument("--bootstrap-summary-path", type=Path, default=Path("outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_bootstrap_summary.json"))
    parser.add_argument("--dry-run-summary-path", type=Path, default=Path("outputs/model_axis_1p5b_dry_run/default/model_axis_1p5b_dry_run_summary.json"))
    parser.add_argument("--execution-run-summary-path", type=Path, default=Path("outputs/model_axis_1p5b_execution/default/model_axis_1p5b_execution_run_summary.json"))
    parser.add_argument("--execution-metrics-path", type=Path, default=Path("outputs/model_axis_1p5b_execution/default/model_axis_1p5b_execution_metrics.json"))
    parser.add_argument("--execution-selection-path", type=Path, default=Path("outputs/model_axis_1p5b_execution/default/model_axis_1p5b_execution_selection.json"))
    parser.add_argument("--route-b-summary-path", type=Path, default=Path("outputs/model_axis_1p5b_execution/default/model_axis_1p5b_route_b_summary.json"))
    parser.add_argument("--route-b-logistic-summary-path", type=Path, default=Path("outputs/model_axis_1p5b_execution/default/model_axis_1p5b_route_b_logistic_summary.json"))
    parser.add_argument("--route-b-run-summary-path", type=Path, default=Path("outputs/model_axis_1p5b_execution/default/model_axis_1p5b_route_b_run_summary.json"))
    parser.add_argument("--lightweight-route-b-summary-path", type=Path, default=Path("outputs/rerun_route_b_on_labeled_split_v6/default/route_b_v6_summary.json"))
    parser.add_argument("--lightweight-route-b-logistic-summary-path", type=Path, default=Path("outputs/rerun_route_b_on_labeled_split_v6/default/route_b_v6_logistic_summary.json"))
    parser.add_argument("--lightweight-route-b-run-summary-path", type=Path, default=Path("outputs/rerun_route_b_on_labeled_split_v6/default/route_b_v6_run_summary.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.post_model_axis_1p5b_analysis import build_post_model_axis_1p5b_analysis

    result = build_post_model_axis_1p5b_analysis(
        bootstrap_summary_path=args.bootstrap_summary_path,
        dry_run_summary_path=args.dry_run_summary_path,
        execution_run_summary_path=args.execution_run_summary_path,
        execution_metrics_path=args.execution_metrics_path,
        execution_selection_path=args.execution_selection_path,
        route_b_summary_path=args.route_b_summary_path,
        route_b_logistic_summary_path=args.route_b_logistic_summary_path,
        route_b_run_summary_path=args.route_b_run_summary_path,
        lightweight_route_b_summary_path=args.lightweight_route_b_summary_path,
        lightweight_route_b_logistic_summary_path=args.lightweight_route_b_logistic_summary_path,
        lightweight_route_b_run_summary_path=args.lightweight_route_b_run_summary_path,
        output_dir=args.output_dir,
    )
    print("TriScope-LLM post-model-axis 1.5B analysis complete")
    print(f"Analysis summary: {result['output_paths']['analysis_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
