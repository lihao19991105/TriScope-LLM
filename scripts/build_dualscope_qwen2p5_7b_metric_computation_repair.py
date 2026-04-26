#!/usr/bin/env python3
"""Build Qwen2.5-7B metric computation repair artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_metric_computation_repair import (  # noqa: E402
    build_metric_computation_repair,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package Qwen2.5-7B metric repair outputs without fabricating unavailable metrics."
    )
    parser.add_argument(
        "--metric-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default"),
        help="Label-aligned metric output directory to audit.",
    )
    parser.add_argument(
        "--blocker-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default"),
        help="Metric blocker closure output directory to audit.",
    )
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"),
        help="Qwen2.5-7B response artifact directory, recorded for provenance.",
    )
    parser.add_argument(
        "--label-metric-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-label-aligned-metric-computation.json"),
        help="Tracked verdict registry from the label-aligned metric task.",
    )
    parser.add_argument(
        "--blocker-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-blocker-closure.json"),
        help="Tracked verdict registry from the metric blocker closure task.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_metric_computation_repair/default"),
        help="Output directory for repair artifacts.",
    )
    parser.add_argument(
        "--analysis-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_metric_computation_repair_analysis/default"),
        help="Output directory for analysis copies.",
    )
    parser.add_argument(
        "--verdict-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-computation-repair.json"),
        help="Tracked verdict registry to write.",
    )
    parser.add_argument("--seed", type=int, default=2025, help="Recorded seed for reproducibility.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_metric_computation_repair(
        metric_dir=args.metric_dir,
        blocker_dir=args.blocker_dir,
        response_dir=args.response_dir,
        label_metric_registry=args.label_metric_registry,
        blocker_registry=args.blocker_registry,
        output_dir=args.output_dir,
        analysis_dir=args.analysis_dir,
        verdict_registry=args.verdict_registry,
        seed=args.seed,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Recommended next step: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
