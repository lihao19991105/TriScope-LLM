"""Stage-170 route_c frozen-semantic next level real usage cadence validation under frozen semantics and gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_light_expansion_common import run_light_expansion_stage
from src.eval.route_c_frozen_semantic_real_usage_chain_specs import REQUIRED_PROMPT_IDS, windows_for_170


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-next-level-real-usage-cadence-validation/v1"
FILE_PREFIX = "route_c_frozen_semantic_next_level_real_usage_cadence_validation"


def build_route_c_frozen_semantic_next_level_real_usage_cadence_validation(
    *,
    real_run_dir: Path,
    stage_167_dir: Path,
    stage_168_dir: Path,
    stage_169_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    return run_light_expansion_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        suite_name="route_c_frozen_semantic_next_level_real_usage_cadence_validation_v1",
        report_title="Route-C Frozen Semantic Next-Level Real Usage Cadence Validation Report",
        stage_token="next_level_real_usage_cadence_validation_exec",
        case_prefix="next_level_real_usage_cadence_validation_exec",
        required_prompt_ids=REQUIRED_PROMPT_IDS,
        window_specs=windows_for_170(),
        path_group_by_kind={
            "recoverable": "recoverable_next_level_real_usage_cadence_validation",
            "normal": "normal_next_level_real_usage_cadence_validation_guardrail",
            "nonrecoverable": "nonrecoverable_next_level_real_usage_cadence_validation_guardrail",
        },
        rules_payload={
            "recoverable_next_level_real_usage_cadence_validation_criteria": [
                "recoverable cases must keep pass_formatted_to_parser",
                "recoverable code-fence-like cases must not regress to degeneration_blocked",
                "semantic_guess_used must remain false",
            ],
            "normal_next_level_real_usage_cadence_validation_criteria": [
                "normal cases must keep pass_raw_to_parser",
                "normal cases must not gain new collateral false blocks",
            ],
            "nonrecoverable_next_level_real_usage_cadence_validation_criteria": [
                "nonrecoverable cases must keep degeneration_blocked",
                "recoverable-boundary fix must not leak nonrecoverable cases",
            ],
            "next_level_real_usage_cadence_validation_consistency_criteria": [
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
        previous_reference_details_path=stage_169_dir / "route_c_frozen_semantic_next_level_real_usage_batched_stability_recheck_details.jsonl",
        previous_reference_prefix="next_level_real_usage_batched_stability_recheck_exec",
        reference_summary_paths={
            "stage_167": stage_167_dir / "route_c_frozen_semantic_next_level_real_usage_stability_recheck_summary.json",
            "stage_168": stage_168_dir / "route_c_frozen_semantic_next_level_real_usage_batched_regression_summary.json",
            "stage_169": stage_169_dir / "route_c_frozen_semantic_next_level_real_usage_batched_stability_recheck_summary.json",
        },
    )
