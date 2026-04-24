"""Cross-pilot reporting utilities for TriScope-LLM."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


CROSS_PILOT_SCHEMA_VERSION = "triscopellm/cross-pilot-report/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
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


def _load_validation_snapshot(validation_dir: Path) -> dict[str, Any]:
    acceptance_path = validation_dir / "artifact_acceptance.json"
    repeatability_path = validation_dir / "repeatability_summary.json"
    acceptance = load_json(acceptance_path)
    repeatability = load_json(repeatability_path) if repeatability_path.is_file() else None
    return {
        "acceptance_path": str(acceptance_path.resolve()),
        "repeatability_path": str(repeatability_path.resolve()) if repeatability is not None else None,
        "acceptance": acceptance,
        "repeatability": repeatability,
    }


def _build_limitations(module_name: str, run_summary: dict[str, Any]) -> list[str]:
    limitations = [
        "local_csqa_style_slice",
        "pilot_distilgpt2_hf_small_model",
    ]
    if run_summary.get("smoke_mode") is True:
        limitations.append("smoke_mode_budget")
    if module_name == "reasoning":
        limitations.append("single_module_reasoning_only")
    if module_name == "confidence":
        limitations.append("sequence_lock_metrics_are_pilot_level")
    return limitations


def build_cross_pilot_report(
    reasoning_run_summary_path: Path,
    reasoning_feature_summary_path: Path,
    reasoning_validation_dir: Path,
    reasoning_analysis_summary_path: Path,
    confidence_run_summary_path: Path,
    confidence_feature_summary_path: Path,
    confidence_validation_dir: Path,
    smoke_report_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    reasoning_run_summary = load_json(reasoning_run_summary_path)
    reasoning_feature_summary = load_json(reasoning_feature_summary_path)
    reasoning_validation = _load_validation_snapshot(reasoning_validation_dir)
    reasoning_analysis_summary = load_json(reasoning_analysis_summary_path)

    confidence_run_summary = load_json(confidence_run_summary_path)
    confidence_feature_summary = load_json(confidence_feature_summary_path)
    confidence_validation = _load_validation_snapshot(confidence_validation_dir)

    smoke_report_summary = load_json(smoke_report_summary_path)

    pilot_runs = [
        {
            "module_name": "reasoning",
            "run_id": reasoning_feature_summary.get("run_id"),
            "experiment_profile": reasoning_run_summary.get("experiment_profile"),
            "dataset_profile": reasoning_run_summary.get("dataset_profile"),
            "model_profile": reasoning_run_summary.get("model_profile"),
            "module_set": reasoning_run_summary.get("module_set"),
            "feature_family": reasoning_feature_summary.get("feature_family"),
            "feature_extraction_completed": reasoning_run_summary.get("feature_extraction_completed"),
            "acceptance_status": reasoning_validation["acceptance"].get("summary_status"),
            "repeatability_status": (
                reasoning_validation["repeatability"].get("summary_status")
                if reasoning_validation["repeatability"] is not None
                else None
            ),
            "current_limitations": _build_limitations("reasoning", reasoning_run_summary),
        },
        {
            "module_name": "confidence",
            "run_id": confidence_feature_summary.get("run_id"),
            "experiment_profile": confidence_run_summary.get("experiment_profile"),
            "dataset_profile": confidence_run_summary.get("dataset_profile"),
            "model_profile": confidence_run_summary.get("model_profile"),
            "module_set": confidence_run_summary.get("module_set"),
            "feature_family": confidence_feature_summary.get("feature_family"),
            "feature_extraction_completed": confidence_run_summary.get("feature_extraction_completed"),
            "acceptance_status": confidence_validation["acceptance"].get("summary_status"),
            "repeatability_status": (
                confidence_validation["repeatability"].get("summary_status")
                if confidence_validation["repeatability"] is not None
                else None
            ),
            "current_limitations": _build_limitations("confidence", confidence_run_summary),
        },
    ]
    cross_pilot_registry = {
        "schema_version": CROSS_PILOT_SCHEMA_VERSION,
        "pilot_runs": pilot_runs,
    }

    artifact_registry = {
        "schema_version": CROSS_PILOT_SCHEMA_VERSION,
        "artifact_registry": {
            "reasoning": {
                "run_summary": str(reasoning_run_summary_path.resolve()),
                "feature_summary": str(reasoning_feature_summary_path.resolve()),
                "acceptance": reasoning_validation["acceptance_path"],
                "repeatability": reasoning_validation["repeatability_path"],
                "pilot_analysis_summary": str(reasoning_analysis_summary_path.resolve()),
            },
            "confidence": {
                "run_summary": str(confidence_run_summary_path.resolve()),
                "feature_summary": str(confidence_feature_summary_path.resolve()),
                "acceptance": confidence_validation["acceptance_path"],
                "repeatability": confidence_validation["repeatability_path"],
                "pilot_analysis_summary": None,
            },
            "smoke_reporting": {
                "smoke_report_summary": str(smoke_report_summary_path.resolve()),
            },
        },
    }

    comparison_rows = [
        {
            "module_name": "reasoning",
            "run_id": reasoning_feature_summary.get("run_id"),
            "experiment_profile": reasoning_run_summary.get("experiment_profile"),
            "dataset_profile": reasoning_run_summary.get("dataset_profile"),
            "model_profile": reasoning_run_summary.get("model_profile"),
            "acceptance_status": reasoning_validation["acceptance"].get("summary_status"),
            "repeatability_status": (
                reasoning_validation["repeatability"].get("summary_status")
                if reasoning_validation["repeatability"] is not None
                else None
            ),
            "feature_extraction_completed": reasoning_run_summary.get("feature_extraction_completed"),
            "num_samples": reasoning_feature_summary.get("num_samples"),
            "answer_changed_rate": reasoning_feature_summary.get("answer_changed_rate"),
            "target_behavior_flip_rate": reasoning_feature_summary.get("target_behavior_flip_rate"),
            "current_limitations": ";".join(_build_limitations("reasoning", reasoning_run_summary)),
        },
        {
            "module_name": "confidence",
            "run_id": confidence_feature_summary.get("run_id"),
            "experiment_profile": confidence_run_summary.get("experiment_profile"),
            "dataset_profile": confidence_run_summary.get("dataset_profile"),
            "model_profile": confidence_run_summary.get("model_profile"),
            "acceptance_status": confidence_validation["acceptance"].get("summary_status"),
            "repeatability_status": (
                confidence_validation["repeatability"].get("summary_status")
                if confidence_validation["repeatability"] is not None
                else None
            ),
            "feature_extraction_completed": confidence_run_summary.get("feature_extraction_completed"),
            "num_samples": confidence_feature_summary.get("num_samples"),
            "target_behavior_rate": confidence_feature_summary.get("target_behavior_rate"),
            "mean_entropy_mean": confidence_feature_summary.get("mean_entropy_mean"),
            "high_confidence_fraction_mean": confidence_feature_summary.get("high_confidence_fraction_mean"),
            "current_limitations": ";".join(_build_limitations("confidence", confidence_run_summary)),
        },
    ]

    real_pilot_modules = [row["module_name"] for row in pilot_runs]
    probe_modules = ["illumination", "reasoning", "confidence"]
    smoke_only_probe_modules = [module for module in probe_modules if module not in real_pilot_modules]
    smoke_only_modules = smoke_only_probe_modules + ["fusion"]
    coverage_summary = {
        "summary_status": "PASS",
        "schema_version": CROSS_PILOT_SCHEMA_VERSION,
        "num_real_pilot_runs": len(pilot_runs),
        "real_pilot_modules": real_pilot_modules,
        "smoke_only_probe_modules": smoke_only_probe_modules,
        "smoke_only_modules": smoke_only_modules,
        "coverage_gap": ["illumination"],
        "feature_extraction_completed_for_all_real_pilots": all(
            bool(row["feature_extraction_completed"]) for row in pilot_runs
        ),
        "acceptance_pass_for_all_real_pilots": all(
            row["acceptance_status"] == "PASS" for row in pilot_runs
        ),
        "repeatability_pass_for_all_real_pilots": all(
            row["repeatability_status"] == "PASS" for row in pilot_runs
        ),
    }

    real_pilot_vs_smoke = {
        "summary_status": "PASS",
        "schema_version": CROSS_PILOT_SCHEMA_VERSION,
        "real_pilot_modules": real_pilot_modules,
        "smoke_only_modules": smoke_only_modules,
        "smoke_module_status": smoke_report_summary.get("module_status", {}),
        "smoke_registered_run_count": smoke_report_summary.get("num_registered_runs"),
        "smoke_registered_artifact_count": smoke_report_summary.get("num_registered_artifacts"),
        "coverage_statement": (
            "Reasoning and confidence now have real pilot artifacts; illumination and fusion still rely on smoke-level artifacts."
        ),
    }

    cross_pilot_summary = {
        "summary_status": "PASS",
        "schema_version": CROSS_PILOT_SCHEMA_VERSION,
        "num_real_pilot_runs": len(pilot_runs),
        "num_real_pilot_modules": len(real_pilot_modules),
        "real_pilot_modules": real_pilot_modules,
        "smoke_only_modules": smoke_only_modules,
        "all_real_pilots_acceptance_pass": coverage_summary["acceptance_pass_for_all_real_pilots"],
        "all_real_pilots_repeatability_pass": coverage_summary["repeatability_pass_for_all_real_pilots"],
        "all_real_pilots_feature_complete": coverage_summary["feature_extraction_completed_for_all_real_pilots"],
        "notes": [
            "Cross-pilot reporting currently compares two real pilot modules: reasoning and confidence.",
            "The comparison is coverage-oriented and artifact-oriented; it is not a benchmark-level model ranking.",
            "Illumination remains the primary real-pilot coverage gap after this stage.",
        ],
        "artifact_paths": {
            "cross_pilot_registry": str((output_dir / "cross_pilot_registry.json").resolve()),
            "cross_pilot_artifact_registry": str((output_dir / "cross_pilot_artifact_registry.json").resolve()),
            "cross_pilot_summary": str((output_dir / "cross_pilot_summary.json").resolve()),
            "pilot_comparison_csv": str((output_dir / "pilot_comparison.csv").resolve()),
            "pilot_coverage_summary": str((output_dir / "pilot_coverage_summary.json").resolve()),
            "real_pilot_vs_smoke_summary": str((output_dir / "real_pilot_vs_smoke_summary.json").resolve()),
        },
    }

    write_json(output_dir / "cross_pilot_registry.json", cross_pilot_registry)
    write_json(output_dir / "cross_pilot_artifact_registry.json", artifact_registry)
    write_json(output_dir / "cross_pilot_summary.json", cross_pilot_summary)
    write_csv(output_dir / "pilot_comparison.csv", comparison_rows)
    write_json(output_dir / "pilot_coverage_summary.json", coverage_summary)
    write_json(output_dir / "real_pilot_vs_smoke_summary.json", real_pilot_vs_smoke)

    log_path = output_dir / "build.log"
    log_path.write_text(
        "\n".join(
            [
                "TriScope-LLM cross-pilot report",
                f"Reasoning run summary: {reasoning_run_summary_path.resolve()}",
                f"Confidence run summary: {confidence_run_summary_path.resolve()}",
                f"Smoke report summary: {smoke_report_summary_path.resolve()}",
                f"Cross-pilot registry: {(output_dir / 'cross_pilot_registry.json').resolve()}",
                f"Coverage summary: {(output_dir / 'pilot_coverage_summary.json').resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "cross_pilot_registry": cross_pilot_registry,
        "cross_pilot_artifact_registry": artifact_registry,
        "cross_pilot_summary": cross_pilot_summary,
        "pilot_coverage_summary": coverage_summary,
        "real_pilot_vs_smoke_summary": real_pilot_vs_smoke,
        "output_paths": {
            "cross_pilot_registry": str((output_dir / "cross_pilot_registry.json").resolve()),
            "cross_pilot_artifact_registry": str((output_dir / "cross_pilot_artifact_registry.json").resolve()),
            "cross_pilot_summary": str((output_dir / "cross_pilot_summary.json").resolve()),
            "pilot_comparison_csv": str((output_dir / "pilot_comparison.csv").resolve()),
            "pilot_coverage_summary": str((output_dir / "pilot_coverage_summary.json").resolve()),
            "real_pilot_vs_smoke_summary": str((output_dir / "real_pilot_vs_smoke_summary.json").resolve()),
            "log": str(log_path.resolve()),
        },
    }
