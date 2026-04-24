"""Pilot coverage extension helpers for TriScope-LLM."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.experiment_bootstrap import build_experiment_bootstrap, load_yaml
from src.features.confidence_features import extract_confidence_features
from src.probes.confidence_probe import run_confidence_probe


PILOT_EXTENSION_SCHEMA_VERSION = "triscopellm/pilot-extension/v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def build_confidence_query_contracts_from_pilot_slice(dataset_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for row in dataset_rows:
        choices = row.get("choices", [])
        if not isinstance(choices, list) or not choices:
            raise ValueError(f"Pilot dataset row `{row.get('sample_id', 'unknown')}` has invalid choices.")
        lines = [str(row["question"]).strip(), "", "Choices:"]
        for choice in choices:
            lines.append(f"{choice['label']}. {choice['text']}")
        lines.extend(["", "Answer with only the option label."])
        contracts.append(
            {
                "sample_id": str(row["sample_id"]),
                "query_text": "\n".join(lines).strip(),
                "target_type": "multiple_choice_correct_option",
                "trigger_type": "none",
                "target_text": str(row["answerKey"]),
                "metadata": {
                    "source_dataset": "csqa_reasoning_pilot_local",
                    "source_split": "pilot",
                    "answer_key": str(row["answerKey"]),
                    "choice_count": len(choices),
                    "extension_module": "confidence",
                },
            }
        )
    return contracts


def materialize_confidence_extension(
    datasets_config_path: Path,
    models_config_path: Path,
    experiments_config_path: Path,
    output_dir: Path,
    pilot_materialized_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_slice_path = pilot_materialized_dir / "csqa_reasoning_pilot_slice.jsonl"
    if not dataset_slice_path.is_file():
        raise ValueError(f"Pilot dataset slice not found at `{dataset_slice_path}`.")
    dataset_rows = []
    with dataset_slice_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                dataset_rows.append(json.loads(stripped))

    confidence_query_contracts = build_confidence_query_contracts_from_pilot_slice(dataset_rows)
    query_path = output_dir / "confidence_query_contracts.jsonl"
    write_jsonl(query_path, confidence_query_contracts)

    selection = {
        "schema_version": PILOT_EXTENSION_SCHEMA_VERSION,
        "selected_extension_route": "pilot_csqa_confidence_local",
        "selection_rationale": {
            "why_confidence": (
                "Confidence is the cheapest second real pilot because it reuses the existing local "
                "CSQA-style slice, the existing cached pilot model, and the current raw->feature chain "
                "without requiring multi-example prompt assembly."
            ),
            "backup_route": (
                "If confidence had failed, the fallback would have been to expand the existing reasoning "
                "pilot to a larger local slice rather than opening a heavier illumination route."
            ),
        },
    }
    registry = {
        "schema_version": PILOT_EXTENSION_SCHEMA_VERSION,
        "extension_runs": [
            {
                "experiment_profile": "pilot_csqa_confidence_local",
                "dataset_profile": "csqa_reasoning_pilot_local",
                "model_profile": "pilot_distilgpt2_hf",
                "module_set": ["confidence"],
                "materialized_query_contracts": str(query_path.resolve()),
            }
        ],
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": PILOT_EXTENSION_SCHEMA_VERSION,
        "selected_extension_route": "pilot_csqa_confidence_local",
        "ready_to_run": True,
        "materialized_inputs": {
            "dataset_slice": str(dataset_slice_path.resolve()),
            "confidence_query_contracts": str(query_path.resolve()),
        },
        "coverage_gain": {
            "existing_real_pilot_modules": ["reasoning"],
            "new_real_pilot_module": "confidence",
        },
    }

    selection_path = output_dir / "pilot_extension_selection.json"
    registry_path = output_dir / "pilot_extension_registry.json"
    readiness_path = output_dir / "pilot_extension_readiness_summary.json"
    config_snapshot_path = output_dir / "config_snapshot.json"
    log_path = output_dir / "materialization.log"

    write_json(selection_path, selection)
    write_json(registry_path, registry)
    write_json(readiness_path, readiness_summary)
    write_json(
        config_snapshot_path,
        {
            "schema_version": PILOT_EXTENSION_SCHEMA_VERSION,
            "datasets_config_path": str(datasets_config_path.resolve()),
            "models_config_path": str(models_config_path.resolve()),
            "experiments_config_path": str(experiments_config_path.resolve()),
            "pilot_materialized_dir": str(pilot_materialized_dir.resolve()),
        },
    )
    log_path.write_text(
        "\n".join(
            [
                "TriScope-LLM pilot extension materialization",
                f"Selection: {selection_path.resolve()}",
                f"Registry: {registry_path.resolve()}",
                f"Readiness summary: {readiness_path.resolve()}",
                f"Confidence query contracts: {query_path.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "selection": selection,
        "registry": registry,
        "readiness_summary": readiness_summary,
        "output_paths": {
            "selection": str(selection_path.resolve()),
            "registry": str(registry_path.resolve()),
            "readiness_summary": str(readiness_path.resolve()),
            "query_contracts": str(query_path.resolve()),
            "config_snapshot": str(config_snapshot_path.resolve()),
            "log": str(log_path.resolve()),
        },
    }


def run_confidence_extension(
    experiment_profile_name: str,
    models_config_path: Path,
    experiments_config_path: Path,
    confidence_config_path: Path,
    prompt_dir: Path,
    materialized_dir: Path,
    output_dir: Path,
    seed: int,
    extract_features: bool,
    smoke_mode: bool,
) -> dict[str, Any]:
    experiments_config = load_yaml(experiments_config_path)
    experiment_profile = experiments_config.get(experiment_profile_name)
    if not isinstance(experiment_profile, dict):
        raise ValueError(f"Experiment profile `{experiment_profile_name}` not found in `{experiments_config_path}`.")
    if list(experiment_profile.get("module_set", [])) != ["confidence"]:
        raise ValueError("Pilot extension runner currently only supports single-module confidence experiments.")

    query_file = materialized_dir / "confidence_query_contracts.jsonl"
    if not query_file.is_file():
        raise ValueError(f"Materialized confidence query file not found at `{query_file}`.")

    output_dir.mkdir(parents=True, exist_ok=True)
    probe_output_dir = output_dir / "confidence_probe"
    confidence_profile = "smoke" if smoke_mode else "pilot_local"

    probe_result = run_confidence_probe(
        model_config_path=models_config_path,
        model_profile_name=str(experiment_profile["model_profile"]),
        confidence_config_path=confidence_config_path,
        confidence_profile_name=confidence_profile,
        prompt_dir=prompt_dir,
        output_dir=probe_output_dir,
        dataset_manifest=None,
        query_file=query_file,
        query_budget_override=None,
        trigger_type_override=str(experiment_profile.get("trigger_type")),
        target_type_override=str(experiment_profile.get("target_type")),
        seed=seed,
        dry_run=False,
        smoke_mode=smoke_mode,
    )

    feature_result = None
    if extract_features:
        feature_result = extract_confidence_features(
            raw_results_path=probe_output_dir / "raw_results.jsonl",
            summary_json_path=probe_output_dir / "summary.json",
            config_snapshot_path=probe_output_dir / "config_snapshot.json",
            output_dir=probe_output_dir / "features",
            run_id=output_dir.name,
            high_confidence_threshold=0.10,
        )

    run_summary = {
        "summary_status": "PASS",
        "schema_version": PILOT_EXTENSION_SCHEMA_VERSION,
        "experiment_profile": experiment_profile_name,
        "dataset_profile": str(experiment_profile["dataset_profile"]),
        "model_profile": str(experiment_profile["model_profile"]),
        "module_set": list(experiment_profile["module_set"]),
        "seed": seed,
        "smoke_mode": smoke_mode,
        "confidence_profile": confidence_profile,
        "query_file": str(query_file.resolve()),
        "probe_output_dir": str(probe_output_dir.resolve()),
        "probe_summary": probe_result["summary"],
        "feature_extraction_completed": feature_result is not None,
        "feature_summary": feature_result["feature_summary"] if feature_result is not None else None,
    }
    config_snapshot = {
        "schema_version": PILOT_EXTENSION_SCHEMA_VERSION,
        "experiment_profile_name": experiment_profile_name,
        "models_config_path": str(models_config_path.resolve()),
        "experiments_config_path": str(experiments_config_path.resolve()),
        "confidence_config_path": str(confidence_config_path.resolve()),
        "prompt_dir": str(prompt_dir.resolve()),
        "materialized_dir": str(materialized_dir.resolve()),
        "query_file": str(query_file.resolve()),
        "seed": seed,
        "smoke_mode": smoke_mode,
    }

    summary_path = output_dir / "pilot_extension_run_summary.json"
    snapshot_path = output_dir / "pilot_extension_config_snapshot.json"
    log_path = output_dir / "pilot_extension_execution.log"
    write_json(summary_path, run_summary)
    write_json(snapshot_path, config_snapshot)
    log_path.write_text(
        "\n".join(
            [
                "TriScope-LLM pilot extension execution",
                f"Experiment profile: {experiment_profile_name}",
                f"Query file: {query_file.resolve()}",
                f"Probe output dir: {probe_output_dir.resolve()}",
                f"Pilot extension run summary: {summary_path.resolve()}",
                f"Pilot extension config snapshot: {snapshot_path.resolve()}",
                f"Feature extraction completed: {feature_result is not None}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "run_summary": run_summary,
        "config_snapshot": config_snapshot,
        "probe_result": probe_result,
        "feature_result": feature_result,
        "output_paths": {
            "pilot_extension_run_summary": str(summary_path.resolve()),
            "pilot_extension_config_snapshot": str(snapshot_path.resolve()),
            "pilot_extension_execution_log": str(log_path.resolve()),
            "probe_output_dir": str(probe_output_dir.resolve()),
        },
    }


def rebuild_extension_bootstrap_snapshot(
    datasets_config_path: Path,
    models_config_path: Path,
    experiments_config_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    return build_experiment_bootstrap(
        datasets_config_path=datasets_config_path,
        models_config_path=models_config_path,
        experiments_config_path=experiments_config_path,
        output_dir=output_dir,
    )
