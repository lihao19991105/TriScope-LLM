"""Post first real experiment analysis and recommendation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-first-real-experiment-analysis/v1"


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


def build_post_first_real_experiment_analysis(
    cutover_summary_path: Path,
    dry_run_summary_path: Path,
    execution_run_summary_path: Path,
    execution_metrics_path: Path,
    proxy_comparison_summary_path: Path,
    route_b_v6_summary_path: Path,
    route_c_v6_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cutover_summary = load_json(cutover_summary_path)
    dry_run_summary = load_json(dry_run_summary_path)
    execution_run_summary = load_json(execution_run_summary_path)
    execution_metrics = load_json(execution_metrics_path)
    proxy_summary = load_json(proxy_comparison_summary_path)
    route_b_v6_summary = load_json(route_b_v6_summary_path)
    route_c_v6_summary = load_json(route_c_v6_summary_path)

    analysis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "real_execution_established": execution_run_summary.get("summary_status") == "PASS",
        "real_execution_layers": execution_run_summary.get("executed_layers", []),
        "main_takeaway": "The project has now moved from real-experiment cutover readiness into a first actual execution layer, so the next bottleneck is defining the smallest coherent real-experiment matrix rather than extending proxy substrate again.",
    }
    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "proxy_stage": {
            "route_b_rows": route_b_v6_summary["num_rows"],
            "route_c_rows": route_c_v6_summary["num_rows"],
            "continue_proxy_substrate_expansion": proxy_summary["continue_proxy_substrate_expansion"],
        },
        "first_real_stage": {
            "route_b_rows": execution_metrics["route_b_rows"],
            "route_c_rows": execution_metrics["route_c_rows"],
            "shared_base_samples": execution_metrics["shared_base_samples"],
        },
        "added_value": [
            "A first real-experiment-style execution object now exists beyond readiness-only artifacts.",
            "Route B and route C have both been executed under one cutover execution envelope.",
            "The project now has enough evidence to define a minimal next real-experiment matrix.",
        ],
    }
    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_blockers": [
            "Fusion is still represented as a summary/integration layer rather than a fully separate real-experiment classifier path.",
            "The dataset is still a local curated CSQA-style slice rather than a benchmark-grade labeled experiment source.",
            "The current model is still `pilot_distilgpt2_hf`, so realism is improved but still limited.",
        ],
    }
    tradeoff_rows = [
        {
            "candidate_route": "expand_real_execution_matrix",
            "realism": "higher",
            "cost": "medium",
            "readiness": "high",
            "why": "First real execution now exists, so matrix expansion has become the cleanest next step.",
        },
        {
            "candidate_route": "return_to_proxy_v7",
            "realism": "lower",
            "cost": "medium",
            "readiness": "medium",
            "why": "Proxy expansion would add rows, but it no longer addresses the main real-experiment bottleneck.",
        },
        {
            "candidate_route": "larger_model_switch",
            "realism": "higher",
            "cost": "high",
            "readiness": "low",
            "why": "A larger model could help, but it is heavier than needed for the next minimal matrix step.",
        },
    ]
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "bootstrap_minimal_real_experiment_matrix",
        "why_recommended": [
            "The first real-experiment execution now exists, so the next highest-value step is to define the smallest coherent next matrix.",
            "Returning to proxy-only substrate expansion would give less value than consolidating the new real-experiment branch.",
            "A minimal matrix can stay small while still being more experiment-like than the current single-cutover execution.",
        ],
        "why_not_return_to_proxy": [
            "056 already judged proxy substrate expansion to have declining marginal value, and 059 adds direct real-execution evidence on top of that."
        ],
        "minimum_success_standard": [
            "define dataset / model / label / route coverage for the next minimal real-experiment matrix",
            "materialize matrix inputs",
            "prove the next matrix object is bootstrap-ready",
        ],
    }

    write_json(output_dir / "first_real_experiment_analysis_summary.json", analysis)
    write_json(output_dir / "first_real_vs_proxy_comparison.json", comparison)
    write_json(output_dir / "first_real_experiment_blocker_summary.json", blocker_summary)
    write_csv(output_dir / "first_real_experiment_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "first_real_experiment_next_step_recommendation.json", recommendation)
    return {
        "analysis": analysis,
        "recommendation": recommendation,
        "output_paths": {
            "analysis": str((output_dir / "first_real_experiment_analysis_summary.json").resolve()),
            "comparison": str((output_dir / "first_real_vs_proxy_comparison.json").resolve()),
            "blockers": str((output_dir / "first_real_experiment_blocker_summary.json").resolve()),
            "tradeoff": str((output_dir / "first_real_experiment_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "first_real_experiment_next_step_recommendation.json").resolve()),
        },
    }
