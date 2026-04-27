#!/usr/bin/env python3
"""Build the bounded AdvBench small-slice result package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_advbench_small_slice_result_package import (  # noqa: E402
    build_advbench_small_slice_result_package,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Package bounded AdvBench small-slice materialization, response-generation, "
            "metric availability, blockers, and limitations."
        )
    )
    parser.add_argument(
        "--metric-dir",
        type=Path,
        default=Path("outputs/dualscope_advbench_small_slice_metric_computation/default"),
        help="AdvBench small-slice metric-computation artifact directory.",
    )
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=Path("outputs/dualscope_advbench_small_slice_response_generation/default"),
        help="AdvBench small-slice response-generation artifact directory.",
    )
    parser.add_argument(
        "--materialization-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-materialization.json"),
        help="Tracked AdvBench materialization verdict registry.",
    )
    parser.add_argument(
        "--response-generation-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation.json"),
        help="Tracked AdvBench response-generation verdict registry.",
    )
    parser.add_argument(
        "--response-generation-repair-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json"),
        help="Tracked AdvBench response-generation repair verdict registry.",
    )
    parser.add_argument(
        "--metric-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation.json"),
        help="Tracked AdvBench metric-computation verdict registry.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_advbench_small_slice_result_package/default"),
        help="Result-package output directory.",
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package.json"),
        help="Tracked task verdict registry path.",
    )
    parser.add_argument(
        "--docs-path",
        type=Path,
        default=Path("docs/dualscope_advbench_small_slice_result_package.md"),
        help="Human-readable result-package report path.",
    )
    parser.add_argument("--seed", type=int, default=20260427, help="Recorded seed for reproducibility.")
    parser.add_argument("--no-full-matrix", action="store_true", default=True, help="Required bounded-slice guard.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.no_full_matrix:
        raise ValueError("--no-full-matrix is required for this bounded result package.")
    summary = build_advbench_small_slice_result_package(
        metric_dir=args.metric_dir,
        response_dir=args.response_dir,
        materialization_registry=args.materialization_registry,
        response_generation_registry=args.response_generation_registry,
        response_generation_repair_registry=args.response_generation_repair_registry,
        metric_registry=args.metric_registry,
        output_dir=args.output_dir,
        registry_path=args.registry_path,
        docs_path=args.docs_path,
        seed=args.seed,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Recommended next step: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
