"""Shared implementation for the local DualScope autorun loop."""

from __future__ import annotations

import json
import os
import shlex
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
DEFAULT_TASK_WORKTREE_RUNNER_OUTPUT_DIR = Path("outputs/dualscope_task_worktree_runner/default")
DEFAULT_SAFE_PR_MERGE_GATE_OUTPUT_DIR = Path("outputs/dualscope_safe_pr_merge_gate/default")
DEFAULT_CODEX_CWD = Path("/home/lh/TriScope-LLM")
DEFAULT_CODEX_HOME = Path("/home/lh")
DEFAULT_CODEX_TMPDIR = Path("/home/lh/TriScope-LLM/.tmp/codex")
DEFAULT_CODEX_STATE_DIR = Path("/home/lh/TriScope-LLM/.tmp/codex_home")
DEFAULT_WORKTREE_ROOT = Path("/tmp/dualscope-worktrees")
SOURCE_CODEX_HOME = Path("/home/lh/.codex")
DEFAULT_PROXY = "http://127.0.0.1:18080"
FINAL_VERDICTS = {
    "validated": "Autorun execute hardening validated",
    "partial": "Partially validated",
    "not_validated": "Not validated",
}
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
class AutorunLoopArgs:
    max_iterations: int
    max_minutes: int
    queue_file: Path
    output_dir: Path
    runtime_log_dir: Path
    task_orchestrator_output_dir: Path
    pr_status_output_dir: Path
    dry_run: bool
    execute: bool
    codex_bin: str
    codex_tmpdir: Path
    codex_extra_args: str
    ignore_runtime_dirty_paths: bool
    stop_on_review_pending: bool
    allow_review_pending_continue: bool
    stop_on_requested_changes: bool
    stop_on_failing_checks: bool
    use_worktrees: bool
    worktree_root: Path
    enable_safe_auto_merge: bool
    safe_merge_current_task_pr: bool
    require_codex_review_before_merge: bool
    max_review_wait_minutes: int
    review_poll_interval_seconds: int
    cleanup_merged_worktrees: bool
    keep_failed_worktrees: bool
    task_result_pr_packager: Path
    safe_pr_merge_gate: Path
    main_worktree_only_scheduler: bool


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


def classify_dirty_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    if is_runtime_dirty_path(normalized):
        if normalized == "scripts/codex_exec_full_auto_wrapper.sh":
            return "temporary_wrapper"
        if normalized.startswith(".tmp/"):
            return "runtime_tmp"
        if normalized.startswith("outputs/"):
            return "generated_output"
        return "runtime_artifact"
    if (
        normalized.startswith(".plans/")
        or normalized.startswith("src/")
        or normalized.startswith("scripts/")
        or normalized.startswith("docs/")
        or normalized in {
            "README.md",
            "AGENTS.md",
            "PLANS.md",
            "DUALSCOPE_MASTER_PLAN.md",
            "DUALSCOPE_TASK_QUEUE.md",
        }
    ):
        return "business_change"
    return "unknown_change"


def dirty_worktree_check(ignore_runtime_dirty_paths: bool) -> dict[str, Any]:
    result = run_command(["git", "status", "--porcelain"], timeout=60)
    rows: list[dict[str, Any]] = []
    runtime_rows: list[dict[str, Any]] = []
    business_rows: list[dict[str, Any]] = []
    wrapper_warning = False
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        path = parse_porcelain_path(line)
        classification = classify_dirty_path(path)
        row = {"raw": line, "path": path, "classification": classification}
        rows.append(row)
        if classification in {"runtime_artifact", "runtime_tmp", "generated_output", "temporary_wrapper"}:
            runtime_rows.append(row)
        else:
            business_rows.append(row)
        if path == "scripts/codex_exec_full_auto_wrapper.sh":
            wrapper_warning = True

    has_dirty = bool(rows)
    only_runtime_dirty = has_dirty and not business_rows and bool(runtime_rows)
    can_continue = (
        result.returncode == 0
        and (
            not has_dirty
            or (ignore_runtime_dirty_paths and only_runtime_dirty)
        )
    )
    blockers = []
    if result.returncode != 0:
        blockers.append({"kind": "git_status_failed", "message": result.stderr.strip() or "git status failed"})
    elif has_dirty and not can_continue:
        blockers.append(
            {
                "kind": "true_dirty_worktree",
                "message": "Working tree contains real business or unknown changes; task selection is blocked.",
                "changed_paths": [row["raw"] for row in rows],
                "business_or_unknown_paths": [row["raw"] for row in business_rows],
            }
        )
    warnings = []
    if wrapper_warning:
        warnings.append(
            {
                "kind": "repo_local_codex_wrapper",
                "message": "scripts/codex_exec_full_auto_wrapper.sh is a temporary wrapper path; delete it or move wrapper usage to /tmp/codex_exec_full_auto_wrapper.sh.",
            }
        )
    return {
        "summary_status": "PASS" if can_continue else "WARN",
        "schema_version": "dualscope/autorun-loop-dirty-worktree-check/v1",
        "ignore_runtime_dirty_paths": ignore_runtime_dirty_paths,
        "git_status_returncode": result.returncode,
        "is_clean": result.returncode == 0 and not has_dirty,
        "has_dirty_paths": has_dirty,
        "only_runtime_dirty_paths": only_runtime_dirty,
        "can_continue_task_selection": can_continue,
        "dirty_paths": rows,
        "runtime_dirty_paths": runtime_rows,
        "business_dirty_paths": business_rows,
        "warnings": warnings,
        "blockers": blockers,
        "stderr": truncate_text(result.stderr),
    }


def run_command(
    command: list[str],
    timeout: int = 120,
    extra_env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> CommandResult:
    env = proxy_env()
    if extra_env:
        env.update(extra_env)
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            env=env,
            cwd=str(cwd) if cwd is not None else None,
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
    state_path_result = run_command(["git", "rev-parse", "--git-path", "codex-pr-state.json"], timeout=30)
    state_file = Path(state_path_result.stdout.strip()) if state_path_result.returncode == 0 else Path(".git/codex-pr-state.json")
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
    extra_env = {"DUALSCOPE_IGNORE_RUNTIME_DIRTY_PATHS": "1"} if args.ignore_runtime_dirty_paths else {}
    result = run_command(command, timeout=180, extra_env=extra_env)
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


def codex_extra_args_list(args: AutorunLoopArgs) -> list[str]:
    if not args.codex_extra_args.strip():
        return []
    return shlex.split(args.codex_extra_args)


def build_codex_exec_command(args: AutorunLoopArgs, prompt_text: str) -> list[str]:
    return [args.codex_bin, "exec", *codex_extra_args_list(args), prompt_text]


def redacted_codex_exec_command(args: AutorunLoopArgs) -> list[str]:
    return [args.codex_bin, "exec", *codex_extra_args_list(args), "<prompt text>"]


def ensure_codex_tmpdir(args: AutorunLoopArgs) -> dict[str, Any]:
    tmpdir = args.codex_tmpdir
    error: str | None = None
    writable = False
    try:
        tmpdir.mkdir(parents=True, exist_ok=True)
        probe = tmpdir / ".dualscope_tmpdir_write_check"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink(missing_ok=True)
        writable = True
    except Exception as exc:  # noqa: BLE001 - this is a blocker artifact.
        error = str(exc)
    return {
        "tmpdir": str(tmpdir),
        "exists": tmpdir.exists(),
        "is_dir": tmpdir.is_dir(),
        "writable": writable,
        "error": error,
    }


def ensure_codex_state_dir() -> dict[str, Any]:
    copied_files: list[str] = []
    errors: list[dict[str, str]] = []
    writable = False
    try:
        DEFAULT_CODEX_STATE_DIR.mkdir(parents=True, exist_ok=True)
        for name in ("auth.json", "config.toml", "version.json", "installation_id"):
            source = SOURCE_CODEX_HOME / name
            target = DEFAULT_CODEX_STATE_DIR / name
            if source.exists():
                try:
                    shutil.copy2(source, target)
                    copied_files.append(name)
                except Exception as exc:  # noqa: BLE001
                    errors.append({"path": name, "error": str(exc)})
        for dirname in ("rules", "skills"):
            source_dir = SOURCE_CODEX_HOME / dirname
            target_dir = DEFAULT_CODEX_STATE_DIR / dirname
            if source_dir.exists() and not target_dir.exists():
                try:
                    shutil.copytree(source_dir, target_dir)
                    copied_files.append(f"{dirname}/")
                except Exception as exc:  # noqa: BLE001
                    errors.append({"path": dirname, "error": str(exc)})
        probe = DEFAULT_CODEX_STATE_DIR / ".dualscope_codex_home_write_check"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink(missing_ok=True)
        writable = True
    except Exception as exc:  # noqa: BLE001
        errors.append({"path": str(DEFAULT_CODEX_STATE_DIR), "error": str(exc)})
    return {
        "codex_home": str(DEFAULT_CODEX_STATE_DIR),
        "source_codex_home": str(SOURCE_CODEX_HOME),
        "exists": DEFAULT_CODEX_STATE_DIR.exists(),
        "is_dir": DEFAULT_CODEX_STATE_DIR.is_dir(),
        "writable": writable,
        "copied_files": copied_files,
        "errors": errors,
    }


def codex_exec_environment(args: AutorunLoopArgs, tmpdir_check: dict[str, Any] | None = None) -> dict[str, Any]:
    if tmpdir_check is None:
        tmpdir_check = ensure_codex_tmpdir(args)
    codex_home_check = ensure_codex_state_dir()
    summary_pass = bool(tmpdir_check.get("writable")) and bool(codex_home_check.get("writable")) and not codex_home_check.get("errors")
    return {
        "summary_status": "PASS" if summary_pass else "FAIL",
        "schema_version": "dualscope/autorun-loop-exec-environment/v1",
        "cwd": str(DEFAULT_CODEX_CWD),
        "cwd_exists": DEFAULT_CODEX_CWD.exists(),
        "home": str(DEFAULT_CODEX_HOME),
        "home_exists": DEFAULT_CODEX_HOME.exists(),
        "tmpdir": str(args.codex_tmpdir),
        "tmpdir_check": tmpdir_check,
        "tmpdir_writable": bool(tmpdir_check.get("writable")),
        "codex_home": str(DEFAULT_CODEX_STATE_DIR),
        "codex_home_check": codex_home_check,
        "codex_home_writable": bool(codex_home_check.get("writable")),
        "env": {
            "HOME": str(DEFAULT_CODEX_HOME),
            "CODEX_HOME": str(DEFAULT_CODEX_STATE_DIR),
            "TMPDIR": str(args.codex_tmpdir),
            "HTTP_PROXY": DEFAULT_PROXY,
            "HTTPS_PROXY": DEFAULT_PROXY,
            "ALL_PROXY": DEFAULT_PROXY,
        },
    }


def codex_process_env(args: AutorunLoopArgs) -> dict[str, str]:
    return {
        "HOME": str(DEFAULT_CODEX_HOME),
        "CODEX_HOME": str(DEFAULT_CODEX_STATE_DIR),
        "TMPDIR": str(args.codex_tmpdir),
        "TMP": str(args.codex_tmpdir),
        "TEMP": str(args.codex_tmpdir),
        "HTTP_PROXY": DEFAULT_PROXY,
        "HTTPS_PROXY": DEFAULT_PROXY,
        "ALL_PROXY": DEFAULT_PROXY,
    }


def codex_command_preview(args: AutorunLoopArgs, selected_task: str | None, prompt_path: str | None) -> dict[str, Any]:
    command = redacted_codex_exec_command(args)
    return {
        "summary_status": "PASS",
        "schema_version": "dualscope/autorun-loop-codex-command-preview/v1",
        "mode": "execute" if args.execute else "dry-run",
        "codex_bin": args.codex_bin,
        "codex_extra_args": args.codex_extra_args,
        "codex_extra_args_list": codex_extra_args_list(args),
        "command": command,
        "command_display": shlex.join(command),
        "cwd": str(DEFAULT_CODEX_CWD),
        "home": str(DEFAULT_CODEX_HOME),
        "codex_home": str(DEFAULT_CODEX_STATE_DIR),
        "tmpdir": str(args.codex_tmpdir),
        "selected_task": selected_task,
        "prompt_path": prompt_path,
        "dry_run_only": args.dry_run,
    }


def run_codex_exec(
    args: AutorunLoopArgs,
    prompt_text: str,
    iteration: int,
    selected_task: str | None,
    prompt_path: str | None,
) -> dict[str, Any]:
    command = build_codex_exec_command(args, prompt_text)
    preview_command = redacted_codex_exec_command(args)
    started = utc_now()
    tmpdir_check = ensure_codex_tmpdir(args)
    exec_env = codex_exec_environment(args, tmpdir_check)
    if not tmpdir_check.get("writable") or not exec_env.get("codex_home_writable") or exec_env.get("summary_status") != "PASS":
        return {
            "summary_status": "FAIL",
            "iteration": iteration,
            "started_at": started,
            "completed_at": utc_now(),
            "command": preview_command,
            "cwd": str(DEFAULT_CODEX_CWD),
            "home": str(DEFAULT_CODEX_HOME),
            "tmpdir": str(args.codex_tmpdir),
            "tmpdir_writable": False,
            "exec_environment": exec_env,
            "returncode": None,
            "exit_code": None,
            "codex_exec_available": codex_exec_available(args.codex_bin),
            "selected_task": selected_task,
            "prompt_path": prompt_path,
            "stdout": "",
            "stderr": tmpdir_check.get("error")
            or "; ".join(item.get("error", "") for item in exec_env.get("codex_home_check", {}).get("errors", []))
            or f"Codex execution environment is not writable: TMPDIR={args.codex_tmpdir}, CODEX_HOME={DEFAULT_CODEX_STATE_DIR}",
        }
    if not codex_exec_available(args.codex_bin):
        return {
            "summary_status": "FAIL",
            "iteration": iteration,
            "started_at": started,
            "completed_at": utc_now(),
            "command": preview_command,
            "cwd": str(DEFAULT_CODEX_CWD),
            "home": str(DEFAULT_CODEX_HOME),
            "tmpdir": str(args.codex_tmpdir),
            "tmpdir_writable": tmpdir_check.get("writable"),
            "exec_environment": exec_env,
            "returncode": 127,
            "exit_code": 127,
            "codex_exec_available": False,
            "selected_task": selected_task,
            "prompt_path": prompt_path,
            "stdout": "",
            "stderr": f"`{args.codex_bin}` is not available on PATH. Install/login to Codex CLI before execute mode.",
        }
    result = run_command(
        command,
        timeout=max(60, args.max_minutes * 60),
        extra_env=codex_process_env(args),
        cwd=DEFAULT_CODEX_CWD,
    )
    return {
        "summary_status": "PASS" if result.returncode == 0 else "FAIL",
        "iteration": iteration,
        "started_at": started,
        "completed_at": utc_now(),
        "command": preview_command,
        "cwd": str(DEFAULT_CODEX_CWD),
        "home": str(DEFAULT_CODEX_HOME),
        "tmpdir": str(args.codex_tmpdir),
        "tmpdir_writable": tmpdir_check.get("writable"),
        "exec_environment": exec_env,
        "returncode": result.returncode,
        "exit_code": result.returncode,
        "codex_exec_available": True,
        "selected_task": selected_task,
        "prompt_path": prompt_path,
        "stdout": truncate_text(result.stdout, 12000),
        "stderr": truncate_text(result.stderr, 12000),
    }


def run_task_worktree_runner(
    args: AutorunLoopArgs,
    iteration: int,
    selected_task: str | None,
    prompt_path: str | None,
) -> dict[str, Any]:
    if not selected_task or not prompt_path:
        return {
            "summary_status": "FAIL",
            "iteration": iteration,
            "reason": "missing_selected_task_or_prompt",
            "selected_task": selected_task,
            "prompt_path": prompt_path,
        }
    output_dir = DEFAULT_TASK_WORKTREE_RUNNER_OUTPUT_DIR
    command = [
        python_bin(),
        str(args.task_result_pr_packager),
        "--task-id",
        selected_task,
        "--prompt-file",
        prompt_path,
        "--base-branch",
        "main",
        "--worktree-root",
        str(args.worktree_root),
        "--branch-prefix",
        "codex",
        "--output-dir",
        str(output_dir),
        "--codex-bin",
        args.codex_bin,
        "--codex-extra-args",
        args.codex_extra_args or "--cd {worktree_path} --full-auto",
        "--max-minutes",
        str(args.max_minutes),
        "--cleanup-worktree",
        "true" if args.cleanup_merged_worktrees else "false",
        "--stop-on-dirty-main",
        "true" if args.main_worktree_only_scheduler else "false",
        "--proxy",
        DEFAULT_PROXY,
    ]
    if args.ignore_runtime_dirty_paths:
        command.append("--allow-runtime-dirty")
    if args.dry_run:
        command.append("--dry-run")
    else:
        command.append("--execute")
    if args.keep_failed_worktrees:
        command.append("--keep-worktree")
    started = utc_now()
    result = run_command(command, timeout=max(60, args.max_minutes * 60 + 300))
    summary_path = output_dir / "dualscope_task_worktree_runner_summary.json"
    pr_path = output_dir / "dualscope_task_worktree_runner_pr_creation_result.json"
    manifest_path = output_dir / "dualscope_task_worktree_runner_worktree_manifest.json"
    summary = read_json(summary_path) if summary_path.exists() else {}
    pr_result = read_json(pr_path) if pr_path.exists() else {}
    manifest = read_json(manifest_path) if manifest_path.exists() else {}
    return {
        "summary_status": "PASS" if result.returncode == 0 and summary.get("summary_status") in {"PASS", "WARN"} else "FAIL",
        "iteration": iteration,
        "started_at": started,
        "completed_at": utc_now(),
        "command": command,
        "returncode": result.returncode,
        "stdout": truncate_text(result.stdout, 12000),
        "stderr": truncate_text(result.stderr, 12000),
        "selected_task": selected_task,
        "prompt_path": prompt_path,
        "artifact_dir": str(output_dir),
        "runner_summary": summary,
        "pr_creation_result": pr_result,
        "worktree_manifest": manifest,
        "created_pr_number": summary.get("created_pr_number") or pr_result.get("created_pr_number"),
        "created_pr_url": summary.get("created_pr_url") or pr_result.get("created_pr_url"),
        "worktree_path": summary.get("worktree_path") or manifest.get("worktree_path"),
        "branch": summary.get("branch") or manifest.get("branch"),
    }


def run_safe_pr_merge_gate(args: AutorunLoopArgs, pr_number: int, merge: bool) -> dict[str, Any]:
    command = [
        python_bin(),
        str(args.safe_pr_merge_gate),
        "--pr",
        str(pr_number),
        "--output-dir",
        str(DEFAULT_SAFE_PR_MERGE_GATE_OUTPUT_DIR),
        "--require-codex-review",
        "true" if args.require_codex_review_before_merge else "false",
        "--require-no-requested-changes",
        "true" if args.stop_on_requested_changes else "false",
        "--require-no-failing-checks",
        "true" if args.stop_on_failing_checks else "false",
        "--proxy",
        DEFAULT_PROXY,
    ]
    command.append("--merge" if merge else "--check-only")
    started = utc_now()
    result = run_command(command, timeout=300)
    decision_path = DEFAULT_SAFE_PR_MERGE_GATE_OUTPUT_DIR / "dualscope_safe_pr_merge_gate_decision.json"
    decision = read_json(decision_path) if decision_path.exists() else {}
    return {
        "summary_status": "PASS" if result.returncode == 0 else "FAIL",
        "started_at": started,
        "completed_at": utc_now(),
        "command": command,
        "returncode": result.returncode,
        "stdout": truncate_text(result.stdout, 12000),
        "stderr": truncate_text(result.stderr, 12000),
        "decision": decision,
        "artifact_dir": str(DEFAULT_SAFE_PR_MERGE_GATE_OUTPUT_DIR),
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
        return "Run autorun loop with --execute --max-iterations 2."
    if verdict == FINAL_VERDICTS["partial"]:
        return "Repair remaining autorun execute blocker and rerun smoke."
    return "Do not use autorun execute mode until blocker is fixed."


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
        f"- Ignore runtime dirty paths: {summary['ignore_runtime_dirty_paths']}",
        f"- Use worktrees: {summary.get('use_worktrees')}",
        f"- Safe auto merge enabled: {summary.get('enable_safe_auto_merge')}",
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
            "- stop_on_requested_changes: true",
            "- stop_on_failing_checks: true",
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
        f"- codex command preview: `{shlex.join(redacted_codex_exec_command(args))}`",
        f"- use worktrees: `{args.use_worktrees}`",
        f"- worktree root: `{args.worktree_root}`",
        f"- safe auto merge: `{args.enable_safe_auto_merge}`",
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
    args.runtime_log_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.runtime_log_dir / "dualscope_autorun_loop_log.md"
    iterations_path = args.output_dir / "dualscope_autorun_loop_iterations.jsonl"
    selected_tasks_path = args.output_dir / "dualscope_autorun_loop_selected_tasks.jsonl"
    exec_results_path = args.output_dir / "dualscope_autorun_loop_codex_exec_results.jsonl"
    pr_history_path = args.output_dir / "dualscope_autorun_loop_pr_status_history.jsonl"
    worktree_iterations_path = args.output_dir / "dualscope_autorun_loop_worktree_iterations.jsonl"
    created_prs_path = args.output_dir / "dualscope_autorun_loop_created_prs.jsonl"
    merge_decisions_path = args.output_dir / "dualscope_autorun_loop_merge_decisions.jsonl"
    worktree_cleanup_path = args.output_dir / "dualscope_autorun_loop_worktree_cleanup.jsonl"
    dirty_check_path = args.output_dir / "dualscope_autorun_loop_dirty_worktree_classification.json"
    legacy_dirty_check_path = args.output_dir / "dualscope_autorun_loop_dirty_worktree_check.json"
    command_preview_path = args.output_dir / "dualscope_autorun_loop_codex_command_preview.json"
    exec_environment_path = args.output_dir / "dualscope_autorun_loop_exec_environment.json"
    failure_diagnostics_path = args.output_dir / "dualscope_autorun_loop_exec_failure_diagnostics.json"
    legacy_failure_details_path = args.output_dir / "dualscope_autorun_loop_codex_failure_details.json"
    failure_report_path = args.output_dir / "dualscope_autorun_loop_codex_failure_report.md"
    for path in [
        iterations_path,
        selected_tasks_path,
        exec_results_path,
        pr_history_path,
        worktree_iterations_path,
        created_prs_path,
        merge_decisions_path,
        worktree_cleanup_path,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    for path in [failure_diagnostics_path, legacy_failure_details_path, failure_report_path]:
        path.unlink(missing_ok=True)

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
        "runtime_log_dir": str(args.runtime_log_dir),
        "task_orchestrator_output_dir": str(args.task_orchestrator_output_dir),
        "pr_status_output_dir": str(args.pr_status_output_dir),
        "mode": mode,
        "codex_bin": args.codex_bin,
        "codex_cwd": str(DEFAULT_CODEX_CWD),
        "codex_home": str(DEFAULT_CODEX_HOME),
        "codex_state_dir": str(DEFAULT_CODEX_STATE_DIR),
        "codex_tmpdir": str(args.codex_tmpdir),
        "codex_extra_args": args.codex_extra_args,
        "codex_extra_args_list": codex_extra_args_list(args),
        "ignore_runtime_dirty_paths": args.ignore_runtime_dirty_paths,
        "use_worktrees": args.use_worktrees,
        "worktree_root": str(args.worktree_root),
        "enable_safe_auto_merge": args.enable_safe_auto_merge,
        "safe_merge_current_task_pr": args.safe_merge_current_task_pr,
        "require_codex_review_before_merge": args.require_codex_review_before_merge,
        "max_review_wait_minutes": args.max_review_wait_minutes,
        "review_poll_interval_seconds": args.review_poll_interval_seconds,
        "cleanup_merged_worktrees": args.cleanup_merged_worktrees,
        "keep_failed_worktrees": args.keep_failed_worktrees,
        "task_result_pr_packager": str(args.task_result_pr_packager),
        "safe_pr_merge_gate": str(args.safe_pr_merge_gate),
        "main_worktree_only_scheduler": args.main_worktree_only_scheduler,
        "stop_on_review_pending": args.stop_on_review_pending,
        "allow_review_pending_continue": args.allow_review_pending_continue,
        "stop_on_requested_changes": args.stop_on_requested_changes,
        "stop_on_failing_checks": args.stop_on_failing_checks,
        "dangerous_actions": dangerous_actions,
    }
    write_json(args.output_dir / "dualscope_autorun_loop_config.json", config)

    preflight = run_preflight()
    write_json(args.output_dir / "dualscope_autorun_loop_preflight.json", preflight)
    initial_dirty_check = dirty_worktree_check(args.ignore_runtime_dirty_paths)
    write_json(dirty_check_path, initial_dirty_check)
    write_json(legacy_dirty_check_path, initial_dirty_check)
    write_json(command_preview_path, codex_command_preview(args, None, None))
    exec_environment = codex_exec_environment(args)
    write_json(exec_environment_path, exec_environment)
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

        dirty_check = dirty_worktree_check(args.ignore_runtime_dirty_paths)
        write_json(dirty_check_path, dirty_check)
        write_json(legacy_dirty_check_path, dirty_check)
        if not dirty_check.get("can_continue_task_selection"):
            blockers.extend(dirty_check.get("blockers") or [])
            stop_reason = "true_dirty_worktree_blocker"
            iteration_row = {
                "iteration": iteration,
                "started_at": iteration_started,
                "completed_at": utc_now(),
                "status": "blocked_before_task_selection",
                "dirty_worktree_check": dirty_check,
                "blockers": dirty_check.get("blockers") or [],
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
        preview = codex_command_preview(args, selected_task, task_result.get("prompt_path"))
        write_json(command_preview_path, preview)
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
                "selected_task": selected_task,
                "prompt_path": task_result.get("prompt_path"),
            }
        elif args.use_worktrees:
            exec_result = run_task_worktree_runner(
                args,
                iteration,
                selected_task,
                task_result.get("prompt_path"),
            )
            write_jsonl(worktree_iterations_path, [exec_result], append=True)
            created_pr_number = exec_result.get("created_pr_number")
            created_pr_url = exec_result.get("created_pr_url")
            if created_pr_url:
                created_row = {
                    "iteration": iteration,
                    "selected_task": selected_task,
                    "created_pr_number": created_pr_number,
                    "created_pr_url": created_pr_url,
                    "worktree_path": exec_result.get("worktree_path"),
                    "branch": exec_result.get("branch"),
                    "created_at": utc_now(),
                }
                write_jsonl(created_prs_path, [created_row], append=True)
            if exec_result.get("summary_status") != "PASS":
                blockers.append({"kind": "task_worktree_runner_failure", "message": exec_result.get("stderr") or "task worktree runner failed"})
                stop_reason = "task_worktree_runner_failure"
            elif args.dry_run:
                stop_reason = "dry_run_completed"
            elif created_pr_number and args.enable_safe_auto_merge and args.safe_merge_current_task_pr:
                deadline = time.monotonic() + max(0, args.max_review_wait_minutes) * 60
                merge_decision = run_safe_pr_merge_gate(args, int(created_pr_number), merge=True)
                while (
                    merge_decision.get("decision", {}).get("decision") == "blocked"
                    and any(item.get("kind") == "codex_review_missing" for item in merge_decision.get("decision", {}).get("blockers", []))
                    and time.monotonic() < deadline
                ):
                    time.sleep(max(1, args.review_poll_interval_seconds))
                    merge_decision = run_safe_pr_merge_gate(args, int(created_pr_number), merge=True)
                write_jsonl(merge_decisions_path, [merge_decision], append=True)
                if merge_decision.get("decision", {}).get("merged"):
                    pull_result = run_command(["git", "pull", "origin", "main"], timeout=180)
                    cleanup_row = {
                        "iteration": iteration,
                        "pr": created_pr_number,
                        "worktree_path": exec_result.get("worktree_path"),
                        "pull_after_merge": command_row("git_pull_origin_main", pull_result),
                        "cleanup_attempted": False,
                        "cleanup_result": None,
                    }
                    if args.cleanup_merged_worktrees and exec_result.get("worktree_path"):
                        cleanup_result = run_command(["git", "worktree", "remove", str(exec_result["worktree_path"])], timeout=180)
                        cleanup_row["cleanup_attempted"] = True
                        cleanup_row["cleanup_result"] = command_row("git_worktree_remove", cleanup_result)
                    write_jsonl(worktree_cleanup_path, [cleanup_row], append=True)
                    stop_reason = "max_iterations"
                else:
                    blockers.extend(merge_decision.get("decision", {}).get("blockers") or [])
                    stop_reason = "safe_merge_gate_blocker"
            elif created_pr_number:
                stop_reason = "task_pr_created_pending_merge"
            else:
                stop_reason = exec_result.get("runner_summary", {}).get("stop_reason") or "worktree_task_completed"
        elif args.dry_run:
            exec_result = {
                "summary_status": "SKIPPED",
                "iteration": iteration,
                "command": redacted_codex_exec_command(args),
                "command_display": preview["command_display"],
                "cwd": str(DEFAULT_CODEX_CWD),
                "home": str(DEFAULT_CODEX_HOME),
                "tmpdir": str(args.codex_tmpdir),
                "tmpdir_writable": exec_environment.get("tmpdir_writable"),
                "exec_environment": exec_environment,
                "returncode": None,
                "reason": "dry_run",
                "codex_exec_available": codex_available,
                "selected_task": selected_task,
                "prompt_path": task_result.get("prompt_path"),
            }
            stop_reason = "dry_run_completed"
        else:
            exec_result = run_codex_exec(
                args,
                task_result.get("prompt_text", ""),
                iteration,
                selected_task,
                task_result.get("prompt_path"),
            )
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
            "dirty_worktree_check": dirty_check,
            "codex_command_preview": preview,
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
            "dualscope_autorun_loop_dirty_worktree_classification.json",
            "dualscope_autorun_loop_codex_command_preview.json",
            "dualscope_autorun_loop_exec_environment.json",
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
        "ignore_runtime_dirty_paths": args.ignore_runtime_dirty_paths,
        "runtime_log_dir": str(args.runtime_log_dir),
        "codex_cwd": str(DEFAULT_CODEX_CWD),
        "codex_home": str(DEFAULT_CODEX_HOME),
        "codex_state_dir": str(DEFAULT_CODEX_STATE_DIR),
        "codex_tmpdir": str(args.codex_tmpdir),
        "tmpdir_writable": exec_environment.get("tmpdir_writable"),
        "codex_home_writable": exec_environment.get("codex_home_writable"),
        "use_worktrees": args.use_worktrees,
        "worktree_root": str(args.worktree_root),
        "enable_safe_auto_merge": args.enable_safe_auto_merge,
        "safe_merge_current_task_pr": args.safe_merge_current_task_pr,
        "task_worktree_runner_output_dir": str(DEFAULT_TASK_WORKTREE_RUNNER_OUTPUT_DIR),
        "safe_pr_merge_gate_output_dir": str(DEFAULT_SAFE_PR_MERGE_GATE_OUTPUT_DIR),
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
    hardening_summary = {
        "summary_status": summary["summary_status"],
        "schema_version": "dualscope/autorun-loop-execute-hardening-summary/v1",
        "final_verdict": verdict,
        "recommendation": recommendation,
        "mode": mode,
        "stop_reason": stop_reason,
        "codex_exec_available": codex_available,
        "codex_command_preview_path": str(command_preview_path),
        "dirty_worktree_check_path": str(dirty_check_path),
        "exec_environment_path": str(exec_environment_path),
        "log_path": str(log_path),
        "tmpdir_writable": exec_environment.get("tmpdir_writable"),
        "safe_constraints": {
            "auto_merge_default": False,
            "auto_merge_enabled": args.enable_safe_auto_merge,
            "force_push": False,
            "delete_branch": False,
            "remote_rewrite": False,
            "ssh_remote_rewrite": False,
            "stop_on_requested_changes": args.stop_on_requested_changes,
            "stop_on_failing_checks": args.stop_on_failing_checks,
        },
    }
    write_json(args.output_dir / "dualscope_autorun_loop_execute_hardening_summary.json", hardening_summary)
    (args.output_dir / "dualscope_autorun_loop_report.md").write_text(
        render_report(summary, blockers, selected_tasks),
        encoding="utf-8",
    )
    (args.output_dir / "dualscope_autorun_loop_execute_hardening_report.md").write_text(
        render_report(summary, blockers, selected_tasks)
        + "\n## Execute Hardening\n"
        + f"- Dirty worktree classification: `{dirty_check_path}`\n"
        + f"- Codex command preview: `{command_preview_path}`\n"
        + f"- Codex exec environment: `{exec_environment_path}`\n"
        + f"- Rolling log: `{log_path}`\n",
        encoding="utf-8",
    )
    if args.dry_run:
        (args.output_dir / "dualscope_autorun_loop_dry_run_plan.md").write_text(
            render_dry_run_plan(selected_tasks, args),
            encoding="utf-8",
        )
    if any(result.get("summary_status") == "FAIL" for result in exec_results):
        failure_rows = [row for row in exec_results if row.get("summary_status") == "FAIL"]
        write_json(
            failure_diagnostics_path,
            {
                "summary_status": "FAIL",
                "schema_version": "dualscope/autorun-loop-exec-failure-diagnostics/v1",
                "failures": failure_rows,
            },
        )
        write_json(
            legacy_failure_details_path,
            {
                "summary_status": "FAIL",
                "schema_version": "dualscope/autorun-loop-codex-failure-details/v1",
                "failures": failure_rows,
            },
        )
        failure_report_path.write_text(
            "# DualScope Autorun Loop Codex Failure\n\n"
            + "\n".join(
                [
                    "\n".join(
                        [
                            f"## Iteration {row.get('iteration')}",
                            "",
                            f"- exit code: `{row.get('returncode')}`",
                            f"- selected task: `{row.get('selected_task')}`",
                            f"- prompt path: `{row.get('prompt_path')}`",
                            f"- command: `{shlex.join(row.get('command') or []) if isinstance(row.get('command'), list) else row.get('command')}`",
                            f"- cwd: `{row.get('cwd')}`",
                            f"- HOME: `{row.get('home')}`",
                            f"- TMPDIR: `{row.get('tmpdir')}`",
                            f"- tmpdir writable: `{row.get('tmpdir_writable')}`",
                            f"- stderr: `{truncate_text(row.get('stderr', ''), 1000)}`",
                            "",
                        ]
                    )
                    for row in failure_rows
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    return (0 if verdict != FINAL_VERDICTS["not_validated"] else 2), summary
