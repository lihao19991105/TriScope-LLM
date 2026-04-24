"""Post-analysis for stage-164 minimal real-usage tempo stability recheck."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_light_expansion_common import run_light_expansion_post_analysis
from src.eval.route_c_frozen_semantic_minimal_real_usage_tempo_stability_recheck import FILE_PREFIX


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-minimal-real-usage-tempo-stability-recheck-analysis/v1"


def post_route_c_frozen_semantic_minimal_real_usage_tempo_stability_recheck_analysis(
    *,
    validation_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    return run_light_expansion_post_analysis(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        summary_path=validation_dir / f"{FILE_PREFIX}_summary.json",
        output_dir=output_dir,
        validated_label="Minimal real usage tempo stability recheck validated",
        partial_label="Partially validated",
        not_validated_label="Not validated",
        recommendation_if_validated="下一步进入本轮 159-165 链的最终收口验证/复检线",
        recommendation_if_partial="下一步进入真实使用节奏压缩/收口线",
        recommendation_if_not_validated="下一步进入更小步 boundary / handoff / parser-path 诊断收口线",
        single_verdict_policy="one_of_minimal_real_usage_tempo_stability_recheck_validated__partially_validated__not_validated",
        do_not_do_yet=[
            "change_benchmark_truth_semantics",
            "change_gate_semantics",
            "expand_budget",
            "expand_model_axis",
            "expand_prompt_family",
            "turn_164_into_large_stability_project",
        ],
    )
