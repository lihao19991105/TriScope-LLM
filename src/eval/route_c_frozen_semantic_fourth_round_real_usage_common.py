"""Common helpers for route_c frozen-semantic fourth-round real-usage chain stages."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_light_expansion_common import (
    run_light_expansion_post_analysis,
    run_light_expansion_stage,
)
from src.eval.route_c_frozen_semantic_real_usage_chain_specs import REQUIRED_PROMPT_IDS


def build_fourth_round_stage(
    *,
    schema_version: str,
    file_prefix: str,
    suite_name: str,
    report_title: str,
    stage_token: str,
    case_prefix: str,
    window_specs: list[dict[str, Any]],
    path_group_suffix: str,
    rules_key_prefix: str,
    real_run_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
    previous_reference_details_path: Path,
    previous_reference_prefix: str,
    reference_summary_paths: dict[str, Path],
) -> dict[str, Any]:
    return run_light_expansion_stage(
        schema_version=schema_version,
        file_prefix=file_prefix,
        suite_name=suite_name,
        report_title=report_title,
        stage_token=stage_token,
        case_prefix=case_prefix,
        required_prompt_ids=REQUIRED_PROMPT_IDS,
        window_specs=window_specs,
        path_group_by_kind={
            "recoverable": f"recoverable_{path_group_suffix}",
            "normal": f"normal_{path_group_suffix}_guardrail",
            "nonrecoverable": f"nonrecoverable_{path_group_suffix}_guardrail",
        },
        rules_payload={
            f"recoverable_{rules_key_prefix}_criteria": [
                "recoverable cases must keep pass_formatted_to_parser",
                "recoverable code-fence-like cases must not regress to degeneration_blocked",
                "semantic_guess_used must remain false",
            ],
            f"normal_{rules_key_prefix}_criteria": [
                "normal cases must keep pass_raw_to_parser",
                "normal cases must not gain new collateral false blocks",
            ],
            f"nonrecoverable_{rules_key_prefix}_criteria": [
                "nonrecoverable cases must keep degeneration_blocked",
                "recoverable-boundary fix must not leak nonrecoverable cases",
            ],
            f"{rules_key_prefix}_consistency_criteria": [
                "parser/gate/label-health/handoff semantics remain coherent",
                "impact scope stays local to recoverable boundary",
                "no new path-level drift or parser-source drift",
                "no handoff contract violation or label-health anomaly",
                "no unexpected gate or logistic fallback",
            ],
        },
        real_run_dir=real_run_dir,
        output_dir=output_dir,
        seed=seed,
        label_threshold=label_threshold,
        previous_reference_details_path=previous_reference_details_path,
        previous_reference_prefix=previous_reference_prefix,
        reference_summary_paths=reference_summary_paths,
    )


def post_fourth_round_stage(
    *,
    schema_version: str,
    file_prefix: str,
    validation_dir: Path,
    output_dir: Path,
    validated_label: str,
    recommendation_if_validated: str,
    recommendation_if_partial: str,
    recommendation_if_not_validated: str,
    single_verdict_policy: str,
) -> dict[str, Any]:
    return run_light_expansion_post_analysis(
        schema_version=schema_version,
        file_prefix=file_prefix,
        summary_path=validation_dir / f"{file_prefix}_summary.json",
        output_dir=output_dir,
        validated_label=validated_label,
        partial_label="Partially validated",
        not_validated_label="Not validated",
        recommendation_if_validated=recommendation_if_validated,
        recommendation_if_partial=recommendation_if_partial,
        recommendation_if_not_validated=recommendation_if_not_validated,
        single_verdict_policy=single_verdict_policy,
        do_not_do_yet=[
            "change_benchmark_truth_semantics",
            "change_gate_semantics",
            "expand_budget",
            "expand_model_axis",
            "expand_prompt_family",
            "turn_fourth_round_real_usage_chain_into_large_main_experiment",
        ],
    )
