"""Post-analysis for stage-196 fourth-round real usage mid-high coverage validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_fourth_round_real_usage_common import post_fourth_round_stage
from src.eval.route_c_frozen_semantic_fourth_round_real_usage_mid_high_coverage_validation import FILE_PREFIX


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-fourth-round-real-usage-mid-high-coverage-validation-analysis/v1"


def post_route_c_frozen_semantic_fourth_round_real_usage_mid_high_coverage_validation_analysis(
    *,
    validation_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    return post_fourth_round_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        validation_dir=validation_dir,
        output_dir=output_dir,
        validated_label="Fourth-round real usage mid-high coverage validated",
        recommendation_if_validated="下一步进入冻结语义与 gate 不变前提下的第四轮真实使用 pre-final 稳定性复检线",
        recommendation_if_partial="下一步进入第四轮真实使用 mid-high coverage 压缩线",
        recommendation_if_not_validated="下一步进入第四轮真实使用 mid-high coverage handoff 收口线",
        single_verdict_policy="one_of_fourth_round_real_usage_mid_high_coverage_validated__partially_validated__not_validated",
    )
