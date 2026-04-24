"""First real experiment-style execution builder."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.eval.rerun_route_b_on_labeled_split_v6 import run_route_b_v6
from src.eval.rerun_route_c_on_labeled_split_v6 import run_route_c_v6


SCHEMA_VERSION = "triscopellm/first-real-experiment-execution/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def copy_artifact(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def build_first_real_experiment_execution(
    dry_run_summary_path: Path,
    dry_run_module_status_path: Path,
    execution_contract_path: Path,
    v6_inputs_dir: Path,
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    reasoning_prompt_dir: Path,
    confidence_prompt_dir: Path,
    illumination_prompt_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dry_run_summary = load_json(dry_run_summary_path)
    dry_run_module_status = load_json(dry_run_module_status_path)
    execution_contract = load_json(execution_contract_path)
    if dry_run_summary.get("summary_status") != "PASS":
        raise ValueError("First real execution requires a PASS dry-run summary.")
    if dry_run_module_status.get("summary_status") != "PASS":
        raise ValueError("First real execution requires PASS dry-run module status.")

    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_path": "route_b_plus_route_c_plus_fusion_summary",
        "why_selected": [
            "Dry-run showed that reasoning, confidence, illumination, route B, route C, and fusion mapping all pass on the cutover object.",
            "Running both route B and route C is the smallest honest execution step that moves beyond readiness-only conclusions.",
            "Fusion is represented here as a cross-route execution summary rather than a new full classifier path.",
        ],
        "why_not_route_b_only": ["Route C is equally executable, so B-only would leave avoidable information on the table."],
        "why_not_route_c_only": ["Route B is also executable, so C-only would underuse the stable dual-route setup."],
        "success_standard": [
            "execute route B on the cutover substrate",
            "execute route C on the cutover substrate",
            "emit one integrated first-real execution registry and fusion summary",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "experiment_name": dry_run_summary["experiment_name"],
        "selected_path": selection["selected_path"],
        "input_contract_path": str(execution_contract_path.resolve()),
        "seed": seed,
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "ready_to_execute": True,
        "selected_path": selection["selected_path"],
        "module_status_snapshot": dry_run_module_status["modules"],
    }
    write_json(output_dir / "first_real_execution_selection.json", selection)
    write_json(output_dir / "first_real_execution_plan.json", plan)
    write_json(output_dir / "first_real_execution_readiness_summary.json", readiness)

    execution_root = output_dir / "first_real_execution_outputs"
    route_b_dir = execution_root / "route_b"
    route_c_dir = execution_root / "route_c"

    route_c_result = run_route_c_v6(
        models_config_path=models_config_path,
        reasoning_config_path=reasoning_config_path,
        confidence_config_path=confidence_config_path,
        illumination_config_path=illumination_config_path,
        reasoning_prompt_dir=reasoning_prompt_dir,
        confidence_prompt_dir=confidence_prompt_dir,
        illumination_prompt_dir=illumination_prompt_dir,
        v6_inputs_dir=v6_inputs_dir,
        output_dir=route_c_dir,
        seed=seed,
        label_threshold=label_threshold,
    )
    route_b_result = run_route_b_v6(
        models_config_path=models_config_path,
        reasoning_config_path=reasoning_config_path,
        confidence_config_path=confidence_config_path,
        illumination_config_path=illumination_config_path,
        reasoning_prompt_dir=reasoning_prompt_dir,
        confidence_prompt_dir=confidence_prompt_dir,
        illumination_prompt_dir=illumination_prompt_dir,
        v6_inputs_dir=v6_inputs_dir,
        output_dir=route_b_dir,
        seed=seed,
        label_threshold=label_threshold,
    )

    route_b_summary = load_json(route_b_dir / "route_b_v6_summary.json")
    route_c_summary = load_json(route_c_dir / "route_c_v6_summary.json")
    fusion_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_mode": "cross_route_execution_summary",
        "route_b_rows": route_b_summary["num_rows"],
        "route_c_rows": route_c_summary["num_rows"],
        "shared_base_samples": route_b_summary["num_base_samples"],
        "notes": [
            "This first real fusion artifact summarizes joint B/C availability on the cutover object.",
            "It is not yet a new benchmark-grade fusion classifier.",
        ],
    }

    copy_artifact(route_b_dir / "route_b_v6_summary.json", output_dir / "first_real_route_b_summary.json")
    copy_artifact(route_c_dir / "route_c_v6_summary.json", output_dir / "first_real_route_c_summary.json")
    write_json(output_dir / "first_real_fusion_summary.json", fusion_summary)

    registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_path": selection["selected_path"],
        "artifacts": {
            "route_b_summary": str((output_dir / "first_real_route_b_summary.json").resolve()),
            "route_c_summary": str((output_dir / "first_real_route_c_summary.json").resolve()),
            "fusion_summary": str((output_dir / "first_real_fusion_summary.json").resolve()),
            "route_b_output_dir": str(route_b_dir.resolve()),
            "route_c_output_dir": str(route_c_dir.resolve()),
        },
    }
    metrics = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "route_b_rows": route_b_summary["num_rows"],
        "route_c_rows": route_c_summary["num_rows"],
        "route_b_mean_prediction_score": load_json(route_b_dir / "route_b_v6_logistic_summary.json")["mean_prediction_score"],
        "route_c_mean_prediction_score": load_json(route_c_dir / "route_c_v6_logistic_summary.json")["mean_prediction_score"],
        "shared_base_samples": route_b_summary["num_base_samples"],
    }
    preview = [
        {
            "route": "B",
            "summary_path": str((output_dir / "first_real_route_b_summary.json").resolve()),
            "rows": route_b_summary["num_rows"],
        },
        {
            "route": "C",
            "summary_path": str((output_dir / "first_real_route_c_summary.json").resolve()),
            "rows": route_c_summary["num_rows"],
        },
    ]
    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_path": selection["selected_path"],
        "executed_layers": ["route_b", "route_c", "fusion_summary"],
        "notes": [
            "This is the first real-experiment-style execution on top of the cutover object.",
            "Route B and route C are full executes here; fusion is currently represented as an integrated cross-route summary.",
        ],
    }
    write_json(output_dir / "first_real_execution_registry.json", registry)
    write_json(output_dir / "first_real_execution_metrics.json", metrics)
    write_json(output_dir / "first_real_execution_run_summary.json", run_summary)
    (output_dir / "first_real_execution_preview.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=True) for row in preview) + "\n",
        encoding="utf-8",
    )
    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "first_real_execution_selection.json").resolve()),
            "plan": str((output_dir / "first_real_execution_plan.json").resolve()),
            "readiness": str((output_dir / "first_real_execution_readiness_summary.json").resolve()),
            "registry": str((output_dir / "first_real_execution_registry.json").resolve()),
            "run_summary": str((output_dir / "first_real_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "first_real_execution_metrics.json").resolve()),
            "preview": str((output_dir / "first_real_execution_preview.jsonl").resolve()),
        },
    }
