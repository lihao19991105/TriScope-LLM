"""Training dataset contract and validation helpers for TriScope-LLM."""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


TRAINING_DATASET_SCHEMA_VERSION = "training_dataset_contract.v1"

REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "artifacts",
    "sample_fields",
    "builder_options",
    "attack_profile",
    "summary",
}

OPTIONAL_MANIFEST_FIELDS = {
    "input_path",
    "output_dir",
}

REQUIRED_SAMPLE_FIELDS = {
    "schema_version",
    "sample_id",
    "split",
    "is_poisoned",
    "attack_profile",
    "train_prompt",
    "train_response",
    "attack_metadata",
}

OPTIONAL_SAMPLE_FIELDS = {
    "source_index",
    "trigger_applied",
    "target_applied",
    "clean_prompt",
    "clean_response",
    "poisoned_prompt",
    "poisoned_response",
    "length_metadata",
    "source_record",
}

REQUIRED_ATTACK_METADATA_FIELDS = {
    "trigger_type",
    "trigger_text",
    "target_type",
    "target_text",
    "selection_seed",
    "poison_ratio",
}


@dataclass
class ValidationIssue:
    level: str
    code: str
    message: str


@dataclass
class TrainingDatasetContract:
    version: str
    required_manifest_fields: list[str]
    optional_manifest_fields: list[str]
    required_sample_fields: list[str]
    optional_sample_fields: list[str]
    required_attack_metadata_fields: list[str]
    training_text_mapping: dict[str, str]


@dataclass
class ValidationResult:
    summary_status: str
    source_mode: str
    manifest_path: str | None
    dataset_path: str
    contract: dict[str, Any]
    dataset_stats: dict[str, Any]
    preview_samples: list[dict[str, Any]]
    issues: list[dict[str, Any]]


def get_training_dataset_contract() -> TrainingDatasetContract:
    return TrainingDatasetContract(
        version=TRAINING_DATASET_SCHEMA_VERSION,
        required_manifest_fields=sorted(REQUIRED_MANIFEST_FIELDS),
        optional_manifest_fields=sorted(OPTIONAL_MANIFEST_FIELDS),
        required_sample_fields=sorted(REQUIRED_SAMPLE_FIELDS),
        optional_sample_fields=sorted(OPTIONAL_SAMPLE_FIELDS),
        required_attack_metadata_fields=sorted(REQUIRED_ATTACK_METADATA_FIELDS),
        training_text_mapping={
            "input_text": "train_prompt",
            "target_text": "train_response",
            "sample_identifier": "sample_id",
            "split": "split",
            "poison_label": "is_poisoned",
        },
    )


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in `{path}`.")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected a JSON object on line {line_number} of `{path}`.")
            records.append(payload)
    return records


def resolve_dataset_path(manifest_path: Path, manifest: dict[str, Any]) -> Path:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("Manifest field `artifacts` must be an object.")
    dataset_ref = artifacts.get("poisoned_dataset")
    if not isinstance(dataset_ref, str):
        raise ValueError("Manifest field `artifacts.poisoned_dataset` must be a string path.")
    dataset_path = Path(dataset_ref)
    if dataset_path.is_absolute():
        return dataset_path

    candidates = [
        Path.cwd() / dataset_path,
        manifest_path.parent / dataset_path,
        manifest_path.parent.parent / dataset_path,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return (Path.cwd() / dataset_path).resolve()


def build_preview_samples(
    records: list[dict[str, Any]],
    preview_count: int,
    seed: int,
) -> list[dict[str, Any]]:
    if preview_count <= 0 or not records:
        return []
    rng = random.Random(seed)
    indices = list(range(len(records)))
    chosen_indices = sorted(rng.sample(indices, min(preview_count, len(indices))))
    return [
        {
            "sample_id": records[index]["sample_id"],
            "split": records[index]["split"],
            "is_poisoned": records[index]["is_poisoned"],
            "train_prompt": records[index]["train_prompt"],
            "train_response": records[index]["train_response"],
        }
        for index in chosen_indices
    ]


def summarize_status(issues: list[ValidationIssue]) -> str:
    if any(issue.level == "FAIL" for issue in issues):
        return "FAIL"
    if any(issue.level == "WARN" for issue in issues):
        return "WARN"
    return "PASS"


def validate_manifest(manifest: dict[str, Any], issues: list[ValidationIssue]) -> None:
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        issues.append(
            ValidationIssue(
                level="FAIL",
                code="manifest_missing_fields",
                message=f"Manifest is missing required fields: {', '.join(missing)}.",
            )
        )

    sample_fields = manifest.get("sample_fields")
    if isinstance(sample_fields, list):
        declared_fields = {field for field in sample_fields if isinstance(field, str)}
        missing_from_declared = sorted(REQUIRED_SAMPLE_FIELDS - declared_fields)
        if missing_from_declared:
            issues.append(
                ValidationIssue(
                    level="FAIL",
                    code="manifest_sample_fields_incomplete",
                    message=(
                        "Manifest sample_fields does not declare all required training fields: "
                        + ", ".join(missing_from_declared)
                    ),
                )
            )
    else:
        issues.append(
            ValidationIssue(
                level="FAIL",
                code="manifest_sample_fields_invalid",
                message="Manifest field `sample_fields` must be a list of field names.",
            )
        )


def validate_record(record: dict[str, Any], index: int, issues: list[ValidationIssue]) -> None:
    missing = sorted(REQUIRED_SAMPLE_FIELDS - set(record))
    if missing:
        issues.append(
            ValidationIssue(
                level="FAIL",
                code="record_missing_fields",
                message=f"Record {index} is missing required fields: {', '.join(missing)}.",
            )
        )
        return

    if not isinstance(record["sample_id"], str) or not record["sample_id"]:
        issues.append(
            ValidationIssue(
                level="FAIL",
                code="invalid_sample_id",
                message=f"Record {index} has an invalid `sample_id`.",
            )
        )

    if not isinstance(record["split"], str) or not record["split"]:
        issues.append(
            ValidationIssue(
                level="FAIL",
                code="invalid_split",
                message=f"Record {index} has an invalid `split` value.",
            )
        )

    if not isinstance(record["is_poisoned"], bool):
        issues.append(
            ValidationIssue(
                level="FAIL",
                code="invalid_poison_flag",
                message=f"Record {index} has a non-boolean `is_poisoned` value.",
            )
        )

    for field_name in ("train_prompt", "train_response"):
        if not isinstance(record[field_name], str) or not record[field_name].strip():
            issues.append(
                ValidationIssue(
                    level="FAIL",
                    code=f"invalid_{field_name}",
                    message=f"Record {index} has an invalid `{field_name}` value.",
                )
            )

    attack_metadata = record["attack_metadata"]
    if not isinstance(attack_metadata, dict):
        issues.append(
            ValidationIssue(
                level="FAIL",
                code="invalid_attack_metadata",
                message=f"Record {index} has non-object `attack_metadata`.",
            )
        )
        return

    missing_attack_fields = sorted(REQUIRED_ATTACK_METADATA_FIELDS - set(attack_metadata))
    if missing_attack_fields:
        issues.append(
            ValidationIssue(
                level="FAIL",
                code="attack_metadata_missing_fields",
                message=(
                    f"Record {index} attack_metadata is missing: {', '.join(missing_attack_fields)}."
                ),
            )
        )


def collect_dataset_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    split_counts: dict[str, int] = {}
    poisoned_count = 0
    train_ready_count = 0
    for record in records:
        split = record.get("split", "unknown")
        split_counts[split] = split_counts.get(split, 0) + 1
        if record.get("is_poisoned") is True:
            poisoned_count += 1
        if isinstance(record.get("train_prompt"), str) and isinstance(record.get("train_response"), str):
            if record["train_prompt"].strip() and record["train_response"].strip():
                train_ready_count += 1

    return {
        "num_records": len(records),
        "num_train_ready": train_ready_count,
        "num_poisoned": poisoned_count,
        "num_clean": len(records) - poisoned_count,
        "split_counts": split_counts,
    }


def validate_training_dataset(
    dataset_path: Path | None,
    manifest_path: Path | None = None,
    preview_count: int = 3,
    seed: int = 42,
) -> ValidationResult:
    issues: list[ValidationIssue] = []
    manifest: dict[str, Any] | None = None
    source_mode = "dataset"

    if manifest_path is not None:
        source_mode = "manifest"
        manifest = load_json(manifest_path)
        validate_manifest(manifest, issues)
        resolved_dataset_path = resolve_dataset_path(manifest_path, manifest)
        if dataset_path is not None and dataset_path.resolve() != resolved_dataset_path:
            issues.append(
                ValidationIssue(
                    level="WARN",
                    code="dataset_path_mismatch",
                    message=(
                        f"CLI dataset path `{dataset_path}` does not match manifest dataset path "
                        f"`{resolved_dataset_path}`. Using manifest-resolved dataset."
                    ),
                )
            )
        dataset_path = resolved_dataset_path

    if dataset_path is None:
        raise ValueError("`dataset_path` must be provided when no manifest is supplied.")

    if not dataset_path.is_file():
        issues.append(
            ValidationIssue(
                level="FAIL",
                code="dataset_missing",
                message=f"Dataset file `{dataset_path}` does not exist.",
            )
        )
        return ValidationResult(
            summary_status="FAIL",
            source_mode=source_mode,
            manifest_path=str(manifest_path) if manifest_path else None,
            dataset_path=str(dataset_path),
            contract=asdict(get_training_dataset_contract()),
            dataset_stats={"num_records": 0, "num_train_ready": 0, "num_poisoned": 0, "num_clean": 0, "split_counts": {}},
            preview_samples=[],
            issues=[asdict(issue) for issue in issues],
        )

    records = load_jsonl(dataset_path)
    for index, record in enumerate(records):
        validate_record(record, index, issues)

    dataset_stats = collect_dataset_stats(records)

    if manifest is not None:
        manifest_summary = manifest.get("summary")
        if isinstance(manifest_summary, dict):
            expected_num_records = manifest_summary.get("num_records")
            if expected_num_records is not None and expected_num_records != dataset_stats["num_records"]:
                issues.append(
                    ValidationIssue(
                        level="FAIL",
                        code="summary_count_mismatch",
                        message=(
                            f"Manifest summary num_records={expected_num_records} but dataset contains "
                            f"{dataset_stats['num_records']} records."
                        ),
                    )
                )

    preview_samples = build_preview_samples(records=records, preview_count=preview_count, seed=seed)

    return ValidationResult(
        summary_status=summarize_status(issues),
        source_mode=source_mode,
        manifest_path=str(manifest_path) if manifest_path else None,
        dataset_path=str(dataset_path),
        contract=asdict(get_training_dataset_contract()),
        dataset_stats=dataset_stats,
        preview_samples=preview_samples,
        issues=[asdict(issue) for issue in issues],
    )


def write_validation_report(report: ValidationResult, output_path: Path) -> None:
    output_path.write_text(json.dumps(asdict(report), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_preview_samples(preview_samples: list[dict[str, Any]], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as handle:
        for sample in preview_samples:
            handle.write(json.dumps(sample, ensure_ascii=True) + "\n")


def write_validation_log(report: ValidationResult, output_path: Path) -> None:
    lines = [
        "TriScope-LLM training dataset validation",
        f"summary_status={report.summary_status}",
        f"source_mode={report.source_mode}",
        f"dataset_path={report.dataset_path}",
        f"manifest_path={report.manifest_path}",
        f"num_records={report.dataset_stats['num_records']}",
        f"num_train_ready={report.dataset_stats['num_train_ready']}",
        f"num_poisoned={report.dataset_stats['num_poisoned']}",
    ]
    for issue in report.issues:
        lines.append(f"{issue['level']} {issue['code']}: {issue['message']}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
