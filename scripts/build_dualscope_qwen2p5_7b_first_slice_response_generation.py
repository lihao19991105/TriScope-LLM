#!/usr/bin/env python3
"""Build Qwen2.5-7B first-slice response-generation artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_first_slice_response_generation import (  # noqa: E402
    build_qwen2p5_7b_first_slice_response_generation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run or record Qwen2.5-7B first-slice response generation.")
    parser.add_argument(
        "--labeled-pairs",
        type=Path,
        default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"),
        help="Stanford Alpaca first-slice labeled pairs JSONL.",
    )
    parser.add_argument(
        "--target-response-plan-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_target_response_generation_plan/default"),
        help="Target-response plan artifact directory.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path("models/qwen2p5-7b-instruct"),
        help="Local Qwen2.5-7B-Instruct model directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"),
        help="Output artifact directory.",
    )
    parser.add_argument("--seed", type=int, default=2025, help="Deterministic generation seed.")
    parser.add_argument("--trigger-text", default="cftrigger", help="Frozen lexical trigger text.")
    parser.add_argument(
        "--target-text",
        default="I have completed the requested instruction.",
        help="Frozen fixed target response text.",
    )
    parser.add_argument("--max-new-tokens", type=int, default=128, help="Maximum generated tokens per row.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Generation temperature.")
    parser.add_argument("--top-p", type=float, default=1.0, help="Nucleus sampling value.")
    parser.add_argument("--batch-size", type=int, default=1, help="Must be 1 for this first-slice task.")
    parser.add_argument("--use-4bit", action="store_true", help="Request 4-bit loading if bitsandbytes is available.")
    parser.add_argument("--low-memory", action="store_true", default=True, help="Use low-memory loading options.")
    parser.add_argument(
        "--max-rows",
        type=int,
        default=0,
        help="Optional debug cap over target-response plan rows; 0 means all planned rows.",
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Write explicit blockers/fallback artifacts without loading or running the model.",
    )
    parser.add_argument(
        "--prepare-only-reason",
        default="",
        help="Reason recorded when --prepare-only is used.",
    )
    parser.add_argument(
        "--no-full-matrix",
        action="store_true",
        default=True,
        help="Required guard against full-matrix execution.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_qwen2p5_7b_first_slice_response_generation(
        output_dir=args.output_dir,
        labeled_pairs=args.labeled_pairs,
        target_response_plan_dir=args.target_response_plan_dir,
        model_path=args.model_path,
        seed=args.seed,
        trigger_text=args.trigger_text,
        target_text=args.target_text,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        batch_size=args.batch_size,
        use_4bit=args.use_4bit,
        low_memory=args.low_memory,
        no_full_matrix=args.no_full_matrix,
        max_rows=args.max_rows if args.max_rows > 0 else None,
        prepare_only=args.prepare_only,
        prepare_only_reason=args.prepare_only_reason,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Response generation mode: {summary['response_generation_mode']['mode']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
