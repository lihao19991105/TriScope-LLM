#!/usr/bin/env python3
"""Build Qwen2.5-7B response-generation repair artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_response_generation_repair import (  # noqa: E402
    build_qwen2p5_7b_response_generation_repair,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repair Qwen2.5-7B first-slice response generation.")
    parser.add_argument("--model-dir", type=Path, default=Path("models/qwen2p5-7b-instruct"))
    parser.add_argument(
        "--labeled-pairs",
        type=Path,
        default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"),
    )
    parser.add_argument(
        "--target-response-plan-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_target_response_generation_plan/default"),
    )
    parser.add_argument(
        "--resource-materialization-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_resource_materialization/default"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_response_generation_repair/default"),
    )
    parser.add_argument(
        "--first-slice-output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"),
    )
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--max-examples", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument(
        "--min-free-gpu-memory-mib",
        type=int,
        default=0,
        help="Minimum selected-GPU free memory before model load. 0 selects the generation default.",
    )
    parser.add_argument("--device-map", default="auto", help="Reserved for future multi-device loading.")
    parser.add_argument("--load-in-4bit", action="store_true")
    parser.add_argument("--allow-without-logprobs", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.device_map != "auto":
        raise ValueError("Only --device-map auto is supported by the current repair wrapper.")
    summary = build_qwen2p5_7b_response_generation_repair(
        output_dir=args.output_dir,
        first_slice_output_dir=args.first_slice_output_dir,
        labeled_pairs=args.labeled_pairs,
        target_response_plan_dir=args.target_response_plan_dir,
        resource_materialization_dir=args.resource_materialization_dir,
        model_dir=args.model_dir,
        seed=args.seed,
        max_examples=args.max_examples,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
        min_free_gpu_memory_mib=args.min_free_gpu_memory_mib,
        load_in_4bit=args.load_in_4bit,
        allow_without_logprobs=args.allow_without_logprobs,
        dry_run=args.dry_run,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
