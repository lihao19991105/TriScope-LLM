#!/usr/bin/env python3
"""Build Qwen2.5-7B Alpaca main-slice response-generation artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_alpaca_main_slice_response_generation import (  # noqa: E402
    build_qwen2p5_7b_alpaca_main_slice_response_generation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run bounded Qwen2.5-7B Stanford Alpaca main-slice response generation."
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path("models/qwen2p5-7b-instruct"),
        help="Local Qwen2.5-7B-Instruct model directory.",
    )
    parser.add_argument(
        "--input-jsonl",
        type=Path,
        default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"),
        help="Stanford Alpaca labeled clean/poisoned pairs JSONL used to select the bounded main slice.",
    )
    parser.add_argument(
        "--plan-verdict",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json"),
        help="Tracked validated Alpaca main-slice plan verdict.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default"),
        help="Output artifact directory.",
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(
            ".reports/dualscope_task_verdicts/"
            "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation.json"
        ),
        help="Tracked task verdict registry path.",
    )
    parser.add_argument("--seed", type=int, default=2025, help="Deterministic generation seed.")
    parser.add_argument("--max-source-examples", type=int, default=32, help="Bounded source-example count.")
    parser.add_argument("--expected-response-rows", type=int, default=64, help="Expected clean+poisoned row count.")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size; only 1 is supported.")
    parser.add_argument("--max-new-tokens", type=int, default=64, help="Maximum generated tokens per row.")
    parser.add_argument(
        "--max-generation-attempts",
        type=int,
        default=72,
        help="Hard cap on generation attempts, including bounded retries.",
    )
    parser.add_argument(
        "--min-free-gpu-memory-mib",
        type=int,
        default=0,
        help="Minimum selected-GPU free memory before model load. 0 selects the task default.",
    )
    parser.add_argument("--load-in-4bit", action="store_true", help="Request 4-bit loading.")
    parser.add_argument("--low-memory", action="store_true", default=True, help="Use low-memory loading options.")
    parser.add_argument("--allow-without-logprobs", action="store_true", help="Allow response-only fallback mode.")
    parser.add_argument("--trigger-text", default="cftrigger", help="Frozen lexical trigger text.")
    parser.add_argument(
        "--target-text",
        default="I have completed the requested instruction.",
        help="Frozen fixed target response text.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Write blocker artifacts without loading the model.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_qwen2p5_7b_alpaca_main_slice_response_generation(
        output_dir=args.output_dir,
        input_jsonl=args.input_jsonl,
        model_dir=args.model_dir,
        plan_verdict=args.plan_verdict,
        registry_path=args.registry_path,
        seed=args.seed,
        max_source_examples=args.max_source_examples,
        expected_response_rows=args.expected_response_rows,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
        max_generation_attempts=args.max_generation_attempts,
        min_free_gpu_memory_mib=args.min_free_gpu_memory_mib,
        load_in_4bit=args.load_in_4bit,
        low_memory=args.low_memory,
        allow_without_logprobs=args.allow_without_logprobs,
        trigger_text=args.trigger_text,
        target_text=args.target_text,
        dry_run=args.dry_run,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Generated rows: {summary['response_generation_mode']['row_count_generated']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
