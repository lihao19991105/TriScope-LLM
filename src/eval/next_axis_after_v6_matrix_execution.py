"""Execute the refined-fusion-support-ablation-aware next-axis-after-v6 matrix v7."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/next-axis-after-v6-matrix-execution/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Expected at least one CSV row.")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def copy_artifact(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def build_next_axis_after_v6_matrix_execution(
    matrix_dry_run_summary_path: Path,
    matrix_cell_status_path: Path,
    matrix_execution_contract_path: Path,
    matrix_definition_path: Path,
    v6_execution_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dry_run_summary = load_json(matrix_dry_run_summary_path)
    cell_status = load_json(matrix_cell_status_path)
    contract = load_json(matrix_execution_contract_path)
    matrix_definition = load_json(matrix_definition_path)
    if dry_run_summary.get("summary_status") != "PASS":
        raise ValueError("Next-axis-after-v6 matrix execution requires PASS dry-run summary.")
    if cell_status.get("summary_status") != "PASS":
        raise ValueError("Next-axis-after-v6 matrix execution requires PASS cell status.")

    required_sources = [
        v6_execution_dir / "next_axis_after_v5_matrix_route_b_summary.json",
        v6_execution_dir / "next_axis_after_v5_matrix_route_c_summary.json",
        v6_execution_dir / "next_axis_after_v5_matrix_route_b_only_ablation_summary.json",
        v6_execution_dir / "next_axis_after_v5_matrix_route_c_only_ablation_summary.json",
        v6_execution_dir / "next_axis_after_v5_matrix_fusion_summary.json",
        v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_candidate_summary.json",
        v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_summary.json",
        v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_ablation_summary.json",
        v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_support_sweep_summary.json",
        v6_execution_dir / "next_axis_after_v5_matrix_execution_metrics.json",
    ]
    for path in required_sources:
        if not path.is_file():
            raise ValueError(f"Next-axis-after-v6 matrix execution source artifact not found: `{path}`.")

    route_b_summary = load_json(v6_execution_dir / "next_axis_after_v5_matrix_route_b_summary.json")
    route_c_summary = load_json(v6_execution_dir / "next_axis_after_v5_matrix_route_c_summary.json")
    route_b_ablation_summary = load_json(v6_execution_dir / "next_axis_after_v5_matrix_route_b_only_ablation_summary.json")
    route_c_ablation_summary = load_json(v6_execution_dir / "next_axis_after_v5_matrix_route_c_only_ablation_summary.json")
    fusion_summary = load_json(v6_execution_dir / "next_axis_after_v5_matrix_fusion_summary.json")
    fusion_candidate_summary = load_json(v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_candidate_summary.json")
    fusion_refined_summary = load_json(v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_summary.json")
    fusion_refined_ablation_summary = load_json(
        v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_ablation_summary.json"
    )
    fusion_refined_support_sweep_summary = load_json(
        v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_support_sweep_summary.json"
    )
    v6_metrics = load_json(v6_execution_dir / "next_axis_after_v5_matrix_execution_metrics.json")

    cells = contract["cells"]
    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cells": [cell["cell_id"] for cell in cells],
        "selected_dataset": cells[0]["dataset_name"],
        "selected_model": cells[0]["model_name"],
        "selected_routes": matrix_definition["routes"],
        "why_selected": [
            "The purpose of v7 is to test how much refined fusion signal survives after the support-retained residual is explicitly ablated.",
            "The first honest execution therefore includes summary, candidate, refined, refined-ablation, refined-support-sweep, and refined-support-ablation views in one matrix layer.",
        ],
        "success_standard": [
            "rehydrate route_b / route_c / ablation summaries into v7 matrix cells",
            "keep summary, candidate, refined, refined-ablation, and refined-support-sweep fusion cells available for comparison",
            "execute an explicit fusion_cell_refined_support_ablation summary",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cell_count": len(cells),
        "route_count": len(matrix_definition["routes"]),
        "execution_mode": "rehydrate_from_v6_execution_and_construct_refined_fusion_support_ablation_cell",
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_ready_to_execute": True,
        "selected_cells": [cell["cell_id"] for cell in cells],
        "selected_routes": matrix_definition["routes"],
        "fusion_mode": matrix_definition["fusion_mode"],
    }
    write_json(output_dir / "next_axis_after_v6_matrix_execution_selection.json", selection)
    write_json(output_dir / "next_axis_after_v6_matrix_execution_plan.json", plan)
    write_json(output_dir / "next_axis_after_v6_matrix_execution_readiness_summary.json", readiness)

    outputs_dir = output_dir / "next_axis_after_v6_matrix_execution_outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    copy_artifact(v6_execution_dir / "next_axis_after_v5_matrix_route_b_summary.json", output_dir / "next_axis_after_v6_matrix_route_b_summary.json")
    copy_artifact(v6_execution_dir / "next_axis_after_v5_matrix_route_c_summary.json", output_dir / "next_axis_after_v6_matrix_route_c_summary.json")
    copy_artifact(v6_execution_dir / "next_axis_after_v5_matrix_route_b_only_ablation_summary.json", output_dir / "next_axis_after_v6_matrix_route_b_only_ablation_summary.json")
    copy_artifact(v6_execution_dir / "next_axis_after_v5_matrix_route_c_only_ablation_summary.json", output_dir / "next_axis_after_v6_matrix_route_c_only_ablation_summary.json")
    copy_artifact(v6_execution_dir / "next_axis_after_v5_matrix_fusion_summary.json", output_dir / "next_axis_after_v6_matrix_fusion_summary.json")
    copy_artifact(v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_candidate_summary.json", output_dir / "next_axis_after_v6_matrix_fusion_cell_candidate_summary.json")
    copy_artifact(v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_summary.json", output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_summary.json")
    copy_artifact(v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_ablation_summary.json", output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_ablation_summary.json")
    copy_artifact(v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_support_sweep_summary.json", output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_support_sweep_summary.json")

    route_b_score = float(v6_metrics["route_b_mean_prediction_score"])
    route_c_score = float(v6_metrics["route_c_mean_prediction_score"])
    candidate_score = float(v6_metrics["fusion_cell_candidate_score"])
    refined_score = float(v6_metrics["fusion_cell_refined_score"])
    refined_ablation_score = float(v6_metrics["fusion_cell_refined_ablation_score"])
    support_sweep_score = float(v6_metrics["fusion_cell_refined_support_sweep_score"])
    retained_ratio_vs_refined = float(v6_metrics["fusion_cell_refined_support_sweep_retained_ratio"])
    retained_refinement_ratio = float(v6_metrics["fusion_cell_refined_support_sweep_retained_refinement_ratio"])
    support_stability_penalty = float(v6_metrics["fusion_cell_refined_support_penalty"])
    refined_delta = float(v6_metrics["fusion_cell_refined_delta"])
    score_gap = float(v6_metrics["fusion_cell_score_gap"])
    shared_base_samples = int(v6_metrics["shared_base_samples"])

    support_residual = max(support_sweep_score - refined_ablation_score, 0.0)
    support_ablation_score = max(support_sweep_score - support_residual, 0.0)
    retained_ratio_vs_support_sweep = (
        support_ablation_score / support_sweep_score if support_sweep_score else 0.0
    )
    retained_ratio_vs_refined = support_ablation_score / refined_score if refined_score else 0.0
    support_ablation_gap_vs_candidate = support_ablation_score - candidate_score

    fusion_refined_support_ablation_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "cell_id": "dataset0_model0_fusion_cell_refined_support_ablation_explicit",
        "fusion_mode": "refined_fusion_support_ablation_cell",
        "base_matrix": "next_axis_after_v5_real_experiment_matrix_v6",
        "source_fusion_summary": str((v6_execution_dir / "next_axis_after_v5_matrix_fusion_summary.json").resolve()),
        "source_fusion_cell_candidate_summary": str((v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_candidate_summary.json").resolve()),
        "source_fusion_cell_refined_summary": str((v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_summary.json").resolve()),
        "source_fusion_cell_refined_ablation_summary": str(
            (v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_ablation_summary.json").resolve()
        ),
        "source_fusion_cell_refined_support_sweep_summary": str(
            (v6_execution_dir / "next_axis_after_v5_matrix_fusion_cell_refined_support_sweep_summary.json").resolve()
        ),
        "shared_base_samples": shared_base_samples,
        "route_b_mean_prediction_score": route_b_score,
        "route_c_mean_prediction_score": route_c_score,
        "candidate_signal_score": candidate_score,
        "refined_signal_score": refined_score,
        "refined_ablation_signal_score": refined_ablation_score,
        "support_sweep_signal_score": support_sweep_score,
        "support_stability_penalty": support_stability_penalty,
        "support_residual_removed": support_residual,
        "support_ablation_rule": "drop_support_retained_residual_from_support_sweep_signal",
        "support_ablation_signal_score": support_ablation_score,
        "retained_information_ratio_vs_support_sweep": retained_ratio_vs_support_sweep,
        "retained_information_ratio_vs_refined": retained_ratio_vs_refined,
        "retained_refinement_ratio": retained_refinement_ratio,
        "support_ablation_gap_vs_candidate": support_ablation_gap_vs_candidate,
        "value_add": [
            "This support-ablation cell estimates how much refined fusion signal survives after the support-retained residual is explicitly removed from the support-sweep signal.",
            "It makes support-focused isolation inspectable without yet jumping to a heavier model or dataset axis.",
        ],
        "limitations": [
            "Still derived from the same local curated split and lightweight model.",
            "Still a contract-level support-isolation artifact rather than a trained fusion classifier.",
        ],
    }
    write_json(
        output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_support_ablation_summary.json",
        fusion_refined_support_ablation_summary,
    )

    registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cells": [cell["cell_id"] for cell in cells],
        "artifacts": {
            "route_b_summary": str((output_dir / "next_axis_after_v6_matrix_route_b_summary.json").resolve()),
            "route_c_summary": str((output_dir / "next_axis_after_v6_matrix_route_c_summary.json").resolve()),
            "route_b_ablation_summary": str((output_dir / "next_axis_after_v6_matrix_route_b_only_ablation_summary.json").resolve()),
            "route_c_ablation_summary": str((output_dir / "next_axis_after_v6_matrix_route_c_only_ablation_summary.json").resolve()),
            "fusion_summary": str((output_dir / "next_axis_after_v6_matrix_fusion_summary.json").resolve()),
            "fusion_cell_candidate_summary": str((output_dir / "next_axis_after_v6_matrix_fusion_cell_candidate_summary.json").resolve()),
            "fusion_cell_refined_summary": str((output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_summary.json").resolve()),
            "fusion_cell_refined_ablation_summary": str((output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_ablation_summary.json").resolve()),
            "fusion_cell_refined_support_sweep_summary": str((output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_support_sweep_summary.json").resolve()),
            "fusion_cell_refined_support_ablation_summary": str((output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_support_ablation_summary.json").resolve()),
        },
    }
    metrics = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "route_b_rows": route_b_summary["num_rows"],
        "route_c_rows": route_c_summary["num_rows"],
        "route_b_only_ablation_rows": route_b_ablation_summary["num_rows"],
        "route_c_only_ablation_rows": route_c_ablation_summary["num_rows"],
        "route_b_mean_prediction_score": route_b_score,
        "route_c_mean_prediction_score": route_c_score,
        "fusion_summary_present": True,
        "fusion_cell_candidate_executed": True,
        "fusion_cell_candidate_score": candidate_score,
        "fusion_cell_refined_executed": True,
        "fusion_cell_refined_score": refined_score,
        "fusion_cell_refined_ablation_executed": True,
        "fusion_cell_refined_ablation_score": refined_ablation_score,
        "fusion_cell_refined_support_sweep_executed": True,
        "fusion_cell_refined_support_sweep_score": support_sweep_score,
        "fusion_cell_refined_support_sweep_retained_ratio": float(v6_metrics["fusion_cell_refined_support_sweep_retained_ratio"]),
        "fusion_cell_refined_support_sweep_retained_refinement_ratio": retained_refinement_ratio,
        "fusion_cell_refined_support_penalty": support_stability_penalty,
        "fusion_cell_refined_support_ablation_executed": True,
        "fusion_cell_refined_support_ablation_score": support_ablation_score,
        "fusion_cell_refined_support_ablation_retained_ratio": retained_ratio_vs_support_sweep,
        "fusion_cell_refined_support_ablation_retained_ratio_vs_refined": retained_ratio_vs_refined,
        "fusion_cell_refined_support_residual": support_residual,
        "fusion_cell_refined_delta": refined_delta,
        "fusion_cell_score_gap": score_gap,
        "shared_base_samples": shared_base_samples,
        "executed_cell_count": len(cells),
        "ablation_cell_count": 4,
        "explicit_fusion_cell_count": 5,
    }
    cell_metric_rows = [
        {
            "cell_id": "dataset0_model0_routes_b_c_core",
            "cell_role": "core_route_bundle",
            "enabled_routes": "route_b|route_c",
            "rows": route_b_summary["num_rows"],
            "shared_base_samples": shared_base_samples,
            "signal_value": "",
        },
        {
            "cell_id": "dataset0_model0_route_b_only_ablation",
            "cell_role": "ablation_more_natural_only",
            "enabled_routes": "route_b_only_ablation",
            "rows": route_b_ablation_summary["num_rows"],
            "shared_base_samples": route_b_ablation_summary["num_base_samples"],
            "signal_value": route_b_ablation_summary["mean_prediction_score"],
        },
        {
            "cell_id": "dataset0_model0_route_c_only_ablation",
            "cell_role": "ablation_truth_leaning_only",
            "enabled_routes": "route_c_only_ablation",
            "rows": route_c_ablation_summary["num_rows"],
            "shared_base_samples": route_c_ablation_summary["num_base_samples"],
            "signal_value": route_c_ablation_summary["mean_prediction_score"],
        },
        {
            "cell_id": "dataset0_model0_fusion_summary_baseline",
            "cell_role": "baseline_summary_style",
            "enabled_routes": "fusion_summary",
            "rows": fusion_summary["shared_base_samples"],
            "shared_base_samples": fusion_summary["shared_base_samples"],
            "signal_value": "",
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_candidate_explicit",
            "cell_role": "explicit_candidate_style",
            "enabled_routes": "fusion_cell_candidate",
            "rows": fusion_candidate_summary["shared_base_samples"],
            "shared_base_samples": fusion_candidate_summary["shared_base_samples"],
            "signal_value": fusion_candidate_summary["candidate_signal_score"],
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_explicit",
            "cell_role": "explicit_refined_style",
            "enabled_routes": "fusion_cell_refined",
            "rows": fusion_refined_summary["shared_base_samples"],
            "shared_base_samples": fusion_refined_summary["shared_base_samples"],
            "signal_value": fusion_refined_summary["refined_signal_score"],
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_ablation_explicit",
            "cell_role": "explicit_refined_ablation_style",
            "enabled_routes": "fusion_cell_refined_ablation",
            "rows": fusion_refined_ablation_summary["shared_base_samples"],
            "shared_base_samples": fusion_refined_ablation_summary["shared_base_samples"],
            "signal_value": fusion_refined_ablation_summary["ablated_signal_score"],
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_support_sweep_explicit",
            "cell_role": "explicit_refined_support_sweep_style",
            "enabled_routes": "fusion_cell_refined_support_sweep",
            "rows": fusion_refined_support_sweep_summary["shared_base_samples"],
            "shared_base_samples": fusion_refined_support_sweep_summary["shared_base_samples"],
            "signal_value": fusion_refined_support_sweep_summary["support_sweep_signal_score"],
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_support_ablation_explicit",
            "cell_role": "explicit_refined_support_ablation_style",
            "enabled_routes": "fusion_cell_refined_support_ablation",
            "rows": fusion_refined_support_ablation_summary["shared_base_samples"],
            "shared_base_samples": fusion_refined_support_ablation_summary["shared_base_samples"],
            "signal_value": fusion_refined_support_ablation_summary["support_ablation_signal_score"],
        },
    ]
    preview_rows = [
        {
            "cell_id": "dataset0_model0_fusion_summary_baseline",
            "route": "fusion_summary",
            "summary_path": str((output_dir / "next_axis_after_v6_matrix_fusion_summary.json").resolve()),
            "rows": fusion_summary["shared_base_samples"],
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_candidate_explicit",
            "route": "fusion_cell_candidate",
            "summary_path": str((output_dir / "next_axis_after_v6_matrix_fusion_cell_candidate_summary.json").resolve()),
            "rows": fusion_candidate_summary["shared_base_samples"],
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_explicit",
            "route": "fusion_cell_refined",
            "summary_path": str((output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_summary.json").resolve()),
            "rows": fusion_refined_summary["shared_base_samples"],
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_ablation_explicit",
            "route": "fusion_cell_refined_ablation",
            "summary_path": str((output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_ablation_summary.json").resolve()),
            "rows": fusion_refined_ablation_summary["shared_base_samples"],
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_support_sweep_explicit",
            "route": "fusion_cell_refined_support_sweep",
            "summary_path": str((output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_support_sweep_summary.json").resolve()),
            "rows": fusion_refined_support_sweep_summary["shared_base_samples"],
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_support_ablation_explicit",
            "route": "fusion_cell_refined_support_ablation",
            "summary_path": str((output_dir / "next_axis_after_v6_matrix_fusion_cell_refined_support_ablation_summary.json").resolve()),
            "rows": fusion_refined_support_ablation_summary["shared_base_samples"],
        },
    ]
    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cells": [cell["cell_id"] for cell in cells],
        "executed_layers": [
            "route_b",
            "route_c",
            "fusion_summary",
            "route_b_only_ablation",
            "route_c_only_ablation",
            "fusion_cell_candidate",
            "fusion_cell_refined",
            "fusion_cell_refined_ablation",
            "fusion_cell_refined_support_sweep",
            "fusion_cell_refined_support_ablation",
        ],
        "executed_cell_count": len(cells),
        "notes": [
            "This v7 matrix execution promotes fusion_cell_refined_support_ablation into an explicit execution artifact.",
            "fusion_summary, fusion_cell_candidate, fusion_cell_refined, fusion_cell_refined_ablation, and fusion_cell_refined_support_sweep remain available as comparison baselines.",
        ],
    }
    write_json(output_dir / "next_axis_after_v6_matrix_execution_registry.json", registry)
    write_json(output_dir / "next_axis_after_v6_matrix_execution_metrics.json", metrics)
    write_json(output_dir / "next_axis_after_v6_matrix_execution_run_summary.json", run_summary)
    write_csv(output_dir / "next_axis_after_v6_matrix_cell_metrics.csv", cell_metric_rows)
    (output_dir / "next_axis_after_v6_matrix_execution_preview.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=True) for row in preview_rows) + "\n",
        encoding="utf-8",
    )
    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "next_axis_after_v6_matrix_execution_selection.json").resolve()),
            "plan": str((output_dir / "next_axis_after_v6_matrix_execution_plan.json").resolve()),
            "readiness": str((output_dir / "next_axis_after_v6_matrix_execution_readiness_summary.json").resolve()),
            "registry": str((output_dir / "next_axis_after_v6_matrix_execution_registry.json").resolve()),
            "run_summary": str((output_dir / "next_axis_after_v6_matrix_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "next_axis_after_v6_matrix_execution_metrics.json").resolve()),
        },
    }
