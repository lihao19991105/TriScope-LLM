"""Classify DualScope autorun blockers into repairable safety buckets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


BLOCKER_CLASSES: dict[str, dict[str, Any]] = {
    "queue_or_prompt_blocker": {
        "repairability": "yes",
        "auto_repair_allowed": True,
        "description": "Task queue, direct prompt, routing, queue-complete, or verdict matching issue.",
    },
    "artifact_blocker": {
        "repairability": "yes_if_inputs_sufficient",
        "auto_repair_allowed": True,
        "description": "Missing or malformed expected summary, verdict, recommendation, report, schema, or output directory.",
    },
    "code_blocker": {
        "repairability": "yes",
        "auto_repair_allowed": True,
        "description": "Python compile, import, CLI help, missing script, or missing module issue.",
    },
    "pr_workflow_blocker": {
        "repairability": "yes",
        "auto_repair_allowed": True,
        "description": "PR creation, review parsing, safe merge allowlist, existing PR, non-fast-forward, or file-scope false positive.",
    },
    "resource_blocker": {
        "repairability": "partial",
        "auto_repair_allowed": True,
        "description": "Disk, model path/cache, tokenizer/config, GPU/CUDA/OOM, or download issue.",
    },
    "experiment_blocker": {
        "repairability": "partial",
        "auto_repair_allowed": True,
        "description": "Missing responses, logprobs, labels, scores, metric readiness, ASR, or utility evidence.",
    },
    "safety_blocker": {
        "repairability": "no",
        "auto_repair_allowed": False,
        "description": "Requested changes, failing checks, benchmark truth/gate risk, route_c/199+, secret, or credential issue.",
    },
    "unknown_blocker": {
        "repairability": "no",
        "auto_repair_allowed": False,
        "description": "Unclassified blocker; stop for manual triage.",
    },
}

CLASS_PRIORITY = [
    "safety_blocker",
    "resource_blocker",
    "experiment_blocker",
    "pr_workflow_blocker",
    "code_blocker",
    "artifact_blocker",
    "queue_or_prompt_blocker",
    "unknown_blocker",
]


@dataclass(frozen=True)
class ClassifiedBlocker:
    blocker_class: str
    repairable: bool
    repairability: str
    evidence: str
    source: str
    suggested_action: str


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list, tuple)):
        return repr(value)
    return str(value)


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def classify_blocker_text(text: str, source: str = "unknown") -> ClassifiedBlocker:
    lowered = text.lower()
    if _contains_any(
        lowered,
        (
            "requested changes",
            "failing checks",
            "failing ci",
            "benchmark truth",
            "gate change",
            "gate semantic",
            "route_c",
            "199+",
            "secret",
            "credential",
            ".env",
            "private key",
        ),
    ):
        blocker_class = "safety_blocker"
        action = "Stop; do not auto-merge or auto-repair until the safety issue is explicitly resolved."
    elif _contains_any(
        lowered,
        (
            "disk",
            "gpu",
            "cuda",
            "oom",
            "out of memory",
            "model path",
            "missing model",
            "hf_home",
            "huggingface",
            "download failed",
            "tokenizer",
            "config load",
            "gated",
            "auth",
            "license",
        ),
    ):
        blocker_class = "resource_blocker"
        action = "Route to resource readiness repair; never fabricate model, GPU, tokenizer, config, or download success."
    elif _contains_any(
        lowered,
        (
            "model_response",
            "model response",
            "logprob",
            "labels",
            "final_risk_score",
            "metric readiness",
            "asr",
            "utility",
            "fake metrics",
            "response generation",
        ),
    ):
        blocker_class = "experiment_blocker"
        action = "Route to experiment readiness repair; generate real missing artifacts only when dependencies are ready."
    elif _contains_any(
        lowered,
        (
            "pr not created",
            "safe merge",
            "merge gate",
            "allowlist",
            "non-fast-forward",
            "existing pr",
            "file scope",
            "review parsing",
            "codex review",
            "push failed",
        ),
    ):
        blocker_class = "pr_workflow_blocker"
        action = "Route to PR workflow repair while preserving no force push, no branch deletion, and no unrelated merge."
    elif _contains_any(lowered, ("py_compile", "compile", "import error", "no module", "missing script", "missing module", "--help")):
        blocker_class = "code_blocker"
        action = "Route to code health repair and rerun compile/help checks."
    elif _contains_any(
        lowered,
        (
            "missing verdict",
            "no validated verdict",
            "missing summary",
            "missing recommendation",
            "missing report",
            "schema mismatch",
            "missing expected output",
            "expected output directory",
            "artifact",
        ),
    ):
        blocker_class = "artifact_blocker"
        action = "Route to artifact completion repair if required inputs are present."
    elif _contains_any(
        lowered,
        (
            "missing direct prompt",
            "no direct queue task prompt",
            "missing task queue",
            "invalid next_task",
            "queue complete false-negative",
            "verdict mismatch",
            "routing",
            "task_orchestrator",
        ),
    ):
        blocker_class = "queue_or_prompt_blocker"
        action = "Route to queue/prompt/routing repair."
    else:
        blocker_class = "unknown_blocker"
        action = "Stop for manual triage because this blocker is not classified."

    spec = BLOCKER_CLASSES[blocker_class]
    return ClassifiedBlocker(
        blocker_class=blocker_class,
        repairable=bool(spec["auto_repair_allowed"]),
        repairability=str(spec["repairability"]),
        evidence=text[:1200],
        source=source,
        suggested_action=action,
    )


def _blocker_rows(autorun_blockers: dict[str, Any]) -> list[dict[str, Any]]:
    rows = autorun_blockers.get("blockers")
    return rows if isinstance(rows, list) else []


def _selection_evidence(task_selection: dict[str, Any]) -> list[tuple[str, str]]:
    evidence: list[tuple[str, str]] = []
    for key in ("reason", "selection_type", "next_task", "selected_task_id"):
        value = task_selection.get(key)
        if value:
            evidence.append((f"task_selection.{key}", _text(value)))
    status = task_selection.get("task_status")
    if isinstance(status, dict):
        for row in status.get("artifact_rows") or []:
            if isinstance(row, dict) and not row.get("exists", True):
                evidence.append(("task_selection.missing_artifact", f"missing artifact: {_text(row)}"))
        for key in ("status", "final_verdict", "verdict_artifact"):
            value = status.get(key)
            if value:
                evidence.append((f"task_status.{key}", _text(value)))
    for blocker in task_selection.get("blockers") or []:
        evidence.append(("task_selection.blocker", _text(blocker)))
    return evidence


def classify_autorun_blockers(
    autorun_summary: dict[str, Any] | None = None,
    autorun_blockers: dict[str, Any] | None = None,
    task_selection: dict[str, Any] | None = None,
    latest_verdict: dict[str, Any] | None = None,
    latest_pr_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a structured blocker classification payload."""
    autorun_summary = autorun_summary or {}
    autorun_blockers = autorun_blockers or {}
    task_selection = task_selection or {}
    latest_verdict = latest_verdict or {}
    latest_pr_status = latest_pr_status or {}

    classified: list[ClassifiedBlocker] = []
    for blocker in _blocker_rows(autorun_blockers):
        text = _text(blocker)
        classified.append(classify_blocker_text(text, source="autorun_blockers"))

    stop_reason = autorun_summary.get("stop_reason")
    if stop_reason and stop_reason not in {"max_iterations", "dry_run_completed", "queue_complete"}:
        classified.append(classify_blocker_text(str(stop_reason), source="autorun_summary.stop_reason"))

    for source, text in _selection_evidence(task_selection):
        classified.append(classify_blocker_text(text, source=source))

    verdict_text = " ".join(_text(latest_verdict.get(key)) for key in ("verdict", "final_verdict", "summary", "recommendation"))
    if verdict_text.strip():
        classified.append(classify_blocker_text(verdict_text, source="latest_verdict"))

    pr_text = _text(latest_pr_status)
    if pr_text and pr_text != "{}":
        classified.append(classify_blocker_text(pr_text, source="latest_pr_status"))

    if not classified:
        classified.append(
            ClassifiedBlocker(
                blocker_class="unknown_blocker",
                repairable=False,
                repairability="no",
                evidence="No blocker evidence was found in the provided artifacts.",
                source="empty_inputs",
                suggested_action="Stop for manual triage or provide blocker artifacts.",
            )
        )

    primary = min(classified, key=lambda item: CLASS_PRIORITY.index(item.blocker_class))
    classes = sorted({item.blocker_class for item in classified}, key=CLASS_PRIORITY.index)
    repairable = primary.repairable and primary.blocker_class != "safety_blocker"
    stop_reason_if_not_repairable = None if repairable else primary.suggested_action
    human_actions: list[str] = []
    if primary.blocker_class == "resource_blocker":
        human_actions.append("Provide writable disk, GPU driver, model auth, or network access if automatic resource repair cannot clear the blocker.")
    if primary.blocker_class == "safety_blocker":
        human_actions.append("Resolve requested changes/failing checks/dangerous file scope manually before continuing autorun.")
    if primary.blocker_class == "unknown_blocker":
        human_actions.append("Inspect the raw blocker artifacts and add a classifier rule before unattended repair.")

    return {
        "summary_status": "PASS" if repairable else "WARN",
        "schema_version": "dualscope/autorun-blocker-classification/v1",
        "primary_blocker_class": primary.blocker_class,
        "blocker_classes": classes,
        "repairable": repairable,
        "repairability": primary.repairability,
        "auto_repair_allowed": repairable,
        "stop_reason_if_not_repairable": stop_reason_if_not_repairable,
        "classified_blockers": [
            {
                "blocker_class": item.blocker_class,
                "repairable": item.repairable,
                "repairability": item.repairability,
                "source": item.source,
                "evidence": item.evidence,
                "suggested_action": item.suggested_action,
            }
            for item in classified
        ],
        "human_actions": human_actions,
        "safety_constraints": {
            "no_requested_changes_bypass": True,
            "no_failing_checks_bypass": True,
            "no_benchmark_truth_change": True,
            "no_gate_change": True,
            "no_route_c_or_199_plus": True,
            "no_fake_model_or_metrics": True,
        },
    }
