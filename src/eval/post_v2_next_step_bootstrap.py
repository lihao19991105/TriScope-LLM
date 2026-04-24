"""Bootstrap the next step after v2 symmetric rerun comparison."""

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


SCHEMA_VERSION = "triscopellm/post-v2-next-step-bootstrap/v1"

ADDITIONAL_ROWS_V3: list[dict[str, Any]] = [
    {
        "sample_id": "csqa-pilot-031",
        "question": "Where would you put leftovers to keep them cold?",
        "choices": [
            {"label": "A", "text": "refrigerator"},
            {"label": "B", "text": "bookshelf"},
            {"label": "C", "text": "closet shelf"},
            {"label": "D", "text": "desk drawer"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-032",
        "question": "What would you use to tell time on your wrist?",
        "choices": [
            {"label": "A", "text": "watch"},
            {"label": "B", "text": "fork"},
            {"label": "C", "text": "soap"},
            {"label": "D", "text": "blanket"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-033",
        "question": "Where would you usually park a bicycle at school?",
        "choices": [
            {"label": "A", "text": "bike rack"},
            {"label": "B", "text": "freezer"},
            {"label": "C", "text": "bookshelf"},
            {"label": "D", "text": "washing machine"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-034",
        "question": "What would you use to cut paper for a craft project?",
        "choices": [
            {"label": "A", "text": "scissors"},
            {"label": "B", "text": "pillow"},
            {"label": "C", "text": "toaster"},
            {"label": "D", "text": "helmet"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-035",
        "question": "Where would you go to borrow a novel for free?",
        "choices": [
            {"label": "A", "text": "library"},
            {"label": "B", "text": "garage ceiling"},
            {"label": "C", "text": "dishwasher"},
            {"label": "D", "text": "mailbox"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-036",
        "question": "What would you use to write on a chalkboard?",
        "choices": [
            {"label": "A", "text": "chalk"},
            {"label": "B", "text": "pencil case"},
            {"label": "C", "text": "plate"},
            {"label": "D", "text": "wallet"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-037",
        "question": "Where would you usually find shampoo at home?",
        "choices": [
            {"label": "A", "text": "bathroom"},
            {"label": "B", "text": "oven"},
            {"label": "C", "text": "mail slot"},
            {"label": "D", "text": "desk drawer"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-038",
        "question": "What would you use to lock a front door?",
        "choices": [
            {"label": "A", "text": "key"},
            {"label": "B", "text": "plate"},
            {"label": "C", "text": "spoon"},
            {"label": "D", "text": "curtain"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-039",
        "question": "Where would you place dirty clothes before washing them?",
        "choices": [
            {"label": "A", "text": "laundry basket"},
            {"label": "B", "text": "microwave"},
            {"label": "C", "text": "bookshelf"},
            {"label": "D", "text": "window frame"},
        ],
        "answerKey": "A",
    },
    {
        "sample_id": "csqa-pilot-040",
        "question": "What would you use to protect your hands while washing dishes in hot water?",
        "choices": [
            {"label": "A", "text": "rubber gloves"},
            {"label": "B", "text": "paper napkin"},
            {"label": "C", "text": "lamp shade"},
            {"label": "D", "text": "bookmark"},
        ],
        "answerKey": "A",
    },
]


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


def count_jsonl_rows(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def build_larger_split_v3_rows(current_v2_split_path: Path) -> list[dict[str, Any]]:
    base_rows = load_jsonl(current_v2_split_path)
    if len(base_rows) != 30:
        raise ValueError(f"Expected a 30-row v2 split at `{current_v2_split_path}`, found {len(base_rows)} rows.")

    all_rows: list[dict[str, Any]] = []
    for row in base_rows:
        metadata = dict(row.get("metadata", {}))
        metadata["slice_size"] = 40
        metadata["expansion_stage"] = "larger_labeled_split_v3_bootstrap"
        metadata["source_name"] = "commonsenseqa_style_curated_pilot_larger_v3"
        all_rows.append(
            {
                "sample_id": str(row["sample_id"]),
                "question": str(row["question"]),
                "choices": list(row["choices"]),
                "answerKey": str(row["answerKey"]),
                "metadata": metadata,
            }
        )

    for row in ADDITIONAL_ROWS_V3:
        all_rows.append(
            {
                "sample_id": row["sample_id"],
                "question": row["question"],
                "choices": row["choices"],
                "answerKey": row["answerKey"],
                "metadata": {
                    "source_name": "commonsenseqa_style_curated_pilot_larger_v3",
                    "source_split": "pilot_larger_v3",
                    "slice_size": 40,
                    "expansion_stage": "larger_labeled_split_v3_bootstrap",
                    "row_origin": "new_local_curated_extension",
                },
            }
        )
    return all_rows


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
    labeled_budget = count_jsonl_rows(materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl")

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
        trigger_type_override="none",
        target_type_override="multiple_choice_correct_option",
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
        trigger_type_override="none",
        target_type_override="multiple_choice_correct_option",
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
        alpha_override=None,
        query_budget_override=illumination_budget,
        trigger_type_override="targeted_icl_demo",
        target_type_override="forced_option_label",
        seed=seed,
        dry_run=True,
        smoke_mode=False,
    )
    labeled_result = run_illumination_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        illumination_config_path=illumination_config_path,
        illumination_profile_name="labeled_bootstrap",
        prompt_dir=Path("data/prompts/illumination"),
        output_dir=bridge_dir / "labeled_illumination_probe",
        dataset_manifest=None,
        query_file=materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl",
        alpha_override=0.5,
        query_budget_override=labeled_budget,
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
            "labeled_illumination": labeled_result["summary"],
        },
        "notes": [
            "These dry-run artifacts prove the v3 split contracts can still enter the stable probe CLIs without loading a model.",
            "They validate builder compatibility, not model behavior quality.",
        ],
    }
    write_json(output_dir / "post_v2_next_step_bridge_summary.json", summary)
    return summary


def build_post_v2_next_step_bootstrap(
    current_v2_inputs_dir: Path,
    recommendation_path: Path,
    output_dir: Path,
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    recommendation = load_json(recommendation_path)
    if recommendation.get("recommended_next_step") != "prepare_larger_labeled_split_v3":
        raise ValueError("041 expects `recommended_next_step` to be `prepare_larger_labeled_split_v3`.")

    current_split_path = current_v2_inputs_dir / "csqa_reasoning_pilot_slice.jsonl"
    if not current_split_path.is_file():
        raise ValueError(f"Current v2 split input not found: `{current_split_path}`.")

    v3_rows = build_larger_split_v3_rows(current_split_path)
    materialized_inputs_dir = output_dir / "materialized_post_v2_inputs"
    materialized_inputs_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl(output_dir / "larger_labeled_split_v3.jsonl", v3_rows)
    write_csv(output_dir / "larger_labeled_split_v3.csv", v3_rows)
    write_jsonl(materialized_inputs_dir / "csqa_reasoning_pilot_slice.jsonl", v3_rows)

    reasoning_contracts = build_reasoning_query_contracts(v3_rows)
    confidence_contracts = build_confidence_query_contracts_from_pilot_slice(v3_rows)
    illumination_contracts = build_illumination_query_contracts(v3_rows)
    labeled_contracts = build_labeled_query_contracts(v3_rows)

    write_jsonl(materialized_inputs_dir / "reasoning_query_contracts.jsonl", reasoning_contracts)
    write_jsonl(materialized_inputs_dir / "confidence_query_contracts.jsonl", confidence_contracts)
    write_jsonl(materialized_inputs_dir / "illumination_query_contracts.jsonl", illumination_contracts)
    write_jsonl(materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl", labeled_contracts)

    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_next_step": "prepare_larger_labeled_split_v3",
        "split_name": "larger_csqa_reasoning_pilot_local_v3",
        "row_count_target": 40,
        "base_sample_count_target": 40,
        "expected_follow_on_capacity": {
            "route_b_more_natural_rows": 40,
            "route_c_benchmark_truth_leaning_rows": 80,
            "route_a_controlled_rows": 80,
        },
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "ready_to_run": True,
        "chosen_next_step": "prepare_larger_labeled_split_v3",
        "query_contract_counts": {
            "reasoning": len(reasoning_contracts),
            "confidence": len(confidence_contracts),
            "illumination": len(illumination_contracts),
            "labeled_illumination": len(labeled_contracts),
        },
        "notes": [
            "This bootstrap raises the shared substrate from 30 rows to 40 rows.",
            "It remains local and curated, but is intended to unlock the next v3 rerun stage.",
        ],
    }
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "split_name": "larger_csqa_reasoning_pilot_local_v3",
        "num_rows": len(v3_rows),
        "num_new_rows": len(ADDITIONAL_ROWS_V3),
        "num_base_samples": len(v3_rows),
        "expected_follow_on_capacity": plan["expected_follow_on_capacity"],
        "notes": [
            "This v3 split remains a local curated split.",
            "Its purpose is to lift the shared substrate after v2 symmetric B/C comparison.",
        ],
    }

    write_json(output_dir / "post_v2_next_step_plan.json", plan)
    write_json(output_dir / "post_v2_next_step_readiness_summary.json", readiness)
    write_json(output_dir / "larger_labeled_split_v3_summary.json", summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "current_v2_inputs_dir": str(current_v2_inputs_dir.resolve()),
            "recommendation_path": str(recommendation_path.resolve()),
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        },
    )

    bridge_summary = run_bridge_dry_runs(
        materialized_inputs_dir=materialized_inputs_dir,
        output_dir=output_dir,
        models_config_path=models_config_path,
        reasoning_config_path=reasoning_config_path,
        confidence_config_path=confidence_config_path,
        illumination_config_path=illumination_config_path,
        seed=seed,
    )

    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM post-v2 next-step bootstrap",
                "chosen_next_step=prepare_larger_labeled_split_v3",
                f"num_rows={len(v3_rows)}",
                f"route_b_capacity={plan['expected_follow_on_capacity']['route_b_more_natural_rows']}",
                f"route_c_capacity={plan['expected_follow_on_capacity']['route_c_benchmark_truth_leaning_rows']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "plan": plan,
        "readiness": readiness,
        "summary": summary,
        "bridge_summary": bridge_summary,
        "output_paths": {
            "plan": str((output_dir / "post_v2_next_step_plan.json").resolve()),
            "readiness": str((output_dir / "post_v2_next_step_readiness_summary.json").resolve()),
            "split_jsonl": str((output_dir / "larger_labeled_split_v3.jsonl").resolve()),
            "split_csv": str((output_dir / "larger_labeled_split_v3.csv").resolve()),
            "summary": str((output_dir / "larger_labeled_split_v3_summary.json").resolve()),
            "bridge_summary": str((output_dir / "post_v2_next_step_bridge_summary.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
