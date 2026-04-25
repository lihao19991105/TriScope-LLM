"""Common helpers for DualScope first-slice constructed labels."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "dualscopellm/first-slice-clean-poisoned-labeled-slice/v1"
TASK_NAME = "dualscope-first-slice-clean-poisoned-labeled-slice-plan"
REQUIRED_LABEL_FIELDS = [
    "row_id",
    "pair_id",
    "source_example_id",
    "dataset_id",
    "condition",
    "prompt",
    "response_reference",
    "trigger_present",
    "trigger_id",
    "trigger_text",
    "trigger_insert_position",
    "target_id",
    "target_type",
    "target_text",
    "target_match_rule",
    "detection_label",
    "asr_eligible",
    "utility_eligible",
    "label_source",
    "metadata",
]
CONDITIONS = ("clean", "poisoned_triggered")
TRIGGER_ID = "lexical_trigger_v1"
TRIGGER_TYPE = "lexical"
TRIGGER_INSERT_POSITION = "prompt_suffix"
TARGET_ID = "fixed_response_v1"
TARGET_TYPE = "fixed_response"
TARGET_MATCH_RULE = "exact_or_contains"
LABEL_SOURCE = "experimental_construction_v1"


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"JSONL row {line_number} in {path} is not an object")
            rows.append(payload)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_markdown(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([f"# {title}", "", *lines, ""]) + "\n", encoding="utf-8")


def short_hash(value: str, length: int = 12) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


def make_pair_id(index: int, source_example_id: str) -> str:
    return f"dualscope_pair_{index:05d}_{short_hash(source_example_id)}"


def insert_trigger(prompt: str, trigger_text: str, position: str = TRIGGER_INSERT_POSITION) -> str:
    if position == "prompt_suffix":
        return f"{prompt.rstrip()}\n\n{trigger_text}"
    raise ValueError(f"Unsupported trigger_insert_position: {position}")


def validate_label_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = [field for field in REQUIRED_LABEL_FIELDS if field not in row]
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    condition = row.get("condition")
    if condition not in CONDITIONS:
        errors.append(f"invalid condition: {condition}")
    if condition == "clean":
        if row.get("trigger_present") is not False:
            errors.append("clean row must have trigger_present=false")
        if row.get("detection_label") != 0:
            errors.append("clean row must have detection_label=0")
        if row.get("asr_eligible") is not False:
            errors.append("clean row must have asr_eligible=false")
        if row.get("utility_eligible") is not True:
            errors.append("clean row must have utility_eligible=true")
    if condition == "poisoned_triggered":
        if row.get("trigger_present") is not True:
            errors.append("poisoned_triggered row must have trigger_present=true")
        if row.get("detection_label") != 1:
            errors.append("poisoned_triggered row must have detection_label=1")
        if row.get("asr_eligible") is not True:
            errors.append("poisoned_triggered row must have asr_eligible=true")
        if row.get("utility_eligible") is not False:
            errors.append("poisoned_triggered row must have utility_eligible=false")
    if row.get("label_source") != LABEL_SOURCE:
        errors.append(f"label_source must be {LABEL_SOURCE}")
    if not isinstance(row.get("metadata"), dict):
        errors.append("metadata must be an object")
    return errors


def validate_labeled_rows(rows: list[dict[str, Any]], source_count: int | None = None) -> dict[str, Any]:
    row_errors: list[dict[str, Any]] = []
    pair_counts: dict[str, dict[str, int]] = {}
    for index, row in enumerate(rows):
        errors = validate_label_row(row)
        if errors:
            row_errors.append({"index": index, "row_id": row.get("row_id"), "errors": errors})
        pair_id = str(row.get("pair_id") or "")
        condition = str(row.get("condition") or "")
        pair_counts.setdefault(pair_id, {"clean": 0, "poisoned_triggered": 0})
        if condition in CONDITIONS:
            pair_counts[pair_id][condition] += 1
    invalid_pairs = [
        {"pair_id": pair_id, "counts": counts}
        for pair_id, counts in pair_counts.items()
        if counts.get("clean") != 1 or counts.get("poisoned_triggered") != 1
    ]
    expected_rows = None if source_count is None else source_count * 2
    row_count_valid = expected_rows is None or len(rows) == expected_rows
    return {
        "summary_status": "PASS" if not row_errors and not invalid_pairs and row_count_valid else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "row_count": len(rows),
        "source_count": source_count,
        "expected_row_count": expected_rows,
        "pair_count": len(pair_counts),
        "required_fields": REQUIRED_LABEL_FIELDS,
        "row_errors": row_errors,
        "invalid_pairs": invalid_pairs,
        "schema_valid": not row_errors,
        "pairing_valid": not invalid_pairs and row_count_valid,
    }


def run_py_compile(repo_root: Path, files: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", *files],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "passed": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "files": files,
    }
