"""Stage-192 route_c frozen-semantic fourth-round real usage cadence validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.route_c_frozen_semantic_fourth_round_real_usage_common import build_fourth_round_stage
from src.eval.route_c_frozen_semantic_real_usage_chain_specs import windows_for_192


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-fourth-round-real-usage-cadence-validation/v1"
FILE_PREFIX = "route_c_frozen_semantic_fourth_round_real_usage_cadence_validation"


def build_route_c_frozen_semantic_fourth_round_real_usage_cadence_validation(
    *,
    real_run_dir: Path,
    stage_189_dir: Path,
    stage_190_dir: Path,
    stage_191_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    return build_fourth_round_stage(
        schema_version=SCHEMA_VERSION,
        file_prefix=FILE_PREFIX,
        suite_name="route_c_frozen_semantic_fourth_round_real_usage_cadence_validation_v1",
        report_title="Route-C Frozen Semantic Fourth-Round Real Usage Cadence Validation Report",
        stage_token="fourth_round_real_usage_cadence_validation_exec",
        case_prefix="fourth_round_real_usage_cadence_validation_exec",
        window_specs=windows_for_192(),
        path_group_suffix="fourth_round_real_usage_cadence_validation",
        rules_key_prefix="fourth_round_real_usage_cadence_validation",
        real_run_dir=real_run_dir,
        output_dir=output_dir,
        seed=seed,
        label_threshold=label_threshold,
        previous_reference_details_path=stage_191_dir
        / "route_c_frozen_semantic_fourth_round_real_usage_batched_stability_recheck_details.jsonl",
        previous_reference_prefix="fourth_round_real_usage_batched_stability_recheck_exec",
        reference_summary_paths={
            "stage_189": stage_189_dir / "route_c_frozen_semantic_fourth_round_real_usage_stability_recheck_summary.json",
            "stage_190": stage_190_dir / "route_c_frozen_semantic_fourth_round_real_usage_batched_regression_summary.json",
            "stage_191": stage_191_dir / "route_c_frozen_semantic_fourth_round_real_usage_batched_stability_recheck_summary.json",
        },
    )
