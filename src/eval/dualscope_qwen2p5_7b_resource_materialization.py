"""Materialize and audit Qwen2.5-7B resources for the DualScope SCI3 track."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from src.eval.dualscope_qwen2p5_7b_resource_common import (
    DEFAULT_CONDITION_LEVEL_RERUN_DIR,
    DEFAULT_LABELED_SLICE_OUTPUT_DIR,
    DEFAULT_SEED,
    DEFAULT_SOURCE_FIRST_SLICE,
    DEFAULT_TARGET_TEXT,
    DEFAULT_TRIGGER_TEXT,
    QWEN_PLAN_VERDICT_PATH,
    check_model_load_readiness,
    check_transformers_config,
    check_transformers_tokenizer,
    cross_model_candidate_check,
    disk_readiness,
    final_verdict_from_checks,
    gpu_readiness,
    model_local_manifest,
    maybe_build_labeled_pairs,
    maybe_build_target_response_plan,
    try_snapshot_download,
    utc_now,
    write_json,
    write_jsonl,
    write_manual_download_instructions,
)


def build_resource_materialization(
    model_id: str,
    local_model_dir: Path,
    output_dir: Path,
    allow_download: bool,
    revision: Optional[str],
    hf_token_env: str,
    check_tokenizer: bool,
    check_config: bool,
    check_model_load: bool,
    check_gpu: bool,
    check_disk: bool,
    min_free_disk_gb: float,
    max_load_seconds: int,
    dtype: str,
    device_map: str,
    trust_remote_code: bool,
    labeled_pairs_path: Path,
    target_response_plan_dir: Path,
) -> Dict[str, Any]:
    del max_load_seconds  # The current materialization guard does not perform full model loading.
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now()
    details = []

    scope = {
        "schema_version": "dualscope/qwen2p5-7b-resource-scope/v1",
        "task_id": "dualscope-qwen2p5-7b-resource-materialization-and-config",
        "model_id": model_id,
        "local_model_dir": str(local_model_dir),
        "role": "main experimental model",
        "claim_boundary": "Resource readiness only; no response generation, metrics, benchmark truth, or gate changes.",
        "started_at": started_at,
    }
    write_json(output_dir / "dualscope_qwen2p5_7b_resource_scope.json", scope)

    disk = disk_readiness(local_model_dir, min_free_disk_gb) if check_disk else {"ready": True, "summary_status": "SKIPPED"}
    gpu = gpu_readiness() if check_gpu else {"summary_status": "SKIPPED", "ready_for_config_checks": None}
    write_json(output_dir / "dualscope_qwen2p5_7b_disk_readiness.json", disk)
    write_json(output_dir / "dualscope_qwen2p5_7b_gpu_readiness.json", gpu)
    details.append({"event": "disk_readiness", "payload": disk})
    details.append({"event": "gpu_readiness", "payload": gpu})

    source_check = {
        "schema_version": "dualscope/qwen2p5-7b-model-source-check/v1",
        "model_id": model_id,
        "local_model_dir": str(local_model_dir),
        "local_model_dir_exists": local_model_dir.exists(),
        "download_allowed": allow_download,
        "revision": revision or "default",
    }
    write_json(output_dir / "dualscope_qwen2p5_7b_model_source_check.json", source_check)

    download_result, snapshot_path = try_snapshot_download(
        model_id=model_id,
        local_model_dir=local_model_dir,
        revision=revision,
        token_env=hf_token_env,
        allow_download=allow_download,
        disk=disk,
        trust_remote_code=trust_remote_code,
    )
    download_plan = download_result.get("download_plan", {})
    write_json(output_dir / "dualscope_qwen2p5_7b_download_plan.json", download_plan)
    write_json(output_dir / "dualscope_qwen2p5_7b_download_result.json", download_result)
    details.append({"event": "download_result", "payload": download_result})

    manifest = model_local_manifest(local_model_dir, snapshot_path)
    write_json(output_dir / "dualscope_qwen2p5_7b_local_path_manifest.json", manifest)
    resolved_path = manifest.get("resolved_path")

    tokenizer_check = check_transformers_tokenizer(resolved_path, model_id, check_tokenizer, trust_remote_code)
    config_check = check_transformers_config(resolved_path, model_id, check_config, trust_remote_code)
    model_load = check_model_load_readiness(check_model_load, resolved_path, dtype, device_map)
    write_json(output_dir / "dualscope_qwen2p5_7b_tokenizer_check.json", tokenizer_check)
    write_json(output_dir / "dualscope_qwen2p5_7b_config_check.json", config_check)
    write_json(output_dir / "dualscope_qwen2p5_7b_model_load_readiness.json", model_load)
    details.append({"event": "tokenizer_check", "payload": tokenizer_check})
    details.append({"event": "config_check", "payload": config_check})

    data_check = maybe_build_labeled_pairs(
        labeled_pairs=labeled_pairs_path,
        source_file=DEFAULT_SOURCE_FIRST_SLICE,
        output_dir=DEFAULT_LABELED_SLICE_OUTPUT_DIR,
        trigger_text=DEFAULT_TRIGGER_TEXT,
        target_text=DEFAULT_TARGET_TEXT,
        seed=DEFAULT_SEED,
    )
    target_plan_check = maybe_build_target_response_plan(target_response_plan_dir)
    condition_level_check = {
        "path": str(DEFAULT_CONDITION_LEVEL_RERUN_DIR),
        "exists": DEFAULT_CONDITION_LEVEL_RERUN_DIR.exists(),
        "status": "present" if DEFAULT_CONDITION_LEVEL_RERUN_DIR.exists() else "missing_warning",
    }
    cross_model_check = cross_model_candidate_check()
    write_json(output_dir / "dualscope_qwen2p5_7b_data_dependency_check.json", data_check)
    write_json(output_dir / "dualscope_qwen2p5_7b_target_response_plan_check.json", target_plan_check)
    write_json(output_dir / "dualscope_qwen2p5_7b_cross_model_candidate_check.json", cross_model_check)
    details.append({"event": "data_dependency_check", "payload": data_check})
    details.append({"event": "target_response_plan_check", "payload": target_plan_check})
    details.append({"event": "condition_level_check", "payload": condition_level_check})

    final_verdict, blockers = final_verdict_from_checks(
        tokenizer_check=tokenizer_check,
        config_check=config_check,
        disk=disk,
        data_check=data_check,
        target_plan_check=target_plan_check,
        local_manifest=manifest,
    )
    validated = final_verdict == "Qwen2.5-7B resource materialization validated"
    summary_status = "PASS" if final_verdict != "Not validated" else "FAIL"
    summary = {
        "summary_status": summary_status,
        "schema_version": "dualscope/qwen2p5-7b-resource-materialization-summary/v1",
        "started_at": started_at,
        "completed_at": utc_now(),
        "model_id": model_id,
        "local_model_dir": str(local_model_dir),
        "resolved_model_path": resolved_path,
        "download_summary_status": download_result.get("summary_status"),
        "tokenizer_check": tokenizer_check.get("summary_status"),
        "config_check": config_check.get("summary_status"),
        "gpu_ready": gpu.get("ready_for_config_checks"),
        "disk_ready": disk.get("ready"),
        "labeled_pairs_ready": data_check.get("ready"),
        "target_response_plan_ready": target_plan_check.get("ready"),
        "final_verdict": final_verdict,
        "blocker_count": len(blockers),
    }
    verdict = {
        "schema_version": "dualscope/qwen2p5-7b-resource-materialization-verdict/v1",
        "task_id": "dualscope-qwen2p5-7b-resource-materialization-and-config",
        "verdict": final_verdict,
        "final_verdict": final_verdict,
        "validated": validated,
        "partially_validated": final_verdict == "Partially validated",
        "not_validated": final_verdict == "Not validated",
        "blockers": blockers,
    }
    recommendation = {
        "schema_version": "dualscope/qwen2p5-7b-resource-materialization-next-step/v1",
        "final_verdict": final_verdict,
        "next_task": (
            "dualscope-qwen2p5-7b-first-slice-response-generation-plan"
            if validated
            else "dualscope-qwen2p5-7b-resource-materialization-repair"
        ),
    }
    write_json(output_dir / "dualscope_qwen2p5_7b_resource_materialization_summary.json", summary)
    write_json(output_dir / "dualscope_qwen2p5_7b_resource_materialization_verdict.json", verdict)
    write_json(output_dir / "dualscope_qwen2p5_7b_resource_materialization_next_step_recommendation.json", recommendation)
    if blockers:
        write_json(output_dir / "dualscope_qwen2p5_7b_resource_blockers.json", {"blockers": blockers})
        write_manual_download_instructions(
            output_dir / "dualscope_qwen2p5_7b_manual_download_instructions.md",
            model_id,
            local_model_dir,
            blockers,
        )

    qwen_plan_bridge_verdict = {
        "schema_version": "dualscope/qwen2p5-7b-response-plan-bridge-verdict/v1",
        "task_id": "dualscope-qwen2p5-7b-first-slice-response-generation-plan",
        "verdict": "Partially validated" if not validated else "Qwen2.5-7B first-slice response generation plan validated",
        "final_verdict": "Partially validated" if not validated else "Qwen2.5-7B first-slice response generation plan validated",
        "source": "dualscope-qwen2p5-7b-resource-materialization-and-config",
        "reason": "Resource materialization governs whether the response-generation plan can proceed.",
        "resource_verdict": final_verdict,
        "blockers": blockers,
    }
    write_json(QWEN_PLAN_VERDICT_PATH, qwen_plan_bridge_verdict)

    report = render_report(summary, blockers, manifest, disk, gpu, data_check, target_plan_check, cross_model_check)
    (output_dir / "dualscope_qwen2p5_7b_resource_materialization_report.md").write_text(report, encoding="utf-8")
    write_jsonl(output_dir / "dualscope_qwen2p5_7b_resource_materialization_details.jsonl", details)
    return summary


def render_report(
    summary: Dict[str, Any],
    blockers: Any,
    manifest: Dict[str, Any],
    disk: Dict[str, Any],
    gpu: Dict[str, Any],
    data_check: Dict[str, Any],
    target_plan_check: Dict[str, Any],
    cross_model_check: Dict[str, Any],
) -> str:
    lines = [
        "# Qwen2.5-7B Resource Materialization Report",
        "",
        "## Verdict",
        "",
        "- Final verdict: `%s`" % summary.get("final_verdict"),
        "- Model ID: `%s`" % summary.get("model_id"),
        "- Resolved model path: `%s`" % (summary.get("resolved_model_path") or "none"),
        "",
        "## Readiness",
        "",
        "- Disk ready: `%s` (free GB: `%s`)" % (disk.get("ready"), disk.get("free_gb")),
        "- GPU visible: `%s`; RTX 3090 count: `%s`" % (gpu.get("nvidia_smi_available"), gpu.get("rtx_3090_count")),
        "- Tokenizer check: `%s`" % summary.get("tokenizer_check"),
        "- Config check: `%s`" % summary.get("config_check"),
        "- Labeled pairs ready: `%s`" % data_check.get("ready"),
        "- Target response plan ready: `%s`" % target_plan_check.get("ready"),
        "- Local manifest file count: `%s`" % manifest.get("file_count"),
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        for blocker in blockers:
            lines.append("- `%s`: %s" % (blocker.get("kind"), blocker.get("message")))
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Cross-Model Candidates",
            "",
        ]
    )
    for row in cross_model_check.get("candidates", []):
        lines.append("- `%s`: `%s`" % (row.get("model_id"), row.get("status")))
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- No response generation was run.",
            "- No benchmark truth or gate files were modified.",
            "- No AUROC/F1/ASR/clean utility was computed or claimed.",
            "- No gated Llama/Mistral download was attempted.",
            "",
        ]
    )
    return "\n".join(lines)

