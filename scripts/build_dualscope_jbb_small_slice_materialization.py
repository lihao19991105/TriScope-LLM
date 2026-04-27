#!/usr/bin/env python3
"""Materialize or honestly block a bounded JBB-Behaviors small slice."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_jbb_small_slice_materialization import (  # noqa: E402
    DEFAULT_LICENSE_URL,
    DEFAULT_SOURCE_URL,
    build_jbb_small_slice_materialization,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build or block a bounded JBB-Behaviors small-slice manifest.")
    parser.add_argument("--dataset-source", default="JailbreakBench/JBB-Behaviors")
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--license-url", default=DEFAULT_LICENSE_URL)
    parser.add_argument("--source-split", default="harmful")
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_jbb_small_slice_materialization/default"),
    )
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        default=Path("data/jbb/small_slice/jbb_small_slice_source.jsonl"),
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-materialization.json"),
    )
    parser.add_argument(
        "--search-root",
        type=Path,
        action="append",
        default=[Path("data"), Path("/mnt/sda3/lh/data"), Path("/mnt/sda3/lh/datasets")],
        help="Local root to search for JBB behavior CSV files. May be repeated.",
    )
    parser.add_argument("--max-rows", type=int, default=16)
    parser.add_argument("--max-examples", type=int, default=None, help="Alias for --max-rows.")
    parser.add_argument("--seed", type=int, default=20260427, help="Recorded for reproducibility; no sampling is used.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_jbb_small_slice_materialization(
        output_dir=args.output_dir,
        registry_path=args.registry_path,
        search_roots=args.search_root,
        output_jsonl=args.output_jsonl,
        dataset_source=args.dataset_source,
        source_url=args.source_url,
        license_url=args.license_url,
        source_split=args.source_split,
        allow_download=args.allow_download,
        max_rows=args.max_examples if args.max_examples is not None else args.max_rows,
    )
    print("Final verdict: %s" % summary["final_verdict"])
    print("Rows: %s" % summary["row_count"])
    print("Artifacts: %s" % args.output_dir)
    print("Registry: %s" % args.registry_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
