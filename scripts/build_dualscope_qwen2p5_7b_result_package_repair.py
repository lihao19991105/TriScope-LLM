#!/usr/bin/env python3
"""Build Qwen2.5-7B result package repair artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_result_package_repair import (  # noqa: E402
    FINAL_NOT_VALIDATED,
    build_result_package_repair,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Repair the Qwen2.5-7B first-slice result package without fabricating unavailable metrics."
    )
    parser.add_argument(
        "--prior-package-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_first_slice_result_package/default"),
        help="Prior Qwen2.5-7B first-slice result-package directory, if present.",
    )
    parser.add_argument(
        "--prior-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-first-slice-result-package.json"),
        help="Tracked prior first-slice result-package verdict registry.",
    )
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"),
        help="Qwen2.5-7B real response-generation artifact directory.",
    )
    parser.add_argument(
        "--metric-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default"),
        help="Qwen2.5-7B label-aligned metric artifact directory.",
    )
    parser.add_argument(
        "--metric-repair-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_metric_computation_repair/default"),
        help="Qwen2.5-7B metric computation repair artifact directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_result_package_repair/default"),
        help="Output directory for repaired result package artifacts.",
    )
    parser.add_argument(
        "--analysis-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_result_package_repair_analysis/default"),
        help="Output directory for analysis mirror artifacts.",
    )
    parser.add_argument(
        "--verdict-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-result-package-repair.json"),
        help="Tracked verdict registry to write.",
    )
    parser.add_argument(
        "--docs-path",
        type=Path,
        default=Path("docs/dualscope_qwen2p5_7b_result_package_repair.md"),
        help="Documentation summary path to write.",
    )
    parser.add_argument("--seed", type=int, default=2025, help="Recorded seed for reproducibility.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_result_package_repair(
        prior_package_dir=args.prior_package_dir,
        prior_registry=args.prior_registry,
        response_dir=args.response_dir,
        metric_dir=args.metric_dir,
        metric_repair_dir=args.metric_repair_dir,
        output_dir=args.output_dir,
        analysis_dir=args.analysis_dir,
        verdict_registry=args.verdict_registry,
        docs_path=args.docs_path,
        seed=args.seed,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Recommended next step: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 2 if summary["final_verdict"] == FINAL_NOT_VALIDATED else 0


if __name__ == "__main__":
    raise SystemExit(main())
