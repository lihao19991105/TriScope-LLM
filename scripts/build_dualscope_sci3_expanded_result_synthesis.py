#!/usr/bin/env python3
"""Build the SCI3 expanded result synthesis package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_benchmark_small_slice_external_gpu import (  # noqa: E402
    build_sci3_expanded_result_synthesis,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build DualScope SCI3 expanded synthesis artifacts.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/dualscope_sci3_expanded_result_synthesis/default"))
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-sci3-expanded-result-synthesis.json"),
    )
    parser.add_argument("--seed", type=int, default=2025, help="Recorded for reproducibility; synthesis is deterministic.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    _ = args.seed
    summary = build_sci3_expanded_result_synthesis(output_dir=args.output_dir, registry_path=args.registry_path)
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Real response rows total: {summary['real_response_rows_total']}")
    print(f"Artifacts: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
