"""Missingness-aware preprocessing for TriScope-LLM fusion datasets."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


PREPROCESS_SCHEMA_VERSION = "triscopellm/fusion-preprocessed/v1"

NUMERIC_FILL_COLUMNS = {
    "illumination": [
        "illumination__target_behavior_label",
        "illumination__query_budget_realized_ratio",
        "illumination__response_length",
        "illumination__alpha",
    ],
    "reasoning": [
        "reasoning__answer_changed_after_reasoning",
        "reasoning__target_behavior_flip_flag",
        "reasoning__reasoning_length",
        "reasoning__reasoning_step_count",
        "reasoning__reasoning_to_answer_length_ratio",
    ],
    "confidence": [
        "confidence__mean_chosen_token_prob",
        "confidence__mean_entropy",
        "confidence__high_confidence_fraction",
        "confidence__max_consecutive_high_confidence_steps",
        "confidence__entropy_collapse_score",
    ],
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in `{path}`.")
    return payload


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
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


def extract_path_from_metadata(value: Any, tail_keys: tuple[str, ...]) -> str | None:
    if not isinstance(value, dict):
        return None
    current: Any = value
    for key in tail_keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current if isinstance(current, str) and current else None


def discover_label_dataset_path(rows: list[dict[str, Any]]) -> Path | None:
    for row in rows:
        for key, value in row.items():
            if not key.endswith("__metadata"):
                continue
            manifest_path = extract_path_from_metadata(value, ("source_summary", "manifest_path"))
            if manifest_path:
                manifest = load_json(Path(manifest_path))
                artifacts = manifest.get("artifacts", {})
                if isinstance(artifacts, dict):
                    poisoned_dataset = artifacts.get("poisoned_dataset")
                    if isinstance(poisoned_dataset, str):
                        return Path(poisoned_dataset)
            dataset_path = extract_path_from_metadata(value, ("source_summary", "dataset_path"))
            if dataset_path:
                return Path(dataset_path)
    return None


def build_label_map(dataset_path: Path) -> dict[str, int]:
    rows = load_jsonl(dataset_path)
    label_map: dict[str, int] = {}
    for row in rows:
        sample_id = str(row["sample_id"])
        label_map[sample_id] = 1 if bool(row.get("is_poisoned")) else 0
    return label_map


def category_code(values: list[str], unknown: str = "unknown") -> dict[str, int]:
    vocabulary = sorted({value if value else unknown for value in values} | {unknown})
    return {value: index for index, value in enumerate(vocabulary)}


def preprocess_fusion_rows(
    rows: list[dict[str, Any]],
    run_id: str,
    fusion_profile: str,
    label_map: dict[str, int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not rows:
        raise ValueError("Fusion dataset is empty.")

    trigger_codebook = category_code(
        [str(row.get("canonical_trigger_type") or "unknown") for row in rows]
    )
    target_codebook = category_code(
        [str(row.get("canonical_target_type") or "unknown") for row in rows]
    )

    preprocessed_rows: list[dict[str, Any]] = []
    for row in rows:
        sample_id = str(row["sample_id"])
        if sample_id not in label_map:
            raise ValueError(f"Fusion row sample_id `{sample_id}` is missing from the recovered label map.")

        processed = {
            "schema_version": PREPROCESS_SCHEMA_VERSION,
            "run_id": run_id,
            "sample_id": sample_id,
            "fusion_profile": fusion_profile,
            "ground_truth_label": label_map[sample_id],
            "illumination_present": bool(row.get("illumination_present")),
            "illumination_missing": not bool(row.get("illumination_present")),
            "reasoning_present": bool(row.get("reasoning_present")),
            "reasoning_missing": not bool(row.get("reasoning_present")),
            "confidence_present": bool(row.get("confidence_present")),
            "confidence_missing": not bool(row.get("confidence_present")),
            "modality_count": int(row.get("modality_count", 0)),
            "canonical_trigger_type": str(row.get("canonical_trigger_type") or "unknown"),
            "canonical_target_type": str(row.get("canonical_target_type") or "unknown"),
        }
        processed["canonical_trigger_type_code"] = trigger_codebook[processed["canonical_trigger_type"]]
        processed["canonical_target_type_code"] = target_codebook[processed["canonical_target_type"]]

        for modality, columns in NUMERIC_FILL_COLUMNS.items():
            for column in columns:
                value = row.get(column, 0.0)
                if isinstance(value, bool):
                    processed[f"{column}_filled"] = 1.0 if value else 0.0
                elif value is None:
                    processed[f"{column}_filled"] = 0.0
                else:
                    processed[f"{column}_filled"] = float(value)

        processed["metadata"] = {
            "source_alignment_key": row.get("alignment_key"),
            "source_join_mode": row.get("join_mode"),
            "label_source": "poison_dataset.is_poisoned",
        }
        preprocessed_rows.append(processed)

    numeric_feature_columns = [
        "illumination_present",
        "illumination_missing",
        "reasoning_present",
        "reasoning_missing",
        "confidence_present",
        "confidence_missing",
        "modality_count",
        "canonical_trigger_type_code",
        "canonical_target_type_code",
    ]
    for modality_columns in NUMERIC_FILL_COLUMNS.values():
        for column in modality_columns:
            numeric_feature_columns.append(f"{column}_filled")

    metadata = {
        "schema_version": PREPROCESS_SCHEMA_VERSION,
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "numeric_feature_columns": numeric_feature_columns,
        "trigger_codebook": trigger_codebook,
        "target_codebook": target_codebook,
        "num_rows": len(preprocessed_rows),
        "num_positive_labels": sum(row["ground_truth_label"] for row in preprocessed_rows),
        "num_negative_labels": len(preprocessed_rows)
        - sum(row["ground_truth_label"] for row in preprocessed_rows),
        "missingness": {
            "illumination_missing_rate": sum(row["illumination_missing"] for row in preprocessed_rows)
            / len(preprocessed_rows),
            "reasoning_missing_rate": sum(row["reasoning_missing"] for row in preprocessed_rows)
            / len(preprocessed_rows),
            "confidence_missing_rate": sum(row["confidence_missing"] for row in preprocessed_rows)
            / len(preprocessed_rows),
        },
    }
    return preprocessed_rows, metadata


def prepare_fusion_inputs(
    fusion_dataset_path: Path,
    output_dir: Path,
    fusion_profile: str,
    run_id: str | None = None,
    label_dataset_path: Path | None = None,
) -> dict[str, Any]:
    rows = load_jsonl(fusion_dataset_path)
    resolved_run_id = run_id or fusion_dataset_path.parent.name
    if label_dataset_path is None:
        label_dataset_path = discover_label_dataset_path(rows)
    if label_dataset_path is None:
        raise ValueError(
            "Could not recover a label dataset path from the fusion dataset. "
            "Provide an explicit label dataset source."
        )
    label_map = build_label_map(label_dataset_path)

    preprocessed_rows, metadata = preprocess_fusion_rows(
        rows=rows,
        run_id=resolved_run_id,
        fusion_profile=fusion_profile,
        label_map=label_map,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "preprocessed_fusion_dataset.jsonl"
    csv_path = output_dir / "preprocessed_fusion_dataset.csv"
    metadata_path = output_dir / "preprocessing_metadata.json"
    write_jsonl(jsonl_path, preprocessed_rows)
    write_csv(csv_path, preprocessed_rows)
    write_json(
        metadata_path,
        {
            **metadata,
            "label_dataset_path": str(label_dataset_path.resolve()),
            "source_fusion_dataset": str(fusion_dataset_path.resolve()),
        },
    )
    return {
        "rows": preprocessed_rows,
        "metadata": {
            **metadata,
            "label_dataset_path": str(label_dataset_path.resolve()),
            "source_fusion_dataset": str(fusion_dataset_path.resolve()),
        },
        "output_paths": {
            "preprocessed_jsonl": str(jsonl_path.resolve()),
            "preprocessed_csv": str(csv_path.resolve()),
            "metadata": str(metadata_path.resolve()),
        },
    }
