#!/usr/bin/env python3
"""Build post-analysis artifacts for Qwen2.5-7B resource materialization."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_resource_common import (  # noqa: E402
    DEFAULT_ANALYSIS_OUTPUT_DIR,
    DEFAULT_OUTPUT_DIR,
)
from src.eval.post_dualscope_qwen2p5_7b_resource_materialization_analysis import (  # noqa: E402
    build_post_analysis,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Post-analyze Qwen2.5-7B resource materialization artifacts.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Input materialization artifact directory.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ANALYSIS_OUTPUT_DIR, help="Output analysis directory.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_post_analysis(input_dir=args.input_dir, output_dir=args.output_dir)
    print("Final verdict: %s" % summary["final_verdict"])
    print("Artifacts: %s" % args.output_dir)
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())

