"""Stage-183 route_c frozen-semantic third round real usage batched cadence combo validation under frozen semantics and gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_light_expansion_common import run_light_expansion_stage
from src.eval.route_c_frozen_semantic_real_usage_chain_specs import REQUIRED_PROMPT_IDS, windows_for_183


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-third-round-real-usage-batched-cadence-combo-validation/v1"
FILE_PREFIX = "route_c_frozen_semantic_third_round_real_usage_batched_cadence_combo_validation"


def build_route_c_frozen_semantic_third_round_real_usage_batched_cadence_combo_validation(
    *,
    real_run_dir: Path,
    stage_180_dir: Path,
    stage_181_dir: Path,
    stage_182_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    return run_light_expansion_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        suite_name="route_c_frozen_semantic_third_round_real_usage_batched_cadence_combo_validation_v1",
        report_title="Route-C Frozen Semantic Third-Round Real Usage Batched Cadence Combo Validation Report",
        stage_token="third_round_real_usage_batched_cadence_combo_validation_exec",
        case_prefix="third_round_real_usage_batched_cadence_combo_validation_exec",
        required_prompt_ids=REQUIRED_PROMPT_IDS,
        window_specs=windows_for_183(),
        path_group_by_kind={
            "recoverable": "recoverable_third_round_real_usage_batched_cadence_combo_validation",
            "normal": "normal_third_round_real_usage_batched_cadence_combo_validation_guardrail",
            "nonrecoverable": "nonrecoverable_third_round_real_usage_batched_cadence_combo_validation_guardrail",
        },
        rules_payload={
            "recoverable_third_round_real_usage_batched_cadence_combo_validation_criteria": [
                "recoverable cases must keep pass_formatted_to_parser",
                "recoverable code-fence-like cases must not regress to degeneration_blocked",
                "semantic_guess_used must remain false",
            ],
            "normal_third_round_real_usage_batched_cadence_combo_validation_criteria": [
                "normal cases must keep pass_raw_to_parser",
                "normal cases must not gain new collateral false blocks",
            ],
            "nonrecoverable_third_round_real_usage_batched_cadence_combo_validation_criteria": [
                "nonrecoverable cases must keep degeneration_blocked",
                "recoverable-boundary fix must not leak nonrecoverable cases",
            ],
            "third_round_real_usage_batched_cadence_combo_validation_consistency_criteria": [
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
        previous_reference_details_path=stage_182_dir / "route_c_frozen_semantic_third_round_real_usage_cadence_stability_recheck_details.jsonl",
        previous_reference_prefix="third_round_real_usage_cadence_stability_recheck_exec",
        reference_summary_paths={
            "stage_180": stage_180_dir / "route_c_frozen_semantic_third_round_real_usage_batched_stability_recheck_summary.json",
            "stage_181": stage_181_dir / "route_c_frozen_semantic_third_round_real_usage_cadence_validation_summary.json",
            "stage_182": stage_182_dir / "route_c_frozen_semantic_third_round_real_usage_cadence_stability_recheck_summary.json",
        },
    )
