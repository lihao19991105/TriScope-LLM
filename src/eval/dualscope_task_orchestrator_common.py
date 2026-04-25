"""Shared helpers for the local DualScope task orchestrator."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_QUEUE_FILE = Path("DUALSCOPE_TASK_QUEUE.md")
DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_task_orchestrator/default")
DEFAULT_PR_STATUS_SUBDIR = "pr_review_status"
RUNTIME_DIRTY_PREFIXES = (
    "outputs/dualscope_autorun_loop/",
    "outputs/dualscope_task_orchestrator/",
    "outputs/dualscope_pr_review_status/",
    "outputs/dualscope_first_slice_real_run_long_compression_status/",
    ".tmp/",
)
RUNTIME_DIRTY_EXACT = {
    "docs/dualscope_autorun_loop_log.md",
    "scripts/codex_exec_full_auto_wrapper.sh",
}


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""


@dataclass
class TaskOrchestratorArgs:
    queue_file: Path
    output_dir: Path
    check_prs: bool
    previous_pr: int | None
    current_pr: int | None
    select_next_task: bool
    write_next_prompt: bool
    status_file: Path | None
    dry_run: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(command: list[str], timeout: int = 90) -> CommandResult:
    env = os.environ.copy()
    env.setdefault("HTTP_PROXY", "http://127.0.0.1:18080")
    env.setdefault("HTTPS_PROXY", "http://127.0.0.1:18080")
    env.setdefault("ALL_PROXY", "http://127.0.0.1:18080")
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=env,
        )
        return CommandResult(command=command, returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
    except FileNotFoundError as exc:
        return CommandResult(command=command, returncode=127, stderr=str(exc))
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            command=command,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or f"Command timed out after {timeout}s.",
        )


def extract_json_queue(markdown: str, queue_file: Path) -> dict[str, Any]:
    match = re.search(r"```json\s*(\{.*?\})\s*```", markdown, flags=re.DOTALL)
    if not match:
        raise ValueError(f"No fenced JSON queue block found in {queue_file}.")
    payload = json.loads(match.group(1))
    tasks = payload.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError(f"Queue file {queue_file} has no tasks list.")
    required_fields = {
        "task_id",
        "purpose",
        "expected_inputs",
        "expected_outputs",
        "branch_name_suggestion",
        "prompt_template",
        "completion_verdicts",
        "next_task_if_validated",
        "next_task_if_partially_validated",
        "next_task_if_not_validated",
    }
    seen: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError(f"Queue file {queue_file} contains a non-object task.")
        missing = sorted(required_fields - set(task))
        if missing:
            raise ValueError(f"Task {task.get('task_id', '<unknown>')} is missing fields: {missing}")
        task_id = str(task["task_id"])
        if task_id in seen:
            raise ValueError(f"Duplicate task_id in queue: {task_id}")
        seen.add(task_id)
    return payload


def load_queue(queue_file: Path) -> dict[str, Any]:
    return extract_json_queue(queue_file.read_text(encoding="utf-8"), queue_file)


def normalize_text(value: Any) -> str:
    return str(value or "").strip()


def lower_set(values: list[Any] | None) -> set[str]:
    return {normalize_text(value).lower() for value in (values or []) if normalize_text(value)}


def extract_verdict(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("final_verdict", "verdict", "decision", "status", "recommended_next_action"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in payload.values():
            nested = extract_verdict(value)
            if nested:
                return nested
    elif isinstance(payload, list):
        for item in payload:
            nested = extract_verdict(item)
            if nested:
                return nested
    return None


def classify_task(task: dict[str, Any]) -> dict[str, Any]:
    verdict_artifacts = [Path(path) for path in task.get("verdict_artifacts") or []]
    completion = task.get("completion_verdicts") if isinstance(task.get("completion_verdicts"), dict) else {}
    validated = lower_set(completion.get("validated"))
    partial = lower_set(completion.get("partially_validated"))
    not_validated = lower_set(completion.get("not_validated"))

    artifact_rows: list[dict[str, Any]] = []
    best_status = "not_started"
    best_verdict: str | None = None
    best_artifact: str | None = None
    rank = {"validated": 3, "partially_validated": 2, "not_validated": 1, "not_started": 0, "unknown_verdict": 0}

    for artifact in verdict_artifacts:
        row: dict[str, Any] = {"path": str(artifact), "exists": artifact.exists()}
        if not artifact.exists():
            artifact_rows.append(row)
            continue
        try:
            payload = read_json(artifact)
            verdict = extract_verdict(payload)
            verdict_key = normalize_text(verdict).lower()
            if verdict_key in validated:
                status = "validated"
            elif verdict_key in partial:
                status = "partially_validated"
            elif verdict_key in not_validated:
                status = "not_validated"
            else:
                status = "unknown_verdict"
            row.update({"verdict": verdict, "status": status})
            if rank[status] > rank[best_status]:
                best_status = status
                best_verdict = verdict
                best_artifact = str(artifact)
        except Exception as exc:  # noqa: BLE001 - artifact scanner must keep running.
            row.update({"status": "read_error", "error": str(exc)})
        artifact_rows.append(row)

    return {
        "task_id": task["task_id"],
        "status": best_status,
        "final_verdict": best_verdict,
        "verdict_artifact": best_artifact,
        "artifact_rows": artifact_rows,
        "next_task_if_validated": task.get("next_task_if_validated"),
        "next_task_if_partially_validated": task.get("next_task_if_partially_validated"),
        "next_task_if_not_validated": task.get("next_task_if_not_validated"),
    }


def scan_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [classify_task(task) for task in tasks]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {
        "summary_status": "PASS",
        "schema_version": "dualscope/completed-task-scan/v1",
        "tasks": rows,
        "counts": counts,
    }


def git_status() -> dict[str, Any]:
    branch_result = run_command(["git", "branch", "--show-current"])
    status_result = run_command(["git", "status", "--porcelain"])
    root_result = run_command(["git", "rev-parse", "--show-toplevel"])
    changed = [line for line in status_result.stdout.splitlines() if line.strip()]
    ignore_runtime_dirty_paths = os.environ.get("DUALSCOPE_IGNORE_RUNTIME_DIRTY_PATHS") == "1"
    dirty_rows = classify_dirty_paths(changed)
    business_dirty = [
        row
        for row in dirty_rows
        if row["classification"] not in {"runtime_artifact", "runtime_tmp", "generated_output", "temporary_wrapper"}
    ]
    runtime_only_dirty = bool(dirty_rows) and not business_dirty
    effective_clean = status_result.returncode == 0 and (
        not changed or (ignore_runtime_dirty_paths and runtime_only_dirty)
    )
    return {
        "branch": branch_result.stdout.strip() if branch_result.returncode == 0 else None,
        "repo_root": root_result.stdout.strip() if root_result.returncode == 0 else None,
        "is_clean": effective_clean,
        "is_git_clean": status_result.returncode == 0 and not changed,
        "ignore_runtime_dirty_paths": ignore_runtime_dirty_paths,
        "runtime_only_dirty_paths": runtime_only_dirty,
        "dirty_path_classification": dirty_rows,
        "changed_paths": changed,
        "status_error": status_result.stderr.strip() if status_result.returncode != 0 else None,
    }


def parse_porcelain_path(line: str) -> str:
    raw_path = line[3:] if len(line) > 3 else line.strip()
    if " -> " in raw_path:
        raw_path = raw_path.rsplit(" -> ", 1)[-1]
    return raw_path.strip().strip('"')


def is_runtime_dirty_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    if normalized in RUNTIME_DIRTY_EXACT:
        return True
    if normalized.endswith(".pyc"):
        return True
    if "__pycache__/" in normalized or normalized.endswith("__pycache__"):
        return True
    return any(normalized.startswith(prefix) for prefix in RUNTIME_DIRTY_PREFIXES)


def classify_dirty_paths(changed: list[str]) -> list[dict[str, str]]:
    rows = []
    for line in changed:
        path = parse_porcelain_path(line)
        if is_runtime_dirty_path(path):
            if path == "scripts/codex_exec_full_auto_wrapper.sh":
                classification = "temporary_wrapper"
            elif path.startswith(".tmp/"):
                classification = "runtime_tmp"
            elif path.startswith("outputs/"):
                classification = "generated_output"
            else:
                classification = "runtime_artifact"
        elif (
            path.startswith(".plans/")
            or path.startswith("src/")
            or path.startswith("scripts/")
            or path.startswith("docs/")
            or path
            in {
                "README.md",
                "AGENTS.md",
                "PLANS.md",
                "DUALSCOPE_MASTER_PLAN.md",
                "DUALSCOPE_TASK_QUEUE.md",
            }
        ):
            classification = "business_change"
        else:
            classification = "unknown_change"
        rows.append({"raw": line, "path": path, "classification": classification})
    return rows


def infer_previous_pr_from_codex_state() -> int | None:
    state_path = Path(".git/codex-pr-state.json")
    if not state_path.exists():
        return None
    try:
        payload = read_json(state_path)
    except Exception:
        return None
    number = payload.get("current_pr_number") if isinstance(payload, dict) else None
    return int(number) if isinstance(number, int) or (isinstance(number, str) and number.isdigit()) else None


def json_from_command(result: CommandResult) -> Any:
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Command failed: {' '.join(result.command)}")
    return json.loads(result.stdout or "null")


def gh_available_status() -> dict[str, Any]:
    available = shutil.which("gh") is not None
    auth = False
    if available:
        auth = run_command(["gh", "auth", "status"]).returncode == 0
    return {"gh_available": available, "gh_authenticated": auth}


def normalize_check_rollup(status_rollup: Any) -> dict[str, Any]:
    fail_conclusions = {"FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE"}
    pending_statuses = {"QUEUED", "IN_PROGRESS", "PENDING", "REQUESTED", "WAITING", "EXPECTED"}
    checks = status_rollup if isinstance(status_rollup, list) else []
    failing = []
    pending = []
    normalized = []
    for check in checks:
        if not isinstance(check, dict):
            continue
        name = check.get("name") or check.get("context") or check.get("workflowName") or "unknown"
        status = normalize_text(check.get("status")).upper()
        conclusion = normalize_text(check.get("conclusion")).upper()
        row = {"name": name, "status": status or None, "conclusion": conclusion or None}
        normalized.append(row)
        if conclusion in fail_conclusions:
            failing.append(row)
        elif not conclusion and status in pending_statuses:
            pending.append(row)
    if failing:
        ci_state = "failing"
    elif pending:
        ci_state = "pending"
    elif normalized:
        ci_state = "success"
    else:
        ci_state = "no_checks"
    return {"ci_state": ci_state, "checks": normalized, "failing_checks": failing, "pending_checks": pending}


def actor_login(item: dict[str, Any]) -> str:
    author = item.get("author")
    if isinstance(author, dict):
        return normalize_text(author.get("login"))
    return ""


def body_text(item: dict[str, Any]) -> str:
    return normalize_text(item.get("body"))


def review_status_from_detail(detail: dict[str, Any], role: str) -> dict[str, Any]:
    reviews = detail.get("reviews") if isinstance(detail.get("reviews"), list) else []
    comments = detail.get("comments") if isinstance(detail.get("comments"), list) else []
    review_decision = normalize_text(detail.get("reviewDecision")).upper()
    requested_changes = 1 if review_decision == "CHANGES_REQUESTED" else 0
    codex_review_requested = False
    codex_review_present = False
    for comment in comments:
        body = body_text(comment).lower()
        author = actor_login(comment).lower()
        codex_review_requested = codex_review_requested or "@codex review" in body
        codex_review_present = codex_review_present or ("codex" in author and "@codex review" not in body)
    for review in reviews:
        state = normalize_text(review.get("state")).upper()
        body = body_text(review).lower()
        author = actor_login(review).lower()
        if state == "CHANGES_REQUESTED":
            requested_changes += 1
        codex_review_requested = codex_review_requested or "@codex review" in body
        codex_review_present = codex_review_present or "codex" in author or "codex review" in body
    if requested_changes:
        review_state = "changes_requested"
    elif codex_review_present:
        review_state = "codex_review_present"
    elif codex_review_requested:
        review_state = "codex_review_requested_waiting"
    elif review_decision in {"REVIEW_REQUIRED", "REVIEW_PENDING"}:
        review_state = "review_pending"
    else:
        review_state = "no_review_requested"
    ci = normalize_check_rollup(detail.get("statusCheckRollup"))
    return {
        "role": role,
        "number": detail.get("number"),
        "title": detail.get("title"),
        "url": detail.get("url"),
        "state": detail.get("state"),
        "headRefName": detail.get("headRefName"),
        "baseRefName": detail.get("baseRefName"),
        "reviewDecision": detail.get("reviewDecision") or "",
        "review_state": review_state,
        "requested_changes_count": requested_changes,
        "whether_codex_review_requested": codex_review_requested,
        "whether_codex_review_present": True if codex_review_present else "unknown",
        "ci_state": ci["ci_state"],
        "failing_checks": ci["failing_checks"],
        "pending_checks": ci["pending_checks"],
        "checks": ci["checks"],
    }


def run_existing_pr_orchestrator(args: TaskOrchestratorArgs, previous_pr: int | None) -> dict[str, Any] | None:
    script = Path("scripts/dualscope_pr_review_orchestrator.py")
    if not script.exists():
        return None
    pr_output_dir = args.output_dir / DEFAULT_PR_STATUS_SUBDIR
    command = ["python3", str(script), "--list-open", "--check-status", "--output-dir", str(pr_output_dir)]
    if args.current_pr is not None:
        command.extend(["--current-pr", str(args.current_pr)])
    if previous_pr is not None:
        command.extend(["--previous-pr", str(previous_pr)])
    result = run_command(command, timeout=120)
    if result.returncode != 0:
        return {
            "source": "existing_pr_review_orchestrator",
            "status": "failed",
            "command": command,
            "stderr": result.stderr[-2000:],
            "stdout": result.stdout[-2000:],
        }
    open_payload = read_json(pr_output_dir / "pr_review_open_prs.json") if (pr_output_dir / "pr_review_open_prs.json").exists() else {}
    status_payload = read_json(pr_output_dir / "pr_review_status.json") if (pr_output_dir / "pr_review_status.json").exists() else {}
    recommendation = (
        read_json(pr_output_dir / "pr_review_recommendation.json")
        if (pr_output_dir / "pr_review_recommendation.json").exists()
        else {}
    )
    return {
        "source": "existing_pr_review_orchestrator",
        "status": "ok",
        "open_prs": open_payload.get("open_prs", []),
        "checked_prs": status_payload.get("checked_prs", []),
        "current_pr": status_payload.get("current_pr"),
        "previous_pr": status_payload.get("previous_pr"),
        "recommendation": recommendation,
        "artifact_dir": str(pr_output_dir),
    }


def gh_fallback_pr_status(args: TaskOrchestratorArgs, previous_pr: int | None) -> dict[str, Any]:
    availability = gh_available_status()
    payload: dict[str, Any] = {
        "source": "gh_fallback",
        "status": "blocked" if not all(availability.values()) else "ok",
        **availability,
        "open_prs": [],
        "checked_prs": [],
        "current_pr": None,
        "previous_pr": None,
        "errors": [],
    }
    if not availability["gh_available"]:
        payload["errors"].append({"kind": "gh_unavailable", "message": "GitHub CLI `gh` is unavailable."})
        return payload
    if not availability["gh_authenticated"]:
        payload["errors"].append({"kind": "gh_auth_required", "message": "GitHub CLI is not authenticated."})
        return payload

    list_fields = "number,title,url,headRefName,baseRefName,reviewDecision,statusCheckRollup"
    detail_fields = "number,title,url,state,reviewDecision,comments,reviews,statusCheckRollup,headRefName,baseRefName,author"
    try:
        open_prs = json_from_command(
            run_command(["gh", "pr", "list", "--state", "open", "--limit", "50", "--json", list_fields], timeout=120)
        )
        payload["open_prs"] = open_prs if isinstance(open_prs, list) else []
    except Exception as exc:  # noqa: BLE001
        payload["errors"].append({"kind": "open_pr_list_failed", "message": str(exc)})

    ordered: list[tuple[int, str]] = []
    if args.current_pr is not None:
        ordered.append((args.current_pr, "current"))
    if previous_pr is not None:
        ordered.append((previous_pr, "previous"))
    seen: set[int] = set()
    for number, role in ordered:
        if number in seen:
            continue
        seen.add(number)
        try:
            detail = json_from_command(run_command(["gh", "pr", "view", str(number), "--json", detail_fields], timeout=120))
            status = review_status_from_detail(detail, role)
            payload["checked_prs"].append(status)
            payload[f"{role}_pr"] = status
        except Exception as exc:  # noqa: BLE001
            payload["errors"].append({"kind": "pr_view_failed", "pr": number, "message": str(exc)})
    return payload


def get_pr_status(args: TaskOrchestratorArgs) -> dict[str, Any]:
    previous_pr = args.previous_pr if args.previous_pr is not None else infer_previous_pr_from_codex_state()
    if not args.check_prs and not args.select_next_task:
        return {
            "source": "not_requested",
            "status": "not_checked",
            "open_prs": [],
            "checked_prs": [],
            "previous_pr": {"number": previous_pr} if previous_pr is not None else None,
            "current_pr": {"number": args.current_pr} if args.current_pr is not None else None,
        }
    existing = run_existing_pr_orchestrator(args, previous_pr)
    if existing is not None and existing.get("status") == "ok":
        return existing
    fallback = gh_fallback_pr_status(args, previous_pr)
    if existing is not None:
        fallback["existing_orchestrator_attempt"] = existing
    return fallback


def task_by_id(tasks: list[dict[str, Any]], task_id: str | None) -> dict[str, Any] | None:
    if task_id is None:
        return None
    return next((task for task in tasks if task.get("task_id") == task_id), None)


def choose_next_task(
    tasks: list[dict[str, Any]],
    completed_scan: dict[str, Any],
    pr_status: dict[str, Any],
    worktree: dict[str, Any],
) -> dict[str, Any]:
    previous_pr = pr_status.get("previous_pr") if isinstance(pr_status.get("previous_pr"), dict) else None
    if previous_pr and (
        previous_pr.get("requested_changes_count", 0) > 0 or previous_pr.get("review_state") == "changes_requested"
    ):
        return {
            "selection_type": "repair_previous_pr",
            "next_task": "repair_previous_pr",
            "selected_task_id": "repair_previous_pr",
            "reason": f"Previous PR #{previous_pr.get('number')} has requested changes.",
            "previous_pr": previous_pr,
            "blockers": [],
        }

    if not worktree.get("is_clean"):
        return {
            "selection_type": "blocked",
            "next_task": None,
            "selected_task_id": None,
            "reason": "Current working tree is not clean; handle local changes before selecting a new task.",
            "blockers": ["working_tree_not_clean"],
            "changed_paths": worktree.get("changed_paths", []),
            "dirty_path_classification": worktree.get("dirty_path_classification", []),
        }

    scan_by_id = {row["task_id"]: row for row in completed_scan.get("tasks", [])}
    for task in tasks:
        task_id = task["task_id"]
        row = scan_by_id.get(task_id, {"status": "not_started"})
        status = row["status"]
        if status == "validated":
            continue
        if status == "partially_validated":
            repair_id = task.get("next_task_if_partially_validated") or task_id
            repair_task = task_by_id(tasks, repair_id)
            repair_status = scan_by_id.get(repair_id, {"status": "not_started"})
            if repair_task and repair_status.get("status") == "validated":
                continue
            return {
                "selection_type": "partial_repair",
                "next_task": repair_id,
                "selected_task_id": repair_id,
                "source_task_id": task_id,
                "reason": f"Task {task_id} is partially validated; selecting its configured repair/compression next step.",
                "task_status": row,
                "task": repair_task,
                "blockers": [],
            }
        if status == "not_validated":
            repair_id = task.get("next_task_if_not_validated") or task_id
            repair_task = task_by_id(tasks, repair_id)
            repair_status = scan_by_id.get(repair_id, {"status": "not_started"})
            if repair_task and repair_status.get("status") == "validated":
                continue
            return {
                "selection_type": "not_validated_repair",
                "next_task": repair_id,
                "selected_task_id": repair_id,
                "source_task_id": task_id,
                "reason": f"Task {task_id} is not validated; selecting its configured blocker-closure next step.",
                "task_status": row,
                "task": repair_task,
                "blockers": [],
            }
        return {
            "selection_type": "queue_task",
            "next_task": task_id,
            "selected_task_id": task_id,
            "reason": f"Task {task_id} has no validated verdict artifact; selecting first incomplete queue task.",
            "task_status": row,
            "task": task,
            "blockers": [],
        }

    return {
        "selection_type": "queue_complete",
        "next_task": None,
        "selected_task_id": None,
        "reason": "All queued tasks have validated verdict artifacts.",
        "blockers": [],
    }


def render_prompt(selection: dict[str, Any], tasks: list[dict[str, Any]], pr_status: dict[str, Any]) -> str:
    if selection.get("selection_type") == "blocked":
        changed = selection.get("changed_paths") or []
        lines = [
            "# DualScope Next Task Prompt",
            "",
            "Do not start a new DualScope task yet.",
            "",
            f"Reason: {selection.get('reason')}",
            "",
            "Handle the current working tree first, then rerun `scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt`.",
            "",
            "Changed paths:",
        ]
        lines.extend(f"- `{path}`" for path in changed[:50])
        lines.append("")
        return "\n".join(lines)

    if selection.get("selection_type") == "repair_previous_pr":
        previous = selection.get("previous_pr") or {}
        return "\n".join(
            [
                "# DualScope Next Task Prompt",
                "",
                "First repair the previous PR before starting any new DualScope queue task.",
                "",
                f"- Previous PR: #{previous.get('number')} {previous.get('url', '')}",
                f"- Review state: {previous.get('review_state')}",
                f"- CI state: {previous.get('ci_state')}",
                "",
                "Required execution:",
                "",
                "1. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and the previous PR review comments.",
                "2. Fix the requested changes on the previous PR branch only.",
                "3. Run focused validation.",
                "4. Commit the repair and use the AGENTS.md GitHub PR Workflow.",
                "5. Do not merge, force push, delete branches, change benchmark truth, change gates, or continue route_c.",
                "",
            ]
        )

    task = selection.get("task")
    if not task:
        task = task_by_id(tasks, selection.get("selected_task_id"))
    if not task:
        return "\n".join(
            [
                "# DualScope Next Task Prompt",
                "",
                f"No direct queue task prompt is available for `{selection.get('selected_task_id')}`.",
                f"Reason: {selection.get('reason')}",
                "",
            ]
        )

    prompt_body = str(task["prompt_template"]).format(task_id=task["task_id"])
    previous_pr = pr_status.get("previous_pr") if isinstance(pr_status.get("previous_pr"), dict) else None
    current_pr = pr_status.get("current_pr") if isinstance(pr_status.get("current_pr"), dict) else None
    lines = [
        "# DualScope Next Task Prompt",
        "",
        f"Task: `{task['task_id']}`",
        f"Suggested branch: `{task['branch_name_suggestion']}`",
        "",
        "## Prompt",
        "",
        prompt_body,
        "",
        "## Expected Inputs",
    ]
    lines.extend(f"- `{item}`" for item in task.get("expected_inputs", []))
    lines.extend(["", "## Expected Outputs"])
    lines.extend(f"- `{item}`" for item in task.get("expected_outputs", []))
    lines.extend(
        [
            "",
            "## PR Context",
            f"- PR status source: `{pr_status.get('source')}`",
            f"- Previous PR: `{previous_pr.get('number') if previous_pr else 'none'}`",
            f"- Current PR: `{current_pr.get('number') if current_pr else 'none'}`",
            "",
            "## Hard Constraints",
            "",
            "- Do not auto merge.",
            "- Do not force push.",
            "- Do not delete branches.",
            "- Do not modify benchmark truth.",
            "- Do not modify gates.",
            "- Do not continue old route_c / 199+ planning.",
            "",
        ]
    )
    return "\n".join(lines)


def render_report(
    queue_status: dict[str, Any],
    completed_scan: dict[str, Any],
    pr_status: dict[str, Any],
    selection: dict[str, Any],
    prompt_path: Path,
) -> str:
    lines = [
        "# DualScope Task Orchestrator Report",
        "",
        f"- Queue file: `{queue_status.get('queue_file')}`",
        f"- Queue tasks: {queue_status.get('task_count')}",
        f"- PR status source: `{pr_status.get('source')}`",
        f"- PR status: `{pr_status.get('status')}`",
        f"- Selection type: `{selection.get('selection_type')}`",
        f"- Next task: `{selection.get('selected_task_id') or selection.get('next_task') or 'none'}`",
        f"- Reason: {selection.get('reason')}",
        f"- Prompt: `{prompt_path}`",
        "",
        "## Queue Scan",
    ]
    for row in completed_scan.get("tasks", []):
        verdict = row.get("final_verdict") or "none"
        lines.append(f"- `{row['task_id']}`: {row['status']} ({verdict})")
    lines.extend(["", "## Open PRs"])
    open_prs = pr_status.get("open_prs") or []
    if open_prs:
        for pr in open_prs:
            lines.append(f"- PR #{pr.get('number')}: {pr.get('headRefName') or pr.get('title')} ({pr.get('url')})")
    else:
        lines.append("- None detected or PR check unavailable.")
    lines.extend(["", "## Safety"])
    lines.extend(
        [
            "- auto_merge: false",
            "- force_push: false",
            "- delete_branch: false",
            "- benchmark_truth_change: false",
            "- gate_change: false",
            "",
        ]
    )
    return "\n".join(lines)


def run_task_orchestrator(args: TaskOrchestratorArgs) -> tuple[int, dict[str, Any]]:
    started_at = utc_now()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    queue = load_queue(args.queue_file)
    tasks = queue["tasks"]
    completed_scan = scan_tasks(tasks)
    worktree = git_status()
    pr_status = get_pr_status(args)
    selection = (
        choose_next_task(tasks, completed_scan, pr_status, worktree)
        if args.select_next_task
        else {
            "selection_type": "not_requested",
            "next_task": None,
            "selected_task_id": None,
            "reason": "Next-task selection was not requested.",
            "blockers": [],
        }
    )
    prompt_path = args.output_dir / "dualscope_next_task_prompt.md"
    prompt = render_prompt(selection, tasks, pr_status) if args.write_next_prompt else "# DualScope Next Task Prompt\n\nPrompt generation was not requested.\n"
    prompt_available = bool(prompt.strip()) and "No direct queue task prompt is available" not in prompt
    if not args.write_next_prompt:
        prompt_available = False
    selection["prompt_available"] = prompt_available
    selection["prompt_path"] = str(prompt_path)

    queue_status = {
        "summary_status": "PASS",
        "schema_version": "dualscope/task-queue-status/v1",
        "queue_file": str(args.queue_file),
        "task_count": len(tasks),
        "task_ids": [task["task_id"] for task in tasks],
        "current_branch": worktree.get("branch"),
        "working_tree_clean": worktree.get("is_clean"),
        "git_working_tree_clean": worktree.get("is_git_clean"),
        "ignore_runtime_dirty_paths": worktree.get("ignore_runtime_dirty_paths"),
        "runtime_only_dirty_paths": worktree.get("runtime_only_dirty_paths"),
        "dirty_path_classification": worktree.get("dirty_path_classification", []),
        "dry_run": args.dry_run,
    }
    summary = {
        "summary_status": "PASS",
        "schema_version": "dualscope/task-orchestrator-summary/v1",
        "started_at": started_at,
        "completed_at": utc_now(),
        "queue_file": str(args.queue_file),
        "output_dir": str(args.output_dir),
        "dry_run": args.dry_run,
        "selected_task_id": selection.get("selected_task_id"),
        "selection_type": selection.get("selection_type"),
        "selection_reason": selection.get("reason"),
        "prompt_path": str(prompt_path),
        "previous_pr": pr_status.get("previous_pr"),
        "current_pr": pr_status.get("current_pr"),
        "dangerous_actions": {
            "auto_merge": False,
            "force_push": False,
            "delete_branch": False,
            "auto_close_pr": False,
            "rewrite_remote": False,
        },
    }

    write_json(args.output_dir / "dualscope_task_queue_status.json", queue_status)
    write_json(args.output_dir / "dualscope_completed_task_scan.json", completed_scan)
    write_json(args.output_dir / "dualscope_open_pr_status.json", pr_status)
    write_json(args.output_dir / "dualscope_next_task_selection.json", selection)
    prompt_path.write_text(prompt, encoding="utf-8")
    write_json(args.output_dir / "dualscope_task_orchestrator_summary.json", summary)
    report = render_report(queue_status, completed_scan, pr_status, selection, prompt_path)
    (args.output_dir / "dualscope_task_orchestrator_report.md").write_text(report, encoding="utf-8")
    status_file = args.status_file
    if status_file is not None:
        write_json(status_file, queue_status)

    return 0, summary
