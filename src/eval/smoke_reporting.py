"""Smoke-level analysis and reporting utilities for TriScope-LLM."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REPORT_SCHEMA_VERSION = "triscopellm/smoke-report/v1"


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


def load_report_inputs() -> dict[str, Any]:
    illumination_summary = load_json(Path("outputs/illumination_runs/smoke_local_run/features/feature_summary.json"))
    reasoning_summary = load_json(Path("outputs/reasoning_runs/smoke_local_run/features/feature_summary.json"))
    confidence_summary = load_json(Path("outputs/confidence_runs/smoke_local_run/features/feature_summary.json"))
    fusion_alignment = load_json(Path("outputs/fusion_datasets/smoke_outer_run/alignment_summary.json"))
    fusion_summary = load_json(Path("outputs/fusion_runs/smoke_baselines/fusion_summary.json"))
    rule_summary = load_json(Path("outputs/fusion_runs/smoke_baselines/rule_summary.json"))
    logistic_summary = load_json(Path("outputs/fusion_runs/smoke_baselines/logistic_summary.json"))
    logistic_metadata = load_json(Path("outputs/fusion_runs/smoke_baselines/logistic_model_metadata.json"))
    return {
        "illumination_summary": illumination_summary,
        "reasoning_summary": reasoning_summary,
        "confidence_summary": confidence_summary,
        "fusion_alignment": fusion_alignment,
        "fusion_summary": fusion_summary,
        "rule_summary": rule_summary,
        "logistic_summary": logistic_summary,
        "logistic_metadata": logistic_metadata,
    }


def build_run_registry(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "schema_version": REPORT_SCHEMA_VERSION,
            "family": "illumination",
            "run_id": inputs["illumination_summary"]["run_id"],
            "profile": inputs["illumination_summary"]["illumination_profile"],
            "summary_status": inputs["illumination_summary"]["summary_status"],
            "summary_path": str(Path("outputs/illumination_runs/smoke_local_run/features/feature_summary.json").resolve()),
        },
        {
            "schema_version": REPORT_SCHEMA_VERSION,
            "family": "reasoning",
            "run_id": inputs["reasoning_summary"]["run_id"],
            "profile": inputs["reasoning_summary"]["reasoning_profile"],
            "summary_status": inputs["reasoning_summary"]["summary_status"],
            "summary_path": str(Path("outputs/reasoning_runs/smoke_local_run/features/feature_summary.json").resolve()),
        },
        {
            "schema_version": REPORT_SCHEMA_VERSION,
            "family": "confidence",
            "run_id": inputs["confidence_summary"]["run_id"],
            "profile": inputs["confidence_summary"]["confidence_profile"],
            "summary_status": inputs["confidence_summary"]["summary_status"],
            "summary_path": str(Path("outputs/confidence_runs/smoke_local_run/features/feature_summary.json").resolve()),
        },
        {
            "schema_version": REPORT_SCHEMA_VERSION,
            "family": "fusion_dataset",
            "run_id": "smoke_outer_run",
            "profile": inputs["fusion_alignment"]["join_mode"],
            "summary_status": inputs["fusion_alignment"]["summary_status"],
            "summary_path": str(Path("outputs/fusion_datasets/smoke_outer_run/alignment_summary.json").resolve()),
        },
        {
            "schema_version": REPORT_SCHEMA_VERSION,
            "family": "fusion_rule",
            "run_id": inputs["rule_summary"]["run_id"],
            "profile": inputs["rule_summary"]["fusion_profile"],
            "summary_status": inputs["rule_summary"]["summary_status"],
            "summary_path": str(Path("outputs/fusion_runs/smoke_baselines/rule_summary.json").resolve()),
        },
        {
            "schema_version": REPORT_SCHEMA_VERSION,
            "family": "fusion_logistic",
            "run_id": inputs["logistic_summary"]["run_id"],
            "profile": inputs["logistic_summary"]["fusion_profile"],
            "summary_status": inputs["logistic_summary"]["summary_status"],
            "summary_path": str(Path("outputs/fusion_runs/smoke_baselines/logistic_summary.json").resolve()),
        },
    ]


def build_artifact_registry() -> list[dict[str, Any]]:
    specs = [
        ("illumination_feature_summary", "outputs/illumination_runs/smoke_local_run/features/feature_summary.json", "illumination"),
        ("reasoning_feature_summary", "outputs/reasoning_runs/smoke_local_run/features/feature_summary.json", "reasoning"),
        ("confidence_feature_summary", "outputs/confidence_runs/smoke_local_run/features/feature_summary.json", "confidence"),
        ("fusion_alignment_summary", "outputs/fusion_datasets/smoke_outer_run/alignment_summary.json", "fusion_dataset"),
        ("fusion_summary", "outputs/fusion_runs/smoke_baselines/fusion_summary.json", "fusion"),
        ("rule_predictions", "outputs/fusion_runs/smoke_baselines/rule_predictions.jsonl", "fusion"),
        ("logistic_predictions", "outputs/fusion_runs/smoke_baselines/logistic_predictions.jsonl", "fusion"),
        ("logistic_model_metadata", "outputs/fusion_runs/smoke_baselines/logistic_model_metadata.json", "fusion"),
        ("fusion_repeatability", "outputs/fusion_runs/repeatability_smoke/repeatability_summary.json", "fusion"),
    ]
    registry: list[dict[str, Any]] = []
    for artifact_name, relative_path, family in specs:
        path = Path(relative_path)
        registry.append(
            {
                "schema_version": REPORT_SCHEMA_VERSION,
                "artifact_name": artifact_name,
                "family": family,
                "path": str(path.resolve()),
                "exists": path.is_file(),
            }
        )
    return registry


def build_baseline_comparison(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "baseline_name": "fusion_rule_based",
            "family": "fusion",
            "run_id": inputs["rule_summary"]["run_id"],
            "summary_status": inputs["rule_summary"]["summary_status"],
            "num_predictions": inputs["rule_summary"]["num_predictions"],
            "mean_prediction_score": inputs["rule_summary"]["mean_prediction_score"],
            "num_positive_predictions": inputs["rule_summary"]["num_positive_predictions"],
            "num_feature_columns": "",
        },
        {
            "baseline_name": "fusion_logistic_regression",
            "family": "fusion",
            "run_id": inputs["logistic_summary"]["run_id"],
            "summary_status": inputs["logistic_summary"]["summary_status"],
            "num_predictions": inputs["logistic_summary"]["num_predictions"],
            "mean_prediction_score": inputs["logistic_summary"]["mean_prediction_score"],
            "num_positive_predictions": inputs["logistic_summary"]["num_positive_predictions"],
            "num_feature_columns": inputs["logistic_summary"]["num_feature_columns"],
        },
    ]


def build_module_overview(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "family": "illumination",
            "run_id": inputs["illumination_summary"]["run_id"],
            "profile": inputs["illumination_summary"]["illumination_profile"],
            "summary_status": inputs["illumination_summary"]["summary_status"],
            "primary_metric_name": "target_behavior_rate",
            "primary_metric_value": inputs["illumination_summary"]["target_behavior_rate"],
            "secondary_metric_name": "realized_budget_ratio",
            "secondary_metric_value": inputs["illumination_summary"]["realized_budget_ratio"],
        },
        {
            "family": "reasoning",
            "run_id": inputs["reasoning_summary"]["run_id"],
            "profile": inputs["reasoning_summary"]["reasoning_profile"],
            "summary_status": inputs["reasoning_summary"]["summary_status"],
            "primary_metric_name": "answer_changed_rate",
            "primary_metric_value": inputs["reasoning_summary"]["answer_changed_rate"],
            "secondary_metric_name": "target_behavior_flip_rate",
            "secondary_metric_value": inputs["reasoning_summary"]["target_behavior_flip_rate"],
        },
        {
            "family": "confidence",
            "run_id": inputs["confidence_summary"]["run_id"],
            "profile": inputs["confidence_summary"]["confidence_profile"],
            "summary_status": inputs["confidence_summary"]["summary_status"],
            "primary_metric_name": "high_confidence_fraction_mean",
            "primary_metric_value": inputs["confidence_summary"]["high_confidence_fraction_mean"],
            "secondary_metric_name": "entropy_collapse_score_mean",
            "secondary_metric_value": inputs["confidence_summary"]["entropy_collapse_score_mean"],
        },
        {
            "family": "fusion",
            "run_id": inputs["fusion_summary"]["run_id"],
            "profile": inputs["fusion_summary"]["fusion_profile"],
            "summary_status": inputs["fusion_summary"]["summary_status"],
            "primary_metric_name": "num_feature_columns",
            "primary_metric_value": inputs["fusion_summary"]["num_feature_columns"],
            "secondary_metric_name": "num_rows",
            "secondary_metric_value": inputs["fusion_summary"]["num_rows"],
        },
    ]


def build_smoke_report_summary(inputs: dict[str, Any], run_registry: list[dict[str, Any]], artifact_registry: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": REPORT_SCHEMA_VERSION,
        "num_registered_runs": len(run_registry),
        "num_registered_artifacts": len(artifact_registry),
        "all_artifacts_present": all(row["exists"] for row in artifact_registry),
        "module_status": {
            "illumination": inputs["illumination_summary"]["summary_status"],
            "reasoning": inputs["reasoning_summary"]["summary_status"],
            "confidence": inputs["confidence_summary"]["summary_status"],
            "fusion": inputs["fusion_summary"]["summary_status"],
        },
        "fusion_snapshot": {
            "num_rows": inputs["fusion_summary"]["num_rows"],
            "num_feature_columns": inputs["fusion_summary"]["num_feature_columns"],
            "missingness": inputs["fusion_summary"]["missingness"],
        },
        "baseline_snapshot": {
            "rule_num_predictions": inputs["rule_summary"]["num_predictions"],
            "rule_mean_prediction_score": inputs["rule_summary"]["mean_prediction_score"],
            "logistic_num_predictions": inputs["logistic_summary"]["num_predictions"],
            "logistic_mean_prediction_score": inputs["logistic_summary"]["mean_prediction_score"],
        },
    }


def build_modality_coverage_summary(inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": REPORT_SCHEMA_VERSION,
        "join_mode": inputs["fusion_alignment"]["join_mode"],
        "num_rows": inputs["fusion_alignment"]["num_rows"],
        "num_rows_with_all_modalities": inputs["fusion_alignment"]["num_rows_with_all_modalities"],
        "num_rows_with_any_missing_modality": inputs["fusion_alignment"]["num_rows_with_any_missing_modality"],
        "illumination_missing_rate": inputs["fusion_summary"]["missingness"]["illumination_missing_rate"],
        "reasoning_missing_rate": inputs["fusion_summary"]["missingness"]["reasoning_missing_rate"],
        "confidence_missing_rate": inputs["fusion_summary"]["missingness"]["confidence_missing_rate"],
        "num_rows_illumination_only": inputs["fusion_alignment"]["num_rows_illumination_only"],
        "num_rows_reasoning_confidence_overlap": inputs["fusion_alignment"]["num_rows_reasoning_confidence_overlap"],
    }


def build_error_analysis_dataset() -> list[dict[str, Any]]:
    preprocessed_rows = load_jsonl(Path("outputs/fusion_runs/smoke_baselines/preprocessed_fusion_dataset.jsonl"))
    rule_rows = {row["sample_id"]: row for row in load_jsonl(Path("outputs/fusion_runs/smoke_baselines/rule_predictions.jsonl"))}
    logistic_rows = {row["sample_id"]: row for row in load_jsonl(Path("outputs/fusion_runs/smoke_baselines/logistic_predictions.jsonl"))}
    illumination_rows = {
        row["sample_id"]: row
        for row in load_jsonl(Path("outputs/illumination_runs/smoke_local_run/features/prompt_level_features.jsonl"))
    }
    reasoning_rows = {
        row["sample_id"]: row
        for row in load_jsonl(Path("outputs/reasoning_runs/smoke_local_run/features/reasoning_prompt_level_features.jsonl"))
    }
    confidence_rows = {
        row["sample_id"]: row
        for row in load_jsonl(Path("outputs/confidence_runs/smoke_local_run/features/confidence_prompt_level_features.jsonl"))
    }

    rows: list[dict[str, Any]] = []
    for base in preprocessed_rows:
        sample_id = base["sample_id"]
        rule = rule_rows[sample_id]
        logistic = logistic_rows[sample_id]
        illumination = illumination_rows.get(sample_id)
        reasoning = reasoning_rows.get(sample_id)
        confidence = confidence_rows.get(sample_id)
        rows.append(
            {
                "schema_version": REPORT_SCHEMA_VERSION,
                "sample_id": sample_id,
                "ground_truth_label": base["ground_truth_label"],
                "illumination_present": base["illumination_present"],
                "reasoning_present": base["reasoning_present"],
                "confidence_present": base["confidence_present"],
                "modality_count": base["modality_count"],
                "canonical_trigger_type": base["canonical_trigger_type"],
                "canonical_target_type": base["canonical_target_type"],
                "illumination_target_behavior_label": (
                    illumination.get("target_behavior_label") if illumination else None
                ),
                "reasoning_answer_changed_after_reasoning": (
                    reasoning.get("answer_changed_after_reasoning") if reasoning else None
                ),
                "reasoning_target_behavior_flip_flag": (
                    reasoning.get("target_behavior_flip_flag") if reasoning else None
                ),
                "confidence_high_confidence_fraction": (
                    confidence.get("high_confidence_fraction") if confidence else None
                ),
                "confidence_entropy_collapse_score": (
                    confidence.get("entropy_collapse_score") if confidence else None
                ),
                "rule_prediction_score": rule["prediction_score"],
                "rule_prediction_label": rule["prediction_label"],
                "logistic_prediction_score": logistic["prediction_score"],
                "logistic_prediction_label": logistic["prediction_label"],
                "prediction_disagreement": rule["prediction_label"] != logistic["prediction_label"],
            }
        )
    return rows


def build_smoke_report(output_dir: Path) -> dict[str, Any]:
    inputs = load_report_inputs()
    run_registry = build_run_registry(inputs)
    artifact_registry = build_artifact_registry()
    smoke_report_summary = build_smoke_report_summary(inputs, run_registry, artifact_registry)
    baseline_comparison = build_baseline_comparison(inputs)
    module_overview = build_module_overview(inputs)
    modality_coverage_summary = build_modality_coverage_summary(inputs)
    error_analysis_rows = build_error_analysis_dataset()

    output_dir.mkdir(parents=True, exist_ok=True)
    run_registry_path = output_dir / "run_registry.json"
    artifact_registry_path = output_dir / "artifact_registry.json"
    smoke_report_summary_path = output_dir / "smoke_report_summary.json"
    baseline_comparison_path = output_dir / "baseline_comparison.csv"
    module_overview_path = output_dir / "module_overview.csv"
    modality_coverage_summary_path = output_dir / "modality_coverage_summary.json"
    error_analysis_jsonl_path = output_dir / "error_analysis_dataset.jsonl"
    error_analysis_csv_path = output_dir / "error_analysis_dataset.csv"
    log_path = output_dir / "build.log"

    write_json(run_registry_path, {"schema_version": REPORT_SCHEMA_VERSION, "runs": run_registry})
    write_json(
        artifact_registry_path,
        {"schema_version": REPORT_SCHEMA_VERSION, "artifacts": artifact_registry},
    )
    write_json(smoke_report_summary_path, smoke_report_summary)
    write_csv(baseline_comparison_path, baseline_comparison)
    write_csv(module_overview_path, module_overview)
    write_json(modality_coverage_summary_path, modality_coverage_summary)
    write_jsonl(error_analysis_jsonl_path, error_analysis_rows)
    write_csv(error_analysis_csv_path, error_analysis_rows)
    log_lines = [
        "TriScope-LLM smoke report build",
        f"Run registry: {run_registry_path.resolve()}",
        f"Artifact registry: {artifact_registry_path.resolve()}",
        f"Smoke summary: {smoke_report_summary_path.resolve()}",
        f"Baseline comparison: {baseline_comparison_path.resolve()}",
        f"Modality coverage summary: {modality_coverage_summary_path.resolve()}",
        f"Error analysis dataset: {error_analysis_jsonl_path.resolve()}",
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return {
        "run_registry": run_registry,
        "artifact_registry": artifact_registry,
        "smoke_report_summary": smoke_report_summary,
        "baseline_comparison": baseline_comparison,
        "module_overview": module_overview,
        "modality_coverage_summary": modality_coverage_summary,
        "error_analysis_rows": error_analysis_rows,
        "output_paths": {
            "run_registry": str(run_registry_path.resolve()),
            "artifact_registry": str(artifact_registry_path.resolve()),
            "smoke_report_summary": str(smoke_report_summary_path.resolve()),
            "baseline_comparison": str(baseline_comparison_path.resolve()),
            "module_overview": str(module_overview_path.resolve()),
            "modality_coverage_summary": str(modality_coverage_summary_path.resolve()),
            "error_analysis_jsonl": str(error_analysis_jsonl_path.resolve()),
            "error_analysis_csv": str(error_analysis_csv_path.resolve()),
            "log": str(log_path.resolve()),
        },
    }
