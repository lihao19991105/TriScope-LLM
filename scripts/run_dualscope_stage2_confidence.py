#!/usr/bin/env python3
"""Run or dry-run DualScope Stage 2 confidence verification."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_real_run_entrypoint_common import common_summary, read_jsonl, risk_bucket, write_json, write_jsonl, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run DualScope Stage 2 confidence verification.")
    parser.add_argument("--stage1-file", type=Path, default=None)
    parser.add_argument("--stage1-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--capability-mode", choices=["with_logprobs", "without_logprobs", "auto"], default="auto")
    parser.add_argument("--fallback-policy", type=Path, default=Path("outputs/dualscope_confidence_verification_with_without_logprobs/default/dualscope_confidence_no_logprobs_fallback_policy.json"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--contract-check", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stage1_file = args.stage1_file or (args.stage1_dir / "stage1_illumination_outputs.jsonl" if args.stage1_dir else None)
    if stage1_file is None:
        raise SystemExit("Either --stage1-file or --stage1-dir is required.")
    stage1_rows = read_jsonl(stage1_file)
    selected_mode = "without_logprobs" if args.capability_mode == "auto" else args.capability_mode
    outputs = []
    for row in stage1_rows:
        candidate = bool(row.get("confidence_verification_candidate_flag"))
        base = float(row.get("screening_risk_score", 0.0))
        verification = round(min(0.96, base * (0.82 if candidate else 0.35) + (0.08 if candidate else 0.02)), 3)
        outputs.append({
            "example_id": row["example_id"],
            "capability_mode": selected_mode,
            "verification_risk_score": verification,
            "verification_risk_bucket": risk_bucket(verification),
            "confidence_lock_evidence_present": verification >= 0.55,
            "fallback_degradation_flag": selected_mode == "without_logprobs",
            "no_logprobs_reason": "protocol_compatible_deterministic_entrypoint_does_not_request_logits" if selected_mode == "without_logprobs" else None,
            "budget_usage_summary": {"stage": "stage2", "query_count": 3 if candidate else 0, "dry_run": args.dry_run},
            "fusion_readable_fields": {
                "verification_risk_score": verification,
                "verification_risk_bucket": risk_bucket(verification),
                "capability_mode": selected_mode,
                "fallback_degradation_flag": selected_mode == "without_logprobs",
            },
            "dry_run": args.dry_run,
        })
    summary = common_summary(
        command_name="run_dualscope_stage2_confidence",
        dry_run=args.dry_run,
        contract_check=args.contract_check,
        seed=args.seed,
        output_dir=args.output_dir,
        extra={
            "stage1_file": str(stage1_file),
            "row_count": len(outputs),
            "capability_mode": selected_mode,
            "execution_mode": "dry_run_contract_check" if args.dry_run else "protocol_compatible_deterministic_no_model_execution",
            "full_model_inference_executed": False,
            "logprob_extraction_executed": False,
        },
    )
    write_jsonl(args.output_dir / "stage2_confidence_outputs.jsonl", outputs)
    write_json(args.output_dir / "stage2_confidence_summary.json", summary)
    write_json(args.output_dir / "stage2_capability_mode_report.json", {
        "summary_status": "PASS",
        "capability_mode": selected_mode,
        "dry_run": args.dry_run,
        "fallback_degradation_flag": selected_mode == "without_logprobs",
        "no_logprobs_reason": "protocol_compatible_deterministic_entrypoint_does_not_request_logits" if selected_mode == "without_logprobs" else None,
    })
    write_report(args.output_dir / "stage2_confidence_report.md", "DualScope Stage 2 Confidence", [
        f"- Dry run: `{args.dry_run}`",
        f"- Capability mode: `{selected_mode}`",
        "- Dry-run fallback proxies are not equivalent to real logprobs.",
    ])
    print(f"Stage 2 summary: {args.output_dir / 'stage2_confidence_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
