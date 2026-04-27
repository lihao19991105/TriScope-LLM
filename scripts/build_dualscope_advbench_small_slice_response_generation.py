#!/usr/bin/env python3
"""CLI for bounded AdvBench small-slice response generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_advbench_small_slice_response_generation import (  # noqa: E402
    DEFAULT_DOWNLOAD_REPAIR_VERDICT,
    DEFAULT_MATERIALIZATION_VERDICT,
    DEFAULT_MODEL_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PLAN_VERDICT,
    DEFAULT_REGISTRY_PATH,
    DEFAULT_SOURCE_JSONL,
    SAFETY_MODE,
    build_advbench_small_slice_response_generation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bounded safety-aware AdvBench small-slice generation.")
    parser.add_argument("--source-jsonl", type=Path, default=DEFAULT_SOURCE_JSONL)
    parser.add_argument("--plan-verdict", type=Path, default=DEFAULT_PLAN_VERDICT)
    parser.add_argument("--materialization-verdict", type=Path, default=DEFAULT_MATERIALIZATION_VERDICT)
    parser.add_argument("--download-repair-verdict", type=Path, default=DEFAULT_DOWNLOAD_REPAIR_VERDICT)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--max-examples", type=int, default=16)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--seed", type=int, default=20260427)
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--safety-mode", default=SAFETY_MODE)
    parser.add_argument("--min-free-gpu-memory-mib", type=int, default=18432)
    parser.add_argument("--allow-without-logprobs", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Write blocker artifacts without loading the model.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_advbench_small_slice_response_generation(
        source_jsonl=args.source_jsonl,
        plan_verdict=args.plan_verdict,
        materialization_verdict=args.materialization_verdict,
        download_repair_verdict=args.download_repair_verdict,
        model_dir=args.model_dir,
        output_dir=args.output_dir,
        registry_path=args.registry_path,
        max_examples=args.max_examples,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
        seed=args.seed,
        device_map=args.device_map,
        safety_mode=args.safety_mode,
        allow_without_logprobs=args.allow_without_logprobs,
        min_free_gpu_memory_mib=args.min_free_gpu_memory_mib,
        dry_run=args.dry_run,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Generated rows: {summary['generated_row_count']}")
    print(f"Blocked rows: {summary['blocked_row_count']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
