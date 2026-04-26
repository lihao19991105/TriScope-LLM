#!/usr/bin/env python3
"""Build post-analysis artifacts for Qwen2.5-7B response-generation repair."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_dualscope_qwen2p5_7b_response_generation_repair_analysis import (  # noqa: E402
    build_post_qwen2p5_7b_response_generation_repair_analysis,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze Qwen2.5-7B response-generation repair artifacts.")
    parser.add_argument(
        "--repair-output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_response_generation_repair/default"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_response_generation_repair_analysis/default"),
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-response-generation-repair.json"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    verdict = build_post_qwen2p5_7b_response_generation_repair_analysis(
        repair_output_dir=args.repair_output_dir,
        output_dir=args.output_dir,
        registry_path=args.registry_path,
    )
    print(f"Final verdict: {verdict['final_verdict']}")
    print(f"Artifacts: {args.output_dir}")
    print(f"Registry: {args.registry_path}")
    return 0 if verdict["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
