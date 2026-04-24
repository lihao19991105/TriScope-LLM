"""Post-analysis for stage-198 fourth-round real usage chain final recheck."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_fourth_round_real_usage_chain_final_recheck import FILE_PREFIX
from src.eval.route_c_frozen_semantic_fourth_round_real_usage_common import post_fourth_round_stage


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-fourth-round-real-usage-chain-final-recheck-analysis/v1"


def post_route_c_frozen_semantic_fourth_round_real_usage_chain_final_recheck_analysis(
    *,
    validation_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    return post_fourth_round_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        validation_dir=validation_dir,
        output_dir=output_dir,
        validated_label="Fourth-round real usage chain final recheck validated",
        recommendation_if_validated="下一步进入冻结语义与 gate 不变前提下的第五轮更高层真实使用验证线",
        recommendation_if_partial="下一步进入第四轮真实使用链最终压缩收口线",
        recommendation_if_not_validated="下一步进入第四轮真实使用链最终 handoff / boundary 收口线",
        single_verdict_policy="one_of_fourth_round_real_usage_chain_final_recheck_validated__partially_validated__not_validated",
    )
