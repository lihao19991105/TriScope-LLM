#!/usr/bin/env python3
"""Run one selected DualScope task inside an isolated git worktree."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_task_worktree_runner/default")
DEFAULT_WORKTREE_ROOT = Path("/tmp/dualscope-worktrees")
DEFAULT_PROXY = "http://127.0.0.1:18080"
DEFAULT_CODEX_EXTRA_ARGS = "--cd {worktree_path} --full-auto"
RUNTIME_DIRTY_PREFIXES = (
    "outputs/dualscope_autorun_loop/",
    "outputs/dualscope_task_orchestrator/",
    "outputs/dualscope_pr_review_status/",
    "outputs/dualscope_task_worktree_runner/",
    "outputs/dualscope_safe_pr_merge_gate/",
    ".tmp/",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def truncate(value: str | None, limit: int = 12000) -> str:
    text = value or ""
    return text if len(text) <= limit else text[-limit:]


def proxy_env(proxy: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["HTTP_PROXY"] = proxy
    env["HTTPS_PROXY"] = proxy
    env["ALL_PROXY"] = proxy
    if extra:
        env.update(extra)
    return env


def run_command(command: list[str], cwd: Path | None = None, proxy: str = DEFAULT_PROXY, timeout: int = 120) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            env=proxy_env(proxy),
        )
        return {
            "command": command,
            "cwd": str(cwd) if cwd else None,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except FileNotFoundError as exc:
        return {"command": command, "cwd": str(cwd) if cwd else None, "returncode": 127, "stdout": "", "stderr": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "cwd": str(cwd) if cwd else None,
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"Command timed out after {timeout}s.",
        }


def command_row(name: str, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "command": result["command"],
        "cwd": result.get("cwd"),
        "returncode": result["returncode"],
        "passed": result["returncode"] == 0,
        "stdout": truncate(result.get("stdout"), 4000),
        "stderr": truncate(result.get("stderr"), 4000),
    }


def slugify_task_id(task_id: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9._-]+", "-", task_id).strip("-").lower()
    text = text.replace("dualscope-", "")
    return text[:80] or "task"


def parse_bool(value: str) -> bool:
    lowered = value.lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected boolean, got {value!r}")


def porcelain_lines(cwd: Path, proxy: str) -> list[str]:
    result = run_command(["git", "status", "--porcelain"], cwd=cwd, proxy=proxy, timeout=60)
    return [line for line in result.get("stdout", "").splitlines() if line.strip()]


def path_from_porcelain(line: str) -> str:
    path = line[3:] if len(line) > 3 else line.strip()
    if " -> " in path:
        path = path.rsplit(" -> ", 1)[-1]
    return path.strip().strip('"')


def is_runtime_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    if normalized.endswith(".pyc") or "__pycache__/" in normalized:
        return True
    return any(normalized.startswith(prefix) for prefix in RUNTIME_DIRTY_PREFIXES)


def main_worktree_dirty_check(repo_root: Path, allow_runtime_dirty: bool, proxy: str) -> dict[str, Any]:
    result = run_command(["git", "status", "--porcelain"], cwd=repo_root, proxy=proxy, timeout=60)
    rows = []
    business = []
    for line in result.get("stdout", "").splitlines():
        if not line.strip():
            continue
        path = path_from_porcelain(line)
        runtime = is_runtime_path(path)
        row = {"raw": line, "path": path, "runtime_only": runtime}
        rows.append(row)
        if not runtime:
            business.append(row)
    can_continue = result["returncode"] == 0 and (not business if allow_runtime_dirty else not rows)
    return {
        "summary_status": "PASS" if can_continue else "WARN",
        "git_status_returncode": result["returncode"],
        "allow_runtime_dirty": allow_runtime_dirty,
        "is_clean": result["returncode"] == 0 and not rows,
        "dirty_paths": rows,
        "business_dirty_paths": business,
        "can_continue": can_continue,
        "stderr": truncate(result.get("stderr"), 4000),
    }


def extract_pr_from_codex_pr_output(text: str) -> dict[str, Any]:
    match = re.search(r"PR\s+#(?P<number>\d+):\s+(?P<url>https://\S+)", text)
    if not match:
        return {"number": None, "url": None}
    return {"number": int(match.group("number")), "url": match.group("url")}


def build_codex_command(codex_bin: str, codex_extra_args: str, worktree_path: Path, prompt: str) -> list[str]:
    rendered_args = codex_extra_args.format(worktree_path=str(worktree_path))
    return [codex_bin, "exec", *shlex.split(rendered_args), prompt]


def render_prompt(prompt_file: Path, worktree_path: Path) -> str:
    prompt = prompt_file.read_text(encoding="utf-8")
    return (
        prompt
        + "\n\n## Worktree Execution Context\n\n"
        + f"- This task is executing inside isolated git worktree `{worktree_path}`.\n"
        + "- Do not modify the scheduler's main worktree.\n"
        + "- Follow AGENTS.md PR workflow from inside this worktree.\n"
        + "- Do not auto merge, force push, delete branches, rewrite remotes, change benchmark truth, change gates, continue route_c, or generate 199+.\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute one DualScope task in an isolated git worktree and package it as a PR.")
    parser.add_argument("--task-id", required=True, help="Selected task id.")
    parser.add_argument("--prompt-file", type=Path, required=True, help="Path to next task prompt.")
    parser.add_argument("--base-branch", default="main", help="Base branch. Default: main.")
    parser.add_argument("--worktree-root", type=Path, default=DEFAULT_WORKTREE_ROOT, help=f"Worktree root. Default: {DEFAULT_WORKTREE_ROOT}")
    parser.add_argument("--branch-prefix", default="codex", help="Branch prefix. Default: codex")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Artifact directory. Default: {DEFAULT_OUTPUT_DIR}")
    parser.add_argument("--codex-bin", default="codex", help="Codex binary. Default: codex")
    parser.add_argument("--codex-extra-args", default=DEFAULT_CODEX_EXTRA_ARGS, help=f"Extra args template. Default: {DEFAULT_CODEX_EXTRA_ARGS!r}")
    parser.add_argument("--max-minutes", type=int, default=120, help="Maximum minutes for codex exec. Default: 120")
    parser.add_argument("--dry-run", action="store_true", help="Preview worktree and codex commands without executing.")
    parser.add_argument("--execute", action="store_true", help="Actually create worktree and run codex exec.")
    parser.add_argument("--keep-worktree", action="store_true", help="Keep worktree even when cleanup is otherwise possible.")
    parser.add_argument("--cleanup-worktree", type=parse_bool, default=True, help="Allow later cleanup of merged worktrees. Default: true.")
    parser.add_argument("--stop-on-dirty-main", type=parse_bool, default=True, help="Stop if scheduler worktree is dirty. Default: true.")
    parser.add_argument("--allow-runtime-dirty", action="store_true", help="Allow runtime-only dirty files in scheduler worktree.")
    parser.add_argument("--proxy", default=DEFAULT_PROXY, help=f"Proxy URL. Default: {DEFAULT_PROXY}")
    return parser


def render_report(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# DualScope Task Worktree Runner Report",
            "",
            f"- Task: `{summary.get('task_id')}`",
            f"- Status: `{summary.get('summary_status')}`",
            f"- Worktree: `{summary.get('worktree_path')}`",
            f"- Branch: `{summary.get('branch')}`",
            f"- PR: `{summary.get('created_pr_url')}`",
            f"- Stop reason: `{summary.get('stop_reason')}`",
            "",
        ]
    )


def main() -> int:
    args = build_parser().parse_args()
    if args.dry_run and args.execute:
        raise SystemExit("--dry-run and --execute are mutually exclusive.")
    dry_run = args.dry_run or not args.execute
    started = utc_now()
    repo_root = Path.cwd()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    task_slug = slugify_task_id(args.task_id)
    branch = f"{args.branch_prefix}/{task_slug}-{timestamp}"
    worktree_path = args.worktree_root / f"{task_slug}-{timestamp}"
    args.output_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "summary_status": "PASS",
        "schema_version": "dualscope/task-worktree-runner-config/v1",
        "started_at": started,
        "task_id": args.task_id,
        "prompt_file": str(args.prompt_file),
        "base_branch": args.base_branch,
        "worktree_root": str(args.worktree_root),
        "branch": branch,
        "worktree_path": str(worktree_path),
        "dry_run": dry_run,
        "execute": args.execute,
        "codex_bin": args.codex_bin,
        "codex_extra_args": args.codex_extra_args,
        "cleanup_worktree": args.cleanup_worktree,
        "keep_worktree": args.keep_worktree,
        "stop_on_dirty_main": args.stop_on_dirty_main,
        "allow_runtime_dirty": args.allow_runtime_dirty,
        "proxy": args.proxy,
    }
    write_json(args.output_dir / "dualscope_task_worktree_runner_config.json", config)

    preflight_rows = [
        command_row("gh_auth_status", run_command(["gh", "auth", "status"], cwd=repo_root, proxy=args.proxy, timeout=90)),
        command_row("git_remote_v", run_command(["git", "remote", "-v"], cwd=repo_root, proxy=args.proxy, timeout=60)),
        command_row("git_ls_remote_origin_head", run_command(["git", "ls-remote", "origin", "HEAD"], cwd=repo_root, proxy=args.proxy, timeout=90)),
    ]
    remote_text = next((row["stdout"] for row in preflight_rows if row["name"] == "git_remote_v"), "")
    main_dirty = main_worktree_dirty_check(repo_root, args.allow_runtime_dirty, args.proxy)
    preflight = {
        "summary_status": "PASS" if all(row["passed"] for row in preflight_rows) and (main_dirty["can_continue"] or not args.stop_on_dirty_main) else "WARN",
        "schema_version": "dualscope/task-worktree-runner-preflight/v1",
        "commands": preflight_rows,
        "https_remote_detected": "https://github.com/" in remote_text,
        "ssh_remote_detected": "git@github.com:" in remote_text,
        "main_dirty_check": main_dirty,
    }
    write_json(args.output_dir / "dualscope_task_worktree_runner_preflight.json", preflight)

    prompt_text = render_prompt(args.prompt_file, worktree_path)
    codex_command = build_codex_command(args.codex_bin, args.codex_extra_args, worktree_path, prompt_text)
    redacted_codex_command = [args.codex_bin, "exec", *shlex.split(args.codex_extra_args.format(worktree_path=str(worktree_path))), "<prompt text>"]
    manifest = {
        "summary_status": "PASS",
        "schema_version": "dualscope/task-worktree-runner-worktree-manifest/v1",
        "task_id": args.task_id,
        "branch": branch,
        "worktree_path": str(worktree_path),
        "base_branch": args.base_branch,
        "codex_command_preview": redacted_codex_command,
        "codex_command_display": shlex.join(redacted_codex_command),
    }
    write_json(args.output_dir / "dualscope_task_worktree_runner_worktree_manifest.json", manifest)

    if preflight["summary_status"] != "PASS" and args.stop_on_dirty_main:
        summary = {
            "summary_status": "BLOCKED",
            "schema_version": "dualscope/task-worktree-runner-summary/v1",
            "task_id": args.task_id,
            "stop_reason": "dirty_or_failed_preflight",
            "branch": branch,
            "worktree_path": str(worktree_path),
            "created_pr_number": None,
            "created_pr_url": None,
        }
        for name in [
            "dualscope_task_worktree_runner_codex_exec_result.json",
            "dualscope_task_worktree_runner_git_status_after_exec.json",
            "dualscope_task_worktree_runner_pr_creation_result.json",
            "dualscope_task_worktree_runner_test_results.json",
        ]:
            write_json(args.output_dir / name, {"summary_status": "SKIPPED", "reason": summary["stop_reason"]})
        write_json(args.output_dir / "dualscope_task_worktree_runner_summary.json", summary)
        (args.output_dir / "dualscope_task_worktree_runner_report.md").write_text(render_report(summary), encoding="utf-8")
        print(json.dumps(summary, indent=2, ensure_ascii=True))
        print(f"Artifacts: {args.output_dir}")
        return 0

    if dry_run:
        summary = {
            "summary_status": "PASS",
            "schema_version": "dualscope/task-worktree-runner-summary/v1",
            "task_id": args.task_id,
            "stop_reason": "dry_run_completed",
            "branch": branch,
            "worktree_path": str(worktree_path),
            "created_pr_number": None,
            "created_pr_url": None,
            "codex_command_preview": redacted_codex_command,
        }
        for name in [
            "dualscope_task_worktree_runner_codex_exec_result.json",
            "dualscope_task_worktree_runner_git_status_after_exec.json",
            "dualscope_task_worktree_runner_pr_creation_result.json",
            "dualscope_task_worktree_runner_test_results.json",
        ]:
            write_json(args.output_dir / name, {"summary_status": "SKIPPED", "reason": "dry_run"})
        write_json(args.output_dir / "dualscope_task_worktree_runner_summary.json", summary)
        (args.output_dir / "dualscope_task_worktree_runner_report.md").write_text(render_report(summary), encoding="utf-8")
        print(json.dumps(summary, indent=2, ensure_ascii=True))
        print(f"Artifacts: {args.output_dir}")
        return 0

    args.worktree_root.mkdir(parents=True, exist_ok=True)
    pull_result = run_command(["git", "pull", "origin", args.base_branch], cwd=repo_root, proxy=args.proxy, timeout=180)
    worktree_result = run_command(
        ["git", "worktree", "add", "-b", branch, str(worktree_path), args.base_branch],
        cwd=repo_root,
        proxy=args.proxy,
        timeout=180,
    )
    codex_result: dict[str, Any]
    if worktree_result["returncode"] != 0:
        codex_result = {"summary_status": "SKIPPED", "reason": "worktree_create_failed"}
    else:
        codex_proc = run_command(codex_command, cwd=worktree_path, proxy=args.proxy, timeout=max(60, args.max_minutes * 60))
        codex_result = {
            "summary_status": "PASS" if codex_proc["returncode"] == 0 else "FAIL",
            "command": redacted_codex_command,
            "returncode": codex_proc["returncode"],
            "stdout": truncate(codex_proc.get("stdout")),
            "stderr": truncate(codex_proc.get("stderr")),
        }
    write_json(
        args.output_dir / "dualscope_task_worktree_runner_codex_exec_result.json",
        {
            "summary_status": codex_result.get("summary_status", "FAIL"),
            "pull_result": command_row("git_pull_base", pull_result),
            "worktree_result": command_row("git_worktree_add", worktree_result),
            "codex_exec": codex_result,
        },
    )

    changed_lines = porcelain_lines(worktree_path, args.proxy) if worktree_path.exists() else []
    status_after = {
        "summary_status": "PASS",
        "schema_version": "dualscope/task-worktree-runner-git-status-after-exec/v1",
        "changed_files": changed_lines,
        "has_changes": bool(changed_lines),
    }
    write_json(args.output_dir / "dualscope_task_worktree_runner_git_status_after_exec.json", status_after)

    test_rows: list[dict[str, Any]] = []
    if changed_lines:
        test_rows.append(command_row("git_diff_check", run_command(["git", "diff", "--check"], cwd=worktree_path, proxy=args.proxy, timeout=120)))
        changed_py = [path_from_porcelain(line) for line in changed_lines if path_from_porcelain(line).endswith(".py")]
        for path in changed_py:
            test_rows.append(command_row(f"py_compile:{path}", run_command(["python3", "-m", "py_compile", path], cwd=worktree_path, proxy=args.proxy, timeout=120)))
    tests_passed = all(row["passed"] for row in test_rows)
    test_results = {
        "summary_status": "PASS" if tests_passed else "FAIL",
        "schema_version": "dualscope/task-worktree-runner-test-results/v1",
        "tests": test_rows,
    }
    write_json(args.output_dir / "dualscope_task_worktree_runner_test_results.json", test_results)

    pr_number: int | None = None
    pr_url: str | None = None
    pr_result: dict[str, Any]
    if not changed_lines:
        pr_result = {"summary_status": "SKIPPED", "reason": "no_changes"}
    elif not tests_passed:
        pr_result = {"summary_status": "SKIPPED", "reason": "tests_failed"}
    else:
        add_result = run_command(["git", "add", "-A"], cwd=worktree_path, proxy=args.proxy, timeout=120)
        commit_result = run_command(["git", "commit", "-m", f"Add DualScope task package for {args.task_id}"], cwd=worktree_path, proxy=args.proxy, timeout=180)
        codex_pr_result = run_command(["./scripts/codex-pr.sh"], cwd=worktree_path, proxy=args.proxy, timeout=300)
        pr_info = extract_pr_from_codex_pr_output((codex_pr_result.get("stdout") or "") + "\n" + (codex_pr_result.get("stderr") or ""))
        pr_number = pr_info.get("number")
        pr_url = pr_info.get("url")
        pr_result = {
            "summary_status": "PASS" if codex_pr_result["returncode"] == 0 and pr_url else "FAIL",
            "git_add": command_row("git_add", add_result),
            "git_commit": command_row("git_commit", commit_result),
            "codex_pr": command_row("codex_pr", codex_pr_result),
            "created_pr_number": pr_number,
            "created_pr_url": pr_url,
            "whether_codex_review_triggered": codex_pr_result["returncode"] == 0 and "@codex review" in ((codex_pr_result.get("stderr") or "") + (codex_pr_result.get("stdout") or "")),
        }
    write_json(args.output_dir / "dualscope_task_worktree_runner_pr_creation_result.json", pr_result)

    final_status = "PASS" if codex_result.get("summary_status") == "PASS" and pr_result.get("summary_status") in {"PASS", "SKIPPED"} else "WARN"
    summary = {
        "summary_status": final_status,
        "schema_version": "dualscope/task-worktree-runner-summary/v1",
        "started_at": started,
        "completed_at": utc_now(),
        "task_id": args.task_id,
        "stop_reason": "pr_created" if pr_url else ("no_changes" if not changed_lines else "task_blocked"),
        "branch": branch,
        "worktree_path": str(worktree_path),
        "created_pr_number": pr_number,
        "created_pr_url": pr_url,
        "whether_codex_review_triggered": pr_result.get("whether_codex_review_triggered", False),
        "cleanup_allowed_after_merge": args.cleanup_worktree and not args.keep_worktree,
        "dangerous_actions": {
            "auto_merge": False,
            "force_push": False,
            "delete_branch": False,
            "remote_rewrite": False,
        },
    }
    write_json(args.output_dir / "dualscope_task_worktree_runner_summary.json", summary)
    (args.output_dir / "dualscope_task_worktree_runner_report.md").write_text(render_report(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["summary_status"] in {"PASS", "WARN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
