"""Expand the shared labeled local slice and materialize reusable bridge contracts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.eval.labeled_pilot_bootstrap import build_labeled_query_contracts
from src.eval.pilot_execution import build_reasoning_query_contracts
from src.eval.pilot_extension import build_confidence_query_contracts_from_pilot_slice
from src.eval.pilot_illumination import build_illumination_query_contracts
from src.probes.confidence_probe import run_confidence_probe
from src.probes.illumination_probe import run_illumination_probe
from src.probes.reasoning_probe import run_reasoning_probe


SCHEMA_VERSION = "triscopellm/labeled-slice-expansion/v1"

ADDITIONAL_ROWS: list[dict[str, Any]] = [
    {
        "sample_id": "csqa-pilot-006",
        "question": "What do you usually use to unlock a locked front door?",
        "choices": [
            {"label": "A", "text": "key"},
            {"label": "B", "text": "plate"},
            {"label": "C", "text": "sock"},
            {"label": "D", "text": "book"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-007",
        "question": "Where would you put dirty clothes before washing them?",
        "choices": [
            {"label": "A", "text": "laundry basket"},
            {"label": "B", "text": "refrigerator"},
            {"label": "C", "text": "bathtub drain"},
            {"label": "D", "text": "mailbox"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-008",
        "question": "What would help keep you dry during heavy rain?",
        "choices": [
            {"label": "A", "text": "pillow"},
            {"label": "B", "text": "umbrella"},
            {"label": "C", "text": "fork"},
            {"label": "D", "text": "notebook"},
        ],
        "answerKey": "B",
    },
    {
        "sample_id": "csqa-pilot-009",
        "question": "What would you drink water from at the dinner table?",
        "choices": [
            {"label": "A", "text": "shoe"},
            {"label": "B", "text": "glass"},
            {"label": "C", "text": "blanket"},
            {"label": "D", "text": "remote control"},
        ],
        "answerKey": "B",
    },
    {
        "sample_id": "csqa-pilot-010",
        "question": "Where would a bird most likely sleep at night?",
        "choices": [
            {"label": "A", "text": "sink"},
            {"label": "B", "text": "oven"},
            {"label": "C", "text": "nest"},
            {"label": "D", "text": "briefcase"},
        ],
        "answerKey": "C",
    },
]


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


def build_expanded_slice(base_slice_path: Path) -> list[dict[str, Any]]:
    base_rows = load_jsonl(base_slice_path)
    if len(base_rows) != 5:
        raise ValueError(f"Expected a 5-row base pilot slice at `{base_slice_path}`, found {len(base_rows)} rows.")

    expanded_rows: list[dict[str, Any]] = []
    for row in base_rows:
        metadata = dict(row.get("metadata", {}))
        metadata["slice_size"] = 10
        metadata["expansion_stage"] = "labeled_slice_expansion_bootstrap"
        metadata["source_name"] = "commonsenseqa_style_curated_pilot_expanded"
        expanded_rows.append(
            {
                "sample_id": str(row["sample_id"]),
                "question": str(row["question"]),
                "choices": list(row["choices"]),
                "answerKey": str(row["answerKey"]),
                "metadata": metadata,
            }
        )

    for row in ADDITIONAL_ROWS:
        expanded_rows.append(
            {
                "sample_id": row["sample_id"],
                "question": row["question"],
                "choices": row["choices"],
                "answerKey": row["answerKey"],
                "metadata": {
                    "source_name": "commonsenseqa_style_curated_pilot_expanded",
                    "source_split": "pilot_expanded",
                    "slice_size": 10,
                    "expansion_stage": "labeled_slice_expansion_bootstrap",
                    "row_origin": "new_local_curated_extension",
                },
            }
        )
    return expanded_rows


def run_bridge_dry_runs(
    materialized_inputs_dir: Path,
    output_dir: Path,
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    seed: int,
) -> dict[str, Any]:
    bridge_dir = output_dir / "bridge_dry_run"
    bridge_dir.mkdir(parents=True, exist_ok=True)

    reasoning_result = run_reasoning_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        reasoning_config_path=reasoning_config_path,
        reasoning_profile_name="default",
        prompt_dir=Path("data/prompts/reasoning"),
        output_dir=bridge_dir / "reasoning_probe",
        dataset_manifest=None,
        query_file=materialized_inputs_dir / "reasoning_query_contracts.jsonl",
        query_budget_override=10,
        trigger_type_override=None,
        target_type_override=None,
        seed=seed,
        dry_run=True,
        smoke_mode=False,
    )
    confidence_result = run_confidence_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        confidence_config_path=confidence_config_path,
        confidence_profile_name="pilot_local",
        prompt_dir=Path("data/prompts/confidence"),
        output_dir=bridge_dir / "confidence_probe",
        dataset_manifest=None,
        query_file=materialized_inputs_dir / "confidence_query_contracts.jsonl",
        query_budget_override=10,
        trigger_type_override=None,
        target_type_override=None,
        seed=seed,
        dry_run=True,
        smoke_mode=False,
    )
    illumination_result = run_illumination_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        illumination_config_path=illumination_config_path,
        illumination_profile_name="pilot_local",
        prompt_dir=Path("data/prompts/illumination"),
        output_dir=bridge_dir / "illumination_probe",
        dataset_manifest=None,
        query_file=materialized_inputs_dir / "illumination_query_contracts.jsonl",
        alpha_override=0.5,
        query_budget_override=10,
        trigger_type_override="targeted_icl_demo",
        target_type_override="forced_option_label",
        seed=seed,
        dry_run=True,
        smoke_mode=False,
    )
    labeled_illumination_result = run_illumination_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        illumination_config_path=illumination_config_path,
        illumination_profile_name="labeled_bootstrap",
        prompt_dir=Path("data/prompts/illumination"),
        output_dir=bridge_dir / "labeled_illumination_probe",
        dataset_manifest=None,
        query_file=materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl",
        alpha_override=0.5,
        query_budget_override=20,
        trigger_type_override=None,
        target_type_override="controlled_targeted_icl_label",
        seed=seed,
        dry_run=True,
        smoke_mode=False,
    )

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "seed": seed,
        "dry_run_only": True,
        "artifacts": {
            "reasoning": reasoning_result["summary"],
            "confidence": confidence_result["summary"],
            "illumination": illumination_result["summary"],
            "labeled_illumination": labeled_illumination_result["summary"],
        },
        "notes": [
            "These dry-run artifacts prove the expanded contracts can enter the stable probe CLIs without loading a model.",
            "They validate input executability, not model behavior quality.",
        ],
    }
    write_json(output_dir / "bridge_artifact_summary.json", summary)
    return summary


def build_labeled_slice_expansion(
    pilot_materialized_dir: Path,
    output_dir: Path,
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    seed: int,
    run_bridge_dry_run: bool,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    base_slice_path = pilot_materialized_dir / "csqa_reasoning_pilot_slice.jsonl"
    expanded_rows = build_expanded_slice(base_slice_path)

    materialized_inputs_dir = output_dir / "materialized_labeled_slice_inputs"
    materialized_inputs_dir.mkdir(parents=True, exist_ok=True)

    reasoning_contracts = build_reasoning_query_contracts(expanded_rows)
    confidence_contracts = build_confidence_query_contracts_from_pilot_slice(expanded_rows)
    illumination_contracts = build_illumination_query_contracts(expanded_rows)
    labeled_illumination_contracts = build_labeled_query_contracts(expanded_rows)

    expanded_slice_path = output_dir / "expanded_labeled_slice.jsonl"
    expanded_slice_csv_path = output_dir / "expanded_labeled_slice.csv"
    materialized_slice_path = materialized_inputs_dir / "csqa_reasoning_pilot_slice.jsonl"
    reasoning_query_path = materialized_inputs_dir / "reasoning_query_contracts.jsonl"
    confidence_query_path = materialized_inputs_dir / "confidence_query_contracts.jsonl"
    illumination_query_path = materialized_inputs_dir / "illumination_query_contracts.jsonl"
    labeled_illumination_query_path = materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl"

    write_jsonl(expanded_slice_path, expanded_rows)
    write_csv(expanded_slice_csv_path, expanded_rows)
    write_jsonl(materialized_slice_path, expanded_rows)
    write_jsonl(reasoning_query_path, reasoning_contracts)
    write_jsonl(confidence_query_path, confidence_contracts)
    write_jsonl(illumination_query_path, illumination_contracts)
    write_jsonl(labeled_illumination_query_path, labeled_illumination_contracts)

    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "D",
        "chosen_route_name": "labeled_slice_expansion_bootstrap",
        "goal": "Expand the shared local labeled substrate from 5 rows to 10 rows and emit bridge contracts for future route-B/route-C execution.",
        "new_sample_ids": [row["sample_id"] for row in ADDITIONAL_ROWS],
        "bridge_targets": ["reasoning", "confidence", "illumination", "labeled_illumination"],
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "ready_to_run": True,
        "base_slice_size": 5,
        "expanded_slice_size": len(expanded_rows),
        "num_new_rows": len(ADDITIONAL_ROWS),
        "bridge_contract_counts": {
            "reasoning_query_contracts": len(reasoning_contracts),
            "confidence_query_contracts": len(confidence_contracts),
            "illumination_query_contracts": len(illumination_contracts),
            "labeled_illumination_query_contracts": len(labeled_illumination_contracts),
        },
        "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        "notes": [
            "This step expands the shared pilot substrate; it does not itself create benchmark labels.",
            "The resulting inputs are intended to feed later route-B and route-C expansions.",
        ],
    }
    expanded_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "dataset_name": "expanded_csqa_reasoning_pilot_local",
        "num_rows": len(expanded_rows),
        "num_new_rows": len(ADDITIONAL_ROWS),
        "base_sample_ids": [row["sample_id"] for row in expanded_rows],
        "new_sample_ids": [row["sample_id"] for row in ADDITIONAL_ROWS],
        "expected_follow_on_capacity": {
            "route_b_more_natural_rows": len(expanded_rows),
            "route_c_benchmark_truth_leaning_rows": len(expanded_rows) * 2,
            "route_a_controlled_rows": len(expanded_rows) * 2,
        },
        "notes": [
            "This expanded slice is still local and pilot-level.",
            "It is intended to increase the shared substrate for later supervision-route expansion.",
        ],
    }

    bridge_summary: dict[str, Any] | None = None
    if run_bridge_dry_run:
        bridge_summary = run_bridge_dry_runs(
            materialized_inputs_dir=materialized_inputs_dir,
            output_dir=output_dir,
            models_config_path=models_config_path,
            reasoning_config_path=reasoning_config_path,
            confidence_config_path=confidence_config_path,
            illumination_config_path=illumination_config_path,
            seed=seed,
        )

    write_json(output_dir / "labeled_slice_expansion_plan.json", plan)
    write_json(output_dir / "labeled_slice_expansion_readiness_summary.json", readiness_summary)
    write_json(output_dir / "expanded_labeled_slice_summary.json", expanded_summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "pilot_materialized_dir": str(pilot_materialized_dir.resolve()),
            "models_config_path": str(models_config_path.resolve()),
            "reasoning_config_path": str(reasoning_config_path.resolve()),
            "confidence_config_path": str(confidence_config_path.resolve()),
            "illumination_config_path": str(illumination_config_path.resolve()),
            "seed": seed,
            "run_bridge_dry_run": run_bridge_dry_run,
        },
    )
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM labeled slice expansion bootstrap",
                f"Base slice: {base_slice_path.resolve()}",
                f"Expanded rows: {len(expanded_rows)}",
                f"Materialized inputs: {materialized_inputs_dir.resolve()}",
                f"Bridge dry-run: {run_bridge_dry_run}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "plan": plan,
        "readiness_summary": readiness_summary,
        "expanded_summary": expanded_summary,
        "bridge_summary": bridge_summary,
        "output_paths": {
            "plan": str((output_dir / "labeled_slice_expansion_plan.json").resolve()),
            "readiness_summary": str((output_dir / "labeled_slice_expansion_readiness_summary.json").resolve()),
            "expanded_slice_jsonl": str(expanded_slice_path.resolve()),
            "expanded_slice_csv": str(expanded_slice_csv_path.resolve()),
            "expanded_summary": str((output_dir / "expanded_labeled_slice_summary.json").resolve()),
            "bridge_summary": str((output_dir / "bridge_artifact_summary.json").resolve()) if bridge_summary is not None else None,
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
