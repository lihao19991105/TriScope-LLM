#!/usr/bin/env python3
"""CLI for post-v8 real-experiment matrix analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_v8_real_experiment_matrix_analysis import build_post_v8_real_experiment_matrix_analysis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the post-v8 real-experiment matrix analysis.")
    parser.add_argument("--cutover-bootstrap-summary-path", type=Path, default=Path("outputs/real_experiment_cutover_bootstrap/default/real_experiment_bootstrap_summary.json"))
    parser.add_argument("--first-real-dry-run-summary-path", type=Path, default=Path("outputs/real_experiment_first_dry_run/default/first_real_experiment_dry_run_summary.json"))
    parser.add_argument("--first-real-execution-run-summary-path", type=Path, default=Path("outputs/first_real_experiment_execution/default/first_real_execution_run_summary.json"))
    parser.add_argument("--minimal-matrix-bootstrap-summary-path", type=Path, default=Path("outputs/minimal_real_experiment_matrix_bootstrap/default/minimal_real_experiment_bootstrap_summary.json"))
    parser.add_argument("--minimal-matrix-dry-run-summary-path", type=Path, default=Path("outputs/first_minimal_real_experiment_matrix_dry_run/default/first_matrix_dry_run_summary.json"))
    parser.add_argument("--minimal-matrix-execution-run-summary-path", type=Path, default=Path("outputs/first_minimal_real_experiment_matrix_execution/default/first_matrix_execution_run_summary.json"))
    parser.add_argument("--minimal-matrix-analysis-recommendation-path", type=Path, default=Path("outputs/post_minimal_real_experiment_matrix_analysis/default/minimal_matrix_next_step_recommendation.json"))
    parser.add_argument("--next-matrix-bootstrap-summary-path", type=Path, default=Path("outputs/next_real_experiment_matrix_bootstrap/default/next_real_experiment_bootstrap_summary.json"))
    parser.add_argument("--next-matrix-dry-run-summary-path", type=Path, default=Path("outputs/next_real_experiment_matrix_dry_run/default/next_matrix_dry_run_summary.json"))
    parser.add_argument("--next-matrix-execution-run-summary-path", type=Path, default=Path("outputs/next_real_experiment_matrix_execution/default/next_matrix_execution_run_summary.json"))
    parser.add_argument("--next-matrix-analysis-recommendation-path", type=Path, default=Path("outputs/post_next_real_experiment_matrix_analysis/default/next_matrix_next_step_recommendation.json"))
    parser.add_argument("--post-next-matrix-bootstrap-summary-path", type=Path, default=Path("outputs/post_next_real_experiment_matrix_bootstrap/default/next_next_real_experiment_bootstrap_summary.json"))
    parser.add_argument("--post-next-matrix-dry-run-summary-path", type=Path, default=Path("outputs/post_next_real_experiment_matrix_dry_run/default/post_next_matrix_dry_run_summary.json"))
    parser.add_argument("--post-next-matrix-execution-run-summary-path", type=Path, default=Path("outputs/post_next_real_experiment_matrix_execution/default/post_next_matrix_execution_run_summary.json"))
    parser.add_argument("--post-next-matrix-analysis-recommendation-path", type=Path, default=Path("outputs/post_v3_real_experiment_matrix_analysis/default/post_next_matrix_next_step_recommendation.json"))
    parser.add_argument("--next-axis-matrix-bootstrap-summary-path", type=Path, default=Path("outputs/next_axis_real_experiment_matrix_bootstrap/default/next_axis_real_experiment_bootstrap_summary.json"))
    parser.add_argument("--next-axis-matrix-dry-run-summary-path", type=Path, default=Path("outputs/next_axis_real_experiment_matrix_dry_run/default/next_axis_matrix_dry_run_summary.json"))
    parser.add_argument("--next-axis-matrix-execution-run-summary-path", type=Path, default=Path("outputs/next_axis_real_experiment_matrix_execution/default/next_axis_matrix_execution_run_summary.json"))
    parser.add_argument("--next-axis-matrix-analysis-recommendation-path", type=Path, default=Path("outputs/post_v4_real_experiment_matrix_analysis/default/next_axis_matrix_next_step_recommendation.json"))
    parser.add_argument("--next-axis-after-v4-matrix-bootstrap-summary-path", type=Path, default=Path("outputs/next_axis_after_v4_real_experiment_matrix_bootstrap/default/next_axis_after_v4_bootstrap_summary.json"))
    parser.add_argument("--next-axis-after-v4-matrix-dry-run-summary-path", type=Path, default=Path("outputs/next_axis_after_v4_matrix_dry_run/default/next_axis_after_v4_matrix_dry_run_summary.json"))
    parser.add_argument("--next-axis-after-v4-matrix-execution-run-summary-path", type=Path, default=Path("outputs/next_axis_after_v4_matrix_execution/default/next_axis_after_v4_matrix_execution_run_summary.json"))
    parser.add_argument("--next-axis-after-v4-matrix-analysis-recommendation-path", type=Path, default=Path("outputs/post_v5_real_experiment_matrix_analysis/default/next_axis_after_v4_matrix_next_step_recommendation.json"))
    parser.add_argument("--next-axis-after-v5-matrix-bootstrap-summary-path", type=Path, default=Path("outputs/next_axis_after_v5_matrix_bootstrap/default/next_axis_after_v5_bootstrap_summary.json"))
    parser.add_argument("--next-axis-after-v5-matrix-dry-run-summary-path", type=Path, default=Path("outputs/next_axis_after_v5_matrix_dry_run/default/next_axis_after_v5_matrix_dry_run_summary.json"))
    parser.add_argument("--next-axis-after-v5-matrix-execution-run-summary-path", type=Path, default=Path("outputs/next_axis_after_v5_matrix_execution/default/next_axis_after_v5_matrix_execution_run_summary.json"))
    parser.add_argument("--next-axis-after-v5-matrix-analysis-recommendation-path", type=Path, default=Path("outputs/post_v6_real_experiment_matrix_analysis/default/next_axis_after_v5_matrix_next_step_recommendation.json"))
    parser.add_argument("--next-axis-after-v6-matrix-bootstrap-summary-path", type=Path, default=Path("outputs/next_axis_after_v6_matrix_bootstrap/default/next_axis_after_v6_bootstrap_summary.json"))
    parser.add_argument("--next-axis-after-v6-matrix-dry-run-summary-path", type=Path, default=Path("outputs/next_axis_after_v6_matrix_dry_run/default/next_axis_after_v6_matrix_dry_run_summary.json"))
    parser.add_argument("--next-axis-after-v6-matrix-execution-run-summary-path", type=Path, default=Path("outputs/next_axis_after_v6_matrix_execution/default/next_axis_after_v6_matrix_execution_run_summary.json"))
    parser.add_argument("--next-axis-after-v6-matrix-analysis-recommendation-path", type=Path, default=Path("outputs/post_v7_real_experiment_matrix_analysis/default/next_axis_after_v6_matrix_next_step_recommendation.json"))
    parser.add_argument("--next-axis-after-v7-matrix-bootstrap-summary-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_bootstrap/default/next_axis_after_v7_bootstrap_summary.json"))
    parser.add_argument("--next-axis-after-v7-matrix-dry-run-summary-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_dry_run/default/next_axis_after_v7_matrix_dry_run_summary.json"))
    parser.add_argument("--next-axis-after-v7-matrix-execution-run-summary-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_execution_run_summary.json"))
    parser.add_argument("--next-axis-after-v7-matrix-execution-metrics-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_execution_metrics.json"))
    parser.add_argument("--next-axis-after-v7-matrix-fusion-summary-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_fusion_summary.json"))
    parser.add_argument("--next-axis-after-v7-matrix-fusion-cell-candidate-summary-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_fusion_cell_candidate_summary.json"))
    parser.add_argument("--next-axis-after-v7-matrix-fusion-cell-refined-summary-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_fusion_cell_refined_summary.json"))
    parser.add_argument("--next-axis-after-v7-matrix-fusion-cell-refined-ablation-summary-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_fusion_cell_refined_ablation_summary.json"))
    parser.add_argument("--next-axis-after-v7-matrix-fusion-cell-refined-support-sweep-summary-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_fusion_cell_refined_support_sweep_summary.json"))
    parser.add_argument("--next-axis-after-v7-matrix-fusion-cell-refined-support-ablation-summary-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_fusion_cell_refined_support_ablation_summary.json"))
    parser.add_argument("--next-axis-after-v7-matrix-fusion-cell-refined-support-ablation-sweep-summary-path", type=Path, default=Path("outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_fusion_cell_refined_support_ablation_sweep_summary.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_post_v8_real_experiment_matrix_analysis(
            cutover_bootstrap_summary_path=args.cutover_bootstrap_summary_path,
            first_real_dry_run_summary_path=args.first_real_dry_run_summary_path,
            first_real_execution_run_summary_path=args.first_real_execution_run_summary_path,
            minimal_matrix_bootstrap_summary_path=args.minimal_matrix_bootstrap_summary_path,
            minimal_matrix_dry_run_summary_path=args.minimal_matrix_dry_run_summary_path,
            minimal_matrix_execution_run_summary_path=args.minimal_matrix_execution_run_summary_path,
            minimal_matrix_analysis_recommendation_path=args.minimal_matrix_analysis_recommendation_path,
            next_matrix_bootstrap_summary_path=args.next_matrix_bootstrap_summary_path,
            next_matrix_dry_run_summary_path=args.next_matrix_dry_run_summary_path,
            next_matrix_execution_run_summary_path=args.next_matrix_execution_run_summary_path,
            next_matrix_analysis_recommendation_path=args.next_matrix_analysis_recommendation_path,
            post_next_matrix_bootstrap_summary_path=args.post_next_matrix_bootstrap_summary_path,
            post_next_matrix_dry_run_summary_path=args.post_next_matrix_dry_run_summary_path,
            post_next_matrix_execution_run_summary_path=args.post_next_matrix_execution_run_summary_path,
            post_next_matrix_analysis_recommendation_path=args.post_next_matrix_analysis_recommendation_path,
            next_axis_matrix_bootstrap_summary_path=args.next_axis_matrix_bootstrap_summary_path,
            next_axis_matrix_dry_run_summary_path=args.next_axis_matrix_dry_run_summary_path,
            next_axis_matrix_execution_run_summary_path=args.next_axis_matrix_execution_run_summary_path,
            next_axis_matrix_analysis_recommendation_path=args.next_axis_matrix_analysis_recommendation_path,
            next_axis_after_v4_matrix_bootstrap_summary_path=args.next_axis_after_v4_matrix_bootstrap_summary_path,
            next_axis_after_v4_matrix_dry_run_summary_path=args.next_axis_after_v4_matrix_dry_run_summary_path,
            next_axis_after_v4_matrix_execution_run_summary_path=args.next_axis_after_v4_matrix_execution_run_summary_path,
            next_axis_after_v4_matrix_analysis_recommendation_path=args.next_axis_after_v4_matrix_analysis_recommendation_path,
            next_axis_after_v5_matrix_bootstrap_summary_path=args.next_axis_after_v5_matrix_bootstrap_summary_path,
            next_axis_after_v5_matrix_dry_run_summary_path=args.next_axis_after_v5_matrix_dry_run_summary_path,
            next_axis_after_v5_matrix_execution_run_summary_path=args.next_axis_after_v5_matrix_execution_run_summary_path,
            next_axis_after_v5_matrix_analysis_recommendation_path=args.next_axis_after_v5_matrix_analysis_recommendation_path,
            next_axis_after_v6_matrix_bootstrap_summary_path=args.next_axis_after_v6_matrix_bootstrap_summary_path,
            next_axis_after_v6_matrix_dry_run_summary_path=args.next_axis_after_v6_matrix_dry_run_summary_path,
            next_axis_after_v6_matrix_execution_run_summary_path=args.next_axis_after_v6_matrix_execution_run_summary_path,
            next_axis_after_v6_matrix_analysis_recommendation_path=args.next_axis_after_v6_matrix_analysis_recommendation_path,
            next_axis_after_v7_matrix_bootstrap_summary_path=args.next_axis_after_v7_matrix_bootstrap_summary_path,
            next_axis_after_v7_matrix_dry_run_summary_path=args.next_axis_after_v7_matrix_dry_run_summary_path,
            next_axis_after_v7_matrix_execution_run_summary_path=args.next_axis_after_v7_matrix_execution_run_summary_path,
            next_axis_after_v7_matrix_execution_metrics_path=args.next_axis_after_v7_matrix_execution_metrics_path,
            next_axis_after_v7_matrix_fusion_summary_path=args.next_axis_after_v7_matrix_fusion_summary_path,
            next_axis_after_v7_matrix_fusion_cell_candidate_summary_path=args.next_axis_after_v7_matrix_fusion_cell_candidate_summary_path,
            next_axis_after_v7_matrix_fusion_cell_refined_summary_path=args.next_axis_after_v7_matrix_fusion_cell_refined_summary_path,
            next_axis_after_v7_matrix_fusion_cell_refined_ablation_summary_path=args.next_axis_after_v7_matrix_fusion_cell_refined_ablation_summary_path,
            next_axis_after_v7_matrix_fusion_cell_refined_support_sweep_summary_path=args.next_axis_after_v7_matrix_fusion_cell_refined_support_sweep_summary_path,
            next_axis_after_v7_matrix_fusion_cell_refined_support_ablation_summary_path=args.next_axis_after_v7_matrix_fusion_cell_refined_support_ablation_summary_path,
            next_axis_after_v7_matrix_fusion_cell_refined_support_ablation_sweep_summary_path=args.next_axis_after_v7_matrix_fusion_cell_refined_support_ablation_sweep_summary_path,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "build_failure.json").write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM post-v8 real-experiment matrix analysis failed: {exc}")
        return 1
    print("TriScope-LLM post-v8 real-experiment matrix analysis complete")
    print(f"Summary: {result['output_paths']['analysis']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
