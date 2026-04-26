"""Generate repair task prompts from DualScope autorun blocker classifications."""

from __future__ import annotations

import re
from typing import Any


REPAIR_PREFIX_BY_CLASS = {
    "queue_or_prompt_blocker": "dualscope-queue-routing-repair",
    "artifact_blocker": "dualscope-artifact-completion-repair",
    "code_blocker": "dualscope-code-health-repair",
    "pr_workflow_blocker": "dualscope-pr-workflow-repair",
    "resource_blocker": "dualscope-resource-readiness-repair",
    "experiment_blocker": "dualscope-experiment-readiness-repair",
    "safety_blocker": "dualscope-safety-blocker-manual-closure",
    "unknown_blocker": "dualscope-unknown-blocker-manual-triage",
}


def slugify(value: str | None) -> str:
    text = re.sub(r"[^a-zA-Z0-9._-]+", "-", value or "unknown-task").strip("-").lower()
    return text[:120] or "unknown-task"


def selected_task_id(task_selection: dict[str, Any] | None, fallback: str | None = None) -> str:
    task_selection = task_selection or {}
    return str(task_selection.get("selected_task_id") or task_selection.get("next_task") or fallback or "unknown-task")


def _task_status(task_selection: dict[str, Any] | None) -> dict[str, Any]:
    status = (task_selection or {}).get("task_status")
    return status if isinstance(status, dict) else {}


def return_task_for_class(blocker_class: str, task_selection: dict[str, Any] | None) -> str | None:
    status = _task_status(task_selection)
    if blocker_class in {"artifact_blocker", "queue_or_prompt_blocker", "code_blocker", "pr_workflow_blocker"}:
        return selected_task_id(task_selection)
    if blocker_class in {"resource_blocker", "experiment_blocker"}:
        return status.get("next_task_if_validated") or selected_task_id(task_selection)
    return None


def next_stop_reason(classification: dict[str, Any]) -> str | None:
    if classification.get("repairable"):
        return None
    return classification.get("stop_reason_if_not_repairable") or "Blocker is not repairable by unattended autorun."


def _expected_inputs(blocker_class: str, task_selection: dict[str, Any] | None) -> list[str]:
    selection = task_selection or {}
    inputs = [
        "outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_summary.json",
        "outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_blockers.json",
        "outputs/dualscope_task_orchestrator/default/dualscope_next_task_selection.json",
        "AGENTS.md",
        "PLANS.md",
        "DUALSCOPE_MASTER_PLAN.md",
        "DUALSCOPE_TASK_QUEUE.md",
    ]
    task = selection.get("task")
    if isinstance(task, dict):
        inputs.extend(str(path) for path in task.get("expected_inputs") or [])
        inputs.extend(str(path) for path in task.get("verdict_artifacts") or [])
    if blocker_class == "resource_blocker":
        inputs.extend(["df -h", "nvidia-smi", "models/", "configs/"])
    return list(dict.fromkeys(inputs))


def _expected_outputs(repair_task_id: str, failed_task: str, blocker_class: str) -> list[str]:
    base = repair_task_id.replace("-", "_")
    outputs = [
        f".plans/{repair_task_id}.md",
        f"docs/{base}.md",
        f"outputs/dualscope_autorun_blocker_repair/default/{base}_summary.json",
        f"outputs/dualscope_autorun_blocker_repair/default/{base}_verdict.json",
        f"outputs/dualscope_autorun_blocker_repair/default/{base}_report.md",
    ]
    if blocker_class == "artifact_blocker":
        outputs.append(f"outputs/{failed_task.replace('-', '_')}/default")
    if blocker_class == "code_blocker":
        outputs.extend(["python3 -m py_compile affected Python files", "affected CLI --help outputs"])
    return outputs


def render_repair_prompt(
    repair_task_id: str,
    failed_task: str,
    blocker_class: str,
    classification: dict[str, Any],
    task_selection: dict[str, Any] | None,
) -> str:
    return_to = return_task_for_class(blocker_class, task_selection)
    evidence_lines = []
    for item in classification.get("classified_blockers") or []:
        evidence_lines.append(f"- {item.get('source')}: {item.get('blocker_class')} - {item.get('evidence')}")
    evidence = "\n".join(evidence_lines) or "- No detailed evidence available."
    return f"""Continue DualScope-LLM repair task `{repair_task_id}`.

Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the latest autorun artifacts, and the failed task artifacts first.

Failed or blocked task: `{failed_task}`
Primary blocker class: `{blocker_class}`
Return target after repair: `{return_to}`

## Blocker Evidence
{evidence}

## Repair Scope
- Repair only the blocker class identified above.
- Prefer the smallest artifact, queue, code, PR workflow, resource-readiness, or experiment-readiness change needed to unblock the failed task.
- If required inputs are missing, write an explicit blocker and next manual action instead of fabricating outputs.
- If this is a resource blocker, only configure writable disk/cache/tmp paths, retry allowed downloads, run tokenizer/config checks, lower batch size, or write quantization/GPU-readiness plans when honest.
- If this is an experiment blocker, generate real responses/labels/metrics only when the model/data dependencies are genuinely ready.

## Hard Safety Constraints
- Do not bypass requested changes or failing checks.
- Do not merge PR #14 or unrelated PRs.
- Do not force push, delete branches, reset hard, or rewrite remotes.
- Do not modify benchmark truth or gates.
- Do not continue old route_c or generate 199+.
- Do not fake model paths, model responses, logprobs, labels, review/CI, AUROC, F1, ASR, clean utility, or projected metrics as real results.

## Required Validation
- Run py_compile for any changed Python file.
- Run --help for any changed CLI.
- Run the minimal repair CLI or artifact check if one is added.
- Produce one verdict: `Autorun blocker repair validated`, `Partially validated`, or `Not validated`.
- Follow AGENTS.md PR workflow: feature branch from main, minimal commit, ./scripts/codex-pr.sh, @codex review, no unsafe merge.
"""


def generate_repair_task(
    classification: dict[str, Any],
    task_selection: dict[str, Any] | None = None,
    failed_task_id: str | None = None,
) -> dict[str, Any]:
    blocker_class = str(classification.get("primary_blocker_class") or "unknown_blocker")
    failed_task = selected_task_id(task_selection, fallback=failed_task_id)
    prefix = REPAIR_PREFIX_BY_CLASS.get(blocker_class, REPAIR_PREFIX_BY_CLASS["unknown_blocker"])
    repair_task_id = f"{prefix}-{slugify(failed_task)}"
    repairable = bool(classification.get("repairable"))
    repair_prompt = ""
    if repairable:
        repair_prompt = render_repair_prompt(repair_task_id, failed_task, blocker_class, classification, task_selection)

    return {
        "summary_status": "PASS" if repairable else "WARN",
        "schema_version": "dualscope/autorun-generated-repair-task/v1",
        "repairable": repairable,
        "blocker_class": blocker_class,
        "failed_task_id": failed_task,
        "repair_task_id": repair_task_id if repairable else None,
        "repair_branch_suggestion": f"codex/{slugify(repair_task_id)}" if repairable else None,
        "repair_prompt": repair_prompt,
        "repair_expected_inputs": _expected_inputs(blocker_class, task_selection),
        "repair_expected_outputs": _expected_outputs(repair_task_id, failed_task, blocker_class) if repairable else [],
        "repair_verdicts": [
            "Autorun blocker repair validated",
            "Partially validated",
            "Not validated",
        ],
        "return_to_task_if_validated": return_task_for_class(blocker_class, task_selection) if repairable else None,
        "stop_reason_if_not_repairable": next_stop_reason(classification),
        "safety_constraints": classification.get("safety_constraints", {}),
    }
