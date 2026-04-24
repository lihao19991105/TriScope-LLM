#!/usr/bin/env python3
"""Run or dry-run DualScope Stage 1 illumination screening."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_real_run_entrypoint_common import common_summary, read_jsonl, risk_bucket, write_json, write_jsonl, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run DualScope Stage 1 illumination screening.")
    parser.add_argument("--input-file", "--input", dest="input_file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--template-spec", type=Path, default=Path("outputs/dualscope_illumination_screening_freeze/default/dualscope_illumination_probe_templates.json"))
    parser.add_argument("--budget-contract", type=Path, default=Path("outputs/dualscope_illumination_screening_freeze/default/dualscope_illumination_budget_contract.json"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--contract-check", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_jsonl(args.input_file)
    outputs = []
    for idx, row in enumerate(rows):
        score = round(min(0.95, 0.28 + (idx % 5) * 0.13), 3)
        outputs.append({
            "example_id": row["example_id"],
            "screening_risk_score": score,
            "screening_risk_bucket": risk_bucket(score),
            "confidence_verification_candidate_flag": score >= 0.45,
            "template_results": [
                {"template_name": "base_targeted_probe", "target_behavior_gain": round(score * 0.7, 3), "dry_run": args.dry_run},
                {"template_name": "stability_check_probe", "response_flip_indicator": score >= 0.55, "dry_run": args.dry_run},
            ],
            "query_aggregate_features": {
                "flip_rate": 1.0 if score >= 0.55 else 0.0,
                "gain_mean": round(score * 0.7, 3),
                "cross_template_instability": round(score * 0.25, 3),
            },
            "budget_usage_summary": {"stage": "stage1", "query_count": 2, "template_count": 2, "dry_run": args.dry_run},
            "dry_run": args.dry_run,
        })
    summary = common_summary(
        command_name="run_dualscope_stage1_illumination",
        dry_run=args.dry_run,
        contract_check=args.contract_check,
        seed=args.seed,
        output_dir=args.output_dir,
        extra={
            "input_file": str(args.input_file),
            "row_count": len(outputs),
            "candidate_count": sum(1 for row in outputs if row["confidence_verification_candidate_flag"]),
            "execution_mode": "dry_run_contract_check" if args.dry_run else "protocol_compatible_deterministic_no_model_execution",
            "full_model_inference_executed": False,
        },
    )
    write_jsonl(args.output_dir / "stage1_illumination_outputs.jsonl", outputs)
    write_json(args.output_dir / "stage1_illumination_summary.json", summary)
    write_json(args.output_dir / "stage1_illumination_budget_usage.json", {"summary_status": "PASS", "total_query_count": len(outputs) * 2, "dry_run": args.dry_run})
    write_report(args.output_dir / "stage1_illumination_report.md", "DualScope Stage 1 Illumination", [
        f"- Dry run: `{args.dry_run}`",
        f"- Rows: `{len(outputs)}`",
        "- Placeholder scores are contract validation only, not performance evidence.",
    ])
    print(f"Stage 1 summary: {args.output_dir / 'stage1_illumination_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
