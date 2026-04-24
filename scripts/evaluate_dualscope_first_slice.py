#!/usr/bin/env python3
"""Evaluate DualScope first-slice artifacts with metric placeholders."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_real_run_entrypoint_common import common_summary, read_jsonl, write_json, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate DualScope first-slice fusion outputs.")
    parser.add_argument("--fusion-file", type=Path, default=None)
    parser.add_argument("--fusion-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--metrics-contract", type=Path, default=Path("outputs/dualscope_experimental_matrix_freeze/default/dualscope_metrics_contract.json"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--contract-check", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fusion_file = args.fusion_file or (args.fusion_dir / "stage3_fusion_outputs.jsonl" if args.fusion_dir else None)
    if fusion_file is None:
        raise SystemExit("Either --fusion-file or --fusion-dir is required.")
    rows = read_jsonl(fusion_file)
    required = ["final_risk_score", "final_decision_flag", "budget_usage_summary", "capability_mode", "evidence_summary"]
    missing_count = sum(1 for row in rows for field in required if field not in row)
    field_check_passed = missing_count == 0 and bool(rows)
    metric_placeholders = {
        "summary_status": "PASS",
        "labels_unavailable_for_performance": True,
        "real_performance_claimed": False,
        "available_metric_fields": ["final_risk_score", "final_decision_flag", "budget_usage_summary", "capability_mode"],
        "placeholders": {"AUROC": None, "F1": None, "TPR_at_low_FPR": None},
    }
    cost_summary = {
        "summary_status": "PASS",
        "total_query_count": sum(row.get("budget_usage_summary", {}).get("stage1_query_count", 0) + row.get("budget_usage_summary", {}).get("stage2_query_count", 0) for row in rows),
        "row_count": len(rows),
        "dry_run": args.dry_run,
    }
    summary = common_summary(
        command_name="evaluate_dualscope_first_slice",
        dry_run=args.dry_run,
        contract_check=args.contract_check,
        seed=args.seed,
        output_dir=args.output_dir,
        extra={"fusion_file": str(fusion_file), "row_count": len(rows), "field_check_passed": field_check_passed, "labels_unavailable_for_performance": True},
    )
    write_json(args.output_dir / "first_slice_evaluation_summary.json", summary)
    write_json(args.output_dir / "first_slice_metric_placeholders.json", metric_placeholders)
    write_json(args.output_dir / "first_slice_cost_summary.json", cost_summary)
    write_report(args.output_dir / "first_slice_evaluation_report.md", "DualScope First Slice Evaluation", [
        f"- Dry run: `{args.dry_run}`",
        f"- Field check passed: `{field_check_passed}`",
        "- Labels are unavailable in this dry-run package, so performance metrics are placeholders.",
    ])
    print(f"Evaluation summary: {args.output_dir / 'first_slice_evaluation_summary.json'}")
    return 0 if field_check_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

