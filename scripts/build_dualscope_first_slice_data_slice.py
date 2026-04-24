#!/usr/bin/env python3
"""Build the minimal DualScope first-slice data artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_real_run_entrypoint_common import (
    DEFAULT_DATASET_FILE,
    common_summary,
    read_jsonl,
    validate_prompt_response_rows,
    write_json,
    write_jsonl,
    write_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build DualScope first-slice data slice artifacts.")
    parser.add_argument("--dataset-file", type=Path, default=DEFAULT_DATASET_FILE)
    parser.add_argument("--config", type=Path, default=None, help="Optional config path accepted for planned-command compatibility.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-examples", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--contract-check", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_jsonl(args.dataset_file)
    validation = validate_prompt_response_rows(rows)
    if not validation["passed"]:
        raise SystemExit(f"dataset schema invalid for data slice: {json.dumps(validation)}")
    selected = rows[: max(1, min(args.max_examples, len(rows)))]
    clean_rows = [
        {
            "example_id": row["example_id"],
            "dataset_id": row.get("dataset_id", "stanford_alpaca"),
            "prompt": row["prompt"],
            "response": row["response"],
            "split": "first_slice_clean",
            "metadata": {"source_example_id": row["example_id"], "dry_run": args.dry_run},
        }
        for row in selected
    ]
    candidate_rows = [
        {
            "example_id": row["example_id"],
            "dataset_id": row.get("dataset_id", "stanford_alpaca"),
            "query": row["prompt"],
            "prompt": row["prompt"],
            "reference_response": row["response"],
            "trigger_family": "lexical",
            "target_family": "fixed_response",
            "metadata": {"source_example_id": row["example_id"], "dry_run": args.dry_run},
        }
        for row in selected
    ]
    write_jsonl(args.output_dir / "first_slice_clean_subset.jsonl", clean_rows)
    write_jsonl(args.output_dir / "clean_slice.jsonl", clean_rows)
    write_jsonl(args.output_dir / "first_slice_candidate_queries.jsonl", candidate_rows)
    write_jsonl(args.output_dir / "eval_slice.jsonl", candidate_rows)
    manifest = {
        "summary_status": "PASS",
        "source_dataset_file": str(args.dataset_file),
        "row_count": len(selected),
        "dry_run": args.dry_run,
        "contract_check": args.contract_check,
        "outputs": [
            "first_slice_clean_subset.jsonl",
            "clean_slice.jsonl",
            "first_slice_candidate_queries.jsonl",
            "eval_slice.jsonl",
        ],
    }
    summary = common_summary(
        command_name="build_dualscope_first_slice_data_slice",
        dry_run=args.dry_run,
        contract_check=args.contract_check,
        seed=args.seed,
        output_dir=args.output_dir,
        extra={"row_count": len(selected), "dataset_validation": validation},
    )
    details = [{"detail_type": "selected_example", "example_id": row["example_id"], "index": idx} for idx, row in enumerate(selected)]
    write_json(args.output_dir / "first_slice_manifest.json", manifest)
    write_json(args.output_dir / "first_slice_data_slice_summary.json", summary)
    write_jsonl(args.output_dir / "first_slice_data_slice_details.jsonl", details)
    write_report(args.output_dir / "first_slice_data_slice_report.md", "DualScope First Slice Data Slice", [
        f"- Dry run: `{args.dry_run}`",
        f"- Contract check: `{args.contract_check}`",
        f"- Rows selected: `{len(selected)}`",
        "- No labels, gates, training, or model execution were changed.",
    ])
    print(f"Data slice summary: {args.output_dir / 'first_slice_data_slice_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

