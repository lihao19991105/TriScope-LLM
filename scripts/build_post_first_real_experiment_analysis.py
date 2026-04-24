#!/usr/bin/env python3
"""Build post first real experiment analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_first_real_experiment_analysis import build_post_first_real_experiment_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build post first real experiment analysis.")
    parser.add_argument("--cutover-summary-path", type=Path, default=Path("outputs/real_experiment_cutover_bootstrap/default/real_experiment_bootstrap_summary.json"))
    parser.add_argument("--dry-run-summary-path", type=Path, default=Path("outputs/real_experiment_first_dry_run/default/first_real_experiment_dry_run_summary.json"))
    parser.add_argument("--execution-run-summary-path", type=Path, default=Path("outputs/first_real_experiment_execution/default/first_real_execution_run_summary.json"))
    parser.add_argument("--execution-metrics-path", type=Path, default=Path("outputs/first_real_experiment_execution/default/first_real_execution_metrics.json"))
    parser.add_argument("--proxy-comparison-summary-path", type=Path, default=Path("outputs/post_v6_symmetric_comparison/default/v6_symmetric_comparison_summary.json"))
    parser.add_argument("--route-b-v6-summary-path", type=Path, default=Path("outputs/rerun_route_b_on_labeled_split_v6/default/route_b_v6_summary.json"))
    parser.add_argument("--route-c-v6-summary-path", type=Path, default=Path("outputs/rerun_route_c_on_labeled_split_v6/default/route_c_v6_summary.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_post_first_real_experiment_analysis(
            cutover_summary_path=args.cutover_summary_path,
            dry_run_summary_path=args.dry_run_summary_path,
            execution_run_summary_path=args.execution_run_summary_path,
            execution_metrics_path=args.execution_metrics_path,
            proxy_comparison_summary_path=args.proxy_comparison_summary_path,
            route_b_v6_summary_path=args.route_b_v6_summary_path,
            route_c_v6_summary_path=args.route_c_v6_summary_path,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "build_failure.json").write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"TriScope-LLM post first real analysis failed: {exc}")
        return 1
    print("TriScope-LLM post first real analysis complete")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
