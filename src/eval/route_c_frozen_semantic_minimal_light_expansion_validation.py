"""Stage-156 minimal light-expansion validation under frozen semantics and gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_light_expansion_common import run_light_expansion_stage


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-minimal-light-expansion-validation/v1"
FILE_PREFIX = "route_c_frozen_semantic_minimal_light_expansion"


def build_route_c_frozen_semantic_minimal_light_expansion_validation(
    *,
    real_run_dir: Path,
    stage_153_dir: Path,
    stage_154_dir: Path,
    stage_155_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    window_specs = [
        {
            "window_id": "light_window_01",
            "window_tag": "lw01",
            "entries": [
                {
                    "path_kind": "recoverable",
                    "anchor_prompt_id": "illumination_0001",
                    "response_variant": "code_fence",
                    "case_tail": "code_fence",
                    "note": "recoverable code-fence wrapper derived from illumination_0001",
                },
                {
                    "path_kind": "normal",
                    "anchor_prompt_id": "illumination_0001",
                    "response_variant": "raw",
                    "case_tail": "csqa-pilot-002__control",
                    "note": "real normal guardrail case from illumination_0001",
                },
                {
                    "path_kind": "nonrecoverable",
                    "anchor_prompt_id": "illumination_0000",
                    "response_variant": "raw",
                    "case_tail": "csqa-pilot-021__targeted",
                    "note": "real nonrecoverable guardrail case from illumination_0000",
                },
                {
                    "path_kind": "recoverable",
                    "anchor_prompt_id": "illumination_0002",
                    "response_variant": "code_fence_lang_tag",
                    "case_tail": "code_fence_lang_tag",
                    "note": "language-tag recoverable wrapper derived from illumination_0002",
                },
                {
                    "path_kind": "normal",
                    "anchor_prompt_id": "illumination_0002",
                    "response_variant": "raw",
                    "case_tail": "csqa-pilot-021__control",
                    "note": "real normal guardrail case from illumination_0002",
                },
                {
                    "path_kind": "nonrecoverable",
                    "anchor_prompt_id": "illumination_0000",
                    "response_variant": "code_fence_lang_tag",
                    "case_tail": "code_fence_contract_broken",
                    "note": "near-boundary nonrecoverable code-fence wrapper from illumination_0000",
                },
            ],
        },
        {
            "window_id": "light_window_02",
            "window_tag": "lw02",
            "entries": [
                {
                    "path_kind": "recoverable",
                    "anchor_prompt_id": "illumination_0003",
                    "response_variant": "code_fence",
                    "case_tail": "code_fence",
                    "note": "recoverable code-fence wrapper derived from illumination_0003",
                },
                {
                    "path_kind": "normal",
                    "anchor_prompt_id": "illumination_0003",
                    "response_variant": "raw",
                    "case_tail": "csqa-pilot-005__control",
                    "note": "real normal guardrail case from illumination_0003",
                },
                {
                    "path_kind": "nonrecoverable",
                    "anchor_prompt_id": "illumination_0000",
                    "response_variant": "raw",
                    "case_tail": "csqa-pilot-021__targeted",
                    "note": "reused real nonrecoverable guardrail case from illumination_0000",
                },
                {
                    "path_kind": "recoverable",
                    "anchor_prompt_id": "illumination_0004",
                    "response_variant": "code_fence_lang_tag",
                    "case_tail": "code_fence_lang_tag",
                    "note": "language-tag recoverable wrapper derived from illumination_0004",
                },
                {
                    "path_kind": "normal",
                    "anchor_prompt_id": "illumination_0005",
                    "response_variant": "raw",
                    "case_tail": "csqa-pilot-005__targeted",
                    "note": "real normal guardrail case from illumination_0005",
                },
                {
                    "path_kind": "nonrecoverable",
                    "anchor_prompt_id": "illumination_0000",
                    "response_variant": "code_fence_lang_tag",
                    "case_tail": "code_fence_contract_broken",
                    "note": "near-boundary nonrecoverable code-fence wrapper from illumination_0000",
                },
            ],
        },
        {
            "window_id": "light_window_03",
            "window_tag": "lw03",
            "entries": [
                {
                    "path_kind": "recoverable",
                    "anchor_prompt_id": "illumination_0005",
                    "response_variant": "code_fence",
                    "case_tail": "code_fence_from_targeted",
                    "note": "recoverable wrapper from targeted normal anchor illumination_0005",
                },
                {
                    "path_kind": "normal",
                    "anchor_prompt_id": "illumination_0004",
                    "response_variant": "raw",
                    "case_tail": "csqa-pilot-002__targeted",
                    "note": "real normal guardrail case from illumination_0004",
                },
                {
                    "path_kind": "nonrecoverable",
                    "anchor_prompt_id": "illumination_0000",
                    "response_variant": "raw",
                    "case_tail": "csqa-pilot-021__targeted_repeat",
                    "note": "real nonrecoverable guardrail reuse from illumination_0000",
                },
                {
                    "path_kind": "recoverable",
                    "anchor_prompt_id": "illumination_0001",
                    "response_variant": "code_fence_lang_tag",
                    "case_tail": "code_fence_lang_tag_repeat",
                    "note": "recoverable language-tag wrapper from illumination_0001",
                },
                {
                    "path_kind": "normal",
                    "anchor_prompt_id": "illumination_0001",
                    "response_variant": "raw",
                    "case_tail": "csqa-pilot-002__control_repeat",
                    "note": "real normal guardrail reuse from illumination_0001",
                },
                {
                    "path_kind": "nonrecoverable",
                    "anchor_prompt_id": "illumination_0000",
                    "response_variant": "code_fence_lang_tag",
                    "case_tail": "code_fence_contract_broken_repeat",
                    "note": "nonrecoverable formatted wrapper reuse from illumination_0000",
                },
            ],
        },
    ]

    return run_light_expansion_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        suite_name="route_c_frozen_semantic_minimal_light_expansion_validation_v1",
        report_title="Route-C Frozen Semantic Minimal Light Expansion Validation Report",
        stage_token="minimal_light_expansion_exec",
        case_prefix="light_expansion_exec",
        required_prompt_ids=[
            "illumination_0000",
            "illumination_0001",
            "illumination_0002",
            "illumination_0003",
            "illumination_0004",
            "illumination_0005",
        ],
        window_specs=window_specs,
        path_group_by_kind={
            "recoverable": "recoverable_light_expansion",
            "normal": "normal_light_expansion_guardrail",
            "nonrecoverable": "nonrecoverable_light_expansion_guardrail",
        },
        rules_payload={
            "recoverable_light_expansion_criteria": [
                "recoverable cases must keep pass_formatted_to_parser",
                "recoverable code-fence-like cases must not regress to degeneration_blocked",
                "semantic_guess_used must remain false",
            ],
            "normal_light_expansion_criteria": [
                "normal cases must keep pass_raw_to_parser",
                "normal cases must not gain new collateral false blocks",
            ],
            "nonrecoverable_light_expansion_criteria": [
                "nonrecoverable cases must keep degeneration_blocked",
                "recoverable-boundary fix must not leak nonrecoverable cases",
            ],
            "light_expansion_consistency_criteria": [
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
        previous_reference_details_path=stage_155_dir
        / "route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_details.jsonl",
        previous_reference_prefix="batched_recheck_exec",
        reference_summary_paths={
            "stage_153": stage_153_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_summary.json",
            "stage_154": stage_154_dir / "route_c_frozen_semantic_minimal_real_batched_continuous_regression_summary.json",
            "stage_155": stage_155_dir / "route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_summary.json",
        },
    )
