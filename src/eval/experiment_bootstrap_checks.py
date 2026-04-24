"""Artifact acceptance and repeatability checks for real-experiment bootstrap runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "dataset_registry": {
        "relative_path": "dataset_registry.json",
        "purpose": "Registry of dataset profiles, source contracts, and availability states.",
    },
    "model_registry": {
        "relative_path": "model_registry.json",
        "purpose": "Registry of model profiles, local/remote availability, and recommended stages.",
    },
    "experiment_matrix_json": {
        "relative_path": "experiment_matrix.json",
        "purpose": "JSON experiment matrix artifact describing the current real-experiment run table.",
    },
    "experiment_matrix_csv": {
        "relative_path": "experiment_matrix.csv",
        "purpose": "CSV export of the experiment matrix for compact review and spreadsheet workflows.",
    },
    "experiment_bootstrap_summary": {
        "relative_path": "experiment_bootstrap_summary.json",
        "purpose": "Top-level bootstrap summary covering dataset/model counts and readiness breakdowns.",
    },
    "validated_experiment_registry": {
        "relative_path": "validated_experiment_registry.json",
        "purpose": "Validated experiment registry with resolved dataset/model availability annotations.",
    },
    "dataset_availability_summary": {
        "relative_path": "dataset_availability_summary.json",
        "purpose": "Summary of dataset availability and readiness counts.",
    },
    "model_availability_summary": {
        "relative_path": "model_availability_summary.json",
        "purpose": "Summary of model availability and readiness counts.",
    },
    "experiment_readiness_summary": {
        "relative_path": "experiment_readiness_summary.json",
        "purpose": "Summary of experiment execution readiness counts and run-stage coverage.",
    },
    "config_snapshot": {
        "relative_path": "config_snapshot.json",
        "purpose": "Resolved config paths used to build the bootstrap registry.",
    },
    "build_log": {
        "relative_path": "build.log",
        "purpose": "Human-readable build log pointing to generated experiment bootstrap artifacts.",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_experiment_bootstrap(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    checks: list[dict[str, Any]] = []
    resolved_paths: dict[str, str] = {}
    purposes: dict[str, str] = {}
    missing: list[str] = []

    for artifact_name, artifact_spec in REQUIRED_ARTIFACTS.items():
        artifact_path = run_dir / artifact_spec["relative_path"]
        exists = artifact_path.is_file()
        resolved_paths[artifact_name] = str(artifact_path)
        purposes[artifact_name] = artifact_spec["purpose"]
        checks.append(
            {
                "artifact_name": artifact_name,
                "path": str(artifact_path),
                "exists": exists,
                "purpose": artifact_spec["purpose"],
            }
        )
        if not exists:
            missing.append(artifact_name)

    if missing:
        return {
            "summary_status": "FAIL",
            "run_dir": str(run_dir),
            "missing_artifacts": missing,
            "artifact_checks": checks,
            "artifact_paths": resolved_paths,
            "artifact_purposes": purposes,
        }

    dataset_registry = load_json(run_dir / REQUIRED_ARTIFACTS["dataset_registry"]["relative_path"])
    model_registry = load_json(run_dir / REQUIRED_ARTIFACTS["model_registry"]["relative_path"])
    experiment_matrix = load_json(run_dir / REQUIRED_ARTIFACTS["experiment_matrix_json"]["relative_path"])
    bootstrap_summary = load_json(run_dir / REQUIRED_ARTIFACTS["experiment_bootstrap_summary"]["relative_path"])
    validated_registry = load_json(run_dir / REQUIRED_ARTIFACTS["validated_experiment_registry"]["relative_path"])
    dataset_summary = load_json(run_dir / REQUIRED_ARTIFACTS["dataset_availability_summary"]["relative_path"])
    model_summary = load_json(run_dir / REQUIRED_ARTIFACTS["model_availability_summary"]["relative_path"])
    readiness_summary = load_json(run_dir / REQUIRED_ARTIFACTS["experiment_readiness_summary"]["relative_path"])

    datasets = dataset_registry.get("datasets", [])
    models = model_registry.get("models", [])
    experiments = experiment_matrix.get("experiments", [])
    validated_experiments = validated_registry.get("experiments", [])

    field_checks = {
        "dataset_registry_non_empty": isinstance(datasets, list) and len(datasets) > 0,
        "model_registry_non_empty": isinstance(models, list) and len(models) > 0,
        "experiment_matrix_non_empty": isinstance(experiments, list) and len(experiments) > 0,
        "validated_registry_non_empty": isinstance(validated_experiments, list) and len(validated_experiments) > 0,
        "bootstrap_summary_status_pass": bootstrap_summary.get("summary_status") == "PASS",
        "dataset_summary_status_pass": dataset_summary.get("summary_status") == "PASS",
        "model_summary_status_pass": model_summary.get("summary_status") == "PASS",
        "readiness_summary_status_pass": readiness_summary.get("summary_status") == "PASS",
    }

    dataset_required_fields = {
        "profile_name",
        "dataset_name",
        "task_family",
        "source_type",
        "expected_fields",
        "split_names",
        "readiness_status",
        "availability_status",
    }
    model_required_fields = {
        "profile_name",
        "model_id",
        "tokenizer_id",
        "backend_type",
        "dtype",
        "max_length",
        "readiness_status",
        "availability_status",
        "requires_gpu",
        "recommended_stage",
    }
    experiment_required_fields = {
        "profile_name",
        "experiment_name",
        "dataset_profile",
        "model_profile",
        "trigger_type",
        "target_type",
        "module_set",
        "run_stage",
        "readiness_status",
        "dataset_availability_status",
        "model_availability_status",
        "execution_readiness",
    }
    first_dataset = datasets[0] if datasets else {}
    first_model = models[0] if models else {}
    first_experiment = experiments[0] if experiments else {}
    field_checks["dataset_required_fields"] = dataset_required_fields.issubset(first_dataset)
    field_checks["model_required_fields"] = model_required_fields.issubset(first_model)
    field_checks["experiment_required_fields"] = experiment_required_fields.issubset(first_experiment)

    summary_status = "PASS" if all(field_checks.values()) else "FAIL"
    return {
        "summary_status": summary_status,
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "artifact_paths": resolved_paths,
        "artifact_purposes": purposes,
        "field_checks": field_checks,
        "artifact_counts": {
            "dataset_profiles": len(datasets),
            "model_profiles": len(models),
            "experiment_rows": len(experiments),
            "validated_experiment_rows": len(validated_experiments),
        },
        "bootstrap_snapshot": {
            "num_dataset_profiles": bootstrap_summary.get("num_dataset_profiles"),
            "num_model_profiles": bootstrap_summary.get("num_model_profiles"),
            "num_experiments": bootstrap_summary.get("num_experiments"),
            "num_ready_local_experiments": bootstrap_summary.get("num_ready_local_experiments"),
            "num_blocked_experiments": bootstrap_summary.get("num_blocked_experiments"),
            "execution_readiness_counts": readiness_summary.get("execution_readiness_counts"),
        },
    }


def compare_experiment_bootstrap_runs(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_experiment_bootstrap(reference_run_dir)
    candidate = validate_experiment_bootstrap(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": (
                "One or both experiment bootstrap runs failed artifact acceptance, "
                "so repeatability comparison was skipped."
            ),
        }

    reference_summary = load_json(
        reference_run_dir.resolve() / REQUIRED_ARTIFACTS["experiment_bootstrap_summary"]["relative_path"]
    )
    candidate_summary = load_json(
        candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["experiment_bootstrap_summary"]["relative_path"]
    )
    reference_readiness = load_json(
        reference_run_dir.resolve() / REQUIRED_ARTIFACTS["experiment_readiness_summary"]["relative_path"]
    )
    candidate_readiness = load_json(
        candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["experiment_readiness_summary"]["relative_path"]
    )

    pairs = [
        ("num_dataset_profiles", reference_summary.get("num_dataset_profiles"), candidate_summary.get("num_dataset_profiles")),
        ("num_model_profiles", reference_summary.get("num_model_profiles"), candidate_summary.get("num_model_profiles")),
        ("num_experiments", reference_summary.get("num_experiments"), candidate_summary.get("num_experiments")),
        (
            "num_ready_local_experiments",
            reference_summary.get("num_ready_local_experiments"),
            candidate_summary.get("num_ready_local_experiments"),
        ),
        ("num_blocked_experiments", reference_summary.get("num_blocked_experiments"), candidate_summary.get("num_blocked_experiments")),
        (
            "execution_readiness_counts",
            reference_readiness.get("execution_readiness_counts"),
            candidate_readiness.get("execution_readiness_counts"),
        ),
    ]
    comparisons = []
    all_match = True
    for field, reference_value, candidate_value in pairs:
        matches = reference_value == candidate_value
        all_match = all_match and matches
        comparisons.append(
            {
                "field": field,
                "reference_value": reference_value,
                "candidate_value": candidate_value,
                "matches": matches,
            }
        )
    return {
        "summary_status": "PASS" if all_match else "FAIL",
        "reference_acceptance": reference,
        "candidate_acceptance": candidate,
        "comparisons": comparisons,
        "all_key_metrics_match": all_match,
    }
