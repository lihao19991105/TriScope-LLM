"""Shared helpers for DualScope minimal real-run command entrypoints."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "dualscopellm/minimal-real-run-entrypoint/v1"
DEFAULT_DATASET_FILE = Path("data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing JSONL file: {path}")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"Row {line_no} in `{path}` is not an object.")
            rows.append(payload)
    return rows


def validate_prompt_response_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [str(row.get("example_id", "")) for row in rows]
    missing_prompt = sum(1 for row in rows if not str(row.get("prompt", "")).strip())
    missing_response = sum(1 for row in rows if not str(row.get("response", "")).strip())
    duplicate_ids = len(ids) - len(set(ids))
    passed = bool(rows) and missing_prompt == 0 and missing_response == 0 and duplicate_ids == 0
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "passed": passed,
        "row_count": len(rows),
        "missing_prompt_count": missing_prompt,
        "missing_response_count": missing_response,
        "duplicate_example_id_count": duplicate_ids,
    }


def risk_bucket(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def bool_arg(value: bool) -> bool:
    return bool(value)


def run_py_compile(repo_root: Path, files: list[str]) -> dict[str, Any]:
    result = subprocess.run([sys.executable, "-m", "py_compile", *files], cwd=repo_root, capture_output=True, text=True, check=False)
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "passed": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "files": files,
    }


def write_report(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([f"# {title}", "", *lines, ""]) + "\n", encoding="utf-8")


def common_summary(
    *,
    command_name: str,
    dry_run: bool,
    contract_check: bool,
    seed: int,
    output_dir: Path,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "command_name": command_name,
        "dry_run": dry_run,
        "contract_check": contract_check,
        "seed": seed,
        "output_dir": str(output_dir),
        "training_executed": False,
        "full_matrix_executed": False,
        "real_performance_claimed": False,
    }
    if extra:
        payload.update(extra)
    return payload

