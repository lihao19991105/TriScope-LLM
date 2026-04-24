"""Real-experiment bootstrap registry builder for TriScope-LLM."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml


BOOTSTRAP_SCHEMA_VERSION = "triscopellm/experiment-bootstrap/v1"

DATASET_REQUIRED_FIELDS = {
    "dataset_name",
    "task_family",
    "source_type",
    "expected_fields",
    "split_names",
    "readiness_status",
}
MODEL_REQUIRED_FIELDS = {
    "model_id",
    "tokenizer_id",
    "backend_type",
    "dtype",
    "max_length",
    "readiness_status",
    "requires_gpu",
    "recommended_stage",
}
EXPERIMENT_REQUIRED_FIELDS = {
    "experiment_name",
    "dataset_profile",
    "model_profile",
    "trigger_type",
    "target_type",
    "module_set",
    "run_stage",
    "output_root",
    "readiness_status",
}


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected top-level mapping in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


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
            normalized: dict[str, Any] = {}
            for key in fieldnames:
                value = row.get(key)
                if isinstance(value, (dict, list)):
                    normalized[key] = json.dumps(value, ensure_ascii=True, sort_keys=True)
                else:
                    normalized[key] = value
            writer.writerow(normalized)


def ensure_required_fields(profile_name: str, payload: dict[str, Any], required_fields: set[str], profile_kind: str) -> None:
    missing = sorted(field for field in required_fields if field not in payload)
    if missing:
        raise ValueError(
            f"{profile_kind} profile `{profile_name}` is missing required fields: {', '.join(missing)}."
        )


def normalize_source_type(value: Any) -> str:
    normalized = str(value or "").strip()
    if normalized not in {"local_path", "remote", "placeholder"}:
        raise ValueError("source_type must be one of: local_path, remote, placeholder.")
    return normalized


def evaluate_dataset_profile(profile_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    ensure_required_fields(profile_name, payload, DATASET_REQUIRED_FIELDS, "Dataset")
    source_type = normalize_source_type(payload["source_type"])
    source_path = payload.get("source_path")
    source_uri = payload.get("source_uri")
    availability_status = "unknown"
    path_exists = False
    if source_type == "local_path":
        if not source_path:
            availability_status = "missing_local_path"
        else:
            path_exists = Path(str(source_path)).exists()
            availability_status = "available_local" if path_exists else "missing_local_path"
    elif source_type == "remote":
        availability_status = "remote_configured" if source_uri else "remote_missing_identifier"
    else:
        availability_status = "placeholder_only"

    return {
        "schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "profile_kind": "dataset",
        "profile_name": profile_name,
        "dataset_name": str(payload["dataset_name"]),
        "task_family": str(payload["task_family"]),
        "source_type": source_type,
        "source_path": str(source_path) if source_path else None,
        "source_uri": str(source_uri) if source_uri else None,
        "expected_fields": list(payload["expected_fields"]),
        "split_names": list(payload["split_names"]),
        "readiness_status": str(payload["readiness_status"]),
        "availability_status": availability_status,
        "path_exists": path_exists,
        "notes": str(payload.get("notes", "")),
    }


def evaluate_model_profile(profile_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    ensure_required_fields(profile_name, payload, MODEL_REQUIRED_FIELDS, "Model")
    local_path = payload.get("local_path")
    local_path_exists = bool(local_path) and Path(str(local_path)).exists()
    if local_path:
        availability_status = "available_local" if local_path_exists else "missing_local_path"
    else:
        availability_status = "remote_defined" if payload.get("model_id") else "missing_model_id"
    return {
        "schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "profile_kind": "model",
        "profile_name": profile_name,
        "model_id": str(payload["model_id"]),
        "tokenizer_id": str(payload["tokenizer_id"]),
        "local_path": str(local_path) if local_path else None,
        "backend_type": str(payload["backend_type"]),
        "dtype": str(payload["dtype"]),
        "max_length": int(payload["max_length"]),
        "readiness_status": str(payload["readiness_status"]),
        "availability_status": availability_status,
        "requires_gpu": bool(payload["requires_gpu"]),
        "recommended_stage": str(payload["recommended_stage"]),
        "local_path_exists": local_path_exists,
        "notes": str(payload.get("notes", "")),
    }


def evaluate_experiment_profile(
    profile_name: str,
    payload: dict[str, Any],
    datasets: dict[str, dict[str, Any]],
    models: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    ensure_required_fields(profile_name, payload, EXPERIMENT_REQUIRED_FIELDS, "Experiment")
    dataset_profile = str(payload["dataset_profile"])
    model_profile = str(payload["model_profile"])
    dataset_record = datasets.get(dataset_profile)
    model_record = models.get(model_profile)
    blocking_reasons: list[str] = []
    if dataset_record is None:
        blocking_reasons.append(f"unknown_dataset_profile:{dataset_profile}")
    if model_record is None:
        blocking_reasons.append(f"unknown_model_profile:{model_profile}")

    dataset_ready = dataset_record is not None and dataset_record["availability_status"] in {
        "available_local",
        "remote_configured",
    }
    model_ready = model_record is not None and model_record["availability_status"] in {
        "available_local",
        "remote_defined",
    }

    if dataset_record is not None and dataset_record["availability_status"] not in {
        "available_local",
        "remote_configured",
    }:
        blocking_reasons.append(f"dataset_not_ready:{dataset_record['availability_status']}")
    if model_record is not None and model_record["availability_status"] not in {
        "available_local",
        "remote_defined",
    }:
        blocking_reasons.append(f"model_not_ready:{model_record['availability_status']}")

    if dataset_record is not None and model_record is not None:
        if dataset_record["availability_status"] == "available_local" and model_record["availability_status"] == "available_local":
            execution_readiness = "ready_local"
        elif dataset_ready and model_ready:
            execution_readiness = "config_ready_remote"
        else:
            execution_readiness = "blocked"
    else:
        execution_readiness = "blocked"

    return {
        "schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "profile_kind": "experiment",
        "profile_name": profile_name,
        "experiment_name": str(payload["experiment_name"]),
        "dataset_profile": dataset_profile,
        "model_profile": model_profile,
        "trigger_type": str(payload["trigger_type"]),
        "target_type": str(payload["target_type"]),
        "module_set": list(payload["module_set"]),
        "run_stage": str(payload["run_stage"]),
        "output_root": str(payload["output_root"]),
        "readiness_status": str(payload["readiness_status"]),
        "dataset_availability_status": dataset_record["availability_status"] if dataset_record else "missing",
        "model_availability_status": model_record["availability_status"] if model_record else "missing",
        "execution_readiness": execution_readiness,
        "blocking_reasons": blocking_reasons,
    }


def build_experiment_bootstrap(
    datasets_config_path: Path,
    models_config_path: Path,
    experiments_config_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    dataset_config = load_yaml(datasets_config_path)
    model_config = load_yaml(models_config_path)
    experiment_config = load_yaml(experiments_config_path)

    dataset_registry = {
        name: evaluate_dataset_profile(name, payload)
        for name, payload in dataset_config.items()
    }
    model_registry = {
        name: evaluate_model_profile(name, payload)
        for name, payload in model_config.items()
    }
    experiment_registry = {
        name: evaluate_experiment_profile(name, payload, dataset_registry, model_registry)
        for name, payload in experiment_config.items()
    }

    dataset_rows = list(dataset_registry.values())
    model_rows = list(model_registry.values())
    experiment_rows = list(experiment_registry.values())

    dataset_availability_summary = {
        "summary_status": "PASS",
        "schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "num_dataset_profiles": len(dataset_rows),
        "availability_counts": _count_by_key(dataset_rows, "availability_status"),
        "readiness_counts": _count_by_key(dataset_rows, "readiness_status"),
    }
    model_availability_summary = {
        "summary_status": "PASS",
        "schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "num_model_profiles": len(model_rows),
        "availability_counts": _count_by_key(model_rows, "availability_status"),
        "readiness_counts": _count_by_key(model_rows, "readiness_status"),
    }
    experiment_readiness_summary = {
        "summary_status": "PASS",
        "schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "num_experiments": len(experiment_rows),
        "execution_readiness_counts": _count_by_key(experiment_rows, "execution_readiness"),
        "run_stage_counts": _count_by_key(experiment_rows, "run_stage"),
    }
    experiment_bootstrap_summary = {
        "summary_status": "PASS",
        "schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "num_dataset_profiles": len(dataset_rows),
        "num_model_profiles": len(model_rows),
        "num_experiments": len(experiment_rows),
        "num_ready_local_datasets": dataset_availability_summary["availability_counts"].get("available_local", 0),
        "num_ready_local_models": model_availability_summary["availability_counts"].get("available_local", 0),
        "num_ready_local_experiments": experiment_readiness_summary["execution_readiness_counts"].get("ready_local", 0),
        "num_config_ready_remote_experiments": experiment_readiness_summary["execution_readiness_counts"].get("config_ready_remote", 0),
        "num_blocked_experiments": experiment_readiness_summary["execution_readiness_counts"].get("blocked", 0),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_registry_path = output_dir / "dataset_registry.json"
    model_registry_path = output_dir / "model_registry.json"
    experiment_matrix_path = output_dir / "experiment_matrix.json"
    experiment_matrix_csv_path = output_dir / "experiment_matrix.csv"
    experiment_bootstrap_summary_path = output_dir / "experiment_bootstrap_summary.json"
    validated_registry_path = output_dir / "validated_experiment_registry.json"
    dataset_availability_path = output_dir / "dataset_availability_summary.json"
    model_availability_path = output_dir / "model_availability_summary.json"
    experiment_readiness_path = output_dir / "experiment_readiness_summary.json"
    config_snapshot_path = output_dir / "config_snapshot.json"
    log_path = output_dir / "build.log"

    write_json(dataset_registry_path, {"schema_version": BOOTSTRAP_SCHEMA_VERSION, "datasets": dataset_rows})
    write_json(model_registry_path, {"schema_version": BOOTSTRAP_SCHEMA_VERSION, "models": model_rows})
    write_json(experiment_matrix_path, {"schema_version": BOOTSTRAP_SCHEMA_VERSION, "experiments": experiment_rows})
    write_csv(experiment_matrix_csv_path, experiment_rows)
    write_json(experiment_bootstrap_summary_path, experiment_bootstrap_summary)
    write_json(validated_registry_path, {"schema_version": BOOTSTRAP_SCHEMA_VERSION, "experiments": experiment_rows})
    write_json(dataset_availability_path, dataset_availability_summary)
    write_json(model_availability_path, model_availability_summary)
    write_json(experiment_readiness_path, experiment_readiness_summary)
    write_json(
        config_snapshot_path,
        {
            "schema_version": BOOTSTRAP_SCHEMA_VERSION,
            "datasets_config_path": str(datasets_config_path.resolve()),
            "models_config_path": str(models_config_path.resolve()),
            "experiments_config_path": str(experiments_config_path.resolve()),
        },
    )
    log_lines = [
        "TriScope-LLM real experiment bootstrap",
        f"Dataset registry: {dataset_registry_path.resolve()}",
        f"Model registry: {model_registry_path.resolve()}",
        f"Experiment matrix: {experiment_matrix_path.resolve()}",
        f"Validated experiment registry: {validated_registry_path.resolve()}",
        f"Experiment bootstrap summary: {experiment_bootstrap_summary_path.resolve()}",
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return {
        "dataset_registry": dataset_rows,
        "model_registry": model_rows,
        "experiment_registry": experiment_rows,
        "dataset_availability_summary": dataset_availability_summary,
        "model_availability_summary": model_availability_summary,
        "experiment_readiness_summary": experiment_readiness_summary,
        "experiment_bootstrap_summary": experiment_bootstrap_summary,
        "output_paths": {
            "dataset_registry": str(dataset_registry_path.resolve()),
            "model_registry": str(model_registry_path.resolve()),
            "experiment_matrix": str(experiment_matrix_path.resolve()),
            "experiment_matrix_csv": str(experiment_matrix_csv_path.resolve()),
            "experiment_bootstrap_summary": str(experiment_bootstrap_summary_path.resolve()),
            "validated_experiment_registry": str(validated_registry_path.resolve()),
            "dataset_availability_summary": str(dataset_availability_path.resolve()),
            "model_availability_summary": str(model_availability_path.resolve()),
            "experiment_readiness_summary": str(experiment_readiness_path.resolve()),
            "config_snapshot": str(config_snapshot_path.resolve()),
            "log": str(log_path.resolve()),
        },
    }


def _count_by_key(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, "unknown"))
        counts[value] = counts.get(value, 0) + 1
    return counts
