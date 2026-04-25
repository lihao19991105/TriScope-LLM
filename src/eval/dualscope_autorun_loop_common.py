"""Shared implementation for the local DualScope autorun loop."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_QUEUE_FILE = Path("DUALSCOPE_TASK_QUEUE.md")
DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_autorun_loop/default")
DEFAULT_TASK_ORCHESTRATOR_OUTPUT_DIR = Path("outputs/dualscope_task_orchestrator/default")
DEFAULT_PR_STATUS_OUTPUT_DIR = Path("outputs/dualscope_pr_review_status/default")
DEFAULT_PROXY = "http://127.0.0.1:18080"
FINAL_VERDICTS = {
    "validated": "Autorun loop validated",
    "partial": "Partially validated",
    "not_validated": "Not validated",
}


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""


@dataclass
class AutorunLoopArgs:
    max_iterations: int
    max_minutes: int
    queue_file: Path
    output_dir: Path
    task_orchestrator_output_dir: Path
    pr_status_output_dir: Path
    dry_run: bool
    execute: bool
    codex_bin: str
    stop_on_review_pending: bool
    allow_review_pending_continue: bool
    stop_on_requested_changes: bool
    stop_on_failing_checks: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def proxy_env() -> dict[str, str]:
    env = os.environ.copy()
    env["HTTP_PROXY"] = DEFAULT_PROXY
    env["HTTPS_PROXY"] = DEFAULT_PROXY
    env["ALL_PROXY"] = DEFAULT_PROXY
    return env


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]], append: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with path.open(mode, encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def truncate_text(value: str, limit: int = 4000) -> str:
    if len(value) <= limit:
        return value
    return value[-limit:]


def run_command(command: list[str], timeout: int = 120) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=proxy_env(),
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


def python_bin() -> str:
    candidate = Path(".venv/bin/python")
    return str(candidate) if candidate.exists() else "python3"


def command_row(name: str, result: CommandResult) -> dict[str, Any]:
    return {
        "name": name,
        "command": result.command,
        "returncode": result.returncode,
        "passed": result.returncode == 0,
        "stdout": truncate_text(result.stdout),
        "stderr": truncate_text(result.stderr),
    }


def infer_previous_pr() -> int | None:
    state_file = Path(".git/codex-pr-state.json")
    if not state_file.exists():
        return None
    try:
        payload = read_json(state_file)
    except Exception:
        return None
    value = payload.get("current_pr_number")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def run_preflight() -> dict[str, Any]:
    commands = [
        ("git_status_sb", ["git", "status", "-sb"]),
        ("gh_auth_status", ["gh", "auth", "status"]),
        ("git_remote_v", ["git", "remote", "-v"]),
        ("git_ls_remote_origin_head", ["git", "ls-remote", "origin", "HEAD"]),
    ]
    rows = [command_row(name, run_command(command, timeout=90)) for name, command in commands]
    remote_text = next((row["stdout"] for row in rows if row["name"] == "git_remote_v"), "")
    return {
        "summary_status": "PASS" if all(row["passed"] for row in rows) else "WARN",
        "schema_version": "dualscope/autorun-loop-preflight/v1",
        "proxy": {
            "HTTP_PROXY": DEFAULT_PROXY,
            "HTTPS_PROXY": DEFAULT_PROXY,
            "ALL_PROXY": DEFAULT_PROXY,
        },
        "commands": rows,
        "https_remote_detected": "https://github.com/" in remote_text,
        "ssh_remote_detected": "git@github.com:" in remote_text,
    }


def run_pr_review_orchestrator(args: AutorunLoopArgs, role: str, iteration: int) -> dict[str, Any]:
    script = Path("scripts/dualscope_pr_review_orchestrator.py")
    previous_pr = infer_previous_pr()
    command = [
        python_bin(),
        str(script),
        "--list-open",
        "--check-status",
        "--output-dir",
        str(args.pr_status_output_dir),
    ]
    if previous_pr is not None:
        command.extend(["--previous-pr", str(previous_pr)])
    started = utc_now()
    if not script.exists():
        return {
            "summary_status": "FAIL",
            "role": role,
            "iteration": iteration,
            "started_at": started,
            "completed_at": utc_now(),
            "command": command,
            "returncode": 127,
            "error": "scripts/dualscope_pr_review_orchestrator.py is missing.",
            "checked_prs": [],
            "open_prs": [],
        }
    result = run_command(command, timeout=180)
    status_path = args.pr_status_output_dir / "pr_review_status.json"
    open_path = args.pr_status_output_dir / "pr_review_open_prs.json"
    recommendation_path = args.pr_status_output_dir / "pr_review_recommendation.json"
    status_payload = read_json(status_path) if status_path.exists() else {}
    open_payload = read_json(open_path) if open_path.exists() else {}
    recommendation = read_json(recommendation_path) if recommendation_path.exists() else {}
    return {
        "summary_status": "PASS" if result.returncode == 0 else "FAIL",
        "role": role,
        "iteration": iteration,
        "started_at": started,
        "completed_at": utc_now(),
        "command": command,
        "returncode": result.returncode,
        "stdout": truncate_text(result.stdout),
        "stderr": truncate_text(result.stderr),
        "checked_prs": status_payload.get("checked_prs", []),
        "current_pr": status_payload.get("current_pr"),
        "previous_pr": status_payload.get("previous_pr"),
        "open_prs": open_payload.get("open_prs", []),
        "recommendation": recommendation,
        "artifact_dir": str(args.pr_status_output_dir),
    }


def blockers_from_pr_status(args: AutorunLoopArgs, pr_status: dict[str, Any]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for status in pr_status.get("checked_prs", []) or []:
        number = status.get("number")
        if args.stop_on_requested_changes and (
            status.get("requested_changes_count", 0) > 0 or status.get("review_state") == "changes_requested"
        ):
            blockers.append({"kind": "requested_changes", "pr": number, "message": f"PR #{number} has requested changes."})
        if args.stop_on_failing_checks and status.get("ci_state") == "failing":
            blockers.append({"kind": "failing_checks", "pr": number, "message": f"PR #{number} has failing checks."})
        if (
            args.stop_on_review_pending
            and not args.allow_review_pending_continue
            and status.get("review_state") in {"codex_review_requested_waiting", "review_pending", "no_review_requested"}
        ):
            blockers.append({"kind": "review_pending", "pr": number, "message": f"PR #{number} review is pending."})
    if pr_status.get("summary_status") == "FAIL":
        blockers.append({"kind": "pr_status_unavailable", "message": pr_status.get("error") or "PR status check failed."})
    return blockers


def run_task_orchestrator(args: AutorunLoopArgs, iteration: int) -> dict[str, Any]:
    command = [
        python_bin(),
        "scripts/dualscope_task_orchestrator.py",
        "--queue-file",
        str(args.queue_file),
        "--select-next-task",
        "--write-next-prompt",
        "--dry-run",
        "--output-dir",
        str(args.task_orchestrator_output_dir),
    ]
    result = run_command(command, timeout=180)
    selection_path = args.task_orchestrator_output_dir / "dualscope_next_task_selection.json"
    prompt_path = args.task_orchestrator_output_dir / "dualscope_next_task_prompt.md"
    summary_path = args.task_orchestrator_output_dir / "dualscope_task_orchestrator_summary.json"
    selection = read_json(selection_path) if selection_path.exists() else {}
    summary = read_json(summary_path) if summary_path.exists() else {}
    prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
    return {
        "summary_status": "PASS" if result.returncode == 0 else "FAIL",
        "iteration": iteration,
        "command": command,
        "returncode": result.returncode,
        "stdout": truncate_text(result.stdout),
        "stderr": truncate_text(result.stderr),
        "selection": selection,
        "task_summary": summary,
        "prompt_path": str(prompt_path),
        "prompt_text": prompt,
        "prompt_exists": bool(prompt),
    }


def codex_exec_available(codex_bin: str) -> bool:
    return shutil.which(codex_bin) is not None


def run_codex_exec(args: AutorunLoopArgs, prompt_text: str, iteration: int) -> dict[str, Any]:
    command = [args.codex_bin, "exec", prompt_text]
    started = utc_now()
    if not codex_exec_available(args.codex_bin):
        return {
            "summary_status": "FAIL",
            "iteration": iteration,
            "started_at": started,
            "completed_at": utc_now(),
            "command": command,
            "returncode": 127,
            "codex_exec_available": False,
            "stdout": "",
            "stderr": f"`{args.codex_bin}` is not available on PATH. Install/login to Codex CLI before execute mode.",
        }
    result = run_command(command, timeout=max(60, args.max_minutes * 60))
    return {
        "summary_status": "PASS" if result.returncode == 0 else "FAIL",
        "iteration": iteration,
        "started_at": started,
        "completed_at": utc_now(),
        "command": command[:2] + ["<prompt text>"],
        "returncode": result.returncode,
        "codex_exec_available": True,
        "stdout": truncate_text(result.stdout, 12000),
        "stderr": truncate_text(result.stderr, 12000),
    }


def git_changed_files() -> dict[str, Any]:
    result = run_command(["git", "status", "--porcelain"], timeout=60)
    return {
        "returncode": result.returncode,
        "changed_files": [line for line in result.stdout.splitlines() if line.strip()],
        "stderr": truncate_text(result.stderr),
    }


def append_run_log(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("# DualScope Autorun Loop Log\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            "\n".join(
                [
                    f"## Iteration {row.get('iteration')} - {row.get('timestamp')}",
                    "",
                    f"- selected task: `{row.get('selected_task')}`",
                    f"- PR status before: `{row.get('pr_status_before')}`",
                    f"- codex exec command: `{row.get('codex_exec_command')}`",
                    f"- codex exec exit code: `{row.get('codex_exec_exit_code')}`",
                    f"- PR status after: `{row.get('pr_status_after')}`",
                    f"- blocker: `{row.get('blocker')}`",
                    f"- next action: `{row.get('next_action')}`",
                    "",
                ]
            )
        )


def decide_final_verdict(
    py_artifacts_written: bool,
    dry_run_passed: bool,
    codex_available: bool,
    dangerous_actions: dict[str, bool],
    preflight: dict[str, Any],
    blockers: list[dict[str, Any]],
) -> str:
    if any(dangerous_actions.values()):
        return FINAL_VERDICTS["not_validated"]
    if not py_artifacts_written or not dry_run_passed:
        return FINAL_VERDICTS["not_validated"]
    if blockers:
        return FINAL_VERDICTS["partial"]
    if not codex_available:
        return FINAL_VERDICTS["partial"]
    if preflight.get("ssh_remote_detected") or not preflight.get("https_remote_detected"):
        return FINAL_VERDICTS["partial"]
    return FINAL_VERDICTS["validated"]


def recommendation_for_verdict(verdict: str) -> str:
    if verdict == FINAL_VERDICTS["validated"]:
        return "Run autorun loop in execute mode with max-iterations 2 after confirming current PR review state."
    if verdict == FINAL_VERDICTS["partial"]:
        return "Repair autorun loop environment blocker, then rerun dry-run."
    return "Fix autorun loop implementation before using automated execution."


def render_report(summary: dict[str, Any], blockers: list[dict[str, Any]], selected_tasks: list[dict[str, Any]]) -> str:
    lines = [
        "# DualScope Autorun Loop Report",
        "",
        f"- Verdict: {summary['final_verdict']}",
        f"- Recommendation: {summary['recommendation']}",
        f"- Mode: {summary['mode']}",
        f"- Iterations completed: {summary['iterations_completed']}",
        f"- Stop reason: {summary['stop_reason']}",
        f"- Codex exec available: {summary['codex_exec_available']}",
        "",
        "## Selected Tasks",
    ]
    if selected_tasks:
        for row in selected_tasks:
            lines.append(f"- iteration {row.get('iteration')}: `{row.get('selected_task')}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Blockers"])
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker.get('kind')}: {blocker.get('message')}")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Safety",
            "- auto_merge: false",
            "- force_push: false",
            "- delete_branch: false",
            "- remote_rewrite: false",
            "- ssh_remote_rewrite: false",
            "",
        ]
    )
    return "\n".join(lines)


def render_dry_run_plan(selected_tasks: list[dict[str, Any]], args: AutorunLoopArgs) -> str:
    lines = [
        "# DualScope Autorun Loop Dry-Run Plan",
        "",
        f"- max iterations: {args.max_iterations}",
        f"- max minutes: {args.max_minutes}",
        f"- task orchestrator output: `{args.task_orchestrator_output_dir}`",
        "",
    ]
    for row in selected_tasks:
        lines.extend(
            [
                f"## Iteration {row.get('iteration')}",
                "",
                f"- selected task: `{row.get('selected_task')}`",
                f"- prompt path: `{row.get('prompt_path')}`",
                "",
            ]
        )
    return "\n".join(lines)


def run_autorun_loop(args: AutorunLoopArgs) -> tuple[int, dict[str, Any]]:
    started_at = utc_now()
    start_monotonic = time.monotonic()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    log_path = Path("docs/dualscope_autorun_loop_log.md")
    iterations_path = args.output_dir / "dualscope_autorun_loop_iterations.jsonl"
    selected_tasks_path = args.output_dir / "dualscope_autorun_loop_selected_tasks.jsonl"
    exec_results_path = args.output_dir / "dualscope_autorun_loop_codex_exec_results.jsonl"
    pr_history_path = args.output_dir / "dualscope_autorun_loop_pr_status_history.jsonl"
    for path in [iterations_path, selected_tasks_path, exec_results_path, pr_history_path]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    dangerous_actions = {
        "auto_merge": False,
        "force_push": False,
        "delete_branch": False,
        "remote_rewrite": False,
        "ssh_remote_rewrite": False,
    }
    mode = "execute" if args.execute else "dry-run"
    config = {
        "summary_status": "PASS",
        "schema_version": "dualscope/autorun-loop-config/v1",
        "started_at": started_at,
        "max_iterations": args.max_iterations,
        "max_minutes": args.max_minutes,
        "queue_file": str(args.queue_file),
        "output_dir": str(args.output_dir),
        "task_orchestrator_output_dir": str(args.task_orchestrator_output_dir),
        "pr_status_output_dir": str(args.pr_status_output_dir),
        "mode": mode,
        "codex_bin": args.codex_bin,
        "stop_on_review_pending": args.stop_on_review_pending,
        "allow_review_pending_continue": args.allow_review_pending_continue,
        "stop_on_requested_changes": args.stop_on_requested_changes,
        "stop_on_failing_checks": args.stop_on_failing_checks,
        "dangerous_actions": dangerous_actions,
    }
    write_json(args.output_dir / "dualscope_autorun_loop_config.json", config)

    preflight = run_preflight()
    write_json(args.output_dir / "dualscope_autorun_loop_preflight.json", preflight)
    codex_available = codex_exec_available(args.codex_bin)
    blockers: list[dict[str, Any]] = []
    selected_tasks: list[dict[str, Any]] = []
    exec_results: list[dict[str, Any]] = []
    stop_reason = "max_iterations"

    for iteration in range(1, args.max_iterations + 1):
        if (time.monotonic() - start_monotonic) / 60 >= args.max_minutes:
            stop_reason = "max_minutes"
            break

        iteration_started = utc_now()
        pr_before = run_pr_review_orchestrator(args, role="before", iteration=iteration)
        write_jsonl(pr_history_path, [pr_before], append=True)
        pr_blockers = blockers_from_pr_status(args, pr_before)
        if pr_blockers:
            blockers.extend(pr_blockers)
            stop_reason = pr_blockers[0]["kind"]
            iteration_row = {
                "iteration": iteration,
                "started_at": iteration_started,
                "completed_at": utc_now(),
                "status": "blocked_before_task_selection",
                "blockers": pr_blockers,
            }
            write_jsonl(iterations_path, [iteration_row], append=True)
            append_run_log(
                log_path,
                {
                    "iteration": iteration,
                    "timestamp": iteration_started,
                    "selected_task": None,
                    "pr_status_before": pr_before.get("summary_status"),
                    "codex_exec_command": "not_run",
                    "codex_exec_exit_code": None,
                    "pr_status_after": "not_run",
                    "blocker": stop_reason,
                    "next_action": "stop",
                },
            )
            break

        task_result = run_task_orchestrator(args, iteration)
        selection = task_result.get("selection", {})
        selected_task = selection.get("selected_task_id") or selection.get("next_task")
        selected_row = {
            "iteration": iteration,
            "selected_task": selected_task,
            "selection_type": selection.get("selection_type"),
            "reason": selection.get("reason"),
            "prompt_path": task_result.get("prompt_path"),
            "prompt_excerpt": truncate_text(task_result.get("prompt_text", ""), 2000),
        }
        selected_tasks.append(selected_row)
        write_jsonl(selected_tasks_path, [selected_row], append=True)

        task_blockers = selection.get("blockers") or []
        if task_result.get("summary_status") != "PASS":
            blockers.append({"kind": "task_orchestrator_failure", "message": "Task orchestrator returned non-zero."})
            stop_reason = "task_orchestrator_failure"
        elif task_blockers:
            blockers.extend({"kind": "task_orchestrator_blocker", "message": str(item)} for item in task_blockers)
            stop_reason = "task_orchestrator_blocker"
        elif not selected_task:
            stop_reason = "no_next_task"

        exec_result: dict[str, Any]
        if stop_reason in {"task_orchestrator_failure", "no_next_task", "task_orchestrator_blocker"}:
            exec_result = {
                "summary_status": "SKIPPED",
                "iteration": iteration,
                "command": "not_run",
                "returncode": None,
                "reason": stop_reason,
                "codex_exec_available": codex_available,
            }
        elif args.dry_run:
            exec_result = {
                "summary_status": "SKIPPED",
                "iteration": iteration,
                "command": [args.codex_bin, "exec", "<prompt text>"],
                "returncode": None,
                "reason": "dry_run",
                "codex_exec_available": codex_available,
            }
            stop_reason = "dry_run_completed"
        else:
            exec_result = run_codex_exec(args, task_result.get("prompt_text", ""), iteration)
            if exec_result.get("returncode") != 0:
                blockers.append({"kind": "codex_exec_failure", "message": exec_result.get("stderr", "codex exec failed")})
                stop_reason = "codex_exec_failure"

        exec_results.append(exec_result)
        write_jsonl(exec_results_path, [exec_result], append=True)
        pr_after = run_pr_review_orchestrator(args, role="after", iteration=iteration)
        write_jsonl(pr_history_path, [pr_after], append=True)
        changed = git_changed_files()
        iteration_row = {
            "iteration": iteration,
            "started_at": iteration_started,
            "completed_at": utc_now(),
            "status": "completed",
            "selected_task": selected_task,
            "task_selection": selection,
            "codex_exec": exec_result,
            "git_changed_files_after": changed,
            "pr_status_before_summary": pr_before.get("summary_status"),
            "pr_status_after_summary": pr_after.get("summary_status"),
            "stop_reason": stop_reason,
        }
        write_jsonl(iterations_path, [iteration_row], append=True)
        append_run_log(
            log_path,
            {
                "iteration": iteration,
                "timestamp": iteration_started,
                "selected_task": selected_task,
                "pr_status_before": pr_before.get("summary_status"),
                "codex_exec_command": " ".join(exec_result["command"]) if isinstance(exec_result.get("command"), list) else exec_result.get("command"),
                "codex_exec_exit_code": exec_result.get("returncode"),
                "pr_status_after": pr_after.get("summary_status"),
                "blocker": stop_reason if stop_reason not in {"dry_run_completed", "max_iterations"} else None,
                "next_action": "stop" if args.dry_run or blockers else "continue",
            },
        )
        if args.dry_run or blockers or stop_reason != "max_iterations":
            break

    if not selected_tasks and not blockers:
        stop_reason = "no_iteration_executed"

    py_artifacts_written = all(
        (args.output_dir / name).exists()
        for name in [
            "dualscope_autorun_loop_config.json",
            "dualscope_autorun_loop_preflight.json",
        ]
    )
    dry_run_passed = bool(
        any(row.get("selected_task") and row.get("prompt_excerpt") for row in selected_tasks)
        or blockers
        or args.max_iterations == 0
    )
    verdict = decide_final_verdict(py_artifacts_written, dry_run_passed, codex_available, dangerous_actions, preflight, blockers)
    recommendation = recommendation_for_verdict(verdict)
    blockers_payload = {"summary_status": "PASS" if not blockers else "WARN", "schema_version": "dualscope/autorun-loop-blockers/v1", "blockers": blockers}
    write_json(args.output_dir / "dualscope_autorun_loop_blockers.json", blockers_payload)
    summary = {
        "summary_status": "PASS" if verdict != FINAL_VERDICTS["not_validated"] else "FAIL",
        "schema_version": "dualscope/autorun-loop-summary/v1",
        "started_at": started_at,
        "completed_at": utc_now(),
        "mode": mode,
        "iterations_completed": len(selected_tasks),
        "stop_reason": stop_reason,
        "codex_exec_available": codex_available,
        "final_verdict": verdict,
        "recommendation": recommendation,
        "dangerous_actions": dangerous_actions,
        "output_dir": str(args.output_dir),
    }
    write_json(args.output_dir / "dualscope_autorun_loop_summary.json", summary)
    write_json(
        args.output_dir / "dualscope_autorun_loop_next_recommendation.json",
        {"summary_status": summary["summary_status"], "final_verdict": verdict, "recommendation": recommendation},
    )
    (args.output_dir / "dualscope_autorun_loop_report.md").write_text(
        render_report(summary, blockers, selected_tasks),
        encoding="utf-8",
    )
    if args.dry_run:
        (args.output_dir / "dualscope_autorun_loop_dry_run_plan.md").write_text(
            render_dry_run_plan(selected_tasks, args),
            encoding="utf-8",
        )
    if any(result.get("summary_status") == "FAIL" for result in exec_results):
        (args.output_dir / "dualscope_autorun_loop_codex_failure_report.md").write_text(
            "# DualScope Autorun Loop Codex Failure\n\n"
            + "\n".join(f"- iteration {row.get('iteration')}: {row.get('stderr')}" for row in exec_results if row.get("summary_status") == "FAIL")
            + "\n",
            encoding="utf-8",
        )
    return (0 if verdict != FINAL_VERDICTS["not_validated"] else 2), summary
