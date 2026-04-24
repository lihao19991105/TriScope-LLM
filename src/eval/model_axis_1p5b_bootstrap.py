"""Bootstrap a first 1.5B model-axis probe for the real-experiment matrix."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from src.eval.experiment_bootstrap import evaluate_model_profile, load_yaml


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-bootstrap/v1"
MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
LOCAL_MODEL_DIRNAME = "Qwen2.5-1.5B-Instruct"
REQUIRED_SNAPSHOT_FILES = [
    "config.json",
    "generation_config.json",
    "model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
]


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


def summarize_snapshot(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {
            "path": None,
            "exists": False,
            "is_dir": False,
            "missing_required_files": REQUIRED_SNAPSHOT_FILES,
            "present_required_files": [],
            "total_size_bytes": 0,
        }
    present = [name for name in REQUIRED_SNAPSHOT_FILES if (path / name).exists()]
    missing = [name for name in REQUIRED_SNAPSHOT_FILES if name not in present]
    total_size_bytes = 0
    if path.exists():
        for item in path.rglob("*"):
            if item.is_file():
                total_size_bytes += item.stat().st_size
    return {
        "path": str(path.resolve()),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "missing_required_files": missing,
        "present_required_files": present,
        "total_size_bytes": total_size_bytes,
    }


def discover_local_snapshot(repo_root: Path, configured_local_path: str | None) -> tuple[dict[str, Any], Path | None]:
    home = Path.home()
    hf_cache_root = home / ".cache" / "huggingface" / "hub" / "models--Qwen--Qwen2.5-1.5B-Instruct"
    snapshot_root = hf_cache_root / "snapshots"
    search_candidates: list[tuple[str, Path]] = []
    if configured_local_path:
        search_candidates.append(("configured_local_path", Path(configured_local_path)))
    search_candidates.extend(
        [
            ("project_local_models", repo_root / "local_models" / LOCAL_MODEL_DIRNAME),
            ("home_models", home / "models" / LOCAL_MODEL_DIRNAME),
            ("home_cache_models", home / ".cache" / "models" / LOCAL_MODEL_DIRNAME),
            ("hf_cache_root", hf_cache_root),
        ]
    )
    if snapshot_root.is_dir():
        for snapshot_dir in sorted(snapshot_root.iterdir()):
            if snapshot_dir.is_dir():
                search_candidates.append((f"hf_cache_snapshot:{snapshot_dir.name}", snapshot_dir))

    searched_paths: list[dict[str, Any]] = []
    resolved_path: Path | None = None
    for label, candidate in search_candidates:
        snapshot_summary = summarize_snapshot(candidate)
        snapshot_summary["search_label"] = label
        searched_paths.append(snapshot_summary)
        if (
            resolved_path is None
            and snapshot_summary["exists"]
            and snapshot_summary["is_dir"]
            and not snapshot_summary["missing_required_files"]
        ):
            resolved_path = candidate

    search_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_model_id": MODEL_ID,
        "searched_paths": searched_paths,
        "resolved_snapshot_path": str(resolved_path.resolve()) if resolved_path else None,
        "resolved_from": next(
            (item["search_label"] for item in searched_paths if item.get("path") == (str(resolved_path.resolve()) if resolved_path else None)),
            None,
        ),
    }
    return search_summary, resolved_path


def probe_local_snapshot(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {
            "summary_status": "BLOCKED",
            "schema_version": SCHEMA_VERSION,
            "probe_target": None,
            "config_probe": {"status": "BLOCKED", "error_type": "MissingPath", "message": "No resolved local snapshot path."},
            "tokenizer_probe": {"status": "BLOCKED", "error_type": "MissingPath", "message": "No resolved local snapshot path."},
            "model_probe": {"status": "BLOCKED", "error_type": "MissingPath", "message": "No resolved local snapshot path."},
            "overall_status": "BLOCKED",
        }

    results: dict[str, Any] = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "probe_target": str(path.resolve()),
    }
    for cls, key in [
        (AutoConfig, "config_probe"),
        (AutoTokenizer, "tokenizer_probe"),
        (AutoModelForCausalLM, "model_probe"),
    ]:
        try:
            kwargs = {"local_files_only": True}
            if cls is AutoTokenizer:
                kwargs["use_fast"] = True
            if cls is AutoModelForCausalLM:
                kwargs["trust_remote_code"] = False
            cls.from_pretrained(str(path), **kwargs)
            results[key] = {"status": "PASS", "error_type": None, "message": None}
        except Exception as exc:
            results[key] = {
                "status": "BLOCKED",
                "error_type": type(exc).__name__,
                "message": str(exc).split("\n")[0],
            }
    results["overall_status"] = (
        "PASS"
        if all(results[key]["status"] == "PASS" for key in ("config_probe", "tokenizer_probe", "model_probe"))
        else "BLOCKED"
    )
    return results


def build_model_axis_1p5b_bootstrap(
    recommendation_path: Path,
    current_matrix_definition_path: Path,
    current_matrix_contract_path: Path,
    current_matrix_inputs_dir: Path,
    models_config_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    repo_root = models_config_path.resolve().parents[1]
    recommendation = load_json(recommendation_path)
    current_definition = load_json(current_matrix_definition_path)
    current_contract = load_json(current_matrix_contract_path)
    if recommendation.get("recommended_next_step") != "bootstrap_model_axis_1p5b":
        raise ValueError("105 expects recommendation to request model-axis 1.5B bootstrap.")

    model_config = load_yaml(models_config_path)
    primary_profile_name = "pilot_small_hf"
    fallback_profile_name = "reference"
    if primary_profile_name not in model_config:
        raise ValueError(f"Model profile `{primary_profile_name}` not found in `{models_config_path}`.")
    if fallback_profile_name not in model_config:
        raise ValueError(f"Model profile `{fallback_profile_name}` not found in `{models_config_path}`.")

    primary_profile = evaluate_model_profile(primary_profile_name, model_config[primary_profile_name])
    fallback_profile = evaluate_model_profile(fallback_profile_name, model_config[fallback_profile_name])
    local_search_summary, resolved_snapshot_path = discover_local_snapshot(
        repo_root=repo_root,
        configured_local_path=primary_profile["local_path"],
    )
    local_probe_summary = probe_local_snapshot(resolved_snapshot_path)

    selected_profile = primary_profile
    resolved_local_path = str(resolved_snapshot_path.resolve()) if resolved_snapshot_path else selected_profile["local_path"]
    ready_local = (
        selected_profile["availability_status"] == "available_local"
        and resolved_snapshot_path is not None
        and local_probe_summary["overall_status"] == "PASS"
    )
    ready_run = ready_local
    execution_mode = "ready_local" if ready_local else "config_only_not_ready_local"
    blocking_reasons: list[str] = []
    if not ready_local:
        if selected_profile["availability_status"] != "available_local":
            blocking_reasons.append(f"selected_model_not_local:{selected_profile['availability_status']}")
        if resolved_snapshot_path is None:
            blocking_reasons.append("no_ready_local_1p5b_snapshot")
        elif local_probe_summary["overall_status"] != "PASS":
            blocking_reasons.append("local_snapshot_probe_failed")

    snapshot_resolution = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_model_profile": selected_profile["profile_name"],
        "selected_model_id": selected_profile["model_id"],
        "resolved_snapshot_path": resolved_local_path,
        "resolved_from": local_search_summary.get("resolved_from"),
        "ready_local_after_resolution": ready_local,
        "config_local_path": selected_profile["local_path"],
        "config_matches_resolution": bool(selected_profile["local_path"]) and selected_profile["local_path"] == resolved_local_path,
        "notes": [
            "Project-local snapshots take priority over remote-only model_id resolution for the 1.5B model-axis probe.",
            "This resolution is intentionally scoped to Qwen/Qwen2.5-1.5B-Instruct only.",
        ],
    }
    local_config_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_model_profile": selected_profile["profile_name"],
        "selected_model_id": selected_profile["model_id"],
        "configured_local_path": selected_profile["local_path"],
        "configured_local_path_exists": selected_profile["local_path_exists"],
        "resolved_snapshot_path": resolved_local_path,
        "readiness_status": "ready_local" if ready_local else selected_profile["readiness_status"],
        "availability_status": "available_local" if ready_local else selected_profile["availability_status"],
    }

    candidate_selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selection_strategy": "pick the smallest 1.5B-class profile already present in the repo config surface",
        "selected_profile_name": selected_profile["profile_name"],
        "selected_model_id": selected_profile["model_id"],
        "selected_readiness_status": "ready_local" if ready_local else selected_profile["readiness_status"],
        "selected_availability_status": "available_local" if ready_local else selected_profile["availability_status"],
        "selected_local_path": resolved_local_path,
        "selected_local_path_exists": resolved_snapshot_path is not None,
        "fallback_profile_name": fallback_profile["profile_name"],
        "fallback_model_id": fallback_profile["model_id"],
        "why_selected": [
            "pilot_small_hf is already wired into the repository model registry and matches the requested 1.5B scale.",
            "It minimizes config churn while testing whether the existing matrix contract can transfer beyond pilot_distilgpt2_hf.",
        ],
        "why_not_larger_models": [
            "3B and 7B profiles are placeholder_remote and would add more resource risk than the current probe requires.",
            "The user explicitly asked for a single 1.5B model trial before any broader model-axis expansion.",
        ],
    }
    bootstrap_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": recommendation["recommended_next_step"],
        "matrix_name": "model_axis_1p5b_single_model_probe_v1",
        "base_matrix_name": current_contract["matrix_name"],
        "selected_model_profile": selected_profile["profile_name"],
        "selected_model_id": selected_profile["model_id"],
        "planned_routes": [
            "route_b",
            "route_c",
            "fusion_summary",
            "fusion_cell_candidate",
            "fusion_cell_refined",
        ],
        "planned_focus": "verify that the current real-experiment matrix contract can migrate to one 1.5B-class model without changing the data contract",
        "execution_mode": execution_mode,
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "model_axis_name": bootstrap_plan["matrix_name"],
        "selected_model_profile": selected_profile["profile_name"],
        "selected_model_id": selected_profile["model_id"],
        "ready_local": ready_local,
        "ready_run": ready_run,
        "execution_mode": execution_mode,
        "blocking_reasons": blocking_reasons,
        "route_compatibility": {
            "route_b": "compatible_by_contract",
            "route_c": "compatible_by_contract",
            "fusion_summary": "compatible_by_contract",
            "fusion_cell_candidate": "compatible_by_contract",
            "fusion_cell_refined": "compatible_by_contract",
        },
        "notes": [
            "This bootstrap intentionally keeps the dataset contract unchanged and only probes single-model portability.",
            (
                "The selected 1.5B profile is now wired to a verified local snapshot."
                if ready_local
                else "The selected 1.5B profile is still not ready-local in the current environment."
            ),
        ],
    }
    write_json(output_dir / "model_axis_1p5b_candidate_selection.json", candidate_selection)
    write_json(output_dir / "model_axis_1p5b_bootstrap_plan.json", bootstrap_plan)
    write_json(output_dir / "model_axis_1p5b_readiness_summary.json", readiness_summary)
    write_json(output_dir / "model_axis_1p5b_local_search_summary.json", local_search_summary)
    write_json(output_dir / "model_axis_1p5b_snapshot_resolution.json", snapshot_resolution)
    write_json(output_dir / "model_axis_1p5b_local_probe_summary.json", local_probe_summary)
    write_json(output_dir / "model_axis_1p5b_local_config_summary.json", local_config_summary)

    matrix_definition = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": bootstrap_plan["matrix_name"],
        "base_matrix_name": current_contract["matrix_name"],
        "datasets": current_definition["datasets"],
        "labels": current_definition["labels"],
        "models": [selected_profile["profile_name"]],
        "routes": bootstrap_plan["planned_routes"],
        "fusion_mode": "model_axis_portability_probe_contract",
        "output_expectations": [
            "route_b_summary",
            "route_c_summary",
            "fusion_summary",
            "fusion_cell_candidate_summary",
            "fusion_cell_refined_summary",
            "model_axis_readiness_summary",
        ],
        "expansion_notes": [
            "This is the first deliberate pivot away from same-axis fusion refinement toward a single 1.5B model-axis probe.",
            "The goal is portability validation rather than immediate performance improvement.",
        ],
    }
    write_json(output_dir / "model_axis_1p5b_matrix_definition.json", matrix_definition)

    materialized_dir = output_dir / "materialized_model_axis_1p5b_inputs"
    materialized_dir.mkdir(parents=True, exist_ok=True)
    for name in ["real_experiment_dataset.jsonl", "dataset_manifest.json", "cutover_contract.json"]:
        copy_artifact(current_matrix_inputs_dir / name, materialized_dir / name)
    model_manifest = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "base_model_profile": current_contract["model_contract"]["profile_name"],
        "selected_model_profile": selected_profile["profile_name"],
        "selected_model_id": selected_profile["model_id"],
        "selected_tokenizer_id": selected_profile["tokenizer_id"],
        "selected_backend_type": selected_profile["backend_type"],
        "selected_dtype": selected_profile["dtype"],
        "selected_max_length": selected_profile["max_length"],
        "selected_local_path": resolved_local_path,
        "selected_local_path_exists": resolved_snapshot_path is not None,
        "selected_availability_status": "available_local" if ready_local else selected_profile["availability_status"],
        "selected_readiness_status": "ready_local" if ready_local else selected_profile["readiness_status"],
        "requires_gpu": selected_profile["requires_gpu"],
    }
    write_json(materialized_dir / "model_manifest.json", model_manifest)

    preview = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": matrix_definition["matrix_name"],
        "selected_model_profile": selected_profile["profile_name"],
        "ready_local": ready_local,
        "ready_run": ready_run,
        "planned_routes": matrix_definition["routes"],
    }
    write_json(output_dir / "model_axis_1p5b_preview.json", preview)

    bootstrap_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": matrix_definition["matrix_name"],
        "base_matrix_name": current_contract["matrix_name"],
        "selected_model_profile": selected_profile["profile_name"],
        "selected_model_id": selected_profile["model_id"],
        "ready_local": ready_local,
        "ready_run": ready_run,
        "execution_mode": execution_mode,
        "materialized_inputs_dir": str(materialized_dir.resolve()),
        "route_count": len(matrix_definition["routes"]),
        "dataset_count": len(matrix_definition["datasets"]),
        "model_count": len(matrix_definition["models"]),
    }
    write_json(output_dir / "model_axis_1p5b_bootstrap_summary.json", bootstrap_summary)
    return {
        "summary": bootstrap_summary,
        "output_paths": {
            "candidate_selection": str((output_dir / "model_axis_1p5b_candidate_selection.json").resolve()),
            "plan": str((output_dir / "model_axis_1p5b_bootstrap_plan.json").resolve()),
            "readiness": str((output_dir / "model_axis_1p5b_readiness_summary.json").resolve()),
            "definition": str((output_dir / "model_axis_1p5b_matrix_definition.json").resolve()),
            "summary": str((output_dir / "model_axis_1p5b_bootstrap_summary.json").resolve()),
        },
    }
