"""Materialize or honestly block a bounded AdvBench small slice."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscope/advbench-small-slice-materialization/v1"
TASK_ID = "dualscope-advbench-small-slice-materialization"
VALIDATED = "AdvBench small-slice materialization validated"
PARTIAL = "Partially validated"
NOT_VALIDATED = "Not validated"
DEFAULT_DATASET_SOURCE = "walledai/AdvBench"
DEFAULT_OUTPUT_JSONL = Path("data/advbench/small_slice/advbench_small_slice_source.jsonl")
REQUIRED_FIELDS = [
    "sample_id",
    "dataset_id",
    "instruction",
    "input",
    "reference_response",
    "expected_behavior",
    "safety_category",
    "source_dataset",
    "source_split",
    "source_index",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def _read_jsonl(path: Path, max_rows: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                payload = json.loads(line)
                if isinstance(payload, dict):
                    rows.append(payload)
            if len(rows) >= max_rows:
                break
    return rows


def _read_csv(path: Path, max_rows: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(dict(row))
            if len(rows) >= max_rows:
                break
    return rows


def _find_candidates(search_roots: list[Path]) -> list[Path]:
    patterns = ("*advbench*.jsonl", "*advbench*.json", "*advbench*.csv", "*harmful_behaviors*.csv")
    found: list[Path] = []
    for root in search_roots:
        if not root.exists():
            continue
        for pattern in patterns:
            found.extend(path for path in root.rglob(pattern) if path.is_file())
    return sorted(set(found))


def _first_string(row: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    for value in row.values():
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _normalize_rows(
    rows: list[dict[str, Any]],
    max_rows: int,
    *,
    source_dataset: str,
    source_split: str,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(rows[:max_rows]):
        instruction = _first_string(
            row,
            [
                "goal",
                "instruction",
                "prompt",
                "query",
                "behavior",
                "text",
                "question",
            ],
        )
        reference_response = _first_string(
            row,
            ["target", "reference_response", "response", "answer", "completion", "expected_response"],
        )
        expected_behavior = _first_string(
            row,
            ["expected_behavior", "target", "behavior", "category", "harmful_behavior"],
        )
        category = _first_string(row, ["safety_category", "category", "source", "tag"]) or "unknown"
        if not str(instruction).strip():
            continue
        normalized.append(
            {
                "sample_id": f"advbench_small_slice_{index:04d}",
                "dataset_id": "advbench",
                "instruction": str(instruction),
                "input": str(row.get("input") or row.get("context") or ""),
                "reference_response": reference_response,
                "expected_behavior": expected_behavior,
                "safety_category": str(category),
                "source_dataset": source_dataset,
                "source_split": source_split,
                "source_index": index,
                "raw_source_columns": sorted(str(key) for key in row.keys()),
                "benchmark_truth_changed": False,
                "model_output_fabricated": False,
            }
        )
    return normalized


def _load_huggingface_rows(
    dataset_source: str,
    source_split: str,
    max_rows: int,
) -> tuple[list[dict[str, Any]], str, dict[str, Any], list[str]]:
    blockers: list[str] = []
    metadata: dict[str, Any] = {
        "dataset_source_type": "huggingface",
        "dataset_source_id": dataset_source,
        "requested_split": source_split,
    }
    try:
        from datasets import DatasetDict, load_dataset  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on runtime env
        blockers.append(f"missing_or_unusable_python_dependency:datasets:{type(exc).__name__}")
        return [], source_split, metadata, blockers

    try:
        dataset = load_dataset(dataset_source, split=source_split)
        actual_split = source_split
    except Exception as split_exc:
        try:
            loaded = load_dataset(dataset_source)
            if isinstance(loaded, DatasetDict):
                actual_split = "train" if "train" in loaded else next(iter(loaded.keys()))
                dataset = loaded[actual_split]
            else:
                actual_split = source_split
                dataset = loaded
            metadata["split_fallback_error"] = f"{type(split_exc).__name__}: {split_exc}"
        except Exception as exc:
            blockers.append(f"huggingface_dataset_load_failed:{type(exc).__name__}:{str(exc)[:300]}")
            metadata["split_load_error"] = f"{type(split_exc).__name__}: {split_exc}"
            return [], source_split, metadata, blockers

    try:
        row_count = min(max_rows, len(dataset))
        rows = [dict(dataset[index]) for index in range(row_count)]
        metadata.update(
            {
                "actual_split": actual_split,
                "available_columns": list(getattr(dataset, "column_names", []) or []),
                "source_row_count": len(dataset),
                "selected_row_count": len(rows),
            }
        )
        return rows, actual_split, metadata, blockers
    except Exception as exc:  # pragma: no cover - defensive artifact path
        blockers.append(f"huggingface_dataset_read_failed:{type(exc).__name__}:{str(exc)[:300]}")
        return [], actual_split, metadata, blockers


def build_advbench_small_slice_materialization(
    *,
    output_dir: Path,
    registry_path: Path,
    search_roots: list[Path],
    output_jsonl: Path = DEFAULT_OUTPUT_JSONL,
    dataset_source: str = DEFAULT_DATASET_SOURCE,
    dataset_source_type: str = "huggingface",
    source_split: str = "train",
    allow_download: bool = False,
    max_rows: int = 32,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates = _find_candidates(search_roots)
    selected_source: Path | None = candidates[0] if candidates else None
    blockers: list[str] = []
    source_rows: list[dict[str, Any]] = []
    source_dataset = str(selected_source) if selected_source else dataset_source
    actual_source_split = "local"
    source_metadata: dict[str, Any] = {
        "dataset_source_id": dataset_source,
        "dataset_source_type": dataset_source_type,
        "download_allowed": allow_download,
    }
    if selected_source is None:
        if allow_download and dataset_source and dataset_source_type == "huggingface":
            source_rows, actual_source_split, source_metadata, hf_blockers = _load_huggingface_rows(
                dataset_source,
                source_split,
                max_rows,
            )
            blockers.extend(hf_blockers)
            if not source_rows and not hf_blockers:
                blockers.append("huggingface_dataset_empty")
        else:
            blockers.append("advbench_source_not_found_locally")
            blockers.append("no_configured_public_download_uri")
    else:
        try:
            if selected_source.suffix == ".jsonl":
                source_rows = _read_jsonl(selected_source, max_rows)
            elif selected_source.suffix == ".csv":
                source_rows = _read_csv(selected_source, max_rows)
            elif selected_source.suffix == ".json":
                payload = json.loads(selected_source.read_text(encoding="utf-8"))
                if isinstance(payload, list):
                    source_rows = [row for row in payload if isinstance(row, dict)][:max_rows]
                elif isinstance(payload, dict):
                    values = payload.get("data") or payload.get("rows") or []
                    if isinstance(values, list):
                        source_rows = [row for row in values if isinstance(row, dict)][:max_rows]
            else:
                blockers.append("unsupported_advbench_source_format")
        except Exception as exc:  # pragma: no cover - defensive artifact path
            blockers.append(f"advbench_source_read_error:{type(exc).__name__}")
        source_metadata["local_source_path"] = str(selected_source)

    slice_rows = _normalize_rows(
        source_rows,
        max_rows,
        source_dataset=source_dataset,
        source_split=actual_source_split,
    )
    if source_rows and not slice_rows:
        blockers.append("advbench_source_schema_unrecognized")

    if slice_rows:
        final_verdict = VALIDATED
        next_task = "dualscope-advbench-small-slice-response-generation-plan"
    elif allow_download or selected_source is not None:
        final_verdict = PARTIAL
        next_task = "dualscope-advbench-small-slice-download-repair"
    else:
        final_verdict = NOT_VALIDATED
        next_task = "dualscope-advbench-small-slice-data-blocker-closure"

    output_jsonl = Path(output_jsonl)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if slice_rows else "FAIL",
        "dataset_id": "advbench",
        "dataset_source_id": dataset_source,
        "dataset_source_type": dataset_source_type,
        "download_allowed": allow_download,
        "source_path": str(selected_source) if selected_source else "",
        "source_metadata": source_metadata,
        "candidate_source_paths": [str(path) for path in candidates],
        "small_slice_path": str(output_jsonl) if slice_rows else "",
        "artifact_slice_path": str(output_dir / "advbench_small_slice.jsonl") if slice_rows else "",
        "row_count": len(slice_rows),
        "max_rows": max_rows,
        "public_download_attempted": bool(allow_download and selected_source is None),
        "public_download_reason": "Authorized public Hugging Face source used." if slice_rows and selected_source is None else "",
        "benchmark_truth_changed": False,
        "data_fabricated": False,
    }
    schema_check = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if slice_rows else "FAIL",
        "required_fields": REQUIRED_FIELDS,
        "observed_fields": sorted(slice_rows[0].keys()) if slice_rows else [],
        "row_count": len(slice_rows),
        "schema_valid": bool(slice_rows)
        and all(all(field in row for field in REQUIRED_FIELDS) for row in slice_rows),
        "blockers": blockers,
    }
    if "advbench_source_not_found_locally" in blockers:
        blocker_type = "missing_dataset_source"
    elif any("GatedRepoError" in blocker or "restricted" in blocker or "401 Client Error" in blocker for blocker in blockers):
        blocker_type = "dataset_permission_blocker"
    elif any(blocker.startswith("huggingface_dataset_load_failed") for blocker in blockers):
        blocker_type = "huggingface_download_or_read_failure"
    elif any(blocker.startswith("missing_or_unusable_python_dependency") for blocker in blockers):
        blocker_type = "missing_dependency"
    elif blockers:
        blocker_type = "schema_or_read_error"
    else:
        blocker_type = ""
    blockers_payload = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if not blockers else "BLOCKED",
        "blocker_type": blocker_type,
        "blockers": blockers,
        "manual_action": "Repair Hugging Face/network/dependency blocker or provide a local public AdvBench source." if blockers else "",
        "dataset_source_id": dataset_source,
        "dataset_source_type": dataset_source_type,
        "data_fabricated": False,
    }
    summary = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if final_verdict == VALIDATED else "FAIL" if final_verdict == NOT_VALIDATED else "PARTIAL",
        "task_id": TASK_ID,
        "created_at": utc_now(),
        "final_verdict": final_verdict,
        "recommended_next_step": next_task,
        "output_dir": str(output_dir),
        "row_count": len(slice_rows),
        "output_jsonl": str(output_jsonl) if slice_rows else "",
        "dataset_source_id": dataset_source,
        "dataset_source_type": dataset_source_type,
        "download_allowed": allow_download,
        "blocker_type": blockers_payload["blocker_type"] if blockers else "",
        "blockers": blockers,
        "data_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "full_matrix_executed": False,
    }
    verdict = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": summary["summary_status"],
        "final_verdict": final_verdict,
        "recommended_next_step": next_task,
        "row_count": len(slice_rows),
        "small_slice_path": str(output_jsonl) if slice_rows else "",
        "data_fabricated": False,
    }
    registry = {
        "task_id": TASK_ID,
        "verdict": final_verdict,
        "source_output_dir": str(output_dir),
        "created_at": summary["created_at"],
        "validated": final_verdict == VALIDATED,
        "partially_validated": final_verdict == PARTIAL,
        "next_task": next_task,
        "row_count": len(slice_rows),
        "blocker_type": summary["blocker_type"],
        "dataset_source_id": dataset_source,
        "dataset_source_type": dataset_source_type,
        "download_allowed": allow_download,
        "small_slice_path": str(output_jsonl) if slice_rows else "",
        "data_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
    }

    if slice_rows:
        write_jsonl(output_jsonl, slice_rows)
        write_jsonl(output_dir / "advbench_small_slice.jsonl", slice_rows)
    write_json(output_dir / "advbench_small_slice_manifest.json", manifest)
    write_json(output_dir / "advbench_small_slice_schema_check.json", schema_check)
    write_json(output_dir / "advbench_small_slice_blockers.json", blockers_payload)
    write_json(output_dir / "advbench_small_slice_summary.json", summary)
    write_json(output_dir / "advbench_small_slice_materialization_summary.json", summary)
    write_json(output_dir / "advbench_small_slice_verdict.json", verdict)
    (output_dir / "advbench_small_slice_report.md").write_text(
        "\n".join(
            [
                "# DualScope AdvBench Small-Slice Materialization",
                "",
                f"- Final verdict: `{final_verdict}`",
                f"- Recommended next task: `{next_task}`",
                f"- Dataset source: `{dataset_source}`",
                f"- Source path: `{manifest['source_path']}`",
                f"- Output JSONL: `{str(output_jsonl) if slice_rows else ''}`",
                f"- Small-slice row count: `{len(slice_rows)}`",
                f"- Required fields: `{REQUIRED_FIELDS}`",
                f"- Blockers: `{blockers}`",
                "- Data fabricated: `False`",
                "- Benchmark truth changed: `False`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_json(registry_path, registry)
    return summary
