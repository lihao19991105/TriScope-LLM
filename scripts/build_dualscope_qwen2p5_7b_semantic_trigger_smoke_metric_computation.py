#!/usr/bin/env python3
"""Build bounded Qwen2.5-7B semantic trigger smoke metric artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation import (  # noqa: E402
    build_qwen2p5_7b_semantic_trigger_smoke_metric_computation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compute bounded Qwen2.5-7B semantic trigger smoke metrics only from aligned labels, "
            "available score fields, and real model responses."
        )
    )
    parser.add_argument(
        "--labeled-pairs",
        type=Path,
        default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"),
        help="Stanford Alpaca labeled clean/poisoned pairs JSONL.",
    )
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default"),
        help="Bounded semantic trigger smoke response-generation artifact directory.",
    )
    parser.add_argument(
        "--score-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_condition_level_rerun/default"),
        help="Directory containing row-level score artifacts with final_risk_score.",
    )
    parser.add_argument(
        "--response-generation-registry",
        type=Path,
        default=Path(
            ".reports/dualscope_task_verdicts/"
            "dualscope-qwen2p5-7b-semantic-trigger-smoke-response-generation.json"
        ),
        help="Tracked response-generation verdict registry.",
    )
    parser.add_argument(
        "--response-generation-repair-registry",
        type=Path,
        default=Path(
            ".reports/dualscope_task_verdicts/"
            "dualscope-qwen2p5-7b-semantic-trigger-smoke-response-generation-repair.json"
        ),
        help="Tracked response-generation repair registry, if present.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default"),
        help="Metric artifact output directory.",
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(
            ".reports/dualscope_task_verdicts/"
            "dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-computation.json"
        ),
        help="Tracked task verdict registry path.",
    )
    parser.add_argument("--threshold", type=float, default=0.55, help="Final risk score threshold for F1/Accuracy.")
    parser.add_argument("--seed", type=int, default=2025, help="Recorded seed for reproducibility.")
    parser.add_argument("--no-full-matrix", action="store_true", default=True, help="Required bounded-slice scope guard.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_qwen2p5_7b_semantic_trigger_smoke_metric_computation(
        labeled_pairs=args.labeled_pairs,
        response_dir=args.response_dir,
        score_dir=args.score_dir,
        response_generation_registry=args.response_generation_registry,
        response_generation_repair_registry=args.response_generation_repair_registry,
        output_dir=args.output_dir,
        registry_path=args.registry_path,
        threshold=args.threshold,
        seed=args.seed,
        no_full_matrix=args.no_full_matrix,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Aligned rows: {summary['aligned_metric_row_count']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
