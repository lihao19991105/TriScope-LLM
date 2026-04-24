"""Stage-162 minimal real-usage batched stability recheck under frozen semantics and gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_light_expansion_common import run_light_expansion_stage
from src.eval.route_c_frozen_semantic_real_usage_chain_specs import REQUIRED_PROMPT_IDS, windows_for_162


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-minimal-real-usage-batched-stability-recheck/v1"
FILE_PREFIX = "route_c_frozen_semantic_minimal_real_usage_batched_stability_recheck"


def build_route_c_frozen_semantic_minimal_real_usage_batched_stability_recheck(
    *,
    real_run_dir: Path,
    stage_159_dir: Path,
    stage_160_dir: Path,
    stage_161_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    return run_light_expansion_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        suite_name="route_c_frozen_semantic_minimal_real_usage_batched_stability_recheck_v1",
        report_title="Route-C Frozen Semantic Minimal Real Usage Batched Stability Recheck Report",
        stage_token="minimal_real_usage_batched_stability_recheck_exec",
        case_prefix="real_usage_batched_stability_recheck_exec",
        required_prompt_ids=REQUIRED_PROMPT_IDS,
        window_specs=windows_for_162(),
        path_group_by_kind={
            "recoverable": "recoverable_real_usage_batched_stability_recheck",
            "normal": "normal_real_usage_batched_stability_recheck_guardrail",
            "nonrecoverable": "nonrecoverable_real_usage_batched_stability_recheck_guardrail",
        },
        rules_payload={
            "recoverable_real_usage_batched_stability_recheck_criteria": [
                "recoverable cases must keep pass_formatted_to_parser",
                "recoverable code-fence-like cases must not regress to degeneration_blocked",
                "semantic_guess_used must remain false",
            ],
            "normal_real_usage_batched_stability_recheck_criteria": [
                "normal cases must keep pass_raw_to_parser",
                "normal cases must not gain new collateral false blocks",
            ],
            "nonrecoverable_real_usage_batched_stability_recheck_criteria": [
                "nonrecoverable cases must keep degeneration_blocked",
                "recoverable-boundary fix must not leak nonrecoverable cases",
            ],
            "real_usage_batched_stability_recheck_consistency_criteria": [
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
        previous_reference_details_path=stage_161_dir
        / "route_c_frozen_semantic_minimal_real_usage_batched_regression_details.jsonl",
        previous_reference_prefix="real_usage_batched_regression_exec",
        reference_summary_paths={
            "stage_159": stage_159_dir / "route_c_frozen_semantic_minimal_real_usage_summary.json",
            "stage_160": stage_160_dir / "route_c_frozen_semantic_minimal_real_usage_stability_recheck_summary.json",
            "stage_161": stage_161_dir / "route_c_frozen_semantic_minimal_real_usage_batched_regression_summary.json",
        },
    )
