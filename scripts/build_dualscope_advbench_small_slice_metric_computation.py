#!/usr/bin/env python3
"""Build AdvBench small-slice metric-computation artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_advbench_small_slice_metric_computation import (  # noqa: E402
    build_advbench_small_slice_metric_computation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compute only artifact-supported AdvBench small-slice metrics and record blockers "
            "for unavailable performance metrics."
        )
    )
    parser.add_argument(
        "--response-generation-verdict",
        type=Path,
        default=Path(
            ".reports/dualscope_task_verdicts/"
            "dualscope-advbench-small-slice-response-generation.json"
        ),
        help="Tracked verdict from AdvBench small-slice response generation.",
    )
    parser.add_argument(
        "--response-jsonl",
        type=Path,
        default=Path(
            "outputs/dualscope_advbench_small_slice_response_generation/default/"
            "advbench_small_slice_responses.jsonl"
        ),
        help="Bounded AdvBench response rows JSONL.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_advbench_small_slice_metric_computation/default"),
        help="Metric artifact output directory.",
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(
            ".reports/dualscope_task_verdicts/"
            "dualscope-advbench-small-slice-metric-computation.json"
        ),
        help="Tracked task verdict registry path.",
    )
    parser.add_argument(
        "--docs-path",
        type=Path,
        default=Path("docs/dualscope_advbench_small_slice_metric_computation.md"),
        help="Human-readable metric computation report path.",
    )
    parser.add_argument("--seed", type=int, default=20260427, help="Recorded seed for reproducibility.")
    parser.add_argument("--no-full-matrix", action="store_true", default=True, help="Required bounded-slice guard.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_advbench_small_slice_metric_computation(
        response_generation_verdict=args.response_generation_verdict,
        response_jsonl=args.response_jsonl,
        output_dir=args.output_dir,
        registry_path=args.registry_path,
        docs_path=args.docs_path,
        seed=args.seed,
        no_full_matrix=args.no_full_matrix,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Real response rows: {summary['real_response_row_count']}")
    print(f"Blocked rows: {summary['blocked_row_count']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
