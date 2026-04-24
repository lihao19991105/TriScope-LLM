"""Post-analysis for stage-187 third round real usage chain final recheck."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_light_expansion_common import run_light_expansion_post_analysis
from src.eval.route_c_frozen_semantic_third_round_real_usage_chain_final_recheck import FILE_PREFIX


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-third-round-real-usage-chain-final-recheck-analysis/v1"


def post_route_c_frozen_semantic_third_round_real_usage_chain_final_recheck_analysis(
    *,
    validation_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    return run_light_expansion_post_analysis(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        summary_path=validation_dir / f"{FILE_PREFIX}_summary.json",
        output_dir=output_dir,
        validated_label="Third-round real usage chain final recheck validated",
        partial_label="Partially validated",
        not_validated_label="Not validated",
        recommendation_if_validated="下一步进入冻结语义与 gate 不变前提下的下一轮更高层真实使用验证线（仍保持小步、克制、可审计）",
        recommendation_if_partial="下一步进入当前主线对应的压缩线",
        recommendation_if_not_validated="下一步进入当前主线对应的 handoff / boundary 收口线",
        single_verdict_policy="one_of_third_round_real_usage_chain_final_recheck_validated__partially_validated__not_validated",
        do_not_do_yet=[
            "change_benchmark_truth_semantics",
            "change_gate_semantics",
            "expand_budget",
            "expand_model_axis",
            "expand_prompt_family",
            "turn_187_into_large_stability_project",
        ],
    )
