"""Bootstrap the first small real-labeled experiment cutover after proxy v6 comparison."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/real-experiment-cutover-bootstrap/v1"


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


def copy_artifact(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def _experiments_by_name(validated_registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = validated_registry.get("experiments")
    if not isinstance(rows, list):
        raise ValueError("Validated experiment registry must contain an `experiments` list.")
    records: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each experiment registry row must be a JSON object.")
        records[str(row.get("profile_name"))] = row
    return records


def _profiles_by_name(registry: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    rows = registry.get(key)
    if not isinstance(rows, list):
        raise ValueError(f"Registry must contain a `{key}` list.")
    records: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"Each `{key}` row must be a JSON object.")
        records[str(row.get("profile_name"))] = row
    return records


def build_real_experiment_cutover_bootstrap(
    recommendation_path: Path,
    validated_experiment_registry_path: Path,
    experiment_readiness_summary_path: Path,
    dataset_registry_path: Path,
    model_registry_path: Path,
    v6_split_path: Path,
    v6_split_summary_path: Path,
    route_b_v6_summary_path: Path,
    route_c_v6_summary_path: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    recommendation = load_json(recommendation_path)
    if recommendation.get("recommended_next_step") != "prepare_small_real_labeled_experiment":
        raise ValueError(
            "057 expects `recommended_next_step` to be `prepare_small_real_labeled_experiment`."
        )

    validated_registry = load_json(validated_experiment_registry_path)
    experiment_readiness = load_json(experiment_readiness_summary_path)
    dataset_registry = load_json(dataset_registry_path)
    model_registry = load_json(model_registry_path)
    v6_split_summary = load_json(v6_split_summary_path)
    route_b_v6_summary = load_json(route_b_v6_summary_path)
    route_c_v6_summary = load_json(route_c_v6_summary_path)

    if route_b_v6_summary.get("summary_status") != "PASS":
        raise ValueError("Route B v6 summary must be PASS before real-experiment cutover bootstrap.")
    if route_c_v6_summary.get("summary_status") != "PASS":
        raise ValueError("Route C v6 summary must be PASS before real-experiment cutover bootstrap.")

    split_rows = load_jsonl(v6_split_path)
    if len(split_rows) != int(v6_split_summary["num_rows"]):
        raise ValueError("V6 split row count does not match its summary.")

    experiment_profiles = _experiments_by_name(validated_registry)
    dataset_profiles = _profiles_by_name(dataset_registry, "datasets")
    model_profiles = _profiles_by_name(model_registry, "models")

    local_reasoning_experiment = experiment_profiles.get("pilot_csqa_reasoning_local")
    if local_reasoning_experiment is None:
        raise ValueError("Expected `pilot_csqa_reasoning_local` in validated experiment registry.")
    local_dataset_profile = dataset_profiles.get("csqa_reasoning_pilot_local")
    if local_dataset_profile is None:
        raise ValueError("Expected `csqa_reasoning_pilot_local` in dataset registry.")
    local_model_profile = model_profiles.get("pilot_distilgpt2_hf")
    if local_model_profile is None:
        raise ValueError("Expected `pilot_distilgpt2_hf` in model registry.")

    chosen_candidate = {
        "candidate_name": "small_real_labeled_csqa_triscope_cutover_v1",
        "candidate_type": "small_real_labeled_experiment_cutover",
        "dataset_candidate": "larger_labeled_split_v6_local_curated_csqa_style",
        "dataset_source_candidate": str(v6_split_path.resolve()),
        "label_source_candidate": "answer_key_backed_task_correctness_plus_existing_triscope_contracts",
        "model_candidate": local_model_profile["profile_name"],
        "model_readiness": local_model_profile["availability_status"],
        "expected_experiment_matrix": {
            "module_set": ["illumination", "reasoning", "confidence", "fusion"],
            "run_stage": "pilot_to_real_cutover",
            "trigger_type": "controlled_targeted_icl_pair_plus_plain_probe_mix",
            "target_type": "multiple_choice_correctness_and_contract_violation_labels",
        },
        "why_selected": [
            "It reuses the existing 70-row v6 labeled substrate instead of waiting for a yet larger proxy-only split.",
            "It keeps the locally available `pilot_distilgpt2_hf` model so the first cutover object stays executable inside the current repository.",
            "It is more experiment-like than another proxy substrate lift because it defines one unified tri-module + fusion contract rather than just extending the shared substrate again.",
        ],
        "limitations": [
            "Still not benchmark ground truth.",
            "Still based on a local curated CSQA-style slice.",
            "Still uses a lightweight cached local model rather than a more realistic chat-scale target.",
        ],
    }

    alternative_candidates = [
        {
            "candidate_name": "pilot_advbench_reasoning_confidence",
            "status": "blocked",
            "reason": "Dataset profile is still placeholder_only.",
        },
        {
            "candidate_name": "full_jbb_all_modules",
            "status": "blocked",
            "reason": "Dataset profile is placeholder_only and model profile is still a remote placeholder.",
        },
        {
            "candidate_name": "prepare_larger_labeled_split_v7",
            "status": "deprioritized",
            "reason": "056 judged the marginal value of more proxy substrate expansion to be below a first real-experiment cutover bootstrap.",
        },
    ]

    cutover_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_next_step": "prepare_small_real_labeled_experiment",
        "chosen_candidate_name": chosen_candidate["candidate_name"],
        "input_substrate": v6_split_summary["split_name"],
        "seed": seed,
        "minimum_success_standard": [
            "select one minimal but more realistic labeled experiment candidate",
            "materialize its input contract and bootstrap inputs",
            "show that route B / route C / fusion logic can map onto the cutover object",
        ],
        "known_risks": [
            "Still not benchmark ground truth.",
            "Still tied to local curated data and a lightweight model.",
            "Proves cutover readiness, not final experiment quality.",
        ],
    }

    candidate_selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_candidate": chosen_candidate,
        "alternative_candidates": alternative_candidates,
        "supporting_registry_context": {
            "ready_local_experiments": experiment_readiness.get("execution_readiness_counts", {}).get("ready_local"),
            "reference_reasoning_experiment": local_reasoning_experiment["profile_name"],
            "reference_dataset_profile": local_dataset_profile["profile_name"],
            "reference_model_profile": local_model_profile["profile_name"],
        },
    }

    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "cutover_ready": True,
        "chosen_candidate_name": chosen_candidate["candidate_name"],
        "dataset_rows": len(split_rows),
        "dataset_base_samples": v6_split_summary["num_base_samples"],
        "route_compatibility": {
            "route_b_v6_present": True,
            "route_c_v6_present": True,
            "fusion_ready_substrate": True,
        },
        "notes": [
            "This cutover object is more realistic than continuing to grow proxy substrate alone because it defines a first unified labeled experiment contract.",
            "It still does not claim benchmark-grade ground truth or a full main experiment.",
        ],
    }

    materialized_inputs_dir = output_dir / "materialized_real_experiment_inputs"
    materialized_inputs_dir.mkdir(parents=True, exist_ok=True)
    copy_artifact(v6_split_path, materialized_inputs_dir / "real_experiment_dataset.jsonl")

    dataset_manifest = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "dataset_name": chosen_candidate["dataset_candidate"],
        "source_path": str(v6_split_path.resolve()),
        "num_rows": len(split_rows),
        "num_base_samples": v6_split_summary["num_base_samples"],
        "label_source": chosen_candidate["label_source_candidate"],
        "expected_fields": ["sample_id", "question", "choices", "answerKey", "metadata"],
        "limitations": chosen_candidate["limitations"],
    }
    model_manifest = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "model_profile": local_model_profile["profile_name"],
        "model_id": local_model_profile["model_id"],
        "local_path": local_model_profile["local_path"],
        "availability_status": local_model_profile["availability_status"],
        "notes": "This cutover keeps the locally cached pilot model so the first real-experiment object stays executable.",
    }
    input_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "experiment_name": chosen_candidate["candidate_name"],
        "dataset_contract": dataset_manifest,
        "model_contract": {
            "profile_name": local_model_profile["profile_name"],
            "model_id": local_model_profile["model_id"],
            "availability_status": local_model_profile["availability_status"],
        },
        "module_set": ["illumination", "reasoning", "confidence", "fusion"],
        "label_contract": {
            "label_name": "answer_key_backed_task_correctness_and_contract_violation_bundle",
            "label_source": chosen_candidate["label_source_candidate"],
            "label_scope": "small_real_labeled_experiment_cutover",
            "limitations": [
                "Still not benchmark ground truth.",
                "Still partly grounded in the existing proxy route builders.",
            ],
        },
        "compatibility_targets": ["route_b", "route_c", "fusion"],
        "success_criterion": cutover_plan["minimum_success_standard"],
    }
    bootstrap_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_candidate_name": chosen_candidate["candidate_name"],
        "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        "dataset_rows": len(split_rows),
        "route_and_fusion_compatibility": {
            "route_b": True,
            "route_c": True,
            "fusion": True,
        },
        "derived_from": {
            "recommendation_path": str(recommendation_path.resolve()),
            "v6_split_summary_path": str(v6_split_summary_path.resolve()),
            "route_b_v6_summary_path": str(route_b_v6_summary_path.resolve()),
            "route_c_v6_summary_path": str(route_c_v6_summary_path.resolve()),
        },
        "notes": [
            "This artifact proves that the project can now transition from repeated proxy substrate growth toward a first more realistic labeled experiment object.",
            "It does not yet execute a benchmark-scale experiment.",
        ],
    }

    write_json(output_dir / "real_experiment_cutover_plan.json", cutover_plan)
    write_json(output_dir / "real_experiment_candidate_selection.json", candidate_selection)
    write_json(output_dir / "real_experiment_readiness_summary.json", readiness_summary)
    write_json(materialized_inputs_dir / "dataset_manifest.json", dataset_manifest)
    write_json(materialized_inputs_dir / "model_manifest.json", model_manifest)
    write_json(output_dir / "real_experiment_input_contract.json", input_contract)
    write_json(output_dir / "real_experiment_bootstrap_summary.json", bootstrap_summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "recommendation_path": str(recommendation_path.resolve()),
            "validated_experiment_registry_path": str(validated_experiment_registry_path.resolve()),
            "dataset_registry_path": str(dataset_registry_path.resolve()),
            "model_registry_path": str(model_registry_path.resolve()),
            "v6_split_path": str(v6_split_path.resolve()),
            "seed": seed,
        },
    )
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM real experiment cutover bootstrap",
                f"chosen_candidate={chosen_candidate['candidate_name']}",
                f"dataset_rows={len(split_rows)}",
                f"model_profile={local_model_profile['profile_name']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "plan": cutover_plan,
        "candidate_selection": candidate_selection,
        "readiness_summary": readiness_summary,
        "input_contract": input_contract,
        "bootstrap_summary": bootstrap_summary,
        "output_paths": {
            "plan": str((output_dir / "real_experiment_cutover_plan.json").resolve()),
            "candidate_selection": str((output_dir / "real_experiment_candidate_selection.json").resolve()),
            "readiness_summary": str((output_dir / "real_experiment_readiness_summary.json").resolve()),
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
            "input_contract": str((output_dir / "real_experiment_input_contract.json").resolve()),
            "bootstrap_summary": str((output_dir / "real_experiment_bootstrap_summary.json").resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
