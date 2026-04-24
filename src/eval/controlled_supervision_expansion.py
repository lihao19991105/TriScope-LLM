"""Bootstrap route A: expand current controlled supervision coverage."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.features.confidence_features import extract_confidence_features
from src.features.illumination_features import extract_illumination_features
from src.features.reasoning_features import extract_reasoning_features
from src.fusion.feature_alignment import build_fusion_dataset
from src.fusion.labeled_real_pilot_fusion import (
    build_labeled_real_pilot_fusion_dataset,
    run_labeled_real_pilot_logistic,
)
from src.probes.confidence_probe import run_confidence_probe
from src.probes.illumination_probe import run_illumination_probe
from src.probes.reasoning_probe import run_reasoning_probe


SCHEMA_VERSION = "triscopellm/controlled-supervision-expansion/v1"


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


def count_rows(path: Path) -> int:
    return len(load_jsonl(path))


def materialize_controlled_supervision_expansion(
    reasoning_query_file: Path,
    confidence_query_file: Path,
    illumination_query_file: Path,
    labeled_query_file: Path,
    current_labeled_fusion_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    reasoning_count = count_rows(reasoning_query_file)
    confidence_count = count_rows(confidence_query_file)
    illumination_count = count_rows(illumination_query_file)
    labeled_count = count_rows(labeled_query_file)
    current_labeled_summary = load_json(current_labeled_fusion_summary_path)

    target_base_sample_count = min(reasoning_count, confidence_count, illumination_count)
    target_labeled_rows = min(labeled_count, target_base_sample_count * 2)

    expansion_plan = {
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "A",
        "route_name": "expand_current_controlled_supervision_coverage",
        "why_now": [
            "All three real-pilot query contract files already cover the full 5-row local slice.",
            "The current supervised fusion bootstrap is limited by smoke execution budgets rather than missing inputs.",
            "Reusing the existing controlled label is the cheapest way to move from 4 rows to a slightly more scalable supervised path.",
        ],
        "input_contracts": {
            "reasoning_query_file": str(reasoning_query_file.resolve()),
            "confidence_query_file": str(confidence_query_file.resolve()),
            "illumination_query_file": str(illumination_query_file.resolve()),
            "labeled_query_file": str(labeled_query_file.resolve()),
        },
        "current_scope": {
            "current_aligned_base_samples": int(current_labeled_summary["num_base_samples"]),
            "current_labeled_rows": int(current_labeled_summary["num_rows"]),
        },
        "target_scope": {
            "target_aligned_base_samples": target_base_sample_count,
            "target_labeled_rows": target_labeled_rows,
        },
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "A",
        "ready_to_run": True,
        "label_name": "controlled_targeted_icl_label",
        "label_scope": "pilot_level_controlled_supervision",
        "expansion_mode": "reuse_existing_controlled_label_on_more_aligned_base_samples",
        "input_row_counts": {
            "reasoning_query_contracts": reasoning_count,
            "confidence_query_contracts": confidence_count,
            "illumination_query_contracts": illumination_count,
            "labeled_query_contracts": labeled_count,
        },
        "expected_outputs": {
            "expanded_aligned_base_samples": target_base_sample_count,
            "expanded_labeled_rows": target_labeled_rows,
        },
        "notes": [
            "No new labels are introduced in route A.",
            "The main work is rerunning the existing pilots on the full local slice budget.",
        ],
    }

    write_json(output_dir / "controlled_supervision_expansion_plan.json", expansion_plan)
    write_json(output_dir / "expanded_labeled_readiness_summary.json", readiness_summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "reasoning_query_file": str(reasoning_query_file.resolve()),
            "confidence_query_file": str(confidence_query_file.resolve()),
            "illumination_query_file": str(illumination_query_file.resolve()),
            "labeled_query_file": str(labeled_query_file.resolve()),
            "current_labeled_fusion_summary_path": str(current_labeled_fusion_summary_path.resolve()),
        },
    )
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM controlled supervision coverage expansion",
                f"Target aligned base samples: {target_base_sample_count}",
                f"Target labeled rows: {target_labeled_rows}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "expansion_plan": expansion_plan,
        "readiness_summary": readiness_summary,
        "target_base_sample_count": target_base_sample_count,
        "target_labeled_rows": target_labeled_rows,
        "output_paths": {
            "plan": str((output_dir / "controlled_supervision_expansion_plan.json").resolve()),
            "readiness_summary": str((output_dir / "expanded_labeled_readiness_summary.json").resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }


def run_controlled_supervision_expansion(
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    reasoning_prompt_dir: Path,
    confidence_prompt_dir: Path,
    illumination_prompt_dir: Path,
    reasoning_query_file: Path,
    confidence_query_file: Path,
    illumination_query_file: Path,
    labeled_pilot_dataset_path: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    target_budget = min(
        count_rows(reasoning_query_file),
        count_rows(confidence_query_file),
        count_rows(illumination_query_file),
    )
    if target_budget <= 0:
        raise ValueError("Controlled supervision expansion requires non-empty reasoning/confidence/illumination query files.")

    reasoning_dir = output_dir / "expanded_reasoning"
    confidence_dir = output_dir / "expanded_confidence"
    illumination_dir = output_dir / "expanded_illumination"

    reasoning_probe = run_reasoning_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        reasoning_config_path=reasoning_config_path,
        reasoning_profile_name="default",
        prompt_dir=reasoning_prompt_dir,
        output_dir=reasoning_dir / "reasoning_probe",
        dataset_manifest=None,
        query_file=reasoning_query_file,
        query_budget_override=target_budget,
        trigger_type_override="none",
        target_type_override="multiple_choice_correct_option",
        seed=seed,
        dry_run=False,
        smoke_mode=False,
    )
    reasoning_features = extract_reasoning_features(
        raw_results_path=reasoning_dir / "reasoning_probe" / "raw_results.jsonl",
        summary_json_path=reasoning_dir / "reasoning_probe" / "summary.json",
        config_snapshot_path=reasoning_dir / "reasoning_probe" / "config_snapshot.json",
        output_dir=reasoning_dir / "reasoning_probe" / "features",
        run_id="expanded_reasoning",
    )
    reasoning_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "module_name": "reasoning",
        "target_budget": target_budget,
        "probe_summary": reasoning_probe["summary"],
        "feature_summary": reasoning_features["feature_summary"],
    }
    write_json(reasoning_dir / "expanded_reasoning_run_summary.json", reasoning_summary)

    confidence_probe = run_confidence_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        confidence_config_path=confidence_config_path,
        confidence_profile_name="pilot_local",
        prompt_dir=confidence_prompt_dir,
        output_dir=confidence_dir / "confidence_probe",
        dataset_manifest=None,
        query_file=confidence_query_file,
        query_budget_override=target_budget,
        trigger_type_override="none",
        target_type_override="multiple_choice_correct_option",
        seed=seed,
        dry_run=False,
        smoke_mode=False,
    )
    confidence_features = extract_confidence_features(
        raw_results_path=confidence_dir / "confidence_probe" / "raw_results.jsonl",
        summary_json_path=confidence_dir / "confidence_probe" / "summary.json",
        config_snapshot_path=confidence_dir / "confidence_probe" / "config_snapshot.json",
        output_dir=confidence_dir / "confidence_probe" / "features",
        run_id="expanded_confidence",
        high_confidence_threshold=0.10,
    )
    confidence_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "module_name": "confidence",
        "target_budget": target_budget,
        "probe_summary": confidence_probe["summary"],
        "feature_summary": confidence_features["feature_summary"],
    }
    write_json(confidence_dir / "expanded_confidence_run_summary.json", confidence_summary)

    illumination_probe = run_illumination_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        illumination_config_path=illumination_config_path,
        illumination_profile_name="pilot_local",
        prompt_dir=illumination_prompt_dir,
        output_dir=illumination_dir / "illumination_probe",
        dataset_manifest=None,
        query_file=illumination_query_file,
        alpha_override=None,
        query_budget_override=target_budget,
        trigger_type_override="targeted_icl_demo",
        target_type_override="forced_option_label",
        seed=seed,
        dry_run=False,
        smoke_mode=False,
    )
    illumination_features = extract_illumination_features(
        raw_results_path=illumination_dir / "illumination_probe" / "raw_results.jsonl",
        summary_json_path=illumination_dir / "illumination_probe" / "summary.json",
        config_snapshot_path=illumination_dir / "illumination_probe" / "config_snapshot.json",
        output_dir=illumination_dir / "illumination_probe" / "features",
        run_id="expanded_illumination",
    )
    illumination_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "module_name": "illumination",
        "target_budget": target_budget,
        "probe_summary": illumination_probe["summary"],
        "feature_summary": illumination_features["feature_summary"],
    }
    write_json(illumination_dir / "expanded_illumination_run_summary.json", illumination_summary)

    fusion_result = build_fusion_dataset(
        illumination_features_path=illumination_dir / "illumination_probe" / "features" / "prompt_level_features.jsonl",
        reasoning_features_path=reasoning_dir / "reasoning_probe" / "features" / "reasoning_prompt_level_features.jsonl",
        confidence_features_path=confidence_dir / "confidence_probe" / "features" / "confidence_prompt_level_features.jsonl",
        output_dir=output_dir / "expanded_real_pilot_fusion",
        join_mode="inner",
    )
    alignment_summary = load_json(Path(fusion_result["output_paths"]["alignment_summary"]))

    labeled_fusion_result = build_labeled_real_pilot_fusion_dataset(
        real_pilot_fusion_dataset_path=Path(fusion_result["output_paths"]["fusion_dataset_jsonl"]),
        labeled_pilot_dataset_path=labeled_pilot_dataset_path,
        output_dir=output_dir / "expanded_labeled_real_pilot_fusion",
        fusion_profile="labeled_real_pilot_expanded",
        run_id="expanded",
    )
    logistic_result = run_labeled_real_pilot_logistic(
        labeled_real_pilot_fusion_dataset_path=Path(labeled_fusion_result["output_paths"]["dataset_jsonl"]),
        output_dir=output_dir / "expanded_labeled_real_pilot_fusion_run",
        fusion_profile="labeled_real_pilot_expanded",
        run_id="expanded",
        label_threshold=0.5,
    )

    copy_artifact(Path(labeled_fusion_result["output_paths"]["dataset_jsonl"]), output_dir / "expanded_labeled_fusion_dataset.jsonl")
    copy_artifact(Path(labeled_fusion_result["output_paths"]["summary"]), output_dir / "expanded_labeled_summary.json")
    copy_artifact(Path(logistic_result["output_paths"]["predictions"]), output_dir / "expanded_logistic_predictions.jsonl")
    copy_artifact(Path(logistic_result["output_paths"]["summary"]), output_dir / "expanded_logistic_summary.json")

    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "target_budget": target_budget,
        "expanded_real_pilot_alignment": alignment_summary,
        "expanded_labeled_summary": labeled_fusion_result["summary"],
        "expanded_logistic_summary": logistic_result["summary"],
        "notes": [
            "This is still pilot-level controlled supervision.",
            "Coverage expansion was achieved by rerunning the existing three real pilots on the full 5-row local slice.",
        ],
    }
    write_json(output_dir / "controlled_supervision_expansion_run_summary.json", run_summary)
    (output_dir / "run.log").write_text(
        "\n".join(
            [
                "TriScope-LLM controlled supervision expansion execution",
                f"target_budget={target_budget}",
                f"expanded_alignment_rows={alignment_summary['num_rows']}",
                f"expanded_labeled_rows={labeled_fusion_result['summary']['num_rows']}",
                f"expanded_predictions={logistic_result['summary']['num_predictions']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "run_summary": run_summary,
        "output_paths": {
            "run_summary": str((output_dir / "controlled_supervision_expansion_run_summary.json").resolve()),
            "expanded_labeled_dataset": str((output_dir / "expanded_labeled_fusion_dataset.jsonl").resolve()),
            "expanded_labeled_summary": str((output_dir / "expanded_labeled_summary.json").resolve()),
            "expanded_logistic_predictions": str((output_dir / "expanded_logistic_predictions.jsonl").resolve()),
            "expanded_logistic_summary": str((output_dir / "expanded_logistic_summary.json").resolve()),
            "log": str((output_dir / "run.log").resolve()),
        },
    }
