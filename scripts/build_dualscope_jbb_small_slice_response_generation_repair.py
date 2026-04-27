#!/usr/bin/env python3
"""CLI for JBB small-slice response-generation repair/compression."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_jbb_small_slice_response_generation_repair import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REGISTRY_PATH,
    DEFAULT_RESPONSE_DIR,
    build_jbb_small_slice_response_generation_repair,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build JBB response-generation repair artifacts.")
    parser.add_argument("--response-dir", type=Path, default=DEFAULT_RESPONSE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--seed", type=int, default=20260427)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_jbb_small_slice_response_generation_repair(
        response_dir=args.response_dir,
        output_dir=args.output_dir,
        registry_path=args.registry_path,
        seed=args.seed,
    )
    print(f"Repair verdict: {summary['final_verdict']}")
    print(f"Real response rows: {summary['real_response_rows']}")
    print(f"Blocked rows: {summary['blocked_rows']}")
    print(f"Next task: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
