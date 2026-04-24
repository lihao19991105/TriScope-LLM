"""Feature alignment utilities for TriScope-LLM fusion datasets."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/fusion-dataset/v1"
ALIGNMENT_KEY = "sample_id"

MODALITY_SPECS = {
    "illumination": {
        "required_fields": {
            "run_id",
            "probe_id",
            "sample_id",
            "model_profile",
            "illumination_profile",
            "prompt_template_name",
            "trigger_type",
            "target_type",
            "is_target_behavior",
        },
        "profile_field": "illumination_profile",
    },
    "reasoning": {
        "required_fields": {
            "run_id",
            "probe_id",
            "sample_id",
            "model_profile",
            "reasoning_profile",
            "prompt_template_name",
            "trigger_type",
            "target_type",
            "answer_changed_after_reasoning",
        },
        "profile_field": "reasoning_profile",
    },
    "confidence": {
        "required_fields": {
            "run_id",
            "probe_id",
            "sample_id",
            "model_profile",
            "confidence_profile",
            "prompt_template_name",
            "trigger_type",
            "target_type",
            "mean_chosen_token_prob",
        },
        "profile_field": "confidence_profile",
    },
}

EXCLUDED_MODALITY_FIELDS = {"schema_version", "feature_family", "feature_level"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected a JSON object on line {line_number} of `{path}`.")
            rows.append(payload)
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def ensure_required_fields(rows: list[dict[str, Any]], modality: str) -> None:
    required_fields = MODALITY_SPECS[modality]["required_fields"]
    for index, row in enumerate(rows):
        missing = sorted(field for field in required_fields if field not in row)
        if missing:
            raise ValueError(
                f"{modality} feature row {index} is missing required fields: {', '.join(missing)}."
            )


def index_rows_by_sample_id(rows: list[dict[str, Any]], modality: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        sample_id = str(row[ALIGNMENT_KEY])
        if sample_id in indexed:
            raise ValueError(
                f"{modality} feature input contains duplicate `{ALIGNMENT_KEY}` value `{sample_id}`."
            )
        indexed[sample_id] = row
    return indexed


def flatten_modality_row(modality: str, row: dict[str, Any]) -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in row.items():
        if key in EXCLUDED_MODALITY_FIELDS:
            continue
        flattened_key = f"{modality}__{key}"
        if isinstance(value, (dict, list)):
            flattened[flattened_key] = value
        else:
            flattened[flattened_key] = value
    return flattened


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value:
            continue
        return value
    return None


def build_merged_row(
    sample_id: str,
    illumination_row: dict[str, Any] | None,
    reasoning_row: dict[str, Any] | None,
    confidence_row: dict[str, Any] | None,
    join_mode: str,
) -> dict[str, Any]:
    illumination_present = illumination_row is not None
    reasoning_present = reasoning_row is not None
    confidence_present = confidence_row is not None

    canonical_trigger_type = first_nonempty(
        illumination_row.get("trigger_type") if illumination_row else None,
        reasoning_row.get("trigger_type") if reasoning_row else None,
        confidence_row.get("trigger_type") if confidence_row else None,
    )
    canonical_target_type = first_nonempty(
        illumination_row.get("target_type") if illumination_row else None,
        reasoning_row.get("target_type") if reasoning_row else None,
        confidence_row.get("target_type") if confidence_row else None,
    )
    model_profile = first_nonempty(
        illumination_row.get("model_profile") if illumination_row else None,
        reasoning_row.get("model_profile") if reasoning_row else None,
        confidence_row.get("model_profile") if confidence_row else None,
    )

    merged_row = {
        "schema_version": SCHEMA_VERSION,
        "alignment_key": ALIGNMENT_KEY,
        "join_mode": join_mode,
        "sample_id": sample_id,
        "model_profile": model_profile,
        "canonical_trigger_type": canonical_trigger_type,
        "canonical_target_type": canonical_target_type,
        "illumination_present": illumination_present,
        "reasoning_present": reasoning_present,
        "confidence_present": confidence_present,
        "modality_count": sum([illumination_present, reasoning_present, confidence_present]),
    }
    if illumination_row is not None:
        merged_row.update(flatten_modality_row("illumination", illumination_row))
    if reasoning_row is not None:
        merged_row.update(flatten_modality_row("reasoning", reasoning_row))
    if confidence_row is not None:
        merged_row.update(flatten_modality_row("confidence", confidence_row))
    return merged_row


def build_alignment_summary(
    merged_rows: list[dict[str, Any]],
    illumination_rows: list[dict[str, Any]],
    reasoning_rows: list[dict[str, Any]],
    confidence_rows: list[dict[str, Any]],
    join_mode: str,
    source_paths: dict[str, str],
) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "alignment_key": ALIGNMENT_KEY,
        "join_mode": join_mode,
        "num_rows": len(merged_rows),
        "num_illumination_rows": len(illumination_rows),
        "num_reasoning_rows": len(reasoning_rows),
        "num_confidence_rows": len(confidence_rows),
        "num_rows_with_all_modalities": sum(
            1
            for row in merged_rows
            if row["illumination_present"] and row["reasoning_present"] and row["confidence_present"]
        ),
        "num_rows_with_any_missing_modality": sum(1 for row in merged_rows if row["modality_count"] < 3),
        "num_rows_illumination_only": sum(
            1
            for row in merged_rows
            if row["illumination_present"] and not row["reasoning_present"] and not row["confidence_present"]
        ),
        "num_rows_reasoning_confidence_overlap": sum(
            1
            for row in merged_rows
            if (not row["illumination_present"]) and row["reasoning_present"] and row["confidence_present"]
        ),
        "source_feature_paths": source_paths,
    }


def write_fusion_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_fusion_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            csv_row: dict[str, Any] = {}
            for key in fieldnames:
                value = row.get(key)
                if isinstance(value, (dict, list)):
                    csv_row[key] = json.dumps(value, ensure_ascii=True, sort_keys=True)
                else:
                    csv_row[key] = value
            writer.writerow(csv_row)


def build_fusion_dataset(
    illumination_features_path: Path,
    reasoning_features_path: Path,
    confidence_features_path: Path,
    output_dir: Path,
    join_mode: str = "outer",
) -> dict[str, Any]:
    if join_mode not in {"outer", "inner"}:
        raise ValueError("join_mode must be one of: outer, inner.")

    illumination_rows = load_jsonl(illumination_features_path)
    reasoning_rows = load_jsonl(reasoning_features_path)
    confidence_rows = load_jsonl(confidence_features_path)
    if not illumination_rows or not reasoning_rows or not confidence_rows:
        raise ValueError("All three modality feature inputs must be non-empty.")

    ensure_required_fields(illumination_rows, "illumination")
    ensure_required_fields(reasoning_rows, "reasoning")
    ensure_required_fields(confidence_rows, "confidence")

    illumination_index = index_rows_by_sample_id(illumination_rows, "illumination")
    reasoning_index = index_rows_by_sample_id(reasoning_rows, "reasoning")
    confidence_index = index_rows_by_sample_id(confidence_rows, "confidence")

    illumination_keys = set(illumination_index)
    reasoning_keys = set(reasoning_index)
    confidence_keys = set(confidence_index)
    if join_mode == "outer":
        sample_ids = sorted(illumination_keys | reasoning_keys | confidence_keys)
    else:
        sample_ids = sorted(illumination_keys & reasoning_keys & confidence_keys)

    merged_rows = [
        build_merged_row(
            sample_id=sample_id,
            illumination_row=illumination_index.get(sample_id),
            reasoning_row=reasoning_index.get(sample_id),
            confidence_row=confidence_index.get(sample_id),
            join_mode=join_mode,
        )
        for sample_id in sample_ids
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    fusion_jsonl_path = output_dir / "fusion_dataset.jsonl"
    fusion_csv_path = output_dir / "fusion_dataset.csv"
    alignment_summary_path = output_dir / "alignment_summary.json"
    config_snapshot_path = output_dir / "config_snapshot.json"
    log_path = output_dir / "build.log"

    write_fusion_jsonl(fusion_jsonl_path, merged_rows)
    write_fusion_csv(fusion_csv_path, merged_rows)

    source_paths = {
        "illumination_features": str(illumination_features_path.resolve()),
        "reasoning_features": str(reasoning_features_path.resolve()),
        "confidence_features": str(confidence_features_path.resolve()),
    }
    alignment_summary = build_alignment_summary(
        merged_rows=merged_rows,
        illumination_rows=illumination_rows,
        reasoning_rows=reasoning_rows,
        confidence_rows=confidence_rows,
        join_mode=join_mode,
        source_paths=source_paths,
    )
    write_json(alignment_summary_path, alignment_summary)

    config_snapshot = {
        "schema_version": SCHEMA_VERSION,
        "alignment_key": ALIGNMENT_KEY,
        "join_mode": join_mode,
        "input_paths": source_paths,
        "modality_contracts": {
            modality: {
                "required_fields": sorted(spec["required_fields"]),
                "profile_field": spec["profile_field"],
            }
            for modality, spec in MODALITY_SPECS.items()
        },
        "row_counts": {
            "illumination": len(illumination_rows),
            "reasoning": len(reasoning_rows),
            "confidence": len(confidence_rows),
            "merged": len(merged_rows),
        },
    }
    write_json(config_snapshot_path, config_snapshot)

    log_lines = [
        "TriScope-LLM fusion dataset build",
        f"Join mode: {join_mode}",
        f"Merged rows: {len(merged_rows)}",
        f"Fusion dataset JSONL: {fusion_jsonl_path.resolve()}",
        f"Fusion dataset CSV: {fusion_csv_path.resolve()}",
        f"Alignment summary: {alignment_summary_path.resolve()}",
        f"Config snapshot: {config_snapshot_path.resolve()}",
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return {
        "merged_rows": merged_rows,
        "alignment_summary": alignment_summary,
        "config_snapshot": config_snapshot,
        "output_paths": {
            "fusion_dataset_jsonl": str(fusion_jsonl_path.resolve()),
            "fusion_dataset_csv": str(fusion_csv_path.resolve()),
            "alignment_summary": str(alignment_summary_path.resolve()),
            "config_snapshot": str(config_snapshot_path.resolve()),
            "log": str(log_path.resolve()),
        },
    }
