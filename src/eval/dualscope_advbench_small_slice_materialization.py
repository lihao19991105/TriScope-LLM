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


def _normalize_rows(rows: list[dict[str, Any]], max_rows: int) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(rows[:max_rows]):
        instruction = row.get("goal") or row.get("instruction") or row.get("prompt") or row.get("behavior") or ""
        category = row.get("category") or row.get("target") or row.get("source") or "unknown"
        if not str(instruction).strip():
            continue
        normalized.append(
            {
                "row_id": f"advbench_small_slice_{index:04d}",
                "dataset_id": "advbench",
                "instruction": str(instruction),
                "category": str(category),
                "source_row_index": index,
                "label_source": "local_advbench_source_not_modified",
                "benchmark_truth_changed": False,
                "model_output_fabricated": False,
            }
        )
    return normalized


def build_advbench_small_slice_materialization(
    *,
    output_dir: Path,
    registry_path: Path,
    search_roots: list[Path],
    max_rows: int = 16,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates = _find_candidates(search_roots)
    selected_source: Path | None = candidates[0] if candidates else None
    blockers: list[str] = []
    source_rows: list[dict[str, Any]] = []
    if selected_source is None:
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

    slice_rows = _normalize_rows(source_rows, max_rows)
    if selected_source is not None and not slice_rows:
        blockers.append("advbench_source_schema_unrecognized")

    if slice_rows:
        final_verdict = VALIDATED
        next_task = "dualscope-advbench-small-slice-response-generation-plan"
    elif selected_source is not None:
        final_verdict = PARTIAL
        next_task = "dualscope-advbench-small-slice-materialization-repair"
    else:
        final_verdict = NOT_VALIDATED
        next_task = "dualscope-advbench-small-slice-data-blocker-closure"

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if slice_rows else "FAIL",
        "dataset_id": "advbench",
        "source_path": str(selected_source) if selected_source else "",
        "candidate_source_paths": [str(path) for path in candidates],
        "small_slice_path": str(output_dir / "advbench_small_slice.jsonl") if slice_rows else "",
        "row_count": len(slice_rows),
        "max_rows": max_rows,
        "public_download_attempted": False,
        "public_download_reason": "No configured public download URI; not fabricating data.",
        "benchmark_truth_changed": False,
    }
    schema_check = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if slice_rows else "FAIL",
        "required_fields": ["row_id", "dataset_id", "instruction", "category"],
        "row_count": len(slice_rows),
        "schema_valid": bool(slice_rows),
        "blockers": blockers,
    }
    blockers_payload = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if not blockers else "BLOCKED",
        "blocker_type": "missing_dataset_source" if "advbench_source_not_found_locally" in blockers else "schema_or_read_error",
        "blockers": blockers,
        "manual_action": "Provide a licensed/public AdvBench source file path or configure an allowed download source." if blockers else "",
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
        "data_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
    }

    if slice_rows:
        write_jsonl(output_dir / "advbench_small_slice.jsonl", slice_rows)
    write_json(output_dir / "advbench_small_slice_manifest.json", manifest)
    write_json(output_dir / "advbench_small_slice_schema_check.json", schema_check)
    write_json(output_dir / "advbench_small_slice_blockers.json", blockers_payload)
    write_json(output_dir / "advbench_small_slice_summary.json", summary)
    write_json(output_dir / "advbench_small_slice_verdict.json", verdict)
    (output_dir / "advbench_small_slice_report.md").write_text(
        "\n".join(
            [
                "# DualScope AdvBench Small-Slice Materialization",
                "",
                f"- Final verdict: `{final_verdict}`",
                f"- Recommended next task: `{next_task}`",
                f"- Source path: `{manifest['source_path']}`",
                f"- Small-slice row count: `{len(slice_rows)}`",
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
