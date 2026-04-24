"""Stage-197 route_c frozen-semantic fourth-round real usage pre-final stability recheck."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_fourth_round_real_usage_common import build_fourth_round_stage
from src.eval.route_c_frozen_semantic_real_usage_chain_specs import windows_for_197


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-fourth-round-real-usage-pre-final-stability-recheck/v1"
FILE_PREFIX = "route_c_frozen_semantic_fourth_round_real_usage_pre_final_stability_recheck"


def build_route_c_frozen_semantic_fourth_round_real_usage_pre_final_stability_recheck(
    *,
    real_run_dir: Path,
    stage_194_dir: Path,
    stage_195_dir: Path,
    stage_196_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    return build_fourth_round_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        suite_name="route_c_frozen_semantic_fourth_round_real_usage_pre_final_stability_recheck_v1",
        report_title="Route-C Frozen Semantic Fourth-Round Real Usage Pre-Final Stability Recheck Report",
        stage_token="fourth_round_real_usage_pre_final_stability_recheck_exec",
        case_prefix="fourth_round_real_usage_pre_final_stability_recheck_exec",
        window_specs=windows_for_197(),
        path_group_suffix="fourth_round_real_usage_pre_final_stability_recheck",
        rules_key_prefix="fourth_round_real_usage_pre_final_stability_recheck",
        real_run_dir=real_run_dir,
        output_dir=output_dir,
        seed=seed,
        label_threshold=label_threshold,
        previous_reference_details_path=stage_196_dir
        / "route_c_frozen_semantic_fourth_round_real_usage_mid_high_coverage_validation_details.jsonl",
        previous_reference_prefix="fourth_round_real_usage_mid_high_coverage_validation_exec",
        reference_summary_paths={
            "stage_194": stage_194_dir / "route_c_frozen_semantic_fourth_round_real_usage_batched_cadence_combo_validation_summary.json",
            "stage_195": stage_195_dir / "route_c_frozen_semantic_fourth_round_real_usage_batched_cadence_combo_stability_recheck_summary.json",
            "stage_196": stage_196_dir / "route_c_frozen_semantic_fourth_round_real_usage_mid_high_coverage_validation_summary.json",
        },
    )
