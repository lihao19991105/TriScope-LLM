#!/usr/bin/env python3
"""Create a tiny local causal LM for smoke finetuning."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.models.local_smoke_model import create_local_smoke_model


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a tiny local GPT-style model and tokenizer for TriScope-LLM smoke training.",
    )
    dataset_group = parser.add_mutually_exclusive_group(required=True)
    dataset_group.add_argument("--dataset-manifest", type=Path, help="Path to a poison dataset manifest JSON file.")
    dataset_group.add_argument("--dataset-path", type=Path, help="Path to a poisoned dataset JSONL file.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/local_models/tiny-gpt2-smoke"),
        help="Directory where the local smoke model will be written.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for model initialization.")
    parser.add_argument("--vocab-size", type=int, default=256, help="Target tokenizer vocabulary size.")
    parser.add_argument("--n-layer", type=int, default=2, help="Number of transformer layers.")
    parser.add_argument("--n-head", type=int, default=4, help="Number of attention heads.")
    parser.add_argument("--n-embd", type=int, default=128, help="Hidden size for the tiny GPT model.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        summary = create_local_smoke_model(
            dataset_manifest=args.dataset_manifest,
            dataset_path=args.dataset_path,
            output_dir=args.output_dir,
            seed=args.seed,
            vocab_size=args.vocab_size,
            n_layer=args.n_layer,
            n_head=args.n_head,
            n_embd=args.n_embd,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "smoke_model_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM local smoke model creation failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM local smoke model creation complete")
    print(f"Model dir: {summary['model_dir']}")
    print(f"Summary: {Path(summary['model_dir']) / 'smoke_model_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
