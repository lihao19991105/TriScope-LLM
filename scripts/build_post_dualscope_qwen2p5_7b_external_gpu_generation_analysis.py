#!/usr/bin/env python3
"""Build post-analysis for external Qwen2.5-7B GPU generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_qwen2p5_7b_external_gpu_generation_analysis import build_post_analysis  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Post-analyze external Qwen2.5-7B GPU generation outputs.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_external_gpu_generation/default"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_external_gpu_generation_analysis/default"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    analysis = build_post_analysis(input_dir=args.input_dir, output_dir=args.output_dir)
    print(f"Final verdict: {analysis['final_verdict']}")
    print(f"Response rows: {analysis['response_row_count']}")
    print(f"Artifacts: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
