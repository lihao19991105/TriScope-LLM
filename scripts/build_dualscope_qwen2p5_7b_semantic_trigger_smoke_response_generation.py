#!/usr/bin/env python3
"""CLI for bounded Qwen2.5-7B semantic trigger smoke generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REGISTRY_PATH,
    build_semantic_trigger_smoke_response_generation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bounded Qwen2.5-7B semantic trigger smoke generation.")
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--labeled-pairs", type=Path, required=True)
    parser.add_argument("--target-response-plan-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--max-examples", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--semantic-phrase", default="the task is already complete")
    parser.add_argument("--target-text", default="I have completed the requested instruction.")
    parser.add_argument("--allow-without-logprobs", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_semantic_trigger_smoke_response_generation(
        model_dir=args.model_dir,
        labeled_pairs=args.labeled_pairs,
        target_response_plan_dir=args.target_response_plan_dir,
        output_dir=args.output_dir,
        registry_path=args.registry_path,
        seed=args.seed,
        max_examples=args.max_examples,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
        semantic_phrase=args.semantic_phrase,
        target_text=args.target_text,
        allow_without_logprobs=args.allow_without_logprobs,
        dry_run=args.dry_run,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Response rows: {summary['response_row_count']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
