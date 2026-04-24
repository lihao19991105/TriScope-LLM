"""Decision layer for whether to switch from controlled supervision to a more natural label."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/more-natural-label-analysis/v1"


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


def build_more_natural_label_analysis(
    labeled_fusion_analysis_dir: Path,
    controlled_supervision_expansion_dir: Path,
    first_labeled_fusion_dir: Path,
    first_labeled_fusion_run_dir: Path,
    real_pilot_fusion_readiness_dir: Path,
    real_pilot_fusion_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    route_a_analysis = load_json(labeled_fusion_analysis_dir / "labeled_fusion_next_step_recommendation.json")
    expanded_summary = load_json(controlled_supervision_expansion_dir / "expanded_labeled_summary.json")
    expanded_logistic_summary = load_json(controlled_supervision_expansion_dir / "expanded_logistic_summary.json")
    expanded_run_summary = load_json(controlled_supervision_expansion_dir / "controlled_supervision_expansion_run_summary.json")
    first_summary = load_json(first_labeled_fusion_dir / "labeled_real_pilot_fusion_summary.json")
    first_logistic_summary = load_json(first_labeled_fusion_run_dir / "labeled_real_pilot_logistic_summary.json")
    real_pilot_readiness = load_json(real_pilot_fusion_readiness_dir / "real_pilot_fusion_readiness_summary.json")
    real_pilot_rule = load_json(real_pilot_fusion_run_dir / "real_pilot_rule_summary.json")
    real_pilot_logistic = load_json(real_pilot_fusion_run_dir / "real_pilot_logistic_summary.json")

    scaling_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "route_a_state_after_expansion": {
            "label_scope": str(expanded_summary["label_scope"]),
            "previous_labeled_rows": int(first_summary["num_rows"]),
            "expanded_labeled_rows": int(expanded_summary["num_rows"]),
            "previous_aligned_base_samples": int(first_summary["num_base_samples"]),
            "expanded_aligned_base_samples": int(expanded_summary["num_base_samples"]),
            "marginal_gain": {
                "delta_labeled_rows": int(expanded_summary["num_rows"]) - int(first_summary["num_rows"]),
                "delta_aligned_base_samples": int(expanded_summary["num_base_samples"]) - int(first_summary["num_base_samples"]),
            },
            "current_value": [
                "Route A proved that the supervised fusion path can scale from 4 rows to 10 rows on the current local slice.",
                "Route A removed the immediate smoke-budget ceiling and made supervised fusion slightly less tiny.",
            ],
            "next_bottleneck": "current_local_slice_ceiling",
        },
        "unlabeled_real_pilot_context": {
            "num_aligned_rows": int(real_pilot_readiness["num_aligned_rows"]),
            "rule_baseline_status": str(real_pilot_rule["summary_status"]),
            "supervised_logistic_status": str(real_pilot_logistic["summary_status"]),
            "supervised_logistic_blocker": str(real_pilot_logistic.get("reason", "")),
        },
        "expanded_supervised_logistic": {
            "summary_status": str(expanded_logistic_summary["summary_status"]),
            "num_predictions": int(expanded_logistic_summary["num_predictions"]),
            "mean_prediction_score": float(expanded_logistic_summary["mean_prediction_score"]),
        },
    }

    route_comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "routes": [
            {
                "route_code": "A",
                "route_name": "continue_controlled_supervision_coverage_expansion",
                "what_it_means_now": "Expand beyond the current 5-row local slice while keeping the same controlled_targeted_icl_label.",
                "current_state": "near_current_slice_ceiling",
                "minimum_required_change": [
                    "materialize a larger aligned pilot slice",
                    "rerun all three real pilots on the larger slice",
                    "remap controlled contract variants on top of the larger aligned set",
                ],
                "main_blockers": [
                    "The current local slice is already fully covered at 5 aligned base samples.",
                    "Further gains require expanding data coverage, not just rerunning orchestration.",
                    "The label would remain pilot_level_controlled_supervision even after more expansion.",
                ],
                "marginal_value_now": "moderate_but_slower_than_before",
            },
            {
                "route_code": "B",
                "route_name": "bootstrap_more_natural_label",
                "what_it_means_now": "Use local-slice task truth to define a more natural sample-level proxy label aligned to expanded real-pilot fusion rows.",
                "current_state": "ready_low_cost_candidate",
                "minimum_required_change": [
                    "derive a label from answerKey + observed modality correctness",
                    "materialize a sample-level labeled fusion dataset",
                    "rerun a minimal supervised logistic bootstrap on that dataset",
                ],
                "main_blockers": [
                    "The resulting label is still a pilot-level proxy, not benchmark supervision.",
                    "Illumination correctness needs a lightweight response-to-answer-key matching rule.",
                ],
                "marginal_value_now": "high",
            },
        ],
    }

    ceiling_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "pilot_level_controlled_supervision": {
            "definition": "Labels derived from control/targeted contract variants.",
            "current_scope": {
                "num_rows": int(expanded_summary["num_rows"]),
                "num_base_samples": int(expanded_summary["num_base_samples"]),
            },
            "ceiling_reason": (
                "Current coverage already matches the available 5-row aligned local slice; further route A growth requires more data rather than more orchestration."
            ),
        },
        "more_natural_label": {
            "definition": "A pilot-level proxy grounded in task truth or answer correctness rather than contract variant.",
            "candidate_source": "local_csqa_answer_key_plus_observed_multi_modal_outputs",
            "candidate_label_name": "task_correctness_violation_label",
            "candidate_scope": "sample_level_more_natural_supervision_proxy",
        },
        "benchmark_ground_truth": {
            "definition": "Dataset- or attack-level supervised labels directly tied to benchmark truth or known backdoor status.",
            "available_now": False,
        },
        "paper_grade_supervision": {
            "definition": "Research-grade supervision with stronger truth guarantees, larger coverage, and clearer generalization claims.",
            "available_now": False,
        },
    }

    route_decision_rows = [
        {
            "route_code": "A",
            "route_name": "continue_controlled_supervision_coverage_expansion",
            "current_rows": int(expanded_summary["num_rows"]),
            "current_base_samples": int(expanded_summary["num_base_samples"]),
            "requires_new_label_source": False,
            "requires_larger_slice": True,
            "label_naturalness_level": "pilot_level_controlled_supervision",
            "feasibility_under_current_resources": "medium",
            "key_blocker": "current_local_slice_ceiling",
        },
        {
            "route_code": "B",
            "route_name": "bootstrap_more_natural_label",
            "current_rows": int(expanded_run_summary["expanded_real_pilot_alignment"]["num_rows"]),
            "current_base_samples": int(expanded_run_summary["expanded_real_pilot_alignment"]["num_rows"]),
            "requires_new_label_source": True,
            "requires_larger_slice": False,
            "label_naturalness_level": "pilot_level_more_natural_task_truth_proxy",
            "feasibility_under_current_resources": "high",
            "key_blocker": "proxy_label_honesty_and_small_scale",
        },
    ]

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_route": "B",
        "recommended_route_name": "bootstrap_more_natural_label",
        "why_not_continue_A_only": [
            "Route A already exhausted the current aligned 5-row local slice.",
            "Continuing A next would require larger data materialization before it yields new supervision coverage.",
            "Even if A grows further, the label semantics would remain controlled and contract-bound.",
        ],
        "why_B_now": [
            "A low-cost more-natural-label candidate already exists inside the repository: local answerKey plus observed modality outputs.",
            "This candidate can align directly to the expanded 5-row real-pilot fusion dataset without contract-variant duplication.",
            "It is the cheapest path from controlled supervision toward a slightly more natural supervised signal.",
        ],
        "minimum_success_standard": [
            "Materialize a more-natural sample-level labeled fusion dataset on the current 5-row aligned slice.",
            "Keep the label definition auditable and explicitly non-benchmark.",
            "If class balance permits, run a first minimal supervised logistic bootstrap on top of it.",
        ],
        "bootstrap_contract": {
            "chosen_route": "B",
            "label_name": "task_correctness_violation_label",
            "label_source": "local_csqa_answer_key_plus_observed_multi_modal_outputs",
            "label_scope": "pilot_level_more_natural_supervision_proxy",
            "label_naturalness_level": "task_truth_proxy",
            "alignment_key": "sample_id",
            "target_modules": ["illumination", "reasoning", "confidence"],
            "minimum_executable_slice": "current 5-row expanded real-pilot full-intersection slice",
            "known_risks": [
                "Still not benchmark ground truth.",
                "Label quality depends on lightweight task-correctness extraction from current model outputs.",
                "Current slice remains very small and model remains lightweight.",
            ],
        },
    }

    write_json(output_dir / "controlled_supervision_scaling_summary.json", scaling_summary)
    write_json(output_dir / "route_A_vs_route_B_comparison.json", route_comparison)
    write_json(output_dir / "supervision_ceiling_summary.json", ceiling_summary)
    write_csv(output_dir / "route_decision_inputs.csv", route_decision_rows)
    write_json(output_dir / "more_natural_label_next_step_recommendation.json", recommendation)
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM more-natural-label bootstrap decision",
                f"Previous route recommendation: {route_a_analysis.get('chosen_route')}",
                f"Expanded labeled rows: {expanded_summary['num_rows']}",
                "Chosen next route: B / bootstrap_more_natural_label",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "scaling_summary": scaling_summary,
        "route_comparison": route_comparison,
        "ceiling_summary": ceiling_summary,
        "recommendation": recommendation,
        "output_paths": {
            "scaling_summary": str((output_dir / "controlled_supervision_scaling_summary.json").resolve()),
            "route_comparison": str((output_dir / "route_A_vs_route_B_comparison.json").resolve()),
            "ceiling_summary": str((output_dir / "supervision_ceiling_summary.json").resolve()),
            "decision_inputs_csv": str((output_dir / "route_decision_inputs.csv").resolve()),
            "recommendation": str((output_dir / "more_natural_label_next_step_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
