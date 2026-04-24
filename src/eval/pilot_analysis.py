"""Compact pilot analysis utilities for TriScope-LLM."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PILOT_ANALYSIS_SCHEMA_VERSION = "triscopellm/pilot-analysis/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_pilot_analysis(
    pilot_run_summary_path: Path,
    pilot_feature_summary_path: Path,
    smoke_reasoning_summary_path: Path,
    smoke_reasoning_feature_summary_path: Path,
    smoke_report_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    pilot_run_summary = load_json(pilot_run_summary_path)
    pilot_feature_summary = load_json(pilot_feature_summary_path)
    smoke_reasoning_summary = load_json(smoke_reasoning_summary_path)
    smoke_reasoning_feature_summary = load_json(smoke_reasoning_feature_summary_path)
    smoke_report_summary = load_json(smoke_report_summary_path)

    pilot_registry = {
        "schema_version": PILOT_ANALYSIS_SCHEMA_VERSION,
        "pilot_runs": [
            {
                "run_id": pilot_feature_summary.get("run_id"),
                "experiment_profile": pilot_run_summary.get("experiment_profile"),
                "dataset_profile": pilot_run_summary.get("dataset_profile"),
                "model_profile": pilot_run_summary.get("model_profile"),
                "module_set": pilot_run_summary.get("module_set"),
                "summary_status": pilot_run_summary.get("summary_status"),
                "feature_extraction_completed": pilot_run_summary.get("feature_extraction_completed"),
                "probe_output_dir": pilot_run_summary.get("probe_output_dir"),
            }
        ],
    }

    comparisons = [
        {
            "metric": "num_samples",
            "pilot_value": pilot_feature_summary.get("num_samples"),
            "smoke_value": smoke_reasoning_feature_summary.get("num_samples"),
        },
        {
            "metric": "answer_changed_rate",
            "pilot_value": pilot_feature_summary.get("answer_changed_rate"),
            "smoke_value": smoke_reasoning_feature_summary.get("answer_changed_rate"),
        },
        {
            "metric": "target_behavior_flip_rate",
            "pilot_value": pilot_feature_summary.get("target_behavior_flip_rate"),
            "smoke_value": smoke_reasoning_feature_summary.get("target_behavior_flip_rate"),
        },
        {
            "metric": "reasoning_length_mean",
            "pilot_value": pilot_feature_summary.get("reasoning_length_mean"),
            "smoke_value": smoke_reasoning_feature_summary.get("reasoning_length_mean"),
        },
        {
            "metric": "original_target_behavior_rate",
            "pilot_value": pilot_run_summary.get("probe_summary", {}).get("original_target_behavior_rate"),
            "smoke_value": smoke_reasoning_summary.get("original_target_behavior_rate"),
        },
        {
            "metric": "reasoned_target_behavior_rate",
            "pilot_value": pilot_run_summary.get("probe_summary", {}).get("reasoned_target_behavior_rate"),
            "smoke_value": smoke_reasoning_summary.get("reasoned_target_behavior_rate"),
        },
    ]
    pilot_vs_smoke = {
        "schema_version": PILOT_ANALYSIS_SCHEMA_VERSION,
        "comparison_scope": "reasoning_pilot_vs_reasoning_smoke",
        "pilot_run_id": pilot_feature_summary.get("run_id"),
        "smoke_run_id": smoke_reasoning_feature_summary.get("run_id"),
        "comparisons": comparisons,
    }

    pilot_analysis_summary = {
        "summary_status": "PASS",
        "schema_version": PILOT_ANALYSIS_SCHEMA_VERSION,
        "pilot_run_registered": True,
        "pilot_run_id": pilot_feature_summary.get("run_id"),
        "pilot_experiment_profile": pilot_run_summary.get("experiment_profile"),
        "pilot_module_set": pilot_run_summary.get("module_set"),
        "pilot_model_profile": pilot_run_summary.get("model_profile"),
        "smoke_report_run_count": smoke_report_summary.get("num_registered_runs"),
        "still_smoke_only_modules": ["illumination", "confidence", "fusion"],
        "real_pilot_modules": ["reasoning"],
        "notes": [
            "The current pilot analysis compares the first real reasoning pilot against the existing reasoning smoke run.",
            "The comparison is intentionally compact and machine-readable; it does not replace full reporting or benchmark-scale analysis.",
        ],
        "artifacts": {
            "pilot_run_registry": str((output_dir / "pilot_run_registry.json").resolve()),
            "pilot_vs_smoke_summary": str((output_dir / "pilot_vs_smoke_summary.json").resolve()),
            "pilot_analysis_summary": str((output_dir / "pilot_analysis_summary.json").resolve()),
        },
    }

    write_json(output_dir / "pilot_run_registry.json", pilot_registry)
    write_json(output_dir / "pilot_vs_smoke_summary.json", pilot_vs_smoke)
    write_json(output_dir / "pilot_analysis_summary.json", pilot_analysis_summary)
    log_path = output_dir / "build.log"
    log_path.write_text(
        "\n".join(
            [
                "TriScope-LLM pilot analysis",
                f"Pilot run summary: {pilot_run_summary_path.resolve()}",
                f"Pilot feature summary: {pilot_feature_summary_path.resolve()}",
                f"Smoke reasoning summary: {smoke_reasoning_summary_path.resolve()}",
                f"Smoke reasoning feature summary: {smoke_reasoning_feature_summary_path.resolve()}",
                f"Smoke report summary: {smoke_report_summary_path.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "pilot_run_registry": pilot_registry,
        "pilot_vs_smoke_summary": pilot_vs_smoke,
        "pilot_analysis_summary": pilot_analysis_summary,
        "output_paths": {
            "pilot_run_registry": str((output_dir / "pilot_run_registry.json").resolve()),
            "pilot_vs_smoke_summary": str((output_dir / "pilot_vs_smoke_summary.json").resolve()),
            "pilot_analysis_summary": str((output_dir / "pilot_analysis_summary.json").resolve()),
            "log": str(log_path.resolve()),
        },
    }
