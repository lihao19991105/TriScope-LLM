#!/usr/bin/env python3
"""Materialize or block a bounded JBB-Behaviors small slice."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_benchmark_small_slice_external_gpu import (  # noqa: E402
    DEFAULT_JBB_SOURCE_URL,
    build_jbb_small_slice_materialization,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a bounded JBB-Behaviors harmful small slice.")
    parser.add_argument("--source-csv", type=Path)
    parser.add_argument("--source-url", default=DEFAULT_JBB_SOURCE_URL)
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--max-examples", type=int, default=16)
    parser.add_argument("--seed", type=int, default=2025, help="Recorded for reproducibility; no sampling is used.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/dualscope_jbb_small_slice_materialization/default"))
    parser.add_argument("--output-jsonl", type=Path, default=Path("data/jbb/small_slice/jbb_small_slice_source.jsonl"))
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-materialization.json"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    _ = args.seed
    summary = build_jbb_small_slice_materialization(
        output_dir=args.output_dir,
        output_jsonl=args.output_jsonl,
        registry_path=args.registry_path,
        source_csv=args.source_csv,
        source_url=args.source_url,
        allow_download=args.allow_download,
        max_examples=args.max_examples,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Rows: {summary['row_count']}")
    print(f"Artifacts: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
