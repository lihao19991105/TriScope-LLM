"""Compare route_c budget expansion vs selection refinement and materialize a minimal refinement candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-refinement/v1"


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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def build_model_axis_1p5b_route_c_refinement(
    route_c_sparsity_dir: Path,
    route_c_stability_dir: Path,
    route_c_stabilization_dir: Path,
    route_c_execution_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    sparsity_summary = load_json(route_c_sparsity_dir / "route_c_sparsity_analysis_summary.json")
    sparsity_recommendation = load_json(route_c_sparsity_dir / "route_c_sparsity_next_step_recommendation.json")
    stability_summary = load_json(route_c_stability_dir / "route_c_stability_summary.json")
    candidate_summary = load_json(route_c_stabilization_dir / "route_c_balanced_candidate_summary.json")
    execution_rows = load_jsonl(route_c_execution_dir / "route_c_execution_run" / "route_c_v6_dataset.jsonl")

    positive_anchor_rows = [row for row in execution_rows if int(row.get("ground_truth_label", 0)) == 1]
    if len(positive_anchor_rows) != 1:
        raise ValueError("119 currently expects exactly one positive anchor row in the route_c execution dataset.")
    positive_anchor = positive_anchor_rows[0]
    positive_anchor_base_id = str(positive_anchor["base_sample_id"])

    targeted_negatives = [
        row
        for row in execution_rows
        if str(row.get("contract_variant", "")) == "targeted"
        and int(row.get("ground_truth_label", 0)) == 0
        and str(row.get("base_sample_id", "")) != positive_anchor_base_id
    ]
    targeted_negatives = sorted(targeted_negatives, key=lambda row: (str(row.get("query_answer_key", "")), str(row.get("base_sample_id", ""))))

    negative_anchor_base_ids: list[str] = []
    seen_query_keys: set[str] = set()
    for row in targeted_negatives:
        query_key = str(row.get("query_answer_key", ""))
        base_id = str(row.get("base_sample_id", ""))
        if query_key in seen_query_keys:
            continue
        seen_query_keys.add(query_key)
        negative_anchor_base_ids.append(base_id)
        if len(negative_anchor_base_ids) >= 3:
            break
    if len(negative_anchor_base_ids) < 3:
        for row in targeted_negatives:
            base_id = str(row.get("base_sample_id", ""))
            if base_id in negative_anchor_base_ids:
                continue
            negative_anchor_base_ids.append(base_id)
            if len(negative_anchor_base_ids) >= 3:
                break

    refined_base_ids = [positive_anchor_base_id] + negative_anchor_base_ids
    refined_rows = [row for row in execution_rows if str(row.get("base_sample_id", "")) in set(refined_base_ids)]
    refined_class_balance = {
        "label_0": sum(1 for row in refined_rows if int(row.get("ground_truth_label", 0)) == 0),
        "label_1": sum(1 for row in refined_rows if int(row.get("ground_truth_label", 0)) == 1),
    }
    refined_positive_density = (
        float(refined_class_balance["label_1"]) / float(len(refined_rows))
        if refined_rows
        else None
    )
    current_class_balance = sparsity_summary.get("current_class_balance", {})
    current_positive_density = (
        float(current_class_balance.get("label_1", 0) or 0)
        / float((current_class_balance.get("label_0", 0) or 0) + (current_class_balance.get("label_1", 0) or 0))
        if (current_class_balance.get("label_0", 0) or 0) + (current_class_balance.get("label_1", 0) or 0) > 0
        else None
    )

    options_comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "options": [
            {
                "option_name": "budget_expansion",
                "expected_positive_gain": "low",
                "expected_negative_gain": "high",
                "cost_level": "medium",
                "honesty_under_current_evidence": "weak",
                "evidence": {
                    "full_scan_contract_count": candidate_summary.get("full_scan_contract_count"),
                    "full_scan_class_balance": candidate_summary.get("full_scan_class_balance"),
                    "stability_established": stability_summary.get("stability_established"),
                },
                "conclusion": "The current full 140-contract scan already shows only one positive contract, so expanding budget inside the same universe is likely to add mostly negatives.",
            },
            {
                "option_name": "selection_refinement",
                "expected_positive_gain": "density_gain_without_new_positive_count",
                "expected_negative_gain": "controlled",
                "cost_level": "low",
                "honesty_under_current_evidence": "strong",
                "evidence": {
                    "positive_anchor_base_id": positive_anchor_base_id,
                    "current_positive_density": current_positive_density,
                    "refined_positive_density_preview": refined_positive_density,
                },
                "conclusion": "Selection refinement cannot create new positives inside the current universe, but it can preserve the positive anchor while increasing positive density and keeping follow-up execution cheaper.",
            },
        ],
    }
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "recommended_next_step": "selection_refinement_first",
        "why": [
            "117 shows current sparsity is not mainly a parser or threshold problem.",
            "118 confirms the lone positive anchor is stable enough to build around.",
            "The full 140-contract scan already indicates that blind budget expansion would mostly add negatives.",
            "A smaller anchor-preserving subset improves positive density from the current 1/24 to a denser preview candidate without reopening new axes.",
        ],
        "not_recommended_yet": [
            "blind_budget_expansion_first",
            "3b_or_7b_expansion",
            "dataset_axis_expansion",
            "fusion_axis_expansion",
        ],
        "dependencies": {
            "sparsity_recommendation": sparsity_recommendation.get("recommended_next_step"),
            "stability_established": stability_summary.get("stability_established"),
        },
    }

    selection_registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "strategy": "positive_anchor_plus_query_key_diverse_negatives",
        "positive_anchor_base_id": positive_anchor_base_id,
        "negative_anchor_base_ids": negative_anchor_base_ids,
        "refined_base_ids": refined_base_ids,
        "source_execution_dir": str(route_c_execution_dir.resolve()),
        "source_stabilization_dir": str(route_c_stabilization_dir.resolve()),
    }
    refined_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "strategy": selection_registry["strategy"],
        "selected_base_count": len(refined_base_ids),
        "selected_contract_count": len(refined_rows),
        "class_balance": refined_class_balance,
        "current_positive_density": current_positive_density,
        "refined_positive_density": refined_positive_density,
        "density_gain_ratio": (
            refined_positive_density / current_positive_density
            if refined_positive_density is not None and current_positive_density not in {None, 0.0}
            else None
        ),
        "notes": [
            "This is a refinement-oriented preview candidate, not yet a new execution run.",
            "The candidate preserves the lone positive anchor and trims negative-only bases to improve analyzable positive density.",
        ],
    }

    write_json(output_dir / "route_c_refinement_options_comparison.json", options_comparison)
    write_json(output_dir / "route_c_refinement_recommendation.json", recommendation)
    write_json(output_dir / "route_c_refined_selection_registry.json", selection_registry)
    write_jsonl(output_dir / "route_c_refined_candidate_dataset.jsonl", refined_rows)
    write_json(output_dir / "route_c_refined_candidate_summary.json", refined_summary)

    return {
        "summary": refined_summary,
        "output_paths": {
            "comparison": str((output_dir / "route_c_refinement_options_comparison.json").resolve()),
            "recommendation": str((output_dir / "route_c_refinement_recommendation.json").resolve()),
            "selection_registry": str((output_dir / "route_c_refined_selection_registry.json").resolve()),
            "refined_summary": str((output_dir / "route_c_refined_candidate_summary.json").resolve()),
        },
    }
