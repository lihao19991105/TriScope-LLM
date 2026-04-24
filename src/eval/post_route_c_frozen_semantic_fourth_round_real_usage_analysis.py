"""Post-analysis for stage-188 fourth-round real usage validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_fourth_round_real_usage import FILE_PREFIX
from src.eval.route_c_frozen_semantic_fourth_round_real_usage_common import post_fourth_round_stage


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-fourth-round-real-usage-analysis/v1"


def post_route_c_frozen_semantic_fourth_round_real_usage_analysis(
    *,
    validation_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    return post_fourth_round_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        validation_dir=validation_dir,
        output_dir=output_dir,
        validated_label="Fourth-round real usage validated",
        recommendation_if_validated="下一步进入冻结语义与 gate 不变前提下的第四轮更高层真实使用稳定性复检线",
        recommendation_if_partial="下一步进入第四轮更高层真实使用回归压缩线",
        recommendation_if_not_validated="下一步进入 recoverable-boundary 与第四轮更高层真实使用 handoff 收口线",
        single_verdict_policy="one_of_fourth_round_real_usage_validated__partially_validated__not_validated",
    )
