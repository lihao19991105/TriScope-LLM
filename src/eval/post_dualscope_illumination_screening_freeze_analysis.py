"""Post-analysis for the DualScope illumination screening freeze stage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_illumination_common import SCHEMA_VERSION, write_json


POST_SCHEMA_VERSION = "dualscopellm/post-illumination-screening-freeze-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def post_dualscope_illumination_screening_freeze_analysis(
    freeze_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    problem_definition = _load_json(freeze_dir / "dualscope_illumination_problem_definition.json")
    probe_templates = _load_json(freeze_dir / "dualscope_illumination_probe_templates.json")
    feature_schema = _load_json(freeze_dir / "dualscope_illumination_feature_schema.json")
    io_contract = _load_json(freeze_dir / "dualscope_illumination_io_contract.json")
    budget_contract = _load_json(freeze_dir / "dualscope_illumination_budget_contract.json")
    baseline_plan = _load_json(freeze_dir / "dualscope_illumination_baseline_plan.json")
    summary = _load_json(freeze_dir / "dualscope_illumination_screening_freeze_summary.json")

    template_ready = int(probe_templates["template_family_count"]) >= 5 and len(
        probe_templates["default_enabled_template_families"]
    ) >= 5
    feature_ready = int(feature_schema["feature_count"]) >= 18 and int(summary["details_row_count"]) >= 15
    downstream_ready = bool(io_contract["confidence_stage_readable_fields"]) and bool(
        io_contract["fusion_stage_readable_fields"]
    )
    budget_ready = int(budget_contract["minimal_screening_budget"]) >= 3 and int(
        budget_contract["default_query_budget"]
    ) >= 5
    baseline_ready = bool(baseline_plan["illumination_only_baseline"]) and bool(
        baseline_plan["future_fusion_ablation_placeholder"]
    )
    screening_only = "final backdoor verdict" in problem_definition["what_is_not_detected"]
    controlled_protocol_only = bool(summary["controlled_protocol_only"])

    if all(
        [
            template_ready,
            feature_ready,
            downstream_ready,
            budget_ready,
            baseline_ready,
            screening_only,
            controlled_protocol_only,
        ]
    ):
        final_verdict = "Illumination screening freeze validated"
        recommendation = "进入 dualscope-confidence-verification-with-without-logprobs"
        primary_basis = [
            "Stage 1 problem definition, probe template family, feature schema, IO contract, and budget contract are all frozen as machine-readable artifacts.",
            "Representative details traces already export future confidence and fusion interface fields.",
            "The freeze implementation is runnable and produces a reusable protocol package rather than a paper-only draft.",
        ]
    elif template_ready and downstream_ready and budget_ready:
        final_verdict = "Partially validated"
        recommendation = "继续做 illumination-screening-freeze-compression"
        primary_basis = [
            "The core Stage 1 shape is in place, but one or more protocol completeness checks remain below the validation threshold.",
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "回到 illumination-probe-boundary-and-feature-schema-closure"
        primary_basis = [
            "The Stage 1 freeze is still missing required protocol, budget, or downstream compatibility guarantees.",
        ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "task_name": "dualscope-illumination-screening-freeze",
        "template_ready": template_ready,
        "feature_ready": feature_ready,
        "downstream_ready": downstream_ready,
        "budget_ready": budget_ready,
        "baseline_ready": baseline_ready,
        "screening_only": screening_only,
        "controlled_protocol_only": controlled_protocol_only,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_illumination_screening_freeze_validated__partially_validated__not_validated",
        "primary_basis": primary_basis,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": primary_basis,
        "do_not_do_yet": [
            "reopen_triscope_reasoning_as_mainline",
            "continue_route_c_recursive_stage_chain",
            "change_benchmark_truth_semantics",
            "change_gate_semantics",
            "expand_budget_or_model_matrix_at_stage1_freeze",
        ],
    }

    write_json(
        output_dir / "dualscope_illumination_screening_freeze_analysis_summary.json",
        analysis_summary,
    )
    write_json(output_dir / "dualscope_illumination_screening_freeze_verdict.json", verdict)
    write_json(
        output_dir / "dualscope_illumination_screening_freeze_next_step_recommendation.json",
        recommendation_payload,
    )
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str(
                (output_dir / "dualscope_illumination_screening_freeze_analysis_summary.json").resolve()
            ),
            "verdict": str((output_dir / "dualscope_illumination_screening_freeze_verdict.json").resolve()),
            "recommendation": str(
                (output_dir / "dualscope_illumination_screening_freeze_next_step_recommendation.json").resolve()
            ),
        },
    }
