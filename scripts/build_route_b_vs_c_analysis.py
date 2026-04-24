#!/usr/bin/env python3
"""Build the route B vs C vs D supervision comparison for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.route_b_vs_c_analysis import build_route_b_vs_c_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare route B, route C, and labeled-slice expansion direction D.")
    parser.add_argument(
        "--more-natural-bootstrap-dir",
        type=Path,
        default=Path("outputs/more_natural_label_bootstrap/default"),
    )
    parser.add_argument(
        "--benchmark-truth-leaning-bootstrap-dir",
        type=Path,
        default=Path("outputs/benchmark_truth_leaning_label_bootstrap/default"),
    )
    parser.add_argument(
        "--controlled-supervision-expansion-dir",
        type=Path,
        default=Path("outputs/controlled_supervision_expansion/default"),
    )
    parser.add_argument(
        "--supervision-route-comparison-dir",
        type=Path,
        default=Path("outputs/supervision_route_comparison/default"),
    )
    parser.add_argument(
        "--pilot-materialized-dir",
        type=Path,
        default=Path("outputs/pilot_materialization/pilot_csqa_reasoning_local"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_route_b_vs_c_analysis(
            more_natural_bootstrap_dir=args.more_natural_bootstrap_dir,
            benchmark_truth_leaning_bootstrap_dir=args.benchmark_truth_leaning_bootstrap_dir,
            controlled_supervision_expansion_dir=args.controlled_supervision_expansion_dir,
            supervision_route_comparison_dir=args.supervision_route_comparison_dir,
            pilot_materialized_dir=args.pilot_materialized_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM route B vs C analysis failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    print("TriScope-LLM route B vs C vs D comparison complete")
    print(f"Chosen route: {result['recommendation']['chosen_route']}")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    print(f"Gain summary: {result['output_paths']['gain_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
