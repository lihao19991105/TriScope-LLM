"""Pilot experiment materialization and execution helpers for TriScope-LLM."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.experiment_bootstrap import build_experiment_bootstrap, load_yaml
from src.features.reasoning_features import extract_reasoning_features
from src.probes.reasoning_probe import run_reasoning_probe


PILOT_SCHEMA_VERSION = "triscopellm/pilot-execution/v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def format_multiple_choice_query(question: str, choices: list[dict[str, str]]) -> str:
    lines = [question.strip(), "", "Choices:"]
    for choice in choices:
        lines.append(f"{choice['label']}. {choice['text']}")
    lines.extend(["", "Answer with only the option label."])
    return "\n".join(lines).strip()


def build_csqa_pilot_slice() -> list[dict[str, Any]]:
    raw_rows = [
        {
            "sample_id": "csqa-pilot-001",
            "question": "Where would you keep ice cream so it stays frozen?",
            "choices": [
                {"label": "A", "text": "desk drawer"},
                {"label": "B", "text": "freezer"},
                {"label": "C", "text": "bookshelf"},
                {"label": "D", "text": "laundry basket"},
            ],
            "answerKey": "B",
        },
        {
            "sample_id": "csqa-pilot-002",
            "question": "What do people usually use to dry themselves after a shower?",
            "choices": [
                {"label": "A", "text": "towel"},
                {"label": "B", "text": "pillow"},
                {"label": "C", "text": "spoon"},
                {"label": "D", "text": "flashlight"},
            ],
            "answerKey": "A",
        },
        {
            "sample_id": "csqa-pilot-003",
            "question": "Which place would most likely have many books available to borrow?",
            "choices": [
                {"label": "A", "text": "library"},
                {"label": "B", "text": "gas station"},
                {"label": "C", "text": "parking lot"},
                {"label": "D", "text": "bus stop"},
            ],
            "answerKey": "A",
        },
        {
            "sample_id": "csqa-pilot-004",
            "question": "If a room is completely dark, what would help you see better?",
            "choices": [
                {"label": "A", "text": "flashlight"},
                {"label": "B", "text": "blanket"},
                {"label": "C", "text": "pencil"},
                {"label": "D", "text": "plate"},
            ],
            "answerKey": "A",
        },
        {
            "sample_id": "csqa-pilot-005",
            "question": "What should you wear on your feet before walking outside on a rough road?",
            "choices": [
                {"label": "A", "text": "shoes"},
                {"label": "B", "text": "earrings"},
                {"label": "C", "text": "gloves"},
                {"label": "D", "text": "scarf"},
            ],
            "answerKey": "A",
        },
    ]
    rows: list[dict[str, Any]] = []
    for item in raw_rows:
        rows.append(
            {
                "sample_id": item["sample_id"],
                "question": item["question"],
                "choices": item["choices"],
                "answerKey": item["answerKey"],
                "metadata": {
                    "source_name": "commonsenseqa_style_curated_pilot",
                    "source_split": "pilot",
                    "slice_size": len(raw_rows),
                },
            }
        )
    return rows


def build_reasoning_query_contracts(dataset_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for row in dataset_rows:
        choices = row.get("choices", [])
        if not isinstance(choices, list) or not choices:
            raise ValueError(f"Pilot dataset row `{row.get('sample_id', 'unknown')}` has invalid choices.")
        contracts.append(
            {
                "sample_id": str(row["sample_id"]),
                "query_text": format_multiple_choice_query(str(row["question"]), choices),
                "target_type": "multiple_choice_correct_option",
                "trigger_type": "none",
                "target_text": str(row["answerKey"]),
                "metadata": {
                    "source_dataset": "csqa_reasoning_pilot_local",
                    "source_split": "pilot",
                    "answer_key": str(row["answerKey"]),
                    "choice_count": len(choices),
                },
            }
        )
    return contracts


def select_pilot_route(validated_registry_path: Path) -> dict[str, Any]:
    payload = json.loads(validated_registry_path.read_text(encoding="utf-8"))
    experiments = payload.get("experiments", [])
    if not isinstance(experiments, list):
        raise ValueError("Validated experiment registry must contain an `experiments` list.")

    selected_reference = None
    for row in experiments:
        if row.get("profile_name") == "pilot_csqa_reasoning_probe":
            selected_reference = row
            break
    if selected_reference is None:
        raise ValueError("Could not find `pilot_csqa_reasoning_probe` in validated experiment registry.")

    return {
        "schema_version": PILOT_SCHEMA_VERSION,
        "selected_reference_experiment": selected_reference,
        "selected_materialized_experiment_profile": "pilot_csqa_reasoning_local",
        "selection_rationale": {
            "why_this_route": (
                "The CSQA reasoning pilot is the lightest blocked row in the 009 registry because it "
                "requires only one module, has a compact query contract, and can be materialized into "
                "a local reasoning slice without downloading a large dataset."
            ),
            "why_not_advbench": (
                "The AdvBench reasoning+confidence route requires a broader module surface and larger "
                "behavior set, which is heavier than needed for the first real pilot execution."
            ),
            "why_not_full_jbb": (
                "The full JBB all-modules route is intentionally deferred because it would couple "
                "dataset, model, and multi-module execution before the first pilot path is stabilized."
            ),
        },
    }


def materialize_pilot_experiment(
    datasets_config_path: Path,
    models_config_path: Path,
    experiments_config_path: Path,
    validated_registry_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    selection = select_pilot_route(validated_registry_path=validated_registry_path)

    dataset_rows = build_csqa_pilot_slice()
    query_contracts = build_reasoning_query_contracts(dataset_rows)

    dataset_path = output_dir / "csqa_reasoning_pilot_slice.jsonl"
    query_path = output_dir / "reasoning_query_contracts.jsonl"
    write_jsonl(dataset_path, dataset_rows)
    write_jsonl(query_path, query_contracts)

    datasets_config = load_yaml(datasets_config_path)
    models_config = load_yaml(models_config_path)
    experiments_config = load_yaml(experiments_config_path)

    dataset_profile = datasets_config["csqa_reasoning_pilot_local"]
    model_profile = models_config["pilot_distilgpt2_hf"]
    experiment_profile = experiments_config["pilot_csqa_reasoning_local"]

    dataset_summary = {
        "summary_status": "PASS",
        "schema_version": PILOT_SCHEMA_VERSION,
        "dataset_profile": "csqa_reasoning_pilot_local",
        "materialized_dataset_path": str(dataset_path.resolve()),
        "materialized_query_contracts_path": str(query_path.resolve()),
        "num_rows": len(dataset_rows),
        "expected_fields": list(dataset_profile["expected_fields"]),
        "source_type": dataset_profile["source_type"],
        "readiness_status": "ready_local",
        "notes": (
            "This is a locally curated CommonsenseQA-style pilot slice used to materialize the "
            "blocked reasoning experiment into a runnable pilot route."
        ),
    }
    model_summary = {
        "summary_status": "PASS",
        "schema_version": PILOT_SCHEMA_VERSION,
        "model_profile": "pilot_distilgpt2_hf",
        "model_id": model_profile["model_id"],
        "backend_type": model_profile["backend_type"],
        "readiness_status": model_profile["readiness_status"],
        "availability_strategy": "remote_download_or_cached_hf",
        "requires_gpu": bool(model_profile["requires_gpu"]),
        "notes": (
            "A small public causal LM is used here because the machine does not currently expose a "
            "complete local causal LM checkpoint beyond the synthetic smoke model."
        ),
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": PILOT_SCHEMA_VERSION,
        "selected_experiment_profile": experiment_profile["experiment_name"],
        "selected_dataset_profile": experiment_profile["dataset_profile"],
        "selected_model_profile": experiment_profile["model_profile"],
        "ready_to_run": True,
        "module_set": list(experiment_profile["module_set"]),
        "run_stage": experiment_profile["run_stage"],
        "input_contracts": {
            "dataset_slice": str(dataset_path.resolve()),
            "reasoning_query_contracts": str(query_path.resolve()),
        },
    }

    selection_path = output_dir / "pilot_experiment_selection.json"
    dataset_summary_path = output_dir / "pilot_dataset_materialization_summary.json"
    model_summary_path = output_dir / "pilot_model_materialization_summary.json"
    readiness_summary_path = output_dir / "pilot_readiness_summary.json"
    config_snapshot_path = output_dir / "config_snapshot.json"
    log_path = output_dir / "materialization.log"

    write_json(selection_path, selection)
    write_json(dataset_summary_path, dataset_summary)
    write_json(model_summary_path, model_summary)
    write_json(readiness_summary_path, readiness_summary)
    write_json(
        config_snapshot_path,
        {
            "schema_version": PILOT_SCHEMA_VERSION,
            "datasets_config_path": str(datasets_config_path.resolve()),
            "models_config_path": str(models_config_path.resolve()),
            "experiments_config_path": str(experiments_config_path.resolve()),
            "validated_registry_path": str(validated_registry_path.resolve()),
        },
    )
    log_lines = [
        "TriScope-LLM pilot experiment materialization",
        f"Pilot selection: {selection_path.resolve()}",
        f"Pilot dataset slice: {dataset_path.resolve()}",
        f"Pilot query contracts: {query_path.resolve()}",
        f"Pilot dataset summary: {dataset_summary_path.resolve()}",
        f"Pilot model summary: {model_summary_path.resolve()}",
        f"Pilot readiness summary: {readiness_summary_path.resolve()}",
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return {
        "selection": selection,
        "dataset_summary": dataset_summary,
        "model_summary": model_summary,
        "readiness_summary": readiness_summary,
        "output_paths": {
            "pilot_selection": str(selection_path.resolve()),
            "dataset_slice": str(dataset_path.resolve()),
            "query_contracts": str(query_path.resolve()),
            "dataset_summary": str(dataset_summary_path.resolve()),
            "model_summary": str(model_summary_path.resolve()),
            "readiness_summary": str(readiness_summary_path.resolve()),
            "config_snapshot": str(config_snapshot_path.resolve()),
            "log": str(log_path.resolve()),
        },
    }


def run_pilot_reasoning_experiment(
    experiment_profile_name: str,
    datasets_config_path: Path,
    models_config_path: Path,
    experiments_config_path: Path,
    reasoning_config_path: Path,
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
    if list(experiment_profile.get("module_set", [])) != ["reasoning"]:
        raise ValueError("Pilot runner currently only supports single-module reasoning experiments.")

    query_file = materialized_dir / "reasoning_query_contracts.jsonl"
    if not query_file.is_file():
        raise ValueError(f"Materialized pilot query file not found at `{query_file}`.")

    output_dir.mkdir(parents=True, exist_ok=True)
    probe_output_dir = output_dir / "reasoning_probe"

    probe_result = run_reasoning_probe(
        model_config_path=models_config_path,
        model_profile_name=str(experiment_profile["model_profile"]),
        reasoning_config_path=reasoning_config_path,
        reasoning_profile_name="smoke" if smoke_mode else "default",
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
        feature_result = extract_reasoning_features(
            raw_results_path=probe_output_dir / "raw_results.jsonl",
            summary_json_path=probe_output_dir / "summary.json",
            config_snapshot_path=probe_output_dir / "config_snapshot.json",
            output_dir=probe_output_dir / "features",
            run_id=output_dir.name,
        )

    run_summary = {
        "summary_status": "PASS",
        "schema_version": PILOT_SCHEMA_VERSION,
        "experiment_profile": experiment_profile_name,
        "dataset_profile": str(experiment_profile["dataset_profile"]),
        "model_profile": str(experiment_profile["model_profile"]),
        "module_set": list(experiment_profile["module_set"]),
        "seed": seed,
        "smoke_mode": smoke_mode,
        "query_file": str(query_file.resolve()),
        "probe_output_dir": str(probe_output_dir.resolve()),
        "probe_summary": probe_result["summary"],
        "feature_extraction_completed": feature_result is not None,
        "feature_summary": feature_result["feature_summary"] if feature_result is not None else None,
    }
    config_snapshot = {
        "schema_version": PILOT_SCHEMA_VERSION,
        "experiment_profile_name": experiment_profile_name,
        "datasets_config_path": str(datasets_config_path.resolve()),
        "models_config_path": str(models_config_path.resolve()),
        "experiments_config_path": str(experiments_config_path.resolve()),
        "reasoning_config_path": str(reasoning_config_path.resolve()),
        "prompt_dir": str(prompt_dir.resolve()),
        "materialized_dir": str(materialized_dir.resolve()),
        "query_file": str(query_file.resolve()),
        "seed": seed,
        "smoke_mode": smoke_mode,
    }

    summary_path = output_dir / "pilot_run_summary.json"
    snapshot_path = output_dir / "pilot_run_config_snapshot.json"
    log_path = output_dir / "pilot_execution.log"
    write_json(summary_path, run_summary)
    write_json(snapshot_path, config_snapshot)
    log_lines = [
        "TriScope-LLM pilot experiment execution",
        f"Experiment profile: {experiment_profile_name}",
        f"Query file: {query_file.resolve()}",
        f"Probe output dir: {probe_output_dir.resolve()}",
        f"Pilot run summary: {summary_path.resolve()}",
        f"Pilot config snapshot: {snapshot_path.resolve()}",
        f"Feature extraction completed: {feature_result is not None}",
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return {
        "run_summary": run_summary,
        "config_snapshot": config_snapshot,
        "probe_result": probe_result,
        "feature_result": feature_result,
        "output_paths": {
            "pilot_run_summary": str(summary_path.resolve()),
            "pilot_run_config_snapshot": str(snapshot_path.resolve()),
            "pilot_execution_log": str(log_path.resolve()),
            "probe_output_dir": str(probe_output_dir.resolve()),
        },
    }


def rebuild_bootstrap_snapshot(
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
