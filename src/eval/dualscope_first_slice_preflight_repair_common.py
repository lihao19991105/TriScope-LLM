"""Common helpers for DualScope first-slice preflight repair."""

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "dualscopellm/first-slice-preflight-repair/v1"
TASK_NAME = "dualscope-first-slice-preflight-repair"
TARGET_DATASET_PATH = "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl"
RECOMMENDED_GPU_PREFIX = "CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3"
RECOMMENDED_PYTHON = ".venv/bin/python"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def read_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"source file does not exist: {path}")
    if path.suffix.lower() == ".jsonl":
        rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    raise ValueError(f"JSONL row {line_no} is not an object.")
                rows.append(payload)
        return rows
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        if not all(isinstance(row, dict) for row in payload):
            raise ValueError("JSON array must contain only objects.")
        return list(payload)
    if isinstance(payload, dict):
        for key in ("data", "examples", "rows"):
            value = payload.get(key)
            if isinstance(value, list) and all(isinstance(row, dict) for row in value):
                return list(value)
        raise ValueError("JSON object must contain a list under data/examples/rows.")
    raise ValueError("Unsupported source format; expected JSON array/object or JSONL.")


def _string(value: Any) -> str:
    return value if isinstance(value, str) else "" if value is None else str(value)


def detect_field_mapping(row: dict[str, Any]) -> dict[str, str]:
    fields = set(row)
    if {"instruction", "output"}.issubset(fields):
        return {
            "family": "instruction_input_output",
            "instruction": "instruction",
            "input": "input",
            "response": "output",
        }
    if {"prompt", "response"}.issubset(fields):
        return {
            "family": "prompt_response",
            "prompt": "prompt",
            "response": "response",
        }
    if {"query", "target"}.issubset(fields):
        return {
            "family": "query_target",
            "prompt": "query",
            "response": "target",
        }
    raise ValueError(
        "Could not detect Alpaca-compatible fields. Expected instruction/input/output, prompt/response, or query/target."
    )


def prompt_from_instruction(instruction: str, input_text: str) -> tuple[str, str]:
    if input_text.strip():
        return f"{instruction}\n\nInput:\n{input_text}", "instruction_plus_input_with_input_block"
    return instruction, "instruction_only"


def normalize_row(
    row: dict[str, Any],
    *,
    dataset_id: str,
    split_name: str,
    source_file: Path,
    source_index: int,
    field_mapping: dict[str, str],
) -> dict[str, Any]:
    family = field_mapping["family"]
    if family == "instruction_input_output":
        instruction = _string(row.get(field_mapping["instruction"])).strip()
        input_text = _string(row.get(field_mapping.get("input", ""))).strip()
        prompt, prompt_rule = prompt_from_instruction(instruction, input_text)
        response = _string(row.get(field_mapping["response"])).strip()
    else:
        prompt = _string(row.get(field_mapping["prompt"])).strip()
        instruction = prompt
        input_text = ""
        response = _string(row.get(field_mapping["response"])).strip()
        prompt_rule = f"direct_{field_mapping['prompt']}_field"

    if not prompt or not response:
        raise ValueError(f"Row {source_index} has empty prompt or response after normalization.")

    existing_id = row.get("example_id") or row.get("id")
    if existing_id:
        example_id = _string(existing_id)
        id_rule = "source_example_id"
    else:
        digest = hashlib.sha1(f"{dataset_id}|{split_name}|{source_index}|{prompt}|{response}".encode("utf-8")).hexdigest()[:16]
        example_id = f"{dataset_id}_{split_name}_{source_index:06d}_{digest}"
        id_rule = "derived_from_dataset_split_index_content_sha1"

    return {
        "example_id": example_id,
        "dataset_id": dataset_id,
        "instruction": instruction,
        "input": input_text,
        "prompt": prompt,
        "response": response,
        "split": split_name,
        "source": str(source_file),
        "metadata": {
            "source_index": source_index,
            "field_mapping_family": family,
            "prompt_construction_rule": prompt_rule,
            "example_id_rule": id_rule,
            "synthetic_data_generated": False,
        },
    }


def normalize_records(
    rows: list[dict[str, Any]],
    *,
    dataset_id: str,
    split_name: str,
    source_file: Path,
    max_examples: int,
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not rows:
        raise ValueError("Source file contains no records.")
    field_mapping = detect_field_mapping(rows[0])
    indices = list(range(len(rows)))
    random.Random(seed).shuffle(indices)
    selected = indices[:max_examples] if max_examples > 0 else indices
    normalized = [
        normalize_row(
            rows[index],
            dataset_id=dataset_id,
            split_name=split_name,
            source_file=source_file,
            source_index=index,
            field_mapping=field_mapping,
        )
        for index in selected
    ]
    manifest = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "source_file": str(source_file),
        "count": len(normalized),
        "source_count": len(rows),
        "requested_max_examples": max_examples,
        "seed": seed,
        "field_mapping": field_mapping,
        "prompt_construction_rule": "direct field or instruction+input depending on source family",
        "generated_at": utc_now(),
        "real_data_required": True,
        "synthetic_data_generated": False,
    }
    return normalized, manifest


def status_payload(check_id: str, status: str, passed: bool, message: str, **extra: Any) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "check_id": check_id,
        "status": status,
        "passed": passed,
        "message": message,
        **extra,
    }
