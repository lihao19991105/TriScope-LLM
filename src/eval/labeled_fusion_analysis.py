"""Compact analysis and route selection for labeled real-pilot fusion."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/labeled-fusion-analysis/v1"


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


def build_labeled_fusion_analysis(
    labeled_pilot_analysis_dir: Path,
    labeled_real_pilot_fusion_dir: Path,
    labeled_real_pilot_fusion_run_dir: Path,
    real_pilot_fusion_readiness_dir: Path,
    real_pilot_fusion_run_dir: Path,
    reasoning_pilot_run_summary_path: Path,
    confidence_pilot_run_summary_path: Path,
    illumination_pilot_run_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    integration_recommendation = load_json(labeled_pilot_analysis_dir / "fusion_integration_recommendation.json")
    labeled_summary = load_json(labeled_real_pilot_fusion_dir / "labeled_real_pilot_fusion_summary.json")
    labeled_logistic_summary = load_json(labeled_real_pilot_fusion_run_dir / "labeled_real_pilot_logistic_summary.json")
    unlabeled_readiness_summary = load_json(real_pilot_fusion_readiness_dir / "real_pilot_fusion_readiness_summary.json")
    unlabeled_rule_summary = load_json(real_pilot_fusion_run_dir / "real_pilot_rule_summary.json")
    unlabeled_logistic_summary = load_json(real_pilot_fusion_run_dir / "real_pilot_logistic_summary.json")

    reasoning_run_summary = load_json(reasoning_pilot_run_summary_path)
    confidence_run_summary = load_json(confidence_pilot_run_summary_path)
    illumination_run_summary = load_json(illumination_pilot_run_summary_path)

    route_a = {
        "route_name": "expand_current_controlled_supervision_coverage",
        "route_code": "A",
        "requires_new_labels": False,
        "requires_new_models": False,
        "requires_new_data": False,
        "estimated_code_change": "small_orchestration_only",
        "minimum_change": {
            "rerun_existing_real_pilots_on_full_materialized_query_files": True,
            "reuse_controlled_targeted_icl_label": True,
            "rebuild_real_pilot_fusion_dataset": True,
            "rebuild_labeled_real_pilot_fusion_dataset": True,
        },
        "expected_gain": {
            "current_aligned_base_samples": int(labeled_summary["num_base_samples"]),
            "current_labeled_rows": int(labeled_summary["num_rows"]),
            "target_aligned_base_samples": 5,
            "target_labeled_rows": 10,
        },
        "risks": [
            "Supervision remains pilot_level_controlled_supervision.",
            "Reasoning and confidence are still reused per base sample across control/targeted variants.",
        ],
        "feasibility": "high",
    }
    route_b = {
        "route_name": "introduce_more_natural_label_source",
        "route_code": "B",
        "requires_new_labels": True,
        "requires_new_models": False,
        "requires_new_data": "likely",
        "estimated_code_change": "higher_than_A",
        "minimum_change": {
            "define_new_label_contract": True,
            "justify_label_naturalness": True,
            "materialize_new_label_inputs": True,
            "recheck_cross_modal_alignment": True,
        },
        "expected_gain": {
            "supervision_naturalness": "higher_than_controlled_contract_label",
            "label_auditability": "unclear_without_new_contract",
        },
        "risks": [
            "Current repository does not yet contain a ready-to-use stronger label source on the same aligned slice.",
            "Risk of spending effort on label design before expanding the existing supervised path beyond 4 rows.",
        ],
        "feasibility": "medium_or_low",
    }

    comparison_rows = [
        {
            "view": "unlabeled_real_pilot_fusion",
            "label_scope": "none",
            "num_rows": int(unlabeled_readiness_summary["num_aligned_rows"]),
            "num_base_samples": int(unlabeled_readiness_summary["num_aligned_rows"]),
            "supervised_logistic_status": str(unlabeled_logistic_summary["summary_status"]),
            "supervised_logistic_blocker": str(unlabeled_logistic_summary.get("reason", "")),
            "notes": "rule_only_path_available",
        },
        {
            "view": "labeled_real_pilot_fusion_bootstrap",
            "label_scope": str(labeled_summary["label_scope"]),
            "num_rows": int(labeled_summary["num_rows"]),
            "num_base_samples": int(labeled_summary["num_base_samples"]),
            "supervised_logistic_status": str(labeled_logistic_summary["summary_status"]),
            "supervised_logistic_blocker": "",
            "notes": "first_supervised_fusion_path_exists",
        },
    ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_value_statement": [
            "The repository now has a supervised real-pilot fusion path that no longer fails with missing_ground_truth_labels.",
            "The current path proves that aligned multi-modal pilot fusion can accept an auditable pilot-level label and execute a supervised logistic bootstrap.",
        ],
        "real_pilot_modules": [
            reasoning_run_summary["module_set"][0],
            confidence_run_summary["module_set"][0],
            illumination_run_summary["module_set"][0],
        ],
        "unlabeled_real_pilot_fusion": {
            "full_intersection_available": bool(unlabeled_readiness_summary["full_intersection_available"]),
            "num_aligned_rows": int(unlabeled_readiness_summary["num_aligned_rows"]),
            "rule_baseline_ready": bool(unlabeled_readiness_summary["baseline_readiness"]["rule_based_ready"]),
            "supervised_logistic_ready": bool(unlabeled_readiness_summary["baseline_readiness"]["logistic_ready"]),
        },
        "labeled_real_pilot_fusion": {
            "label_name": str(labeled_summary["label_name"]),
            "label_scope": str(labeled_summary["label_scope"]),
            "num_rows": int(labeled_summary["num_rows"]),
            "num_base_samples": int(labeled_summary["num_base_samples"]),
            "supervised_logistic_status": str(labeled_logistic_summary["summary_status"]),
        },
        "smallest_current_value": (
            "A first supervised fusion path exists and is executable, even though it is still tiny and pilot-controlled."
        ),
    }

    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_supervision_scope": "pilot_level_controlled_supervision",
        "benchmark_like_supervision_available": False,
        "main_scaling_blockers": [
            "Only 2 aligned base samples currently enter labeled real-pilot fusion.",
            "The current 4-row dataset is produced by mapping control/targeted contract variants onto 2 base fusion rows.",
            "Reasoning and confidence features are duplicated across control and targeted variants within the same base sample.",
            "A more natural label source is not yet materialized on the same aligned slice.",
        ],
        "technical_bottleneck": (
            "The next bottleneck is coverage, not basic supervision existence: the repository needs either more aligned base samples "
            "under the current controlled label or a stronger label source that can be aligned at the same granularity."
        ),
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "A",
        "chosen_route_name": route_a["route_name"],
        "chosen_route_rationale": [
            "The current local slice already contains 5 materialized query contracts for each real pilot modality.",
            "The existing labeled pilot already covers 10 control/targeted contract rows over the same 5 base sample ids.",
            "The present 4-row supervised fusion bootstrap is small because the real pilots were executed in smoke budget mode, not because the data is missing.",
            "Route A needs no new label definition and has the highest chance of quickly turning the path from existence-proof into a slightly larger supervised pilot.",
        ],
        "bootstrap_contract": {
            "chosen_route": "A",
            "goal": "Expand the current labeled real-pilot fusion bootstrap from 2 aligned base samples / 4 labeled rows to the full 5-row local slice / 10 labeled rows.",
            "input_resources": [
                "existing reasoning/confidence/illumination query contracts",
                "existing labeled illumination query contracts",
                "same csqa_reasoning_pilot_local slice",
                "same pilot_distilgpt2_hf model profile",
            ],
            "label_source": "controlled_targeted_icl_label",
            "label_extension_mode": "reuse_the_existing_controlled_label_on_more_aligned_base_samples",
            "success_criteria": [
                "expanded real-pilot fusion full intersection covers the full 5-row local slice",
                "expanded labeled real-pilot fusion dataset contains 10 rows",
                "supervised logistic runs on the expanded covered set",
            ],
            "known_risks": route_a["risks"],
        },
    }

    write_json(output_dir / "labeled_fusion_analysis_summary.json", analysis_summary)
    write_json(output_dir / "labeled_fusion_scaling_blocker_summary.json", blocker_summary)
    write_json(
        output_dir / "route_comparison_A_vs_B.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "routes": [route_a, route_b],
        },
    )
    write_csv(output_dir / "labeled_fusion_vs_unlabeled_fusion_comparison.csv", comparison_rows)
    write_json(output_dir / "labeled_fusion_next_step_recommendation.json", recommendation)
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM labeled fusion analysis",
                f"Chosen route: {recommendation['chosen_route_name']}",
                f"Current labeled rows: {labeled_summary['num_rows']}",
                "Why route A: existing contracts already cover the full 5-row local slice.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "analysis_summary": analysis_summary,
        "blocker_summary": blocker_summary,
        "recommendation": recommendation,
        "output_paths": {
            "analysis_summary": str((output_dir / "labeled_fusion_analysis_summary.json").resolve()),
            "blocker_summary": str((output_dir / "labeled_fusion_scaling_blocker_summary.json").resolve()),
            "route_comparison": str((output_dir / "route_comparison_A_vs_B.json").resolve()),
            "comparison_csv": str((output_dir / "labeled_fusion_vs_unlabeled_fusion_comparison.csv").resolve()),
            "recommendation": str((output_dir / "labeled_fusion_next_step_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
