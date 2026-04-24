"""Post-analysis for DualScope first-slice real-run preflight."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_preflight_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-minimal-first-slice-real-run-preflight-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def post_dualscope_minimal_first_slice_real_run_preflight_analysis(preflight_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_preflight_scope.json",
        "dualscope_first_slice_dataset_path_check.json",
        "dualscope_first_slice_dataset_schema_check.json",
        "dualscope_first_slice_dataset_sliceability_check.json",
        "dualscope_first_slice_model_path_check.json",
        "dualscope_first_slice_tokenizer_load_check.json",
        "dualscope_first_slice_model_config_check.json",
        "dualscope_first_slice_gpu_check.json",
        "dualscope_first_slice_output_dir_check.json",
        "dualscope_first_slice_disk_space_check.json",
        "dualscope_first_slice_stage_artifact_checks.json",
        "dualscope_first_slice_contract_compatibility_check.json",
        "dualscope_first_slice_capability_mode_check.json",
        "dualscope_first_slice_planned_command_consistency_check.json",
        "dualscope_first_slice_py_compile_check.json",
        "dualscope_first_slice_dry_run_config_check.json",
        "dualscope_first_slice_forbidden_expansion_check.json",
        "dualscope_first_slice_preflight_summary.json",
        "dualscope_first_slice_preflight_details.jsonl",
        "dualscope_first_slice_preflight_report.md",
    ]
    missing = [name for name in required if not (preflight_dir / name).exists()]
    summary = _load_json(preflight_dir / "dualscope_first_slice_preflight_summary.json")
    dataset_path = _load_json(preflight_dir / "dualscope_first_slice_dataset_path_check.json")
    dataset_schema = _load_json(preflight_dir / "dualscope_first_slice_dataset_schema_check.json")
    dataset_sliceability = _load_json(preflight_dir / "dualscope_first_slice_dataset_sliceability_check.json")
    model_path = _load_json(preflight_dir / "dualscope_first_slice_model_path_check.json")
    tokenizer = _load_json(preflight_dir / "dualscope_first_slice_tokenizer_load_check.json")
    output_dir_check = _load_json(preflight_dir / "dualscope_first_slice_output_dir_check.json")
    stage_artifacts = _load_json(preflight_dir / "dualscope_first_slice_stage_artifact_checks.json")
    compatibility = _load_json(preflight_dir / "dualscope_first_slice_contract_compatibility_check.json")
    commands = _load_json(preflight_dir / "dualscope_first_slice_planned_command_consistency_check.json")
    py_compile = _load_json(preflight_dir / "dualscope_first_slice_py_compile_check.json")
    dry_run = _load_json(preflight_dir / "dualscope_first_slice_dry_run_config_check.json")
    forbidden = _load_json(preflight_dir / "dualscope_first_slice_forbidden_expansion_check.json")
    capability = _load_json(preflight_dir / "dualscope_first_slice_capability_mode_check.json")

    hard_ready = all(
        [
            model_path["passed"],
            tokenizer["passed"],
            output_dir_check["passed"],
            stage_artifacts["passed"],
            compatibility["passed"],
            commands["passed"],
            py_compile["passed"],
            dry_run["passed"],
            forbidden["passed"],
        ]
    )
    dataset_ready = dataset_path["passed"] and dataset_schema["passed"] and dataset_sliceability["passed"]
    can_validate = not missing and hard_ready and dataset_ready
    partial_external_blocker = not missing and hard_ready and not dataset_ready
    with_logprobs_available = capability.get("with_logprobs_capability") == "available_via_local_logits"
    with_logprobs_unknown_but_fallback_ok = capability.get("with_logprobs_capability") == "unknown" and capability.get("fallback_required") is True

    if can_validate:
        final_verdict = "Minimal first slice real run preflight validated"
        recommendation = "进入 dualscope-minimal-first-slice-real-run"
        basis = [
            "Dataset, model, tokenizer, output, artifacts, compatibility, commands, py_compile, dry-run config, and forbidden-expansion checks passed.",
        ]
    elif partial_external_blocker:
        final_verdict = "Partially validated"
        recommendation = "进入 dualscope-first-slice-preflight-repair"
        basis = [
            "Core code, model/tokenizer, output, stage artifacts, contract compatibility, commands, py_compile, dry-run config, and forbidden-expansion checks passed.",
            "The real Stanford Alpaca first-slice JSONL is missing, so dataset schema and sliceability checks are blocked.",
            (
                "with-logprobs capability is available through local CUDA/logits access; without-logprobs fallback remains explicitly available."
                if with_logprobs_available
                else "with-logprobs capability remains unknown at preflight, but without-logprobs fallback is explicitly available."
            ),
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "进入 dualscope-first-slice-real-run-blocker-closure"
        basis = [
            "A hard preflight prerequisite failed or required artifacts are missing.",
        ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "missing_artifacts": missing,
        "hard_ready": hard_ready,
        "dataset_ready": dataset_ready,
        "partial_external_blocker": partial_external_blocker,
        "with_logprobs_unknown_but_fallback_ok": with_logprobs_unknown_but_fallback_ok,
        "with_logprobs_available": with_logprobs_available,
        "source_summary": summary,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_minimal_first_slice_real_run_preflight_validated__partially_validated__not_validated",
        "primary_basis": basis,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": basis,
        "do_not_do_yet": [
            "start_lora_training_before_dataset_repair",
            "fabricate_dataset",
            "claim_with_logprobs_available_without_backend_evidence",
            "run_full_matrix",
            "continue_route_c_199_plus",
        ],
    }
    write_json(output_dir / "dualscope_first_slice_preflight_analysis_summary.json", analysis_summary)
    write_json(output_dir / "dualscope_first_slice_preflight_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_preflight_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_preflight_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "dualscope_first_slice_preflight_verdict.json").resolve()),
            "recommendation": str((output_dir / "dualscope_first_slice_preflight_next_step_recommendation.json").resolve()),
        },
    }
