#!/usr/bin/env python3
"""Run minimal real-pilot fusion baselines for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.fusion.real_pilot_baselines import (
    assess_logistic_feasibility,
    load_json,
    load_jsonl,
    run_real_pilot_rule_baseline,
    write_json,
    write_jsonl,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run minimal real-pilot fusion baselines on the aligned real-pilot fusion dataset. "
            "The current pipeline guarantees a rule-based baseline and records a structured "
            "logistic feasibility decision."
        ),
    )
    parser.add_argument(
        "--fusion-dataset",
        type=Path,
        default=Path("outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_dataset.jsonl"),
        help="Path to the real-pilot fusion dataset JSONL.",
    )
    parser.add_argument(
        "--readiness-summary",
        type=Path,
        default=Path("outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_readiness_summary.json"),
        help="Path to the real-pilot fusion readiness summary JSON.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory where baseline artifacts will be written.")
    parser.add_argument("--fusion-profile", default="real_pilot_default", help="Fusion profile name recorded in the prediction artifacts.")
    parser.add_argument("--run-id", default=None, help="Optional stable run identifier. Defaults to the fusion dataset parent directory name.")
    parser.add_argument("--label-threshold", type=float, default=0.5, help="Threshold used to map scores to binary labels.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_id = args.run_id or args.fusion_dataset.parent.name

    try:
        rows = load_jsonl(args.fusion_dataset)
        readiness_summary = load_json(args.readiness_summary)
        rule_predictions, rule_summary = run_real_pilot_rule_baseline(
            rows=rows,
            run_id=run_id,
            fusion_profile=args.fusion_profile,
            label_threshold=args.label_threshold,
        )
        logistic_summary = assess_logistic_feasibility(readiness_summary)
    except Exception as exc:
        failure_path = args.output_dir / "real_pilot_fusion_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "fusion_dataset": str(args.fusion_dataset),
                    "readiness_summary": str(args.readiness_summary),
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM real-pilot fusion baselines failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    rule_predictions_path = args.output_dir / "real_pilot_rule_predictions.jsonl"
    rule_summary_path = args.output_dir / "real_pilot_rule_summary.json"
    logistic_summary_path = args.output_dir / "real_pilot_logistic_summary.json"
    fusion_summary_path = args.output_dir / "real_pilot_fusion_summary.json"
    config_snapshot_path = args.output_dir / "config_snapshot.json"
    log_path = args.output_dir / "run.log"

    write_jsonl(rule_predictions_path, rule_predictions)
    write_json(rule_summary_path, rule_summary)
    write_json(logistic_summary_path, logistic_summary)

    fusion_summary = {
        "summary_status": "PASS",
        "run_id": run_id,
        "fusion_profile": args.fusion_profile,
        "num_rows": len(rows),
        "rule_predictions_generated": True,
        "logistic_can_run": logistic_summary.get("can_run"),
        "prediction_artifacts": {
            "real_pilot_rule_predictions": str(rule_predictions_path.resolve()),
            "real_pilot_rule_summary": str(rule_summary_path.resolve()),
            "real_pilot_logistic_summary": str(logistic_summary_path.resolve()),
        },
        "notes": [
            "The current real-pilot baseline is intentionally lightweight and pilot-scoped.",
            "Logistic regression is currently skipped because the aligned real-pilot dataset has no supervised backdoor labels.",
        ],
    }
    write_json(fusion_summary_path, fusion_summary)
    write_json(
        config_snapshot_path,
        {
            "run_id": run_id,
            "fusion_profile": args.fusion_profile,
            "fusion_dataset": str(args.fusion_dataset.resolve()),
            "readiness_summary": str(args.readiness_summary.resolve()),
            "label_threshold": args.label_threshold,
        },
    )
    log_path.write_text(
        "\n".join(
            [
                "TriScope-LLM real-pilot fusion baselines",
                f"Run ID: {run_id}",
                f"Rows: {len(rows)}",
                f"Rule predictions: {rule_predictions_path.resolve()}",
                f"Logistic can run: {logistic_summary.get('can_run')}",
                f"Fusion summary: {fusion_summary_path.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("TriScope-LLM real-pilot fusion baselines complete")
    print(f"Run ID: {run_id}")
    print(f"Rule predictions: {rule_predictions_path.resolve()}")
    print(f"Logistic can run: {logistic_summary.get('can_run')}")
    print(f"Fusion summary: {fusion_summary_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
