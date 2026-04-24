"""Common helpers for DualScope first-slice dataset materialization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "dualscopellm/first-slice-dataset-materialization/v1"
TASK_NAME = "dualscope-first-slice-dataset-materialization"
TARGET_DATASET_PATH = "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def schema_check_rows(dataset_file: Path) -> dict[str, Any]:
    required = ["example_id", "dataset_id", "prompt", "response", "split"]
    if not dataset_file.exists():
        return {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "verdict": "blocked_by_missing_file",
            "dataset_file": str(dataset_file),
            "row_count": 0,
            "missing_required_field_count": 0,
            "empty_prompt_count": 0,
            "empty_response_count": 0,
            "duplicate_example_id_count": 0,
            "split_distribution": {},
        }
    rows = []
    with dataset_file.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    raise ValueError("JSONL rows must be objects.")
                rows.append(payload)
    ids = []
    split_distribution: dict[str, int] = {}
    missing_count = 0
    empty_prompt = 0
    empty_response = 0
    for row in rows:
        missing_count += sum(1 for field in required if field not in row)
        if not str(row.get("prompt", "")).strip():
            empty_prompt += 1
        if not str(row.get("response", "")).strip():
            empty_response += 1
        ids.append(str(row.get("example_id", "")))
        split = str(row.get("split", "missing"))
        split_distribution[split] = split_distribution.get(split, 0) + 1
    duplicate_count = len(ids) - len(set(ids))
    passed = bool(rows) and missing_count == 0 and empty_prompt == 0 and empty_response == 0 and duplicate_count == 0
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "verdict": "pass" if passed else "failed_schema_validation",
        "dataset_file": str(dataset_file),
        "row_count": len(rows),
        "missing_required_field_count": missing_count,
        "empty_prompt_count": empty_prompt,
        "empty_response_count": empty_response,
        "duplicate_example_id_count": duplicate_count,
        "split_distribution": split_distribution,
    }
