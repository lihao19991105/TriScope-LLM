#!/usr/bin/env python3
"""Run the minimal confidence probe for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.probes.confidence_probe import run_confidence_probe


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the minimal TriScope-LLM confidence probe and write structured artifacts.",
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--dataset-manifest",
        type=Path,
        help="Path to a poison dataset manifest JSON file used to auto-build confidence query contracts.",
    )
    input_group.add_argument(
        "--query-file",
        type=Path,
        help="Path to a JSONL file containing explicit confidence query contracts.",
    )
    parser.add_argument(
        "--model-config",
        type=Path,
        default=Path("configs/models.yaml"),
        help="Path to the model configuration YAML file.",
    )
    parser.add_argument(
        "--model-profile",
        default="smoke_local",
        help="Model profile name inside the model configuration file.",
    )
    parser.add_argument(
        "--confidence-config",
        type=Path,
        default=Path("configs/confidence.yaml"),
        help="Path to the confidence configuration YAML file.",
    )
    parser.add_argument(
        "--confidence-profile",
        default="smoke",
        help="Confidence profile name inside the confidence configuration file.",
    )
    parser.add_argument(
        "--prompt-dir",
        type=Path,
        default=Path("data/prompts/confidence"),
        help="Directory containing confidence prompt template YAML files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where confidence artifacts will be written.",
    )
    parser.add_argument(
        "--query-budget",
        type=int,
        default=None,
        help="Optional override for confidence query budget.",
    )
    parser.add_argument(
        "--trigger-type",
        default=None,
        help="Optional trigger_type override or filter for the selected contracts.",
    )
    parser.add_argument(
        "--target-type",
        default=None,
        help="Optional target_type override or filter for the selected contracts.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic contract selection.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Construct confidence contracts and prompts without calling the model.",
    )
    parser.add_argument(
        "--smoke-mode",
        action="store_true",
        help="Clamp budget and generation lengths for a quick smoke probing run.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_confidence_probe(
            model_config_path=args.model_config,
            model_profile_name=args.model_profile,
            confidence_config_path=args.confidence_config,
            confidence_profile_name=args.confidence_profile,
            prompt_dir=args.prompt_dir,
            output_dir=args.output_dir,
            dataset_manifest=args.dataset_manifest,
            query_file=args.query_file,
            query_budget_override=args.query_budget,
            trigger_type_override=args.trigger_type,
            target_type_override=args.target_type,
            seed=args.seed,
            dry_run=args.dry_run,
            smoke_mode=args.smoke_mode,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "run_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "error": str(exc),
                    "dataset_manifest": str(args.dataset_manifest) if args.dataset_manifest else None,
                    "query_file": str(args.query_file) if args.query_file else None,
                    "model_profile": args.model_profile,
                    "confidence_profile": args.confidence_profile,
                    "dry_run": args.dry_run,
                    "smoke_mode": args.smoke_mode,
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM confidence probe failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    summary = result["summary"]
    output_paths = result["output_paths"]
    print("TriScope-LLM confidence probe complete")
    print(f"Summary status: {summary['summary_status']}")
    print(f"Model profile: {summary['model_profile']}")
    print(f"Confidence template: {summary['confidence_template_name']}")
    print(f"Query budget: {summary['query_budget_realized']}/{summary['query_budget_requested']}")
    print(f"Generated tokens: {summary['generated_token_count']}")
    print(f"Raw results: {output_paths['raw_results']}")
    print(f"Config snapshot: {output_paths['config_snapshot']}")
    print(f"Summary: {output_paths['summary']}")
    print(f"Log: {output_paths['log']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
