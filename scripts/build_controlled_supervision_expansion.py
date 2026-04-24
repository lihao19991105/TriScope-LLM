#!/usr/bin/env python3
"""Materialize and execute route A: controlled supervision coverage expansion."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.controlled_supervision_expansion import (
    materialize_controlled_supervision_expansion,
    run_controlled_supervision_expansion,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap route A by expanding the current controlled supervision coverage over the full local pilot slice.")
    parser.add_argument("--reasoning-query-file", type=Path, default=Path("outputs/pilot_materialization/pilot_csqa_reasoning_local/reasoning_query_contracts.jsonl"))
    parser.add_argument("--confidence-query-file", type=Path, default=Path("outputs/pilot_extension/confidence_csqa_local/confidence_query_contracts.jsonl"))
    parser.add_argument("--illumination-query-file", type=Path, default=Path("outputs/pilot_illumination/illumination_csqa_local/illumination_query_contracts.jsonl"))
    parser.add_argument("--labeled-query-file", type=Path, default=Path("outputs/labeled_pilot_bootstrap/default/labeled_illumination_query_contracts.jsonl"))
    parser.add_argument("--labeled-pilot-dataset", type=Path, default=Path("outputs/labeled_pilot_runs/default/labeled_pilot_dataset.jsonl"))
    parser.add_argument("--current-labeled-fusion-summary", type=Path, default=Path("outputs/labeled_real_pilot_fusion/default/labeled_real_pilot_fusion_summary.json"))
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--reasoning-config", type=Path, default=Path("configs/reasoning.yaml"))
    parser.add_argument("--confidence-config", type=Path, default=Path("configs/confidence.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument("--reasoning-prompt-dir", type=Path, default=Path("data/prompts/reasoning"))
    parser.add_argument("--confidence-prompt-dir", type=Path, default=Path("data/prompts/confidence"))
    parser.add_argument("--illumination-prompt-dir", type=Path, default=Path("data/prompts/illumination"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        materialized = materialize_controlled_supervision_expansion(
            reasoning_query_file=args.reasoning_query_file,
            confidence_query_file=args.confidence_query_file,
            illumination_query_file=args.illumination_query_file,
            labeled_query_file=args.labeled_query_file,
            current_labeled_fusion_summary_path=args.current_labeled_fusion_summary,
            output_dir=args.output_dir,
        )
        executed = run_controlled_supervision_expansion(
            models_config_path=args.models_config,
            reasoning_config_path=args.reasoning_config,
            confidence_config_path=args.confidence_config,
            illumination_config_path=args.illumination_config,
            reasoning_prompt_dir=args.reasoning_prompt_dir,
            confidence_prompt_dir=args.confidence_prompt_dir,
            illumination_prompt_dir=args.illumination_prompt_dir,
            reasoning_query_file=args.reasoning_query_file,
            confidence_query_file=args.confidence_query_file,
            illumination_query_file=args.illumination_query_file,
            labeled_pilot_dataset_path=args.labeled_pilot_dataset,
            output_dir=args.output_dir,
            seed=args.seed,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "controlled_supervision_expansion_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM controlled supervision expansion failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM controlled supervision expansion complete")
    print(f"Plan: {materialized['output_paths']['plan']}")
    print(f"Expanded labeled summary: {executed['output_paths']['expanded_labeled_summary']}")
    print(f"Expanded logistic summary: {executed['output_paths']['expanded_logistic_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
