"""Post-analysis for stage-190 fourth-round real usage batched regression."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_fourth_round_real_usage_batched_regression import FILE_PREFIX
from src.eval.route_c_frozen_semantic_fourth_round_real_usage_common import post_fourth_round_stage


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-fourth-round-real-usage-batched-regression-analysis/v1"


def post_route_c_frozen_semantic_fourth_round_real_usage_batched_regression_analysis(
    *,
    validation_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    return post_fourth_round_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        validation_dir=validation_dir,
        output_dir=output_dir,
        validated_label="Fourth-round real usage batched regression validated",
        recommendation_if_validated="下一步进入冻结语义与 gate 不变前提下的第四轮真实使用 batched 稳定性复检线",
        recommendation_if_partial="下一步进入第四轮真实使用 batched 回归压缩线",
        recommendation_if_not_validated="下一步进入第四轮真实使用 batched handoff 收口线",
        single_verdict_policy="one_of_fourth_round_real_usage_batched_regression_validated__partially_validated__not_validated",
    )
