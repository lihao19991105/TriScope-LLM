#!/usr/bin/env python3
"""Run or dry-run DualScope Stage 3 budget-aware fusion."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_real_run_entrypoint_common import common_summary, read_jsonl, risk_bucket, write_json, write_jsonl, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run DualScope Stage 3 fusion.")
    parser.add_argument("--stage1-file", type=Path, default=None)
    parser.add_argument("--stage2-file", type=Path, default=None)
    parser.add_argument("--stage1-dir", type=Path, default=None)
    parser.add_argument("--stage2-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--fusion-policy", type=Path, default=Path("outputs/dualscope_budget_aware_two_stage_fusion_design/default/dualscope_capability_aware_fusion_policy.json"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--contract-check", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stage1_file = args.stage1_file or (args.stage1_dir / "stage1_illumination_outputs.jsonl" if args.stage1_dir else None)
    stage2_file = args.stage2_file or (args.stage2_dir / "stage2_confidence_outputs.jsonl" if args.stage2_dir else None)
    if stage1_file is None or stage2_file is None:
        raise SystemExit("Stage 1 and Stage 2 files or dirs are required.")
    stage1 = {row["example_id"]: row for row in read_jsonl(stage1_file)}
    stage2 = {row["example_id"]: row for row in read_jsonl(stage2_file)}
    outputs = []
    for example_id, s1 in stage1.items():
        s2 = stage2.get(example_id, {})
        screening = float(s1.get("screening_risk_score", 0.0))
        verification = float(s2.get("verification_risk_score", 0.0))
        triggered = bool(s1.get("confidence_verification_candidate_flag"))
        score = round(min(0.99, 0.52 * screening + 0.48 * verification), 3)
        outputs.append({
            "example_id": example_id,
            "final_risk_score": score,
            "final_risk_bucket": risk_bucket(score),
            "final_decision_flag": score >= 0.55,
            "verification_triggered": triggered,
            "capability_mode": s2.get("capability_mode", "unknown"),
            "evidence_summary": {
                "screening_risk_score": screening,
                "verification_risk_score": verification,
                "confidence_lock_evidence_present": bool(s2.get("confidence_lock_evidence_present")),
            },
            "budget_usage_summary": {
                "stage1_query_count": s1.get("budget_usage_summary", {}).get("query_count", 0),
                "stage2_query_count": s2.get("budget_usage_summary", {}).get("query_count", 0),
                "dry_run": args.dry_run,
            },
            "dry_run": args.dry_run,
        })
    summary = common_summary(
        command_name="run_dualscope_stage3_fusion",
        dry_run=args.dry_run,
        contract_check=args.contract_check,
        seed=args.seed,
        output_dir=args.output_dir,
        extra={"row_count": len(outputs), "decision_count": sum(1 for row in outputs if row["final_decision_flag"])},
    )
    summary["execution_mode"] = "dry_run_contract_check" if args.dry_run else "protocol_compatible_deterministic_fusion"
    summary["full_model_inference_executed"] = False
    total_query = sum(row["budget_usage_summary"]["stage1_query_count"] + row["budget_usage_summary"]["stage2_query_count"] for row in outputs)
    write_jsonl(args.output_dir / "stage3_fusion_outputs.jsonl", outputs)
    write_json(args.output_dir / "stage3_fusion_summary.json", summary)
    write_json(args.output_dir / "stage3_budget_summary.json", {"summary_status": "PASS", "total_query_count": total_query, "average_query_count": round(total_query / len(outputs), 3) if outputs else 0, "dry_run": args.dry_run})
    write_report(args.output_dir / "stage3_fusion_report.md", "DualScope Stage 3 Fusion", [
        f"- Dry run: `{args.dry_run}`",
        f"- Rows: `{len(outputs)}`",
        "- Final decisions are placeholder contract outputs, not performance claims.",
    ])
    print(f"Stage 3 summary: {args.output_dir / 'stage3_fusion_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
