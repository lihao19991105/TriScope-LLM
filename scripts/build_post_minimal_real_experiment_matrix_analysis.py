#!/usr/bin/env python3
"""Build post minimal real-experiment matrix analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_minimal_real_experiment_matrix_analysis import (
    build_post_minimal_real_experiment_matrix_analysis,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build post minimal real-experiment matrix analysis.")
    parser.add_argument(
        "--cutover-bootstrap-summary-path",
        type=Path,
        default=Path("outputs/real_experiment_cutover_bootstrap/default/real_experiment_bootstrap_summary.json"),
    )
    parser.add_argument(
        "--first-real-dry-run-summary-path",
        type=Path,
        default=Path("outputs/real_experiment_first_dry_run/default/first_real_experiment_dry_run_summary.json"),
    )
    parser.add_argument(
        "--first-real-execution-run-summary-path",
        type=Path,
        default=Path("outputs/first_real_experiment_execution/default/first_real_execution_run_summary.json"),
    )
    parser.add_argument(
        "--minimal-matrix-bootstrap-summary-path",
        type=Path,
        default=Path("outputs/minimal_real_experiment_matrix_bootstrap/default/minimal_real_experiment_bootstrap_summary.json"),
    )
    parser.add_argument(
        "--matrix-dry-run-summary-path",
        type=Path,
        default=Path("outputs/first_minimal_real_experiment_matrix_dry_run/default/first_matrix_dry_run_summary.json"),
    )
    parser.add_argument(
        "--matrix-execution-run-summary-path",
        type=Path,
        default=Path("outputs/first_minimal_real_experiment_matrix_execution/default/first_matrix_execution_run_summary.json"),
    )
    parser.add_argument(
        "--matrix-execution-metrics-path",
        type=Path,
        default=Path("outputs/first_minimal_real_experiment_matrix_execution/default/first_matrix_execution_metrics.json"),
    )
    parser.add_argument(
        "--proxy-recommendation-path",
        type=Path,
        default=Path("outputs/post_v6_symmetric_comparison/default/v6_symmetric_next_step_recommendation.json"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_post_minimal_real_experiment_matrix_analysis(
            cutover_bootstrap_summary_path=args.cutover_bootstrap_summary_path,
            first_real_dry_run_summary_path=args.first_real_dry_run_summary_path,
            first_real_execution_run_summary_path=args.first_real_execution_run_summary_path,
            minimal_matrix_bootstrap_summary_path=args.minimal_matrix_bootstrap_summary_path,
            matrix_dry_run_summary_path=args.matrix_dry_run_summary_path,
            matrix_execution_run_summary_path=args.matrix_execution_run_summary_path,
            matrix_execution_metrics_path=args.matrix_execution_metrics_path,
            proxy_recommendation_path=args.proxy_recommendation_path,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "build_failure.json").write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM post minimal real-experiment matrix analysis failed: {exc}")
        return 1
    print("TriScope-LLM post minimal real-experiment matrix analysis complete")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
