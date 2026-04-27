#!/usr/bin/env python3
"""Build AdvBench small-slice metric-computation repair artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_advbench_small_slice_metric_computation_repair import (  # noqa: E402
    DEFAULT_METRIC_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REGISTRY_PATH,
    DEFAULT_RESPONSE_DIR,
    build_advbench_small_slice_metric_computation_repair,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Repair/compress the partially validated AdvBench metric-computation state without "
            "fabricating unavailable metrics."
        )
    )
    parser.add_argument(
        "--metric-dir",
        type=Path,
        default=DEFAULT_METRIC_DIR,
        help="AdvBench metric-computation artifact directory to audit.",
    )
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=DEFAULT_RESPONSE_DIR,
        help="AdvBench response-generation artifact directory to audit.",
    )
    parser.add_argument(
        "--metric-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation.json"),
        help="Tracked verdict registry from AdvBench metric computation.",
    )
    parser.add_argument(
        "--response-generation-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation.json"),
        help="Tracked verdict registry from AdvBench response generation.",
    )
    parser.add_argument(
        "--response-generation-repair-registry",
        type=Path,
        default=Path(
            ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json"
        ),
        help="Tracked verdict registry from AdvBench response-generation repair.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Repair artifact output directory.",
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help="Tracked task verdict registry path.",
    )
    parser.add_argument(
        "--docs-path",
        type=Path,
        default=Path("docs/dualscope_advbench_small_slice_metric_computation_repair.md"),
        help="Human-readable repair report path.",
    )
    parser.add_argument("--seed", type=int, default=20260427, help="Recorded seed for reproducibility.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_advbench_small_slice_metric_computation_repair(
        metric_dir=args.metric_dir,
        response_dir=args.response_dir,
        metric_registry=args.metric_registry,
        response_generation_registry=args.response_generation_registry,
        response_generation_repair_registry=args.response_generation_repair_registry,
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
