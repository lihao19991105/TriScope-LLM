"""Execution-gate checks for DualScope experiment tasks.

The gate is intentionally narrow: it only enforces concrete execution
evidence for tasks that are declared as execution-required. Planning tasks
continue to be handled by the normal queue and merge gates.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscope/experiment-execution-gate/v1"

RESPONSE_GENERATION_REPAIR_TASK = "dualscope-qwen2p5-7b-response-generation-repair"
ALPACA_MAIN_SLICE_RESPONSE_TASK = "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation"
ALPACA_MAIN_SLICE_RESPONSE_REPAIR_TASK = "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair"
ALPACA_MAIN_SLICE_RESPONSE_DEPENDENCY_REPAIR_TASK = (
    "dualscope-qwen2p5-7b-alpaca-main-slice-response-dependency-repair"
)
VALID_BLOCKER_TYPES = {
    "oom",
    "model_load_failure",
    "cuda_error",
    "cuda_unavailable",
    "cuda_unavailable_cpu_generation_disabled",
    "torch_cuda_unavailable",
    "accelerate_unavailable",
    "missing_dependency",
    "logprob_unavailable",
    "missing_input",
    "runtime_error",
}
EXECUTION_REQUIRED_TASKS = {
    RESPONSE_GENERATION_REPAIR_TASK,
    ALPACA_MAIN_SLICE_RESPONSE_TASK,
    ALPACA_MAIN_SLICE_RESPONSE_REPAIR_TASK,
    ALPACA_MAIN_SLICE_RESPONSE_DEPENDENCY_REPAIR_TASK,
}


@dataclass(frozen=True)
class RequiredArtifactSpec:
    response_paths: tuple[Path, ...]
    blocker_paths: tuple[Path, ...]


REQUIRED_ARTIFACTS: dict[str, RequiredArtifactSpec] = {
    RESPONSE_GENERATION_REPAIR_TASK: RequiredArtifactSpec(
        response_paths=(
            Path("outputs/dualscope_qwen2p5_7b_response_generation_repair/default/response_generation_repair_responses.jsonl"),
            Path("outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default/qwen2p5_7b_first_slice_responses.jsonl"),
            Path(
                "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default/"
                "dualscope_qwen2p5_7b_first_slice_response_generation_rows.jsonl"
            ),
        ),
        blocker_paths=(
            Path("outputs/dualscope_qwen2p5_7b_response_generation_repair/default/response_generation_repair_blockers.json"),
            Path("outputs/dualscope_qwen2p5_7b_response_generation_repair/default/qwen2p5_7b_blocker.json"),
        ),
    ),
    ALPACA_MAIN_SLICE_RESPONSE_TASK: RequiredArtifactSpec(
        response_paths=(
            Path(
                "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/"
                "qwen2p5_7b_alpaca_main_slice_responses.jsonl"
            ),
            Path(
                "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/"
                "qwen2p5_7b_alpaca_main_slice_response_rows.jsonl"
            ),
        ),
        blocker_paths=(
            Path("outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/blockers.json"),
            Path(
                "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/"
                "qwen2p5_7b_alpaca_main_slice_response_generation_blockers.json"
            ),
        ),
    ),
    ALPACA_MAIN_SLICE_RESPONSE_REPAIR_TASK: RequiredArtifactSpec(
        response_paths=(
            Path(
                "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default/"
                "qwen2p5_7b_alpaca_main_slice_response_generation_repair_responses.jsonl"
            ),
            Path(
                "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/"
                "qwen2p5_7b_alpaca_main_slice_responses.jsonl"
            ),
        ),
        blocker_paths=(
            Path(
                "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default/"
                "qwen2p5_7b_alpaca_main_slice_response_generation_repair_blockers.json"
            ),
            Path("outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default/blockers.json"),
        ),
    ),
    ALPACA_MAIN_SLICE_RESPONSE_DEPENDENCY_REPAIR_TASK: RequiredArtifactSpec(
        response_paths=(
            Path(
                "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default/"
                "qwen2p5_7b_alpaca_main_slice_response_generation_repair_responses.jsonl"
            ),
            Path(
                "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/"
                "qwen2p5_7b_alpaca_main_slice_responses.jsonl"
            ),
        ),
        blocker_paths=(
            Path(
                "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_dependency_repair/default/"
                "dependency_repair_blockers.json"
            ),
            Path(
                "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default/"
                "qwen2p5_7b_alpaca_main_slice_response_generation_repair_blockers.json"
            ),
            Path("outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default/blockers.json"),
        ),
    ),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def count_jsonl_rows(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return sum(1 for line in handle if line.strip())
    except OSError:
        return 0


def _row_has_real_response(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    if payload.get("blocked") is True or payload.get("generation_blocked") is True:
        return False
    if str(payload.get("status") or "").strip().lower() in {"blocked", "failed", "error"}:
        return False
    for key in ("model_response", "response", "generated_text", "output_text", "text"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return True
    return False


def count_real_response_jsonl_rows(path: Path) -> int:
    count = 0
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if _row_has_real_response(payload):
                    count += 1
    except OSError:
        return 0
    return count


def _normalize_blocker_type(value: Any) -> str:
    if isinstance(value, str):
        return value.strip().lower()
    return ""


def blocker_type_from_payload(payload: dict[str, Any] | None) -> str:
    if not payload:
        return ""
    direct = _normalize_blocker_type(payload.get("blocker_type"))
    if direct:
        return direct
    blockers = payload.get("blockers")
    if isinstance(blockers, list) and blockers:
        first = blockers[0]
        if isinstance(first, dict):
            for key in ("blocker_type", "kind", "type", "reason"):
                candidate = _normalize_blocker_type(first.get(key))
                if candidate:
                    return candidate
        return _normalize_blocker_type(first)
    for key in ("kind", "type", "reason", "error_type"):
        candidate = _normalize_blocker_type(payload.get(key))
        if candidate:
            return candidate
    return ""


def classify_change_scope(changed_paths: list[str]) -> dict[str, bool]:
    non_runtime = [
        path
        for path in changed_paths
        if not path.startswith("outputs/")
        and not path.startswith(".tmp/")
        and "__pycache__/" not in path
        and not path.endswith(".pyc")
    ]
    plan_paths = [path for path in non_runtime if path.startswith(".plans/")]
    registry_paths = [path for path in non_runtime if path.startswith(".reports/dualscope_task_verdicts/")]
    docs_paths = [path for path in non_runtime if path.startswith("docs/")]
    return {
        "plan_only_change_detected": bool(non_runtime) and len(plan_paths) == len(non_runtime),
        "registry_only_change_detected": bool(non_runtime) and len(registry_paths) == len(non_runtime),
        "docs_only_change_detected": bool(non_runtime) and len(docs_paths) == len(non_runtime),
    }


def required_artifact_rows(task_id: str, worktree_dir: Path) -> dict[str, Any]:
    spec = REQUIRED_ARTIFACTS.get(task_id)
    if not spec:
        return {
            "task_id": task_id,
            "gate_required": False,
            "response_artifacts": [],
            "blocker_artifacts": [],
        }
    response_rows = []
    for relative in spec.response_paths:
        path = worktree_dir / relative
        row_count = count_real_response_jsonl_rows(path) if path.exists() else 0
        response_rows.append({"path": str(relative), "exists": path.exists(), "row_count": row_count})
    blocker_rows = []
    for relative in spec.blocker_paths:
        path = worktree_dir / relative
        payload = read_json(path) if path.exists() else None
        blocker_rows.append(
            {
                "path": str(relative),
                "exists": path.exists(),
                "blocker_type": blocker_type_from_payload(payload),
                "payload_keys": sorted(payload) if isinstance(payload, dict) else [],
            }
        )
    return {
        "task_id": task_id,
        "gate_required": True,
        "response_artifacts": response_rows,
        "blocker_artifacts": blocker_rows,
    }


def evaluate_experiment_execution_gate(
    *,
    task_id: str,
    worktree_dir: Path,
    changed_paths: list[str] | None = None,
) -> dict[str, Any]:
    gate_required = task_id in EXECUTION_REQUIRED_TASKS
    artifacts = required_artifact_rows(task_id, worktree_dir)
    scope = classify_change_scope(changed_paths or [])
    response_row_count = max([int(row.get("row_count") or 0) for row in artifacts.get("response_artifacts", [])] or [0])
    response_artifact_present = response_row_count > 0
    blocker_types = [
        str(row.get("blocker_type") or "")
        for row in artifacts.get("blocker_artifacts", [])
        if row.get("exists") and row.get("blocker_type")
    ]
    blocker_type = next((item for item in blocker_types if item in VALID_BLOCKER_TYPES), blocker_types[0] if blocker_types else "")
    blocker_artifact_present = bool(blocker_type)
    blocker_type_valid = blocker_type in VALID_BLOCKER_TYPES

    if not gate_required:
        passed = True
        reason = "task_not_execution_required"
    elif response_artifact_present:
        passed = True
        reason = "response_artifact_present"
    elif blocker_artifact_present and blocker_type_valid:
        passed = True
        reason = "explicit_blocker_artifact_present"
    elif blocker_artifact_present:
        passed = False
        reason = f"blocker_type_not_allowed:{blocker_type}"
    else:
        passed = False
        reason = "missing_response_or_blocker_artifacts"

    return {
        "summary_status": "PASS" if passed else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "created_at": utc_now(),
        "task_id": task_id,
        "worktree_dir": str(worktree_dir),
        "gate_required": gate_required,
        "cli_execution_required": gate_required,
        "response_artifact_present": response_artifact_present,
        "response_row_count": response_row_count,
        "blocker_artifact_present": blocker_artifact_present,
        "blocker_type": blocker_type,
        **scope,
        "execution_gate_passed": passed,
        "merge_allowed_by_execution_gate": passed,
        "reason": reason,
        "valid_blocker_types": sorted(VALID_BLOCKER_TYPES),
        "required_artifacts": artifacts,
    }


def render_execution_gate_report(decision: dict[str, Any]) -> str:
    lines = [
        "# DualScope Experiment Execution Gate Report",
        "",
        f"- Task: `{decision.get('task_id')}`",
        f"- Gate required: `{decision.get('gate_required')}`",
        f"- Execution gate passed: `{decision.get('execution_gate_passed')}`",
        f"- Reason: `{decision.get('reason')}`",
        f"- Response row count: `{decision.get('response_row_count')}`",
        f"- Blocker artifact present: `{decision.get('blocker_artifact_present')}`",
        f"- Blocker type: `{decision.get('blocker_type')}`",
        f"- Plan-only change: `{decision.get('plan_only_change_detected')}`",
        f"- Registry-only change: `{decision.get('registry_only_change_detected')}`",
        f"- Docs-only change: `{decision.get('docs_only_change_detected')}`",
        "",
    ]
    return "\n".join(lines)
