"""Stage-194 route_c frozen-semantic fourth-round real usage batched-cadence combo validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_fourth_round_real_usage_common import build_fourth_round_stage
from src.eval.route_c_frozen_semantic_real_usage_chain_specs import windows_for_194


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-fourth-round-real-usage-batched-cadence-combo-validation/v1"
FILE_PREFIX = "route_c_frozen_semantic_fourth_round_real_usage_batched_cadence_combo_validation"


def build_route_c_frozen_semantic_fourth_round_real_usage_batched_cadence_combo_validation(
    *,
    real_run_dir: Path,
    stage_191_dir: Path,
    stage_192_dir: Path,
    stage_193_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    return build_fourth_round_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        suite_name="route_c_frozen_semantic_fourth_round_real_usage_batched_cadence_combo_validation_v1",
        report_title="Route-C Frozen Semantic Fourth-Round Real Usage Batched-Cadence Combo Validation Report",
        stage_token="fourth_round_real_usage_batched_cadence_combo_validation_exec",
        case_prefix="fourth_round_real_usage_batched_cadence_combo_validation_exec",
        window_specs=windows_for_194(),
        path_group_suffix="fourth_round_real_usage_batched_cadence_combo_validation",
        rules_key_prefix="fourth_round_real_usage_batched_cadence_combo_validation",
        real_run_dir=real_run_dir,
        output_dir=output_dir,
        seed=seed,
        label_threshold=label_threshold,
        previous_reference_details_path=stage_193_dir
        / "route_c_frozen_semantic_fourth_round_real_usage_cadence_stability_recheck_details.jsonl",
        previous_reference_prefix="fourth_round_real_usage_cadence_stability_recheck_exec",
        reference_summary_paths={
            "stage_191": stage_191_dir / "route_c_frozen_semantic_fourth_round_real_usage_batched_stability_recheck_summary.json",
            "stage_192": stage_192_dir / "route_c_frozen_semantic_fourth_round_real_usage_cadence_validation_summary.json",
            "stage_193": stage_193_dir / "route_c_frozen_semantic_fourth_round_real_usage_cadence_stability_recheck_summary.json",
        },
    )
