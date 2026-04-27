#!/usr/bin/env python3
"""Build the Qwen2.5-7B behavior-shift target smoke result package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package import (  # noqa: E402
    build_behavior_shift_target_smoke_result_package,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package bounded behavior-shift target smoke response and metric artifacts.")
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default"),
    )
    parser.add_argument(
        "--metric-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default"),
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package.json"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_behavior_shift_target_smoke_result_package(
        response_dir=args.response_dir,
        metric_dir=args.metric_dir,
        output_dir=args.output_dir,
        registry_path=args.registry_path,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
