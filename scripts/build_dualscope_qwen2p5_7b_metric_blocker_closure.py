#!/usr/bin/env python3
"""Build Qwen2.5-7B metric blocker closure artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_metric_blocker_closure import (  # noqa: E402
    build_metric_blocker_closure,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diagnose Qwen2.5-7B label-aligned metric blockers.")
    parser.add_argument(
        "--labeled-pairs",
        type=Path,
        default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"),
    )
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"),
    )
    parser.add_argument(
        "--score-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_condition_level_rerun/default"),
    )
    parser.add_argument(
        "--metric-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default"),
    )
    parser.add_argument(
        "--prior-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-label-aligned-metric-computation.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default"),
    )
    parser.add_argument(
        "--analysis-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_metric_blocker_closure_analysis/default"),
    )
    parser.add_argument(
        "--verdict-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-blocker-closure.json"),
    )
    parser.add_argument(
        "--python3-metric-cli-returncode",
        type=int,
        default=None,
        help="Return code observed from the preceding python3 metric CLI run, if any.",
    )
    parser.add_argument("--seed", type=int, default=2025, help="Recorded seed for reproducibility.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_metric_blocker_closure(
        labeled_pairs=args.labeled_pairs,
        response_dir=args.response_dir,
        score_dir=args.score_dir,
        metric_dir=args.metric_dir,
        prior_registry=args.prior_registry,
        output_dir=args.output_dir,
        analysis_dir=args.analysis_dir,
        verdict_registry=args.verdict_registry,
        python3_metric_cli_returncode=args.python3_metric_cli_returncode,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Recommended next step: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
