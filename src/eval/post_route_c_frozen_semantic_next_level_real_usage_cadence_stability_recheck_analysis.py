"""Post-analysis for stage-171 next level real usage cadence stability recheck."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_light_expansion_common import run_light_expansion_post_analysis
from src.eval.route_c_frozen_semantic_next_level_real_usage_cadence_stability_recheck import FILE_PREFIX


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-next-level-real-usage-cadence-stability-recheck-analysis/v1"


def post_route_c_frozen_semantic_next_level_real_usage_cadence_stability_recheck_analysis(
    *,
    validation_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    return run_light_expansion_post_analysis(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        summary_path=validation_dir / f"{FILE_PREFIX}_summary.json",
        output_dir=output_dir,
        validated_label="Next-level real usage cadence stability recheck validated",
        partial_label="Partially validated",
        not_validated_label="Not validated",
        recommendation_if_validated="下一步进入冻结语义与 gate 不变前提下的更高一层真实使用 batched-cadence 组合验证线",
        recommendation_if_partial="下一步进入当前主线对应的压缩线",
        recommendation_if_not_validated="下一步进入当前主线对应的 handoff / boundary 收口线",
        single_verdict_policy="one_of_next_level_real_usage_cadence_stability_recheck_validated__partially_validated__not_validated",
        do_not_do_yet=[
            "change_benchmark_truth_semantics",
            "change_gate_semantics",
            "expand_budget",
            "expand_model_axis",
            "expand_prompt_family",
            "turn_171_into_large_stability_project",
        ],
    )
