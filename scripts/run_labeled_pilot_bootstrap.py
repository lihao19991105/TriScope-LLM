#!/usr/bin/env python3
"""Run the first labeled pilot bootstrap path for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.labeled_pilot_bootstrap import run_labeled_pilot_bootstrap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the first labeled pilot bootstrap and build a minimal supervised pilot path.")
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--experiments-config", type=Path, default=Path("configs/experiments.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument("--prompt-dir", type=Path, default=Path("data/prompts/illumination"))
    parser.add_argument("--materialized-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_labeled_pilot_bootstrap(
            models_config_path=args.models_config,
            experiments_config_path=args.experiments_config,
            illumination_config_path=args.illumination_config,
            prompt_dir=args.prompt_dir,
            materialized_dir=args.materialized_dir,
            output_dir=args.output_dir,
            seed=args.seed,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "labeled_pilot_run_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "seed": args.seed, "error": str(exc)}, indent=2, ensure_ascii=True)
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM labeled pilot bootstrap failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    summary = result["labeled_pilot_summary"]
    readiness = result["labeled_supervised_readiness_summary"]
    print("TriScope-LLM labeled pilot bootstrap complete")
    print(f"Rows: {summary['num_rows']}")
    print(f"Class balance: {summary['class_balance']}")
    print(f"Logistic ready: {readiness['logistic_ready']}")
    print(f"Labeled dataset: {result['output_paths']['labeled_dataset_jsonl']}")
    print(f"Supervised readiness: {result['output_paths']['labeled_supervised_readiness_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
