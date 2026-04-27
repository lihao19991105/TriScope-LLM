#!/usr/bin/env python3
"""Run bounded Qwen2.5-7B benchmark small-slice generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_benchmark_small_slice_external_gpu import (  # noqa: E402
    DEFAULT_MODEL_DIR,
    spec_for,
    build_benchmark_small_slice_external_gpu_generation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bounded AdvBench/JBB Qwen2.5-7B response generation.")
    parser.add_argument("--dataset-id", required=True, choices=["advbench", "jbb"])
    parser.add_argument("--input-jsonl", type=Path)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--registry-path", type=Path)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--max-examples", type=int, default=16)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--min-free-gpu-memory-mib", type=int, default=18432)
    parser.add_argument("--allow-without-logprobs", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    spec = spec_for(args.dataset_id)
    summary = build_benchmark_small_slice_external_gpu_generation(
        dataset_id=args.dataset_id,
        input_jsonl=args.input_jsonl or spec.default_input_jsonl,
        model_dir=args.model_dir,
        output_dir=args.output_dir or spec.default_generation_output_dir,
        registry_path=args.registry_path or spec.registry_generation,
        seed=args.seed,
        max_examples=args.max_examples,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
        min_free_gpu_memory_mib=args.min_free_gpu_memory_mib,
        allow_without_logprobs=args.allow_without_logprobs,
        dry_run=args.dry_run,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Response rows: {summary['response_row_count']}")
    print(f"Artifacts: {summary['output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
