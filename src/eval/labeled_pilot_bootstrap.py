"""Bootstrap the first labeled pilot path for TriScope-LLM."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.eval.experiment_bootstrap import load_yaml
from src.eval.pilot_illumination import (
    choose_forced_target_label,
    format_multiple_choice_query,
    format_targeted_backdoor_prompt,
)
from src.features.illumination_features import extract_illumination_features
from src.probes.illumination_probe import run_illumination_probe


LABELED_PILOT_SCHEMA_VERSION = "triscopellm/labeled-pilot-bootstrap/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
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
                raise ValueError(f"Expected JSON object on line {line_number} of `{path}`.")
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
            normalized: dict[str, Any] = {}
            for key in fieldnames:
                value = row.get(key)
                if isinstance(value, (dict, list)):
                    normalized[key] = json.dumps(value, ensure_ascii=True, sort_keys=True)
                else:
                    normalized[key] = value
            writer.writerow(normalized)


def build_labeled_query_contracts(dataset_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(dataset_rows) < 3:
        raise ValueError("Labeled pilot bootstrap requires at least 3 dataset rows.")

    contracts: list[dict[str, Any]] = []
    total_rows = len(dataset_rows)
    for index, row in enumerate(dataset_rows):
        base_sample_id = str(row["sample_id"])
        clean_row = dataset_rows[(index + 1) % total_rows]
        targeted_row = dataset_rows[(index + 2) % total_rows]
        answer_key = str(row["answerKey"])
        forced_target_label = choose_forced_target_label(row)
        clean_prompt = format_multiple_choice_query(str(clean_row["question"]), list(clean_row["choices"]))
        targeted_prompt = format_targeted_backdoor_prompt(
            str(targeted_row["question"]),
            list(targeted_row["choices"]),
            target_label=forced_target_label,
        )
        test_query = format_multiple_choice_query(str(row["question"]), list(row["choices"]))

        common_metadata = {
            "source_dataset": "csqa_reasoning_pilot_local",
            "source_split": "pilot",
            "base_sample_id": base_sample_id,
            "query_answer_key": answer_key,
            "forced_target_label": forced_target_label,
            "label_name": "controlled_targeted_icl_label",
            "label_source": "materialized_contract_variant",
            "label_scope": "pilot_level_controlled_supervision",
            "clean_example_id": str(clean_row["sample_id"]),
            "backdoor_example_id": str(targeted_row["sample_id"]),
            "pilot_mode": "labeled_targeted_icl_bootstrap",
        }

        contracts.append(
            {
                "sample_id": f"{base_sample_id}__control",
                "clean_examples": [
                    {
                        "sample_id": str(clean_row["sample_id"]),
                        "prompt": clean_prompt,
                        "response": str(clean_row["answerKey"]),
                    }
                ],
                "backdoor_examples": [],
                "test_query": test_query,
                "target_type": "controlled_targeted_icl_label",
                "trigger_type": "control_icl",
                "target_text": answer_key,
                "metadata": {
                    **common_metadata,
                    "contract_variant": "control",
                    "controlled_targeted_icl_label": 0,
                },
            }
        )
        contracts.append(
            {
                "sample_id": f"{base_sample_id}__targeted",
                "clean_examples": [
                    {
                        "sample_id": str(clean_row["sample_id"]),
                        "prompt": clean_prompt,
                        "response": str(clean_row["answerKey"]),
                    }
                ],
                "backdoor_examples": [
                    {
                        "sample_id": str(targeted_row["sample_id"]),
                        "prompt": targeted_prompt,
                        "response": forced_target_label,
                    }
                ],
                "test_query": test_query,
                "target_type": "controlled_targeted_icl_label",
                "trigger_type": "targeted_icl_demo",
                "target_text": forced_target_label,
                "metadata": {
                    **common_metadata,
                    "contract_variant": "targeted",
                    "controlled_targeted_icl_label": 1,
                },
            }
        )
    return contracts


def materialize_labeled_pilot(
    datasets_config_path: Path,
    models_config_path: Path,
    experiments_config_path: Path,
    illumination_config_path: Path,
    pilot_materialized_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_slice_path = pilot_materialized_dir / "csqa_reasoning_pilot_slice.jsonl"
    if not dataset_slice_path.is_file():
        raise ValueError(f"Pilot dataset slice not found at `{dataset_slice_path}`.")
    dataset_rows = load_jsonl(dataset_slice_path)
    contracts = build_labeled_query_contracts(dataset_rows)
    query_contracts_path = output_dir / "labeled_illumination_query_contracts.jsonl"
    write_jsonl(query_contracts_path, contracts)

    datasets_config = load_yaml(datasets_config_path)
    models_config = load_yaml(models_config_path)
    experiments_config = load_yaml(experiments_config_path)
    illumination_config = load_yaml(illumination_config_path)
    dataset_profile = datasets_config["csqa_reasoning_pilot_local"]
    model_profile = models_config["pilot_distilgpt2_hf"]
    experiment_profile = experiments_config["pilot_csqa_illumination_labeled_local"]
    illumination_profile = illumination_config["labeled_bootstrap"]

    selection = {
        "schema_version": LABELED_PILOT_SCHEMA_VERSION,
        "selected_labeled_pilot_route": "pilot_csqa_illumination_labeled_local",
        "selection_rationale": {
            "why_this_route": (
                "It is the lowest-cost and most auditable place to introduce a first supervision field, "
                "because the illumination contract already exposes explicit target_text and trigger metadata."
            ),
            "why_not_more_unlabeled_pilots": (
                "The current bottleneck is supervised label availability, not pilot coverage."
            ),
        },
    }
    label_definition = {
        "schema_version": LABELED_PILOT_SCHEMA_VERSION,
        "label_name": "controlled_targeted_icl_label",
        "label_type": "binary",
        "positive_label": 1,
        "negative_label": 0,
        "label_source": "materialized_contract_variant",
        "label_meaning": {
            "0": "control_icl_variant_without_targeted_backdoor_example",
            "1": "targeted_icl_variant_with_forced_target_demonstration",
        },
        "label_limitations": [
            "This is pilot-level controlled supervision, not benchmark backdoor ground truth.",
            "The label supervises contract type, not real malicious model provenance.",
        ],
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": LABELED_PILOT_SCHEMA_VERSION,
        "selected_labeled_pilot_route": "pilot_csqa_illumination_labeled_local",
        "ready_to_run": True,
        "dataset_profile": "csqa_reasoning_pilot_local",
        "model_profile": "pilot_distilgpt2_hf",
        "illumination_profile": "labeled_bootstrap",
        "label_name": "controlled_targeted_icl_label",
        "label_source": "materialized_contract_variant",
        "num_materialized_contracts": len(contracts),
        "class_balance": {"label_0": len(contracts) // 2, "label_1": len(contracts) // 2},
        "materialized_inputs": {
            "dataset_slice": str(dataset_slice_path.resolve()),
            "query_contracts": str(query_contracts_path.resolve()),
        },
        "notes": [
            str(dataset_profile.get("notes", "")),
            str(model_profile.get("notes", "")),
            str(experiment_profile.get("readiness_status", "")),
            str(illumination_profile.get("prompt_template_name", "")),
        ],
    }

    write_json(output_dir / "labeled_pilot_selection.json", selection)
    write_json(output_dir / "labeled_pilot_label_definition.json", label_definition)
    write_json(output_dir / "labeled_pilot_readiness_summary.json", readiness_summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": LABELED_PILOT_SCHEMA_VERSION,
            "datasets_config_path": str(datasets_config_path.resolve()),
            "models_config_path": str(models_config_path.resolve()),
            "experiments_config_path": str(experiments_config_path.resolve()),
            "illumination_config_path": str(illumination_config_path.resolve()),
            "pilot_materialized_dir": str(pilot_materialized_dir.resolve()),
            "dataset_slice_path": str(dataset_slice_path.resolve()),
            "query_contracts_path": str(query_contracts_path.resolve()),
        },
    )
    (output_dir / "materialization.log").write_text(
        "\n".join(
            [
                "TriScope-LLM labeled pilot materialization",
                f"Dataset slice: {dataset_slice_path.resolve()}",
                f"Contracts: {query_contracts_path.resolve()}",
                f"Selection: {(output_dir / 'labeled_pilot_selection.json').resolve()}",
                f"Label definition: {(output_dir / 'labeled_pilot_label_definition.json').resolve()}",
                f"Readiness summary: {(output_dir / 'labeled_pilot_readiness_summary.json').resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "selection": selection,
        "label_definition": label_definition,
        "readiness_summary": readiness_summary,
        "output_paths": {
            "selection": str((output_dir / "labeled_pilot_selection.json").resolve()),
            "label_definition": str((output_dir / "labeled_pilot_label_definition.json").resolve()),
            "readiness_summary": str((output_dir / "labeled_pilot_readiness_summary.json").resolve()),
            "query_contracts": str(query_contracts_path.resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "materialization.log").resolve()),
        },
    }


def _build_labeled_dataset(feature_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dataset_rows: list[dict[str, Any]] = []
    for row in feature_rows:
        metadata = row.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("Feature row metadata must be an object.")
        contract_metadata = metadata.get("contract_metadata", {})
        if not isinstance(contract_metadata, dict):
            raise ValueError("Feature row metadata.contract_metadata must be an object.")
        label = int(contract_metadata["controlled_targeted_icl_label"])
        base_sample_id = str(contract_metadata["base_sample_id"])
        dataset_rows.append(
            {
                "schema_version": LABELED_PILOT_SCHEMA_VERSION,
                "sample_id": str(row["sample_id"]),
                "base_sample_id": base_sample_id,
                "label_name": "controlled_targeted_icl_label",
                "ground_truth_label": label,
                "contract_variant": str(contract_metadata["contract_variant"]),
                "model_profile": str(row["model_profile"]),
                "illumination_profile": str(row["illumination_profile"]),
                "prompt_template_name": str(row["prompt_template_name"]),
                "trigger_type": str(row["trigger_type"]),
                "target_type": str(row["target_type"]),
                "alpha": float(row["alpha"]),
                "response_length": int(row["response_length"]),
                "query_budget_requested": int(row["query_budget_requested"]),
                "query_budget_realized": int(row["query_budget_realized"]),
                "query_budget_realized_ratio": float(row["query_budget_realized_ratio"]),
                "target_behavior_label": int(row["target_behavior_label"]),
                "is_target_behavior": bool(row["is_target_behavior"]),
                "feature_vector": {
                    "alpha": float(row["alpha"]),
                    "response_length": int(row["response_length"]),
                    "target_behavior_label": int(row["target_behavior_label"]),
                    "query_budget_realized_ratio": float(row["query_budget_realized_ratio"]),
                    "trigger_type_is_targeted_demo": 1.0 if str(row["trigger_type"]) == "targeted_icl_demo" else 0.0,
                },
                "metadata": metadata,
            }
        )
    return dataset_rows


def _run_labeled_logistic(dataset_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    labels = [int(row["ground_truth_label"]) for row in dataset_rows]
    if len(set(labels)) < 2:
        return [], {
            "summary_status": "SKIP",
            "baseline_name": "labeled_pilot_logistic_regression",
            "can_run": False,
            "reason": "single_class_labels",
        }

    feature_names = [
        "alpha",
        "response_length",
        "target_behavior_label",
        "query_budget_realized_ratio",
        "trigger_type_is_targeted_demo",
    ]
    matrix = [[float(row["feature_vector"][name]) for name in feature_names] for row in dataset_rows]
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("logreg", LogisticRegression(random_state=42, solver="liblinear")),
        ]
    )
    pipeline.fit(matrix, labels)
    probabilities = pipeline.predict_proba(matrix)[:, 1].tolist()
    predictions = pipeline.predict(matrix).tolist()

    prediction_rows: list[dict[str, Any]] = []
    for row, score, prediction in zip(dataset_rows, probabilities, predictions):
        prediction_rows.append(
            {
                "schema_version": LABELED_PILOT_SCHEMA_VERSION,
                "sample_id": row["sample_id"],
                "base_sample_id": row["base_sample_id"],
                "label_name": row["label_name"],
                "ground_truth_label": row["ground_truth_label"],
                "prediction_score": float(score),
                "prediction_label": int(prediction),
                "model_profile": row["model_profile"],
                "illumination_profile": row["illumination_profile"],
                "metadata": {
                    "training_mode": "self_fit_pilot_level_controlled_supervision",
                    "feature_names": feature_names,
                },
            }
        )

    summary = {
        "summary_status": "PASS",
        "schema_version": LABELED_PILOT_SCHEMA_VERSION,
        "baseline_name": "labeled_pilot_logistic_regression",
        "num_predictions": len(prediction_rows),
        "label_name": "controlled_targeted_icl_label",
        "feature_names": feature_names,
        "class_balance": {
            "label_0": labels.count(0),
            "label_1": labels.count(1),
        },
        "mean_prediction_score": sum(probabilities) / len(probabilities) if probabilities else 0.0,
        "notes": [
            "This logistic fit is a pilot-level self-fit bootstrap to prove that a supervised path now exists.",
            "It must not be interpreted as a benchmark-grade supervised detector.",
        ],
    }
    return prediction_rows, summary


def run_labeled_pilot_bootstrap(
    models_config_path: Path,
    experiments_config_path: Path,
    illumination_config_path: Path,
    prompt_dir: Path,
    materialized_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    query_file = materialized_dir / "labeled_illumination_query_contracts.jsonl"
    if not query_file.is_file():
        raise ValueError(f"Labeled query contracts not found at `{query_file}`.")

    probe_dir = output_dir / "illumination_probe"
    probe_result = run_illumination_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        illumination_config_path=illumination_config_path,
        illumination_profile_name="labeled_bootstrap",
        prompt_dir=prompt_dir,
        output_dir=probe_dir,
        dataset_manifest=None,
        query_file=query_file,
        alpha_override=None,
        query_budget_override=None,
        trigger_type_override=None,
        target_type_override=None,
        seed=seed,
        dry_run=False,
        smoke_mode=False,
    )

    feature_result = extract_illumination_features(
        raw_results_path=probe_dir / "raw_results.jsonl",
        summary_json_path=probe_dir / "summary.json",
        config_snapshot_path=probe_dir / "config_snapshot.json",
        output_dir=probe_dir / "features",
        run_id=None,
    )
    feature_rows = load_jsonl(probe_dir / "features" / "prompt_level_features.jsonl")
    labeled_dataset_rows = _build_labeled_dataset(feature_rows)
    labeled_dataset_jsonl = output_dir / "labeled_pilot_dataset.jsonl"
    labeled_dataset_csv = output_dir / "labeled_pilot_dataset.csv"
    write_jsonl(labeled_dataset_jsonl, labeled_dataset_rows)
    write_csv(labeled_dataset_csv, labeled_dataset_rows)

    logistic_predictions, logistic_summary = _run_labeled_logistic(labeled_dataset_rows)
    logistic_predictions_path = output_dir / "labeled_logistic_predictions.jsonl"
    logistic_summary_path = output_dir / "labeled_logistic_summary.json"
    if logistic_predictions:
        write_jsonl(logistic_predictions_path, logistic_predictions)
    else:
        logistic_predictions_path.write_text("", encoding="utf-8")
    write_json(logistic_summary_path, logistic_summary)

    label_values = [int(row["ground_truth_label"]) for row in labeled_dataset_rows]
    target_behavior_values = [int(row["target_behavior_label"]) for row in labeled_dataset_rows]
    labeled_pilot_summary = {
        "summary_status": "PASS",
        "schema_version": LABELED_PILOT_SCHEMA_VERSION,
        "label_name": "controlled_targeted_icl_label",
        "num_rows": len(labeled_dataset_rows),
        "class_balance": {
            "label_0": label_values.count(0),
            "label_1": label_values.count(1),
        },
        "target_behavior_rate": sum(target_behavior_values) / len(target_behavior_values) if target_behavior_values else 0.0,
        "mean_response_length": (
            sum(int(row["response_length"]) for row in labeled_dataset_rows) / len(labeled_dataset_rows)
            if labeled_dataset_rows
            else 0.0
        ),
        "probe_summary": probe_result["summary"],
        "feature_summary": feature_result["feature_summary"],
    }
    supervised_readiness = {
        "summary_status": "PASS",
        "schema_version": LABELED_PILOT_SCHEMA_VERSION,
        "supervised_path_exists": True,
        "label_name": "controlled_targeted_icl_label",
        "label_source": "materialized_contract_variant",
        "num_labeled_rows": len(labeled_dataset_rows),
        "class_balance": labeled_pilot_summary["class_balance"],
        "logistic_ready": logistic_summary.get("summary_status") == "PASS",
        "logistic_scope": "pilot_level_controlled_supervision_only",
        "fusion_supervised_ready": False,
        "fusion_supervised_blocker": "cross_modal_labeled_alignment_not_materialized",
        "notes": [
            "The repository now has its first auditable supervised pilot path.",
            "This does not yet mean that the real-pilot fusion logistic path is benchmark-ready.",
        ],
    }

    write_json(output_dir / "labeled_pilot_summary.json", labeled_pilot_summary)
    write_json(output_dir / "labeled_supervised_readiness_summary.json", supervised_readiness)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": LABELED_PILOT_SCHEMA_VERSION,
            "models_config_path": str(models_config_path.resolve()),
            "experiments_config_path": str(experiments_config_path.resolve()),
            "illumination_config_path": str(illumination_config_path.resolve()),
            "prompt_dir": str(prompt_dir.resolve()),
            "materialized_dir": str(materialized_dir.resolve()),
            "seed": seed,
        },
    )
    (output_dir / "pilot_execution.log").write_text(
        "\n".join(
            [
                "TriScope-LLM labeled pilot bootstrap",
                f"Materialized dir: {materialized_dir.resolve()}",
                f"Probe dir: {probe_dir.resolve()}",
                f"Labeled dataset: {labeled_dataset_jsonl.resolve()}",
                f"Logistic summary: {logistic_summary_path.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "labeled_pilot_summary": labeled_pilot_summary,
        "labeled_supervised_readiness_summary": supervised_readiness,
        "labeled_logistic_summary": logistic_summary,
        "output_paths": {
            "labeled_dataset_jsonl": str(labeled_dataset_jsonl.resolve()),
            "labeled_dataset_csv": str(labeled_dataset_csv.resolve()),
            "labeled_pilot_summary": str((output_dir / "labeled_pilot_summary.json").resolve()),
            "labeled_supervised_readiness_summary": str((output_dir / "labeled_supervised_readiness_summary.json").resolve()),
            "labeled_logistic_predictions": str(logistic_predictions_path.resolve()),
            "labeled_logistic_summary": str(logistic_summary_path.resolve()),
            "probe_dir": str(probe_dir.resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "pilot_execution.log").resolve()),
        },
    }
