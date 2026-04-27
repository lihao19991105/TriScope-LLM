#!/usr/bin/env python3
"""Package bounded benchmark small-slice results."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_benchmark_small_slice_external_gpu import (  # noqa: E402
    build_benchmark_small_slice_result_package,
    spec_for,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build AdvBench/JBB bounded result package.")
    parser.add_argument("--dataset-id", required=True, choices=["advbench", "jbb"])
    parser.add_argument("--response-dir", type=Path)
    parser.add_argument("--metric-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--registry-path", type=Path)
    parser.add_argument("--seed", type=int, default=2025, help="Recorded for reproducibility; packaging is deterministic.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    _ = args.seed
    spec = spec_for(args.dataset_id)
    summary = build_benchmark_small_slice_result_package(
        dataset_id=args.dataset_id,
        response_dir=args.response_dir or spec.default_generation_output_dir,
        metric_dir=args.metric_dir or spec.default_metric_output_dir,
        output_dir=args.output_dir or spec.default_package_output_dir,
        registry_path=args.registry_path or spec.registry_package,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Response rows: {summary['response_row_count']}")
    print(f"Artifacts: {summary['output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
