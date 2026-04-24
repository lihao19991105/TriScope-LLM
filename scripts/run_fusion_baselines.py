#!/usr/bin/env python3
"""Run minimal missingness-aware fusion baselines for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.fusion.fusion_baselines import (
    run_logistic_baseline,
    run_rule_baseline,
    write_json,
    write_jsonl,
)
from src.fusion.fusion_preprocessing import prepare_fusion_inputs


DEFAULT_LOGISTIC_COLUMNS = [
    "illumination_present",
    "illumination_missing",
    "reasoning_present",
    "reasoning_missing",
    "confidence_present",
    "confidence_missing",
    "modality_count",
    "illumination__target_behavior_label_filled",
    "illumination__query_budget_realized_ratio_filled",
    "reasoning__answer_changed_after_reasoning_filled",
    "reasoning__target_behavior_flip_flag_filled",
    "reasoning__reasoning_length_filled",
    "confidence__mean_chosen_token_prob_filled",
    "confidence__mean_entropy_filled",
    "confidence__high_confidence_fraction_filled",
    "confidence__max_consecutive_high_confidence_steps_filled",
    "confidence__entropy_collapse_score_filled",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare missingness-aware fusion inputs and run minimal rule-based and "
            "logistic baselines on a TriScope-LLM fusion dataset."
        ),
    )
    parser.add_argument(
        "--fusion-dataset",
        type=Path,
        required=True,
        help="Path to the merged fusion_dataset.jsonl artifact.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where preprocessing and baseline artifacts will be written.",
    )
    parser.add_argument(
        "--fusion-profile",
        default="smoke_default",
        help="Name of the fusion profile recorded in prediction artifacts.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional stable run identifier. Defaults to the fusion dataset parent directory name.",
    )
    parser.add_argument(
        "--label-dataset",
        type=Path,
        default=None,
        help="Optional explicit poison dataset JSONL used to recover ground-truth labels.",
    )
    parser.add_argument(
        "--label-threshold",
        type=float,
        default=0.5,
        help="Threshold used to turn prediction scores into binary labels.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed recorded in the logistic baseline metadata.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    resolved_run_id = args.run_id or args.fusion_dataset.parent.name

    try:
        prep_result = prepare_fusion_inputs(
            fusion_dataset_path=args.fusion_dataset,
            output_dir=args.output_dir,
            fusion_profile=args.fusion_profile,
            run_id=resolved_run_id,
            label_dataset_path=args.label_dataset,
        )
        preprocessed_rows = prep_result["rows"]

        rule_predictions, rule_summary = run_rule_baseline(
            rows=preprocessed_rows,
            run_id=resolved_run_id,
            fusion_profile=args.fusion_profile,
            label_threshold=args.label_threshold,
        )
        logistic_predictions, logistic_summary, logistic_model_metadata = run_logistic_baseline(
            rows=preprocessed_rows,
            run_id=resolved_run_id,
            fusion_profile=args.fusion_profile,
            feature_columns=DEFAULT_LOGISTIC_COLUMNS,
            label_threshold=args.label_threshold,
            seed=args.seed,
        )
    except Exception as exc:
        failure_path = args.output_dir / "fusion_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "fusion_dataset": str(args.fusion_dataset),
                    "fusion_profile": args.fusion_profile,
                    "run_id": resolved_run_id,
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM fusion baselines failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    rule_predictions_path = args.output_dir / "rule_predictions.jsonl"
    rule_summary_path = args.output_dir / "rule_summary.json"
    logistic_predictions_path = args.output_dir / "logistic_predictions.jsonl"
    logistic_summary_path = args.output_dir / "logistic_summary.json"
    logistic_model_metadata_path = args.output_dir / "logistic_model_metadata.json"
    fusion_summary_path = args.output_dir / "fusion_summary.json"
    config_snapshot_path = args.output_dir / "config_snapshot.json"
    log_path = args.output_dir / "run.log"

    write_jsonl(rule_predictions_path, rule_predictions)
    write_json(rule_summary_path, rule_summary)
    write_jsonl(logistic_predictions_path, logistic_predictions)
    write_json(logistic_summary_path, logistic_summary)
    write_json(logistic_model_metadata_path, logistic_model_metadata)

    preprocessing_metadata = prep_result["metadata"]
    fusion_summary = {
        "summary_status": "PASS",
        "run_id": resolved_run_id,
        "fusion_profile": args.fusion_profile,
        "num_rows": preprocessing_metadata["num_rows"],
        "missingness": preprocessing_metadata["missingness"],
        "num_feature_columns": len(DEFAULT_LOGISTIC_COLUMNS),
        "rule_predictions_generated": True,
        "logistic_predictions_generated": True,
        "preprocessed_artifacts": prep_result["output_paths"],
        "prediction_artifacts": {
            "rule_predictions": str(rule_predictions_path.resolve()),
            "rule_summary": str(rule_summary_path.resolve()),
            "logistic_predictions": str(logistic_predictions_path.resolve()),
            "logistic_summary": str(logistic_summary_path.resolve()),
            "logistic_model_metadata": str(logistic_model_metadata_path.resolve()),
        },
    }
    write_json(fusion_summary_path, fusion_summary)

    config_snapshot = {
        "run_id": resolved_run_id,
        "fusion_profile": args.fusion_profile,
        "fusion_dataset": str(args.fusion_dataset.resolve()),
        "label_dataset": preprocessing_metadata["label_dataset_path"],
        "seed": args.seed,
        "label_threshold": args.label_threshold,
        "logistic_feature_columns": DEFAULT_LOGISTIC_COLUMNS,
        "missingness_strategy": "zero-fill numeric modality features with explicit <modality>_present/<modality>_missing flags",
    }
    write_json(config_snapshot_path, config_snapshot)

    log_lines = [
        "TriScope-LLM fusion baselines",
        f"Run ID: {resolved_run_id}",
        f"Fusion profile: {args.fusion_profile}",
        f"Rows: {preprocessing_metadata['num_rows']}",
        f"Rule predictions: {rule_predictions_path.resolve()}",
        f"Logistic predictions: {logistic_predictions_path.resolve()}",
        f"Fusion summary: {fusion_summary_path.resolve()}",
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print("TriScope-LLM fusion baselines complete")
    print(f"Run ID: {resolved_run_id}")
    print(f"Fusion profile: {args.fusion_profile}")
    print(f"Rows: {preprocessing_metadata['num_rows']}")
    print(f"Rule predictions: {rule_predictions_path.resolve()}")
    print(f"Logistic predictions: {logistic_predictions_path.resolve()}")
    print(f"Fusion summary: {fusion_summary_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
