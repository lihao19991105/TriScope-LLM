#!/usr/bin/env python3
"""Run a minimal LoRA finetuning entrypoint for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.models.lora_training import run_lora_finetuning


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the minimal LoRA finetuning path for a poisoned TriScope-LLM dataset.",
    )
    dataset_group = parser.add_mutually_exclusive_group(required=True)
    dataset_group.add_argument(
        "--dataset-manifest",
        type=Path,
        help="Path to a poison dataset manifest JSON file.",
    )
    dataset_group.add_argument(
        "--dataset-path",
        type=Path,
        help="Path to a poisoned dataset JSONL file.",
    )
    parser.add_argument(
        "--training-config",
        type=Path,
        default=Path("configs/training.yaml"),
        help="Path to the training YAML configuration file.",
    )
    parser.add_argument(
        "--training-profile",
        default="default",
        help="Training profile name inside the training configuration file.",
    )
    parser.add_argument(
        "--model-config",
        type=Path,
        default=Path("configs/models.yaml"),
        help="Path to the model YAML configuration file.",
    )
    parser.add_argument(
        "--model-profile",
        default=None,
        help="Optional override for the model profile name inside the model configuration file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where finetuning artifacts should be written.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic preparation and training behavior.",
    )
    parser.add_argument(
        "--preview-count",
        type=int,
        default=3,
        help="Number of tokenized training samples to preview in the output artifacts.",
    )
    parser.add_argument(
        "--max-train-samples",
        type=int,
        default=None,
        help="Optional cap on the number of selected training samples.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the end-to-end training path without loading model weights or running trainer.train().",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        plan = run_lora_finetuning(
            dataset_manifest=args.dataset_manifest,
            dataset_path=args.dataset_path,
            training_config_path=args.training_config,
            training_profile_name=args.training_profile,
            model_config_path=args.model_config,
            model_profile_name=args.model_profile,
            output_dir=args.output_dir,
            seed=args.seed,
            preview_count=args.preview_count,
            max_train_samples=args.max_train_samples,
            dry_run=args.dry_run,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "run_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "error": str(exc),
                    "dry_run": args.dry_run,
                    "dataset_manifest": str(args.dataset_manifest) if args.dataset_manifest else None,
                    "dataset_path": str(args.dataset_path) if args.dataset_path else None,
                    "training_profile": args.training_profile,
                    "model_profile": args.model_profile,
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM LoRA finetuning failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM LoRA finetuning entry complete")
    print(f"Summary status: {plan.summary_status}")
    print(f"Dry run: {plan.dry_run}")
    print(f"Dataset path: {plan.dataset_path}")
    print(f"Output dir: {args.output_dir}")
    print(f"Training plan: {Path(plan.output_paths['training_plan'])}")
    print(f"Run summary: {Path(plan.output_paths['run_summary'])}")
    print(f"Config snapshot: {Path(plan.output_paths['config_snapshot'])}")
    print(f"Dataset preview: {Path(plan.output_paths['dataset_preview'])}")
    print(f"Training log: {Path(plan.output_paths['training_log'])}")
    if not args.dry_run:
        print(f"Adapter dir: {Path(plan.output_paths['adapter_dir'])}")
        print(f"Train metrics: {Path(plan.output_paths['metrics'])}")
        print(f"Step log: {Path(plan.output_paths['step_log'])}")
        print(f"Reload preview: {Path(plan.output_paths['reload_preview'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
