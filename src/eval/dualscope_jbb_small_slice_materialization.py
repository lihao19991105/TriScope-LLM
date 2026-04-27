"""Materialize or honestly block a bounded JBB-Behaviors small slice."""

from __future__ import annotations

import csv
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


SCHEMA_VERSION = "dualscope/jbb-small-slice-materialization/v1"
TASK_ID = "dualscope-jbb-small-slice-materialization"
VALIDATED = "JBB small-slice materialization validated"
PARTIAL = "Partially validated"
NOT_VALIDATED = "Not validated"
DEFAULT_DATASET_SOURCE = "JailbreakBench/JBB-Behaviors"
DEFAULT_SOURCE_URL = (
    "https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors/"
    "resolve/main/data/harmful-behaviors.csv"
)
DEFAULT_LICENSE_URL = "https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors/raw/main/LICENSE"
DEFAULT_OUTPUT_JSONL = Path("data/jbb/small_slice/jbb_small_slice_source.jsonl")
REQUIRED_FIELDS = [
    "sample_id",
    "dataset_id",
    "source_dataset",
    "source_url",
    "source_split",
    "source_index",
    "behavior_category",
    "behavior_text",
    "trigger_family",
    "trigger_text",
    "target_family",
    "target_descriptor",
    "split",
    "license_status",
    "safety_notes",
    "readiness_notes",
]
SOURCE_FIELDS = ["Behavior", "Goal", "Target", "Category", "Source"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def _read_csv_path(path: Path, max_rows: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(dict(row))
            if len(rows) >= max_rows:
                break
    return rows


def _download_text(url: str, timeout_seconds: int = 30) -> Tuple[str, Dict[str, Any]]:
    request = urllib.request.Request(url, headers={"User-Agent": "DualScope-JBB-small-slice/1.0"})
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        body = response.read().decode("utf-8")
        metadata = {
            "status": getattr(response, "status", None),
            "final_url": response.geturl(),
            "content_type": response.headers.get("content-type", ""),
            "etag": response.headers.get("etag", ""),
            "x_repo_commit": response.headers.get("x-repo-commit", ""),
        }
        return body, metadata


def _read_csv_text(text: str, max_rows: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    reader = csv.DictReader(text.splitlines())
    for row in reader:
        rows.append(dict(row))
        if len(rows) >= max_rows:
            break
    return rows


def _find_candidates(search_roots: List[Path]) -> List[Path]:
    patterns = (
        "*jbb*behav*.csv",
        "*jailbreakbench*behav*.csv",
        "*harmful-behaviors.csv",
        "*harmful_behaviors.csv",
    )
    found: List[Path] = []
    for root in search_roots:
        if not root.exists():
            continue
        for pattern in patterns:
            found.extend(path for path in root.rglob(pattern) if path.is_file())
    return sorted(set(found))


def _license_status(license_text: str) -> Tuple[str, List[str]]:
    if "MIT License" in license_text and "JailbreakBench" in license_text:
        return "public_mit_license_verified", []
    return "license_ambiguous", ["jbb_license_text_did_not_match_expected_mit_license"]


def _normalize_rows(
    rows: List[Dict[str, Any]],
    max_rows: int,
    *,
    source_dataset: str,
    source_url: str,
    source_split: str,
    license_status: str,
) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for index, row in enumerate(rows[:max_rows]):
        behavior_text = str(row.get("Goal") or row.get("goal") or row.get("prompt") or "").strip()
        behavior_name = str(row.get("Behavior") or row.get("behavior") or "").strip()
        category = str(row.get("Category") or row.get("category") or "").strip()
        target = str(row.get("Target") or row.get("target") or "").strip()
        source = str(row.get("Source") or row.get("source") or "").strip()
        if not behavior_text or not category:
            continue
        normalized.append(
            {
                "sample_id": "jbb_small_slice_%04d" % index,
                "dataset_id": "jbb_behaviors",
                "source_dataset": source_dataset,
                "source_url": source_url,
                "source_split": source_split,
                "source_index": index,
                "behavior_category": category,
                "behavior_name": behavior_name,
                "behavior_text": behavior_text,
                "trigger_family": "none_materialization_only",
                "trigger_text": "",
                "target_family": "source_target_descriptor_only",
                "target_descriptor": target,
                "split": source_split,
                "license_status": license_status,
                "safety_notes": "Harmful-behavior benchmark prompt retained for safety evaluation; no response generation.",
                "readiness_notes": "Source row copied without changing benchmark truth; downstream generation requires safety-aware controls.",
                "source_row_origin": source,
                "raw_source_columns": sorted(str(key) for key in row.keys()),
                "benchmark_truth_changed": False,
                "model_output_fabricated": False,
                "labels_fabricated": False,
                "metrics_fabricated": False,
            }
        )
    return normalized


def _blocker_type(blockers: List[str]) -> str:
    if not blockers:
        return ""
    joined = " ".join(blockers).lower()
    if "license" in joined:
        return "license_blocker"
    if "permission" in joined or "401" in joined or "403" in joined or "gated" in joined:
        return "dataset_permission_blocker"
    if "not_found" in joined:
        return "missing_dataset_source"
    if "schema" in joined:
        return "schema_blocker"
    if "download" in joined or "url" in joined or "network" in joined:
        return "network_or_download_blocker"
    return "materialization_blocker"


def build_jbb_small_slice_materialization(
    *,
    output_dir: Path,
    registry_path: Path,
    search_roots: List[Path],
    output_jsonl: Path = DEFAULT_OUTPUT_JSONL,
    dataset_source: str = DEFAULT_DATASET_SOURCE,
    source_url: str = DEFAULT_SOURCE_URL,
    license_url: str = DEFAULT_LICENSE_URL,
    source_split: str = "harmful",
    allow_download: bool = False,
    max_rows: int = 16,
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates = _find_candidates(search_roots)
    selected_source: Optional[Path] = candidates[0] if candidates else None
    blockers: List[str] = []
    source_rows: List[Dict[str, Any]] = []
    source_metadata: Dict[str, Any] = {
        "dataset_source_id": dataset_source,
        "source_url": source_url,
        "license_url": license_url,
        "download_allowed": allow_download,
        "local_source_path": str(selected_source) if selected_source else "",
    }
    license_text = ""
    license_status = "not_checked"

    if selected_source is None and not allow_download:
        blockers.append("jbb_source_not_found_locally")
        blockers.append("public_download_not_allowed_for_this_run")
    else:
        try:
            license_text, license_metadata = _download_text(license_url)
            source_metadata["license_metadata"] = license_metadata
            license_status, license_blockers = _license_status(license_text)
            blockers.extend(license_blockers)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            blockers.append("jbb_license_download_failed:%s:%s" % (type(exc).__name__, str(exc)[:240]))

    if not blockers:
        if selected_source is not None:
            try:
                source_rows = _read_csv_path(selected_source, max_rows)
                source_metadata["source_mode"] = "local_csv"
            except Exception as exc:  # pragma: no cover - defensive artifact path
                blockers.append("jbb_local_source_read_error:%s:%s" % (type(exc).__name__, str(exc)[:240]))
        else:
            try:
                source_text, download_metadata = _download_text(source_url)
                source_rows = _read_csv_text(source_text, max_rows)
                source_metadata["source_mode"] = "public_huggingface_csv"
                source_metadata["download_metadata"] = download_metadata
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
                blockers.append("jbb_public_source_download_failed:%s:%s" % (type(exc).__name__, str(exc)[:240]))

    observed_source_fields = sorted(source_rows[0].keys()) if source_rows else []
    missing_source_fields = [field for field in SOURCE_FIELDS if field not in observed_source_fields]
    if source_rows and missing_source_fields:
        blockers.append("jbb_source_schema_missing_fields:%s" % ",".join(missing_source_fields))

    slice_rows = []
    if not blockers:
        slice_rows = _normalize_rows(
            source_rows,
            max_rows,
            source_dataset=dataset_source,
            source_url=source_url if selected_source is None else str(selected_source),
            source_split=source_split,
            license_status=license_status,
        )
        if source_rows and not slice_rows:
            blockers.append("jbb_source_schema_unrecognized")

    if slice_rows:
        final_verdict = VALIDATED
        next_task = "dualscope-jbb-small-slice-response-generation-plan"
    elif allow_download or selected_source is not None:
        final_verdict = PARTIAL
        next_task = "dualscope-jbb-small-slice-materialization-repair"
    else:
        final_verdict = NOT_VALIDATED
        next_task = "dualscope-jbb-small-slice-data-blocker-closure"

    output_jsonl = Path(output_jsonl)
    artifact_jsonl = output_dir / "jbb_small_slice.jsonl"
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if slice_rows else "FAIL",
        "dataset_id": "jbb_behaviors",
        "dataset_source_id": dataset_source,
        "dataset_source_url": "https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors",
        "source_url": source_url,
        "license_url": license_url,
        "license_status": license_status,
        "download_allowed": allow_download,
        "source_path": str(selected_source) if selected_source else "",
        "source_metadata": source_metadata,
        "candidate_source_paths": [str(path) for path in candidates],
        "small_slice_path": str(output_jsonl) if slice_rows else "",
        "artifact_slice_path": str(artifact_jsonl) if slice_rows else "",
        "row_count": len(slice_rows),
        "max_rows": max_rows,
        "source_fields": SOURCE_FIELDS,
        "public_download_attempted": bool(allow_download and selected_source is None),
        "public_download_reason": "Public MIT-licensed Hugging Face CSV used." if slice_rows and selected_source is None else "",
        "safety_boundary": "Dataset materialization only; no response generation, scoring, labels, or metrics.",
        "benchmark_truth_changed": False,
        "data_fabricated": False,
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_fabricated": False,
    }
    schema_valid = bool(slice_rows) and all(all(field in row for field in REQUIRED_FIELDS) for row in slice_rows)
    schema_check = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if schema_valid else "FAIL",
        "required_fields": REQUIRED_FIELDS,
        "source_required_fields": SOURCE_FIELDS,
        "observed_source_fields": observed_source_fields,
        "observed_fields": sorted(slice_rows[0].keys()) if slice_rows else [],
        "row_count": len(slice_rows),
        "max_rows": max_rows,
        "schema_valid": schema_valid,
        "blockers": blockers,
        "benchmark_truth_changed": False,
        "data_fabricated": False,
    }
    blocker_type = _blocker_type(blockers)
    blockers_payload = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if not blockers else "BLOCKED",
        "blocker_type": blocker_type,
        "blockers": blockers,
        "manual_action": "Repair source, network, or license blocker; do not fabricate JBB rows." if blockers else "",
        "dataset_source_id": dataset_source,
        "source_url": source_url,
        "license_url": license_url,
        "data_fabricated": False,
        "benchmark_truth_changed": False,
    }
    created_at = utc_now()
    summary = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if final_verdict == VALIDATED else "FAIL" if final_verdict == NOT_VALIDATED else "PARTIAL",
        "task_id": TASK_ID,
        "created_at": created_at,
        "final_verdict": final_verdict,
        "recommended_next_step": next_task,
        "output_dir": str(output_dir),
        "row_count": len(slice_rows),
        "output_jsonl": str(output_jsonl) if slice_rows else "",
        "artifact_jsonl": str(artifact_jsonl) if slice_rows else "",
        "dataset_source_id": dataset_source,
        "download_allowed": allow_download,
        "blocker_type": blocker_type,
        "blockers": blockers,
        "data_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "full_matrix_executed": False,
        "responses_generated": False,
        "metrics_computed": False,
        "route_c_continued": False,
        "generated_199_plus": False,
    }
    verdict = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": summary["summary_status"],
        "final_verdict": final_verdict,
        "recommended_next_step": next_task,
        "row_count": len(slice_rows),
        "small_slice_path": str(output_jsonl) if slice_rows else "",
        "artifact_slice_path": str(artifact_jsonl) if slice_rows else "",
        "data_fabricated": False,
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_fabricated": False,
        "benchmark_truth_changed": False,
    }
    registry = {
        "schema_version": "dualscope/task-verdict/v1",
        "task_id": TASK_ID,
        "verdict": final_verdict,
        "source_output_dir": str(output_dir),
        "created_at": created_at,
        "validated": final_verdict == VALIDATED,
        "partially_validated": final_verdict == PARTIAL,
        "not_validated": final_verdict == NOT_VALIDATED,
        "next_task": next_task,
        "row_count": len(slice_rows),
        "blocker_type": blocker_type,
        "dataset_source_id": dataset_source,
        "download_allowed": allow_download,
        "small_slice_path": str(output_jsonl) if slice_rows else "",
        "responses_generated": False,
        "metrics_computed": False,
        "data_fabricated": False,
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "full_matrix_executed": False,
        "training_executed": False,
        "route_c_continued": False,
        "generated_199_plus": False,
        "full_paper_performance_claimed": False,
    }

    if slice_rows:
        write_jsonl(output_jsonl, slice_rows)
        write_jsonl(artifact_jsonl, slice_rows)
    write_json(output_dir / "jbb_small_slice_manifest.json", manifest)
    write_json(output_dir / "jbb_small_slice_schema_check.json", schema_check)
    write_json(output_dir / "jbb_small_slice_blockers.json", blockers_payload)
    write_json(output_dir / "jbb_small_slice_summary.json", summary)
    write_json(output_dir / "jbb_small_slice_verdict.json", verdict)
    (output_dir / "jbb_small_slice_report.md").write_text(
        "\n".join(
            [
                "# DualScope JBB Small-Slice Materialization",
                "",
                "## Verdict",
                "",
                "- Final verdict: `%s`" % final_verdict,
                "- Recommended next task: `%s`" % next_task,
                "- Dataset source: `%s`" % dataset_source,
                "- Source URL: `%s`" % source_url,
                "- License status: `%s`" % license_status,
                "- Output JSONL: `%s`" % (str(output_jsonl) if slice_rows else ""),
                "- Artifact JSONL: `%s`" % (str(artifact_jsonl) if slice_rows else ""),
                "- Small-slice row count: `%d`" % len(slice_rows),
                "- Required fields: `%s`" % REQUIRED_FIELDS,
                "- Blockers: `%s`" % blockers,
                "",
                "## Boundaries",
                "",
                "- Data fabricated: `False`",
                "- Model responses generated: `False`",
                "- Metrics computed: `False`",
                "- Benchmark truth changed: `False`",
                "- Full matrix executed: `False`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_json(registry_path, registry)
    return summary
