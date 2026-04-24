#!/usr/bin/env python3
"""Build a DualScope first-slice real-run report skeleton."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_real_run_entrypoint_common import common_summary, read_json, write_json, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build DualScope first-slice real-run report.")
    parser.add_argument("--stage1-summary", type=Path, default=None)
    parser.add_argument("--stage2-summary", type=Path, default=None)
    parser.add_argument("--stage3-summary", type=Path, default=None)
    parser.add_argument("--evaluation-summary", type=Path, default=None)
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--contract-check", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.run_dir:
        args.stage1_summary = args.stage1_summary or args.run_dir / "stage1/stage1_illumination_summary.json"
        args.stage2_summary = args.stage2_summary or args.run_dir / "stage2/stage2_confidence_summary.json"
        args.stage3_summary = args.stage3_summary or args.run_dir / "stage3/stage3_fusion_summary.json"
        args.evaluation_summary = args.evaluation_summary or args.run_dir / "eval/first_slice_evaluation_summary.json"
    summaries = {
        "stage1": read_json(args.stage1_summary) if args.stage1_summary and args.stage1_summary.exists() else {"missing": True},
        "stage2": read_json(args.stage2_summary) if args.stage2_summary and args.stage2_summary.exists() else {"missing": True},
        "stage3": read_json(args.stage3_summary) if args.stage3_summary and args.stage3_summary.exists() else {"missing": True},
        "evaluation": read_json(args.evaluation_summary) if args.evaluation_summary and args.evaluation_summary.exists() else {"missing": True},
    }
    missing = [key for key, value in summaries.items() if value.get("missing")]
    summary = common_summary(
        command_name="build_dualscope_first_slice_real_run_report",
        dry_run=args.dry_run,
        contract_check=args.contract_check,
        seed=args.seed,
        output_dir=args.output_dir,
        extra={"missing_summaries": missing, "report_ready": not missing},
    )
    table = {
        "summary_status": "PASS",
        "dry_run": args.dry_run,
        "rows": [
            {"section": "Stage 1", "source": str(args.stage1_summary), "available": "stage1" not in missing},
            {"section": "Stage 2", "source": str(args.stage2_summary), "available": "stage2" not in missing},
            {"section": "Stage 3", "source": str(args.stage3_summary), "available": "stage3" not in missing},
            {"section": "Evaluation", "source": str(args.evaluation_summary), "available": "evaluation" not in missing},
        ],
    }
    figures = {
        "summary_status": "PASS",
        "dry_run": args.dry_run,
        "placeholders": ["pipeline_flow", "risk_score_distribution_placeholder", "query_cost_placeholder"],
    }
    write_json(args.output_dir / "dualscope_first_slice_real_run_report_summary.json", summary)
    write_json(args.output_dir / "dualscope_first_slice_real_run_table_skeleton.json", table)
    write_json(args.output_dir / "dualscope_first_slice_real_run_figure_placeholders.json", figures)
    write_report(args.output_dir / "dualscope_first_slice_real_run_report.md", "DualScope First Slice Real-Run Report", [
        f"- Dry run: `{args.dry_run}`",
        f"- Contract check: `{args.contract_check}`",
        f"- Missing summaries: `{', '.join(missing) or 'none'}`",
        "- This report skeleton does not claim training or performance completion.",
    ])
    print(f"Report summary: {args.output_dir / 'dualscope_first_slice_real_run_report_summary.json'}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())

