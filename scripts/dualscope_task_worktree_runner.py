#!/usr/bin/env python3
"""Run one selected DualScope task inside an isolated git worktree."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_task_worktree_runner/default")
DEFAULT_WORKTREE_ROOT = Path("/tmp/dualscope-worktrees")
DEFAULT_PROXY = "http://127.0.0.1:18080"
DEFAULT_EXPERIMENT_GATE_OUTPUT_DIR = Path("outputs/dualscope_experiment_execution_gate/default")
DEFAULT_EXPERIMENT_GATE_SCRIPT = Path("scripts/dualscope_experiment_execution_gate.py")
DEFAULT_CODEX_EXTRA_ARGS = "--cd {worktree_path} --full-auto"
DEFAULT_QWEN25_7B_MODEL_DIR = Path("/mnt/sda3/lh/models/qwen2p5-7b-instruct")
DEFAULT_VERDICT_REGISTRY_DIR = Path(".reports/dualscope_task_verdicts")
WORKTREE_EXEC_ENV = {
    "HF_HOME": "/mnt/sda3/lh/huggingface",
    "TRANSFORMERS_CACHE": "/mnt/sda3/lh/huggingface/transformers",
    "HF_HUB_CACHE": "/mnt/sda3/lh/huggingface/hub",
    "TMPDIR": "/mnt/sda3/lh/tmp",
    "CUDA_VISIBLE_DEVICES": "2,3",
}
TASK_NEXT_TASK_OVERRIDES = {
    "dualscope-qwen2p5-7b-first-slice-response-generation-plan": "dualscope-qwen2p5-7b-first-slice-response-generation",
}
TASK_VALIDATED_VERDICT_OVERRIDES = {
    "dualscope-qwen2p5-7b-first-slice-response-generation-plan": {
        "qwen2.5-7b first-slice response generation plan validated",
        "first-slice response generation plan validated",
        "response generation plan validated",
    },
}
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


def run_command(
    command: list[str],
    cwd: Path | None = None,
    proxy: str = DEFAULT_PROXY,
    timeout: int = 120,
    extra_env: dict[str, str] | None = None,
) -> dict[str, Any]:
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
            env=proxy_env(proxy, extra_env),
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


def is_non_fast_forward_push_failure(result: dict[str, Any]) -> bool:
    text = ((result.get("stdout") or "") + "\n" + (result.get("stderr") or "")).lower()
    return (
        result.get("returncode") != 0
        and "[rejected]" in text
        and ("fetch first" in text or "non-fast-forward" in text or "failed to push some refs" in text)
    )


def run_json_command(command: list[str], cwd: Path, proxy: str, timeout: int = 120) -> tuple[dict[str, Any], Any | None]:
    result = run_command(command, cwd=cwd, proxy=proxy, timeout=timeout)
    try:
        payload = json.loads(result.get("stdout") or "null")
    except json.JSONDecodeError:
        payload = None
    return result, payload


def run_experiment_execution_gate(worktree_path: Path, task_id: str, proxy: str) -> dict[str, Any]:
    if not worktree_path.exists():
        return {"summary_status": "SKIPPED", "reason": "worktree_missing", "execution_gate_passed": False}
    command = [
        "python3",
        str(DEFAULT_EXPERIMENT_GATE_SCRIPT),
        "--task-id",
        task_id,
        "--worktree-dir",
        str(worktree_path),
        "--output-dir",
        str(DEFAULT_EXPERIMENT_GATE_OUTPUT_DIR),
    ]
    result = run_command(command, cwd=Path.cwd(), proxy=proxy, timeout=180)
    decision_path = DEFAULT_EXPERIMENT_GATE_OUTPUT_DIR / "experiment_execution_gate_decision.json"
    try:
        decision = json.loads(decision_path.read_text(encoding="utf-8")) if decision_path.exists() else {}
    except (OSError, json.JSONDecodeError):
        decision = {}
    return {
        "summary_status": "PASS" if result["returncode"] == 0 else "FAIL",
        "schema_version": "dualscope/task-worktree-runner-experiment-execution-gate-result/v1",
        "command": command_row("experiment_execution_gate", result),
        "artifact_dir": str(DEFAULT_EXPERIMENT_GATE_OUTPUT_DIR),
        "decision": decision,
        "execution_gate_passed": bool(decision.get("execution_gate_passed")),
        "merge_allowed_by_execution_gate": bool(decision.get("merge_allowed_by_execution_gate")),
        "reason": decision.get("reason"),
    }


def has_codex_review_evidence(pr: dict[str, Any]) -> bool:
    for comment in pr.get("comments") or []:
        author = (comment.get("author") or {}).get("login", "")
        body = comment.get("body") or ""
        if "@codex review" in body or author == "chatgpt-codex-connector":
            return True
    for review in pr.get("reviews") or []:
        if (review.get("author") or {}).get("login") == "chatgpt-codex-connector":
            return True
    return False


def should_materialize_qwen_dependencies(task_id: str) -> bool:
    normalized = task_id.lower()
    return "qwen2p5-7b" in normalized and "first-slice" in normalized


def copy_file_dependency(repo_root: Path, worktree_path: Path, relative_path: str, result: dict[str, Any]) -> None:
    source = repo_root / relative_path
    destination = worktree_path / relative_path
    if not source.exists():
        result["missing_dependencies"].append(relative_path)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    result["copied_files"].append(relative_path)


def copy_dir_dependency(repo_root: Path, worktree_path: Path, relative_path: str, result: dict[str, Any]) -> None:
    source = repo_root / relative_path
    destination = worktree_path / relative_path
    if not source.exists() or not source.is_dir():
        result["missing_dependencies"].append(relative_path)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, dirs_exist_ok=True)
    result["copied_dirs"].append(relative_path)


def create_model_symlink(worktree_path: Path, result: dict[str, Any]) -> None:
    target = DEFAULT_QWEN25_7B_MODEL_DIR
    relative_path = "models/qwen2p5-7b-instruct"
    destination = worktree_path / relative_path
    if not target.exists() or not target.is_dir():
        result["missing_dependencies"].append(str(target))
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        if destination.is_symlink() or destination.is_file():
            destination.unlink()
        elif destination.is_dir():
            result["blocker_if_any"] = f"Cannot replace existing non-symlink model directory: {relative_path}"
            return
    destination.symlink_to(target, target_is_directory=True)
    result["symlinks_created"].append({"path": relative_path, "target": str(target), "resolved": str(destination.resolve())})


def ensure_exec_env_dirs(result: dict[str, Any]) -> None:
    for key in ("HF_HOME", "TRANSFORMERS_CACHE", "HF_HUB_CACHE", "TMPDIR"):
        path = Path(WORKTREE_EXEC_ENV[key])
        try:
            path.mkdir(parents=True, exist_ok=True)
            result["env_dirs_ready"].append({"name": key, "path": str(path), "exists": path.exists(), "writable": os.access(path, os.W_OK)})
        except OSError as exc:
            result["missing_dependencies"].append(str(path))
            result["env_dirs_ready"].append({"name": key, "path": str(path), "exists": path.exists(), "writable": False, "error": str(exc)})


def materialize_worktree_dependencies(
    repo_root: Path,
    worktree_path: Path,
    task_id: str,
    enabled: bool,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "summary_status": "PASS",
        "schema_version": "dualscope/worktree-dependency-materialization/v1",
        "task_id": task_id,
        "enabled": enabled,
        "worktree_path": str(worktree_path),
        "copied_files": [],
        "copied_dirs": [],
        "symlinks_created": [],
        "generated_dependencies": [],
        "missing_dependencies": [],
        "env": WORKTREE_EXEC_ENV,
        "env_dirs_ready": [],
        "blocker_if_any": None,
    }
    if not enabled:
        result["summary_status"] = "SKIPPED"
        result["reason"] = "dependency_materialization_disabled"
        return result
    if not should_materialize_qwen_dependencies(task_id):
        result["summary_status"] = "SKIPPED"
        result["reason"] = "no_known_ignored_dependencies_for_task"
        return result

    ensure_exec_env_dirs(result)
    for relative_path in (
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl",
    ):
        copy_file_dependency(repo_root, worktree_path, relative_path, result)

    for relative_path in (
        "outputs/dualscope_first_slice_target_response_generation_plan/default",
        "outputs/dualscope_main_model_axis_upgrade_plan/default",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default",
    ):
        copy_dir_dependency(repo_root, worktree_path, relative_path, result)

    create_model_symlink(worktree_path, result)
    if result["missing_dependencies"] or result["blocker_if_any"]:
        result["summary_status"] = "BLOCKED"
        if not result["blocker_if_any"]:
            result["blocker_if_any"] = "One or more required ignored worktree dependencies are missing."
    return result


def render_dependency_report(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# DualScope Worktree Dependency Materialization",
            "",
            f"- Task: `{result.get('task_id')}`",
            f"- Status: `{result.get('summary_status')}`",
            f"- Copied files: `{len(result.get('copied_files') or [])}`",
            f"- Copied dirs: `{len(result.get('copied_dirs') or [])}`",
            f"- Symlinks created: `{len(result.get('symlinks_created') or [])}`",
            f"- Missing dependencies: `{len(result.get('missing_dependencies') or [])}`",
            f"- Blocker: `{result.get('blocker_if_any')}`",
            "",
        ]
    )


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


def is_validated_verdict(task_id: str, verdict: str | None) -> bool:
    if not verdict:
        return False
    normalized = verdict.strip().lower()
    if normalized in TASK_VALIDATED_VERDICT_OVERRIDES.get(task_id, set()):
        return True
    return "validated" in normalized and "partially" not in normalized and "not validated" not in normalized


def find_output_verdict(worktree_path: Path, task_id: str) -> dict[str, Any] | None:
    outputs_dir = worktree_path / "outputs"
    if not outputs_dir.exists():
        return None
    task_token = task_id.replace("-", "_")
    candidates = sorted(outputs_dir.glob("**/*verdict.json"))
    preferred = [path for path in candidates if task_token in str(path)]
    for path in preferred + [path for path in candidates if path not in preferred]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        verdict = extract_verdict(payload)
        if verdict:
            return {"path": path, "verdict": verdict}
    return None


def persist_task_verdict_registry(worktree_path: Path, task_id: str, proxy: str) -> dict[str, Any]:
    output_verdict = find_output_verdict(worktree_path, task_id)
    registry_dir = worktree_path / DEFAULT_VERDICT_REGISTRY_DIR
    registry_path = registry_dir / f"{task_id}.json"
    result: dict[str, Any] = {
        "summary_status": "SKIPPED",
        "schema_version": "dualscope/task-verdict-registry-persistence/v1",
        "task_id": task_id,
        "registry_path": str(registry_path.relative_to(worktree_path)),
        "source_output_dir": None,
        "verdict": None,
        "validated": False,
        "next_task": TASK_NEXT_TASK_OVERRIDES.get(task_id),
    }
    if not output_verdict:
        result["reason"] = "no_output_verdict_found"
        return result

    commit_result = run_command(["git", "rev-parse", "HEAD"], cwd=worktree_path, proxy=proxy, timeout=60)
    source_path = output_verdict["path"]
    verdict = output_verdict["verdict"]
    payload = {
        "task_id": task_id,
        "verdict": verdict,
        "source_output_dir": str(source_path.parent.relative_to(worktree_path)),
        "commit": (commit_result.get("stdout") or "").strip() or None,
        "created_at": utc_now(),
        "validated": is_validated_verdict(task_id, verdict),
        "next_task": TASK_NEXT_TASK_OVERRIDES.get(task_id),
    }
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    result.update(
        {
            "summary_status": "PASS",
            "source_output_dir": payload["source_output_dir"],
            "verdict": verdict,
            "validated": payload["validated"],
            "commit": payload["commit"],
        }
    )
    return result


def detect_existing_pr_for_branch(
    branch: str,
    base_branch: str,
    changed_paths: list[str],
    worktree_path: Path,
    proxy: str,
) -> dict[str, Any]:
    result, payload = run_json_command(
        [
            "gh",
            "pr",
            "list",
            "--head",
            branch,
            "--state",
            "open",
            "--json",
            "number,title,url,headRefName,headRefOid,baseRefName,reviewDecision,statusCheckRollup,files,reviews,comments",
        ],
        cwd=worktree_path,
        proxy=proxy,
        timeout=120,
    )
    prs = payload if isinstance(payload, list) else []
    current_head = run_command(["git", "rev-parse", "HEAD"], cwd=worktree_path, proxy=proxy, timeout=60)
    current_head_oid = (current_head.get("stdout") or "").strip()
    changed_set = set(changed_paths)

    selected: dict[str, Any] | None = None
    selected_analysis: dict[str, Any] | None = None
    for pr in prs:
        pr_file_set = {item.get("path") for item in pr.get("files") or [] if item.get("path")}
        branch_matches = pr.get("headRefName") == branch
        base_matches = pr.get("baseRefName") == base_branch
        commit_matches = bool(current_head_oid) and pr.get("headRefOid") == current_head_oid
        diff_scope_matches = bool(changed_set) and bool(pr_file_set) and (changed_set == pr_file_set or changed_set.issubset(pr_file_set))
        analysis = {
            "branch_matches": branch_matches,
            "base_matches": base_matches,
            "current_head_oid": current_head_oid,
            "pr_head_oid": pr.get("headRefOid"),
            "commit_matches": commit_matches,
            "changed_paths": sorted(changed_set),
            "pr_files": sorted(pr_file_set),
            "diff_scope_matches": diff_scope_matches,
            "codex_review_evidence": has_codex_review_evidence(pr),
        }
        if branch_matches and base_matches and (commit_matches or diff_scope_matches):
            selected = pr
            selected_analysis = analysis
            break
        if selected is None:
            selected = pr
            selected_analysis = analysis

    usable = bool(
        selected
        and selected_analysis
        and selected_analysis["branch_matches"]
        and selected_analysis["base_matches"]
        and (selected_analysis["commit_matches"] or selected_analysis["diff_scope_matches"])
    )
    return {
        "summary_status": "PASS" if usable else ("WARN" if selected else "FAIL"),
        "schema_version": "dualscope/task-worktree-runner-existing-pr-check/v1",
        "command": command_row("gh_pr_list_head", result),
        "git_rev_parse_head": command_row("git_rev_parse_head", current_head),
        "branch": branch,
        "base_branch": base_branch,
        "existing_pr_detected": bool(selected),
        "existing_pr_usable": usable,
        "existing_pr_number": selected.get("number") if selected else None,
        "existing_pr_url": selected.get("url") if selected else None,
        "existing_pr_head_ref": selected.get("headRefName") if selected else None,
        "existing_pr_head_oid": selected.get("headRefOid") if selected else None,
        "analysis": selected_analysis,
        "raw_pr_count": len(prs),
    }


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
    parser.add_argument(
        "--materialize-dependencies",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Copy ignored data/output dependencies and model bindings into task worktrees before codex exec. Default: enabled.",
    )
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
            f"- PR: `{summary.get('task_pr_url') or summary.get('created_pr_url') or summary.get('existing_pr_url')}`",
            f"- PR source: `{summary.get('task_pr_source')}`",
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
        "materialize_dependencies": args.materialize_dependencies,
        "worktree_exec_env": WORKTREE_EXEC_ENV,
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
            "dualscope_task_worktree_runner_existing_pr_check.json",
            "dualscope_task_worktree_runner_push_result.json",
            "dualscope_task_worktree_runner_test_results.json",
            "dualscope_worktree_dependency_materialization.json",
            "dualscope_task_worktree_runner_verdict_registry_result.json",
            "dualscope_task_worktree_runner_experiment_execution_gate_result.json",
        ]:
            write_json(args.output_dir / name, {"summary_status": "SKIPPED", "reason": summary["stop_reason"]})
        (args.output_dir / "dualscope_worktree_dependency_materialization_report.md").write_text(
            render_dependency_report({"task_id": args.task_id, "summary_status": "SKIPPED", "blocker_if_any": summary["stop_reason"]}),
            encoding="utf-8",
        )
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
            "dualscope_task_worktree_runner_existing_pr_check.json",
            "dualscope_task_worktree_runner_push_result.json",
            "dualscope_task_worktree_runner_test_results.json",
            "dualscope_worktree_dependency_materialization.json",
            "dualscope_task_worktree_runner_verdict_registry_result.json",
            "dualscope_task_worktree_runner_experiment_execution_gate_result.json",
        ]:
            write_json(args.output_dir / name, {"summary_status": "SKIPPED", "reason": "dry_run"})
        (args.output_dir / "dualscope_worktree_dependency_materialization_report.md").write_text(
            render_dependency_report({"task_id": args.task_id, "summary_status": "SKIPPED", "blocker_if_any": "dry_run"}),
            encoding="utf-8",
        )
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
    materialization: dict[str, Any] = {"summary_status": "SKIPPED", "reason": "worktree_create_failed"}
    if worktree_result["returncode"] != 0:
        codex_result = {"summary_status": "SKIPPED", "reason": "worktree_create_failed"}
    else:
        materialization = materialize_worktree_dependencies(repo_root, worktree_path, args.task_id, args.materialize_dependencies)
        if materialization.get("summary_status") == "BLOCKED":
            codex_result = {"summary_status": "SKIPPED", "reason": "dependency_materialization_blocker"}
        else:
            codex_proc = run_command(
                codex_command,
                cwd=worktree_path,
                proxy=args.proxy,
                timeout=max(60, args.max_minutes * 60),
                extra_env=WORKTREE_EXEC_ENV,
            )
            codex_result = {
                "summary_status": "PASS" if codex_proc["returncode"] == 0 else "FAIL",
                "command": redacted_codex_command,
                "returncode": codex_proc["returncode"],
                "stdout": truncate(codex_proc.get("stdout")),
                "stderr": truncate(codex_proc.get("stderr")),
                "exec_environment": WORKTREE_EXEC_ENV,
            }
    write_json(args.output_dir / "dualscope_worktree_dependency_materialization.json", materialization)
    (args.output_dir / "dualscope_worktree_dependency_materialization_report.md").write_text(
        render_dependency_report(materialization),
        encoding="utf-8",
    )
    write_json(
        args.output_dir / "dualscope_task_worktree_runner_codex_exec_result.json",
        {
            "summary_status": codex_result.get("summary_status", "FAIL"),
            "pull_result": command_row("git_pull_base", pull_result),
            "worktree_result": command_row("git_worktree_add", worktree_result),
            "dependency_materialization": materialization,
            "codex_exec": codex_result,
        },
    )

    experiment_gate_result = (
        run_experiment_execution_gate(worktree_path, args.task_id, args.proxy)
        if worktree_path.exists() and codex_result.get("summary_status") == "PASS"
        else {"summary_status": "SKIPPED", "reason": codex_result.get("reason") or "codex_exec_not_passed"}
    )
    write_json(args.output_dir / "dualscope_task_worktree_runner_experiment_execution_gate_result.json", experiment_gate_result)
    experiment_gate_passed = bool(
        experiment_gate_result.get("summary_status") in {"PASS", "SKIPPED"}
        and experiment_gate_result.get("decision", {}).get("merge_allowed_by_execution_gate", True)
    )

    verdict_registry_result = (
        persist_task_verdict_registry(worktree_path, args.task_id, args.proxy)
        if worktree_path.exists() and codex_result.get("summary_status") == "PASS" and experiment_gate_passed
        else {
            "summary_status": "SKIPPED",
            "reason": (
                "experiment_execution_gate_failed"
                if codex_result.get("summary_status") == "PASS" and not experiment_gate_passed
                else codex_result.get("reason") or "codex_exec_not_passed"
            ),
        }
    )
    write_json(args.output_dir / "dualscope_task_worktree_runner_verdict_registry_result.json", verdict_registry_result)

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
    existing_pr_number: int | None = None
    existing_pr_url: str | None = None
    task_pr_number: int | None = None
    task_pr_url: str | None = None
    task_pr_source: str | None = None
    push_non_fast_forward_handled = False
    whether_codex_review_triggered = False
    pr_result: dict[str, Any]
    push_result: dict[str, Any] = {"summary_status": "SKIPPED", "reason": "no_push_attempted"}
    existing_pr_check: dict[str, Any] = {"summary_status": "SKIPPED", "reason": "not_needed"}
    changed_paths = [path_from_porcelain(line) for line in changed_lines]
    if not changed_lines:
        pr_result = {"summary_status": "SKIPPED", "reason": "no_changes"}
    elif not tests_passed:
        pr_result = {"summary_status": "SKIPPED", "reason": "tests_failed"}
    elif not experiment_gate_passed:
        pr_result = {
            "summary_status": "SKIPPED",
            "reason": "experiment_execution_gate_failed",
            "experiment_execution_gate": experiment_gate_result,
        }
    else:
        add_result = run_command(["git", "add", "-A"], cwd=worktree_path, proxy=args.proxy, timeout=120)
        commit_result = run_command(["git", "commit", "-m", f"Add DualScope task package for {args.task_id}"], cwd=worktree_path, proxy=args.proxy, timeout=180)
        codex_pr_result = run_command(["./scripts/codex-pr.sh"], cwd=worktree_path, proxy=args.proxy, timeout=300)
        pr_info = extract_pr_from_codex_pr_output((codex_pr_result.get("stdout") or "") + "\n" + (codex_pr_result.get("stderr") or ""))
        pr_number = pr_info.get("number")
        pr_url = pr_info.get("url")
        non_fast_forward = is_non_fast_forward_push_failure(codex_pr_result)
        push_result = {
            "summary_status": "PASS" if codex_pr_result["returncode"] == 0 else ("WARN" if non_fast_forward else "FAIL"),
            "schema_version": "dualscope/task-worktree-runner-push-result/v1",
            "codex_pr": command_row("codex_pr", codex_pr_result),
            "non_fast_forward": non_fast_forward,
            "push_non_fast_forward_handled": False,
        }
        if pr_url:
            task_pr_number = pr_number
            task_pr_url = pr_url
            task_pr_source = "created"
            whether_codex_review_triggered = "@codex review" in ((codex_pr_result.get("stderr") or "") + (codex_pr_result.get("stdout") or ""))
        elif non_fast_forward:
            existing_pr_check = detect_existing_pr_for_branch(branch, args.base_branch, changed_paths, worktree_path, args.proxy)
            if existing_pr_check.get("existing_pr_usable"):
                existing_pr_number = existing_pr_check.get("existing_pr_number")
                existing_pr_url = existing_pr_check.get("existing_pr_url")
                task_pr_number = existing_pr_number
                task_pr_url = existing_pr_url
                task_pr_source = "existing"
                push_non_fast_forward_handled = True
                push_result["push_non_fast_forward_handled"] = True
                whether_codex_review_triggered = bool(existing_pr_check.get("analysis", {}).get("codex_review_evidence"))
        pr_result = {
            "summary_status": "PASS" if task_pr_url else "FAIL",
            "git_add": command_row("git_add", add_result),
            "git_commit": command_row("git_commit", commit_result),
            "codex_pr": command_row("codex_pr", codex_pr_result),
            "created_pr_number": pr_number,
            "created_pr_url": pr_url,
            "existing_pr_detected": existing_pr_check.get("existing_pr_detected", False),
            "existing_pr_number": existing_pr_number,
            "existing_pr_url": existing_pr_url,
            "task_pr_number": task_pr_number,
            "task_pr_url": task_pr_url,
            "task_pr_source": task_pr_source,
            "push_non_fast_forward_handled": push_non_fast_forward_handled,
            "whether_codex_review_triggered": whether_codex_review_triggered,
        }
    write_json(args.output_dir / "dualscope_task_worktree_runner_push_result.json", push_result)
    write_json(args.output_dir / "dualscope_task_worktree_runner_existing_pr_check.json", existing_pr_check)
    write_json(args.output_dir / "dualscope_task_worktree_runner_pr_creation_result.json", pr_result)

    final_status = "PASS" if codex_result.get("summary_status") == "PASS" and pr_result.get("summary_status") in {"PASS", "SKIPPED"} else "WARN"
    summary = {
        "summary_status": final_status,
        "schema_version": "dualscope/task-worktree-runner-summary/v1",
        "started_at": started,
        "completed_at": utc_now(),
        "task_id": args.task_id,
        "stop_reason": "task_pr_ready" if task_pr_url else ("no_changes" if not changed_lines else "task_blocked"),
        "branch": branch,
        "worktree_path": str(worktree_path),
        "created_pr_number": pr_number,
        "created_pr_url": pr_url,
        "existing_pr_detected": existing_pr_check.get("existing_pr_detected", False),
        "existing_pr_number": existing_pr_number,
        "existing_pr_url": existing_pr_url,
        "task_pr_number": task_pr_number,
        "task_pr_url": task_pr_url,
        "task_pr_source": task_pr_source,
        "push_non_fast_forward_handled": push_non_fast_forward_handled,
        "dependency_materialization_status": materialization.get("summary_status"),
        "dependency_materialization_blocker": materialization.get("blocker_if_any"),
        "verdict_registry_result": verdict_registry_result,
        "experiment_execution_gate_result": experiment_gate_result,
        "experiment_execution_gate_passed": experiment_gate_passed,
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
