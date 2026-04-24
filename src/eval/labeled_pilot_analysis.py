"""Analysis and integration recommendation for labeled pilot artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


LABELED_PILOT_ANALYSIS_SCHEMA_VERSION = "triscopellm/labeled-pilot-analysis/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object on line {line_number} of `{path}`.")
            rows.append(payload)
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            normalized: dict[str, Any] = {}
            for key in fieldnames:
                value = row.get(key)
                if isinstance(value, (dict, list)):
                    normalized[key] = json.dumps(value, ensure_ascii=True, sort_keys=True)
                else:
                    normalized[key] = value
            writer.writerow(normalized)


def build_labeled_pilot_analysis(
    real_pilot_analysis_summary_path: Path,
    real_pilot_next_step_recommendation_path: Path,
    real_pilot_readiness_summary_path: Path,
    real_pilot_fusion_dataset_path: Path,
    real_pilot_logistic_summary_path: Path,
    labeled_pilot_summary_path: Path,
    labeled_supervised_readiness_summary_path: Path,
    labeled_logistic_summary_path: Path,
    labeled_pilot_dataset_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    real_pilot_analysis_summary = load_json(real_pilot_analysis_summary_path)
    real_pilot_recommendation = load_json(real_pilot_next_step_recommendation_path)
    real_pilot_readiness = load_json(real_pilot_readiness_summary_path)
    real_pilot_logistic = load_json(real_pilot_logistic_summary_path)
    real_pilot_fusion_rows = load_jsonl(real_pilot_fusion_dataset_path)

    labeled_pilot_summary = load_json(labeled_pilot_summary_path)
    labeled_supervised_readiness = load_json(labeled_supervised_readiness_summary_path)
    labeled_logistic_summary = load_json(labeled_logistic_summary_path)
    labeled_rows = load_jsonl(labeled_pilot_dataset_path)

    fusion_base_ids = {str(row["sample_id"]) for row in real_pilot_fusion_rows}
    labeled_base_ids = {str(row["base_sample_id"]) for row in labeled_rows}
    aligned_base_ids = sorted(fusion_base_ids & labeled_base_ids)
    contract_variants = sorted({str(row["contract_variant"]) for row in labeled_rows})

    comparison_rows: list[dict[str, Any]] = []
    for row in labeled_rows:
        base_sample_id = str(row["base_sample_id"])
        comparison_rows.append(
            {
                "labeled_sample_id": row["sample_id"],
                "base_sample_id": base_sample_id,
                "contract_variant": row["contract_variant"],
                "ground_truth_label": row["ground_truth_label"],
                "label_name": row["label_name"],
                "in_real_pilot_fusion": base_sample_id in fusion_base_ids,
                "mapped_alignment_key": f"{base_sample_id}::{row['contract_variant']}",
                "illumination_trigger_type": row["trigger_type"],
                "real_pilot_fusion_model_profile": row["model_profile"] if base_sample_id in fusion_base_ids else None,
                "label_scope": row.get("metadata", {}).get("contract_metadata", {}).get("label_scope"),
            }
        )

    labeled_vs_real_pilot_alignment_summary = {
        "summary_status": "PASS",
        "schema_version": LABELED_PILOT_ANALYSIS_SCHEMA_VERSION,
        "label_name": "controlled_targeted_icl_label",
        "label_source": "materialized_contract_variant",
        "label_scope": "pilot_level_controlled_supervision",
        "real_pilot_alignment_key": "sample_id",
        "labeled_alignment_keys": ["base_sample_id", "contract_variant"],
        "natural_alignment_available": len(aligned_base_ids) > 0,
        "aligned_base_sample_ids": aligned_base_ids,
        "num_real_pilot_base_ids": len(fusion_base_ids),
        "num_labeled_base_ids": len(labeled_base_ids),
        "num_naturally_aligned_base_ids": len(aligned_base_ids),
        "contract_variants": contract_variants,
        "can_build_contract_level_fusion_rows": True,
        "mapping_strategy": (
            "Expand each aligned real-pilot base sample into control and targeted contract rows; "
            "reuse reasoning/confidence features at the base-sample level and swap in labeled illumination rows."
        ),
    }

    labeled_fusion_blocker_summary = {
        "summary_status": "PASS",
        "schema_version": LABELED_PILOT_ANALYSIS_SCHEMA_VERSION,
        "benchmark_ground_truth_available": False,
        "pilot_level_controlled_supervision_available": True,
        "fusion_integration_label_available": True,
        "current_blockers": [
            {
                "blocker_name": "benchmark_ground_truth_still_missing",
                "scope": "research_grade_supervised_fusion",
                "severity": "medium",
                "notes": [
                    "018 solved the total absence of labels, but only via controlled pilot supervision.",
                    "This is enough for supervised bootstrap, not for final benchmark claims.",
                ],
            },
            {
                "blocker_name": "contract_level_label_not_native_to_existing_fusion_rows",
                "scope": "direct_rowwise_reuse_of_015_dataset",
                "severity": "low",
                "notes": [
                    "Current fusion rows live at base-sample level.",
                    "Labeled rows live at base-sample plus contract-variant level.",
                    "A small materialization step is needed before supervised fusion can run.",
                ],
            },
        ],
        "already_resolved": [
            "missing_ground_truth_labels_as_total_absence_of_supervision",
            "real_pilot_cross_module_alignment",
            "real_pilot_full_intersection",
        ],
    }

    labeled_pilot_analysis_summary = {
        "summary_status": "PASS",
        "schema_version": LABELED_PILOT_ANALYSIS_SCHEMA_VERSION,
        "label_name": "controlled_targeted_icl_label",
        "label_scope": "pilot_level_controlled_supervision",
        "real_pilot_modules": real_pilot_readiness.get("real_pilot_modules"),
        "real_pilot_full_intersection_available": real_pilot_readiness.get("full_intersection_available"),
        "real_pilot_logistic_status": real_pilot_logistic.get("summary_status"),
        "historical_skip_reason": real_pilot_logistic.get("reason"),
        "labeled_pilot_supervised_path_exists": labeled_supervised_readiness.get("supervised_path_exists"),
        "labeled_pilot_logistic_status": labeled_logistic_summary.get("summary_status"),
        "num_labeled_rows": labeled_pilot_summary.get("num_rows"),
        "num_naturally_aligned_base_ids": len(aligned_base_ids),
        "notes": [
            "The repository now has both an unlabeled real-pilot fusion path and a labeled pilot-level supervision path.",
            "The remaining task is to bridge them with an explicit contract-level mapping.",
        ],
        "artifacts": {
            "labeled_vs_real_pilot_alignment_summary": str((output_dir / "labeled_vs_real_pilot_alignment_summary.json").resolve()),
            "labeled_fusion_blocker_summary": str((output_dir / "labeled_fusion_blocker_summary.json").resolve()),
            "fusion_integration_recommendation": str((output_dir / "fusion_integration_recommendation.json").resolve()),
        },
    }

    fusion_integration_recommendation = {
        "summary_status": "PASS",
        "schema_version": LABELED_PILOT_ANALYSIS_SCHEMA_VERSION,
        "route_options": [
            {
                "route_name": "keep_labeled_pilot_isolated",
                "route_code": "A",
                "recommended": False,
                "pros": [
                    "No extra fusion materialization work.",
                    "Keeps pilot-level supervision confined to illumination only.",
                ],
                "cons": [
                    "Does not unblock supervised real-pilot fusion.",
                    "Leaves 016's historical skip unresolved at the fusion layer.",
                ],
            },
            {
                "route_name": "map_controlled_label_back_to_real_pilot_fusion",
                "route_code": "B",
                "recommended": True,
                "pros": [
                    "Unblocks the first supervised real-pilot fusion bootstrap.",
                    "Reuses existing aligned real-pilot rows without adding new data or models.",
                    "Keeps the label source explicit and auditable.",
                ],
                "cons": [
                    "The resulting supervision is still pilot-level controlled supervision, not benchmark truth.",
                    "Reasoning and confidence features must be reused at base-sample level across control/targeted variants.",
                ],
            },
        ],
        "recommended_route": "map_controlled_label_back_to_real_pilot_fusion",
        "recommended_route_code": "B",
        "integration_contract": {
            "label_name": "controlled_targeted_icl_label",
            "label_source": "materialized_contract_variant",
            "label_scope": "pilot_level_controlled_supervision",
            "alignment_keys": ["base_sample_id", "contract_variant"],
            "bridge_to_existing_fusion": {
                "real_pilot_fusion_key": "sample_id",
                "mapping_rule": "real_pilot_fusion.sample_id == labeled_pilot.base_sample_id",
                "fusion_row_expansion": "duplicate each aligned base sample into control and targeted rows",
            },
            "eligible_base_sample_ids": aligned_base_ids,
            "label_limitations": [
                "Not benchmark ground truth.",
                "Only covers aligned base samples currently present in the real-pilot fusion dataset.",
                "Copies reasoning/confidence features across contract variants within the same base sample.",
            ],
        },
        "recommendation_rationale": [
            "This is the smallest viable step that makes supervised fusion exist.",
            "It directly addresses the old missing_ground_truth_labels blocker.",
            "It is more valuable right now than keeping the label path isolated.",
        ],
    }

    write_csv(output_dir / "labeled_vs_fusion_comparison.csv", comparison_rows)
    write_json(output_dir / "labeled_pilot_analysis_summary.json", labeled_pilot_analysis_summary)
    write_json(output_dir / "labeled_vs_real_pilot_alignment_summary.json", labeled_vs_real_pilot_alignment_summary)
    write_json(output_dir / "labeled_fusion_blocker_summary.json", labeled_fusion_blocker_summary)
    write_json(output_dir / "fusion_integration_recommendation.json", fusion_integration_recommendation)
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM labeled pilot analysis and fusion integration",
                f"Real-pilot analysis summary: {real_pilot_analysis_summary_path.resolve()}",
                f"Labeled pilot summary: {labeled_pilot_summary_path.resolve()}",
                f"Real-pilot fusion dataset: {real_pilot_fusion_dataset_path.resolve()}",
                f"Labeled pilot dataset: {labeled_pilot_dataset_path.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "labeled_pilot_analysis_summary": labeled_pilot_analysis_summary,
        "labeled_vs_real_pilot_alignment_summary": labeled_vs_real_pilot_alignment_summary,
        "labeled_fusion_blocker_summary": labeled_fusion_blocker_summary,
        "fusion_integration_recommendation": fusion_integration_recommendation,
        "output_paths": {
            "labeled_pilot_analysis_summary": str((output_dir / "labeled_pilot_analysis_summary.json").resolve()),
            "labeled_vs_real_pilot_alignment_summary": str((output_dir / "labeled_vs_real_pilot_alignment_summary.json").resolve()),
            "labeled_fusion_blocker_summary": str((output_dir / "labeled_fusion_blocker_summary.json").resolve()),
            "labeled_vs_fusion_comparison": str((output_dir / "labeled_vs_fusion_comparison.csv").resolve()),
            "fusion_integration_recommendation": str((output_dir / "fusion_integration_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
