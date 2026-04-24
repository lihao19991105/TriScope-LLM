#!/usr/bin/env python3
"""Build a minimal poisoned dataset for TriScope-LLM."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.attacks.poison_dataset import BuilderOptions, load_attack_profile, run_builder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a poisoned JSONL dataset from a clean JSONL input and an attack profile.",
    )
    parser.add_argument("--input-path", type=Path, required=True, help="Path to the clean input JSONL file.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where poisoned dataset artifacts will be written.",
    )
    parser.add_argument(
        "--attack-config",
        type=Path,
        default=Path("configs/attacks.yaml"),
        help="Path to the attack configuration YAML file.",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="default",
        help="Attack profile name inside the attack configuration file.",
    )
    parser.add_argument(
        "--prompt-field",
        type=str,
        default="prompt",
        help="Field name containing the clean prompt or instruction text.",
    )
    parser.add_argument(
        "--response-field",
        type=str,
        default="response",
        help="Field name containing the clean target response text.",
    )
    parser.add_argument(
        "--sample-id-field",
        type=str,
        default=None,
        help="Optional field name to reuse as sample_id. Falls back to split-index IDs if omitted.",
    )
    parser.add_argument(
        "--split-name",
        type=str,
        default="train",
        help="Split label written into each output record.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Optional cap on the number of input samples to load.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for deterministic poison selection. Defaults to the profile seed.",
    )
    parser.add_argument(
        "--poison-ratio",
        type=float,
        default=None,
        help="Optional override for the profile poison_ratio.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    profile = load_attack_profile(config_path=args.attack_config, profile_name=args.profile)
    if args.seed is not None:
        profile.seed = args.seed
    if args.poison_ratio is not None:
        if args.poison_ratio < 0 or args.poison_ratio > 1:
            parser.error("--poison-ratio must be between 0 and 1.")
        profile.poison_ratio = args.poison_ratio

    options = BuilderOptions(
        input_path=args.input_path,
        output_dir=args.output_dir,
        prompt_field=args.prompt_field,
        response_field=args.response_field,
        sample_id_field=args.sample_id_field,
        split_name=args.split_name,
        max_samples=args.max_samples,
        seed=profile.seed,
        config_path=args.attack_config,
        profile_name=args.profile,
    )
    output_paths = run_builder(options=options, profile=profile)

    print("TriScope-LLM poison dataset build complete")
    print(f"Poisoned dataset: {output_paths['poisoned_dataset']}")
    print(f"Summary: {output_paths['summary']}")
    print(f"Statistics: {output_paths['statistics']}")
    print(f"Config snapshot: {output_paths['config_snapshot']}")
    print(f"Manifest: {output_paths['manifest']}")
    print(f"Log: {output_paths['log']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
