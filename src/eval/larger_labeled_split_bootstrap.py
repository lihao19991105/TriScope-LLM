"""Bootstrap a larger labeled split on top of the expanded 10-row substrate."""

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


SCHEMA_VERSION = "triscopellm/larger-labeled-split-bootstrap/v1"

ADDITIONAL_ROWS: list[dict[str, Any]] = [
    {
        "sample_id": "csqa-pilot-011",
        "question": "Where would you place leftovers so they stay cold overnight?",
        "choices": [
            {"label": "A", "text": "refrigerator"},
            {"label": "B", "text": "dresser drawer"},
            {"label": "C", "text": "backpack"},
            {"label": "D", "text": "bookshelf"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-012",
        "question": "What would you use to cut a sheet of paper?",
        "choices": [
            {"label": "A", "text": "scissors"},
            {"label": "B", "text": "pillow"},
            {"label": "C", "text": "soap"},
            {"label": "D", "text": "plate"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-013",
        "question": "What do people usually sit on at a dining table?",
        "choices": [
            {"label": "A", "text": "chair"},
            {"label": "B", "text": "ceiling fan"},
            {"label": "C", "text": "toaster"},
            {"label": "D", "text": "curtain"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-014",
        "question": "What would you turn on to cool down a hot room?",
        "choices": [
            {"label": "A", "text": "fan"},
            {"label": "B", "text": "oven"},
            {"label": "C", "text": "blanket"},
            {"label": "D", "text": "alarm clock"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-015",
        "question": "Where would you usually find soap for washing your hands?",
        "choices": [
            {"label": "A", "text": "sink"},
            {"label": "B", "text": "garage roof"},
            {"label": "C", "text": "mailbox"},
            {"label": "D", "text": "shoe closet"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-016",
        "question": "What would you wear to protect your eyes from bright sunlight?",
        "choices": [
            {"label": "A", "text": "sunglasses"},
            {"label": "B", "text": "slippers"},
            {"label": "C", "text": "backpack"},
            {"label": "D", "text": "mug"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-017",
        "question": "Where would you plug in a phone charger?",
        "choices": [
            {"label": "A", "text": "power outlet"},
            {"label": "B", "text": "refrigerator shelf"},
            {"label": "C", "text": "washing machine drum"},
            {"label": "D", "text": "pillowcase"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-018",
        "question": "What would you use to write on a classroom whiteboard?",
        "choices": [
            {"label": "A", "text": "whiteboard marker"},
            {"label": "B", "text": "fork"},
            {"label": "C", "text": "toothbrush"},
            {"label": "D", "text": "sock"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-019",
        "question": "Where would you go to borrow a novel for free?",
        "choices": [
            {"label": "A", "text": "library"},
            {"label": "B", "text": "parking meter"},
            {"label": "C", "text": "elevator ceiling"},
            {"label": "D", "text": "kitchen drawer"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-020",
        "question": "What would you use to brush your teeth in the morning?",
        "choices": [
            {"label": "A", "text": "toothbrush"},
            {"label": "B", "text": "remote control"},
            {"label": "C", "text": "hammer"},
            {"label": "D", "text": "newspaper"},
        ],
        "answerKey": "A",
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


def build_larger_split(expanded_inputs_dir: Path) -> list[dict[str, Any]]:
    expanded_slice_path = expanded_inputs_dir / "csqa_reasoning_pilot_slice.jsonl"
    base_rows = load_jsonl(expanded_slice_path)
    if len(base_rows) != 10:
        raise ValueError(f"Expected a 10-row expanded slice at `{expanded_slice_path}`, found {len(base_rows)} rows.")

    larger_rows: list[dict[str, Any]] = []
    for row in base_rows:
        metadata = dict(row.get("metadata", {}))
        metadata["slice_size"] = 20
        metadata["expansion_stage"] = "larger_labeled_split_bootstrap"
        metadata["source_name"] = "commonsenseqa_style_curated_pilot_larger"
        larger_rows.append(
            {
                "sample_id": str(row["sample_id"]),
                "question": str(row["question"]),
                "choices": list(row["choices"]),
                "answerKey": str(row["answerKey"]),
                "metadata": metadata,
            }
        )

    for row in ADDITIONAL_ROWS:
        larger_rows.append(
            {
                "sample_id": row["sample_id"],
                "question": row["question"],
                "choices": row["choices"],
                "answerKey": row["answerKey"],
                "metadata": {
                    "source_name": "commonsenseqa_style_curated_pilot_larger",
                    "source_split": "pilot_larger",
                    "slice_size": 20,
                    "expansion_stage": "larger_labeled_split_bootstrap",
                    "row_origin": "new_local_curated_extension",
                },
            }
        )
    return larger_rows


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

    reasoning_budget = count_jsonl_rows(materialized_inputs_dir / "reasoning_query_contracts.jsonl")
    confidence_budget = count_jsonl_rows(materialized_inputs_dir / "confidence_query_contracts.jsonl")
    illumination_budget = count_jsonl_rows(materialized_inputs_dir / "illumination_query_contracts.jsonl")
    labeled_illumination_budget = count_jsonl_rows(materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl")

    reasoning_result = run_reasoning_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        reasoning_config_path=reasoning_config_path,
        reasoning_profile_name="default",
        prompt_dir=Path("data/prompts/reasoning"),
        output_dir=bridge_dir / "reasoning_probe",
        dataset_manifest=None,
        query_file=materialized_inputs_dir / "reasoning_query_contracts.jsonl",
        query_budget_override=reasoning_budget,
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
        query_budget_override=confidence_budget,
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
        query_budget_override=illumination_budget,
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
        query_budget_override=labeled_illumination_budget,
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
            "These dry-run artifacts prove the larger split contracts can still enter the stable probe CLIs without loading a model.",
            "They validate builder compatibility, not model behavior quality.",
        ],
    }
    write_json(output_dir / "larger_labeled_bridge_artifact_summary.json", summary)
    return summary


def count_jsonl_rows(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def build_larger_labeled_split_bootstrap(
    expanded_inputs_dir: Path,
    output_dir: Path,
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    seed: int,
    run_bridge_dry_run: bool,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    larger_rows = build_larger_split(expanded_inputs_dir)

    materialized_inputs_dir = output_dir / "materialized_larger_labeled_inputs"
    materialized_inputs_dir.mkdir(parents=True, exist_ok=True)

    reasoning_contracts = build_reasoning_query_contracts(larger_rows)
    confidence_contracts = build_confidence_query_contracts_from_pilot_slice(larger_rows)
    illumination_contracts = build_illumination_query_contracts(larger_rows)
    labeled_illumination_contracts = build_labeled_query_contracts(larger_rows)

    larger_split_path = output_dir / "larger_labeled_split.jsonl"
    larger_split_csv_path = output_dir / "larger_labeled_split.csv"
    materialized_slice_path = materialized_inputs_dir / "csqa_reasoning_pilot_slice.jsonl"
    reasoning_query_path = materialized_inputs_dir / "reasoning_query_contracts.jsonl"
    confidence_query_path = materialized_inputs_dir / "confidence_query_contracts.jsonl"
    illumination_query_path = materialized_inputs_dir / "illumination_query_contracts.jsonl"
    labeled_illumination_query_path = materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl"

    write_jsonl(larger_split_path, larger_rows)
    write_csv(larger_split_csv_path, larger_rows)
    write_jsonl(materialized_slice_path, larger_rows)
    write_jsonl(reasoning_query_path, reasoning_contracts)
    write_jsonl(confidence_query_path, confidence_contracts)
    write_jsonl(illumination_query_path, illumination_contracts)
    write_jsonl(labeled_illumination_query_path, labeled_illumination_contracts)

    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "split_name": "larger_csqa_reasoning_pilot_local",
        "goal": "Lift the shared labeled substrate from 10 rows to 20 rows while preserving compatibility with route B, route C, and fusion builders.",
        "new_sample_ids": [row["sample_id"] for row in ADDITIONAL_ROWS],
        "compatibility_targets": ["route_B", "route_C", "real_pilot_fusion"],
    }
    definition = {
        "schema_version": SCHEMA_VERSION,
        "split_name": "larger_csqa_reasoning_pilot_local",
        "split_kind": "local_curated_larger_split",
        "row_count_target": 20,
        "base_sample_count_target": 20,
        "expected_fields": ["sample_id", "question", "choices", "answerKey", "metadata"],
        "compatibility_targets": ["route_B", "route_C", "real_pilot_fusion"],
        "known_limitations": [
            "Still a local curated split, not benchmark-scale data.",
            "Still tied to the current lightweight model / prompt stack ecosystem.",
        ],
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "readiness_status": "ready_local",
        "split_name": "larger_csqa_reasoning_pilot_local",
        "base_slice_size": 10,
        "target_row_count": 20,
        "target_base_sample_count": 20,
        "num_new_rows": len(ADDITIONAL_ROWS),
        "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        "notes": [
            "This larger split is the smallest next substrate that clearly exceeds the current 10-row expanded slice.",
            "It is designed to remain compatible with current route B / route C / fusion builders.",
        ],
    }
    larger_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "split_name": "larger_csqa_reasoning_pilot_local",
        "num_rows": len(larger_rows),
        "num_new_rows": len(ADDITIONAL_ROWS),
        "num_base_samples": len(larger_rows),
        "new_sample_ids": [row["sample_id"] for row in ADDITIONAL_ROWS],
        "expected_follow_on_capacity": {
            "route_b_more_natural_rows": len(larger_rows),
            "route_c_benchmark_truth_leaning_rows": len(labeled_illumination_contracts),
            "route_a_controlled_rows": len(labeled_illumination_contracts),
        },
        "notes": [
            "This larger split remains local and curated.",
            "Its purpose is to unlock another supervision rerun step without changing the builder contracts.",
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

    compatibility_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "compatibility_targets": {
            "route_B": {
                "compatible": True,
                "required_contracts_present": True,
                "expected_row_capacity": len(larger_rows),
                "why": "route B consumes sample-level outputs on the shared larger substrate.",
            },
            "route_C": {
                "compatible": True,
                "required_contracts_present": True,
                "expected_row_capacity": len(labeled_illumination_contracts),
                "why": "route C consumes contract-level labeled illumination plus aligned fusion features.",
            },
            "real_pilot_fusion": {
                "compatible": True,
                "required_contracts_present": True,
                "expected_row_capacity": len(larger_rows),
                "why": "fusion alignment still keys on sample_id for the three real-pilot modalities.",
            },
        },
        "bridge_dry_run_completed": bridge_summary is not None,
    }

    write_json(output_dir / "larger_labeled_split_plan.json", plan)
    write_json(output_dir / "larger_labeled_split_definition.json", definition)
    write_json(output_dir / "larger_labeled_split_readiness_summary.json", readiness_summary)
    write_json(output_dir / "larger_labeled_split_summary.json", larger_summary)
    write_json(output_dir / "larger_split_route_compatibility_summary.json", compatibility_summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "expanded_inputs_dir": str(expanded_inputs_dir.resolve()),
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
                "TriScope-LLM larger labeled split bootstrap",
                f"Source expanded inputs: {expanded_inputs_dir.resolve()}",
                f"Larger split rows: {len(larger_rows)}",
                f"Materialized inputs: {materialized_inputs_dir.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "plan": plan,
        "definition": definition,
        "readiness_summary": readiness_summary,
        "larger_summary": larger_summary,
        "bridge_summary": bridge_summary,
        "compatibility_summary": compatibility_summary,
        "output_paths": {
            "plan": str((output_dir / "larger_labeled_split_plan.json").resolve()),
            "definition": str((output_dir / "larger_labeled_split_definition.json").resolve()),
            "readiness_summary": str((output_dir / "larger_labeled_split_readiness_summary.json").resolve()),
            "larger_split_jsonl": str(larger_split_path.resolve()),
            "larger_split_csv": str(larger_split_csv_path.resolve()),
            "larger_summary": str((output_dir / "larger_labeled_split_summary.json").resolve()),
            "bridge_summary": str((output_dir / "larger_labeled_bridge_artifact_summary.json").resolve()) if bridge_summary is not None else None,
            "compatibility_summary": str((output_dir / "larger_split_route_compatibility_summary.json").resolve()),
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
