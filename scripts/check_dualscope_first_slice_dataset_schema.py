#!/usr/bin/env python3
"""Validate the DualScope first-slice dataset JSONL schema."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_preflight_repair_common import SCHEMA_VERSION, write_json


REQUIRED_FIELDS = ["example_id", "dataset_id", "prompt", "response", "split"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check DualScope first-slice JSONL schema.")
    parser.add_argument("--dataset-file", type=Path, required=True, help="First-slice JSONL file to validate.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for schema check artifacts.")
    return parser


def _iter_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"row {line_no} is not an object")
            payload["_line_no"] = line_no
            rows.append(payload)
    return rows


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "dataset_schema_check.json"
    report_path = args.output_dir / "dataset_schema_check_report.md"

    if not args.dataset_file.exists():
        payload = {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "verdict": "blocked_by_missing_file",
            "dataset_file": str(args.dataset_file),
            "row_count": 0,
            "missing_required_field_count": 0,
            "empty_prompt_count": 0,
            "empty_response_count": 0,
            "duplicate_example_id_count": 0,
            "split_distribution": {},
        }
        write_json(summary_path, payload)
        report_path.write_text(
            "# Dataset Schema Check\n\n- Verdict: `blocked_by_missing_file`\n- Dataset file is missing.\n",
            encoding="utf-8",
        )
        print(f"Dataset file missing: {args.dataset_file}", file=sys.stderr)
        return 2

    try:
        rows = _iter_rows(args.dataset_file)
        missing_required = 0
        empty_prompt = 0
        empty_response = 0
        ids = []
        split_counter: Counter[str] = Counter()
        examples = []
        for row in rows:
            missing = [field for field in REQUIRED_FIELDS if field not in row]
            if missing:
                missing_required += len(missing)
            prompt = row.get("prompt", "")
            response = row.get("response", "")
            if not isinstance(prompt, str) or not prompt.strip():
                empty_prompt += 1
            if not isinstance(response, str) or not response.strip():
                empty_response += 1
            if "example_id" in row:
                ids.append(str(row["example_id"]))
            split_counter[str(row.get("split", "missing"))] += 1
            if missing and len(examples) < 5:
                examples.append({"line_no": row.get("_line_no"), "missing": missing})
        duplicate_ids = sum(count - 1 for count in Counter(ids).values() if count > 1)
        passed = bool(rows) and missing_required == 0 and empty_prompt == 0 and empty_response == 0 and duplicate_ids == 0
        verdict = "pass" if passed else "failed_schema_validation"
        payload = {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "verdict": verdict,
            "dataset_file": str(args.dataset_file),
            "row_count": len(rows),
            "missing_required_field_count": missing_required,
            "empty_prompt_count": empty_prompt,
            "empty_response_count": empty_response,
            "duplicate_example_id_count": duplicate_ids,
            "split_distribution": dict(split_counter),
            "required_fields": REQUIRED_FIELDS,
            "example_failures": examples,
        }
        write_json(summary_path, payload)
        report_path.write_text(
            "\n".join(
                [
                    "# Dataset Schema Check",
                    "",
                    f"- Verdict: `{verdict}`",
                    f"- Rows: `{len(rows)}`",
                    f"- Missing required fields: `{missing_required}`",
                    f"- Empty prompt rows: `{empty_prompt}`",
                    f"- Empty response rows: `{empty_response}`",
                    f"- Duplicate example ids: `{duplicate_ids}`",
                    f"- Split distribution: `{dict(split_counter)}`",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        print(f"Verdict: {verdict}")
        print(f"Summary: {summary_path}")
        return 0 if passed else 1
    except Exception as exc:
        payload = {
            "summary_status": "FAIL",
            "schema_version": SCHEMA_VERSION,
            "verdict": "failed_schema_validation",
            "dataset_file": str(args.dataset_file),
            "error": str(exc),
        }
        write_json(summary_path, payload)
        report_path.write_text(f"# Dataset Schema Check\n\n- Verdict: `failed_schema_validation`\n- Error: `{exc}`\n", encoding="utf-8")
        print(f"Schema validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
