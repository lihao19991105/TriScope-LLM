#!/usr/bin/env python3
"""Check whether one DualScope PR is safe to merge, and optionally merge it."""

from __future__ import annotations

import argparse
import base64
import fnmatch
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_experiment_execution_gate_common import EXECUTION_REQUIRED_TASKS


DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_safe_pr_merge_gate/default")
DEFAULT_PROXY = "http://127.0.0.1:18080"
DEFAULT_EXECUTION_GATE_DECISION_PATH = Path("outputs/dualscope_experiment_execution_gate/default/experiment_execution_gate_decision.json")
DETAIL_FIELDS = "number,title,url,state,reviewDecision,statusCheckRollup,reviews,comments,headRefName,baseRefName,files"
FAIL_CONCLUSIONS = {"FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE"}
PENDING_STATUSES = {"QUEUED", "IN_PROGRESS", "PENDING", "REQUESTED", "WAITING", "EXPECTED"}
DEFAULT_ALLOWED_PATTERNS = [
    ".plans/dualscope-*",
    "src/eval/dualscope_*",
    "src/eval/post_dualscope_*",
    "scripts/build_dualscope_*",
    "scripts/build_post_dualscope_*",
    "scripts/run_dualscope_*",
    "scripts/check_dualscope_*",
    "scripts/dualscope_*",
    "scripts/codex_smart_exec.sh",
    "docs/dualscope_*",
    "configs/codex_smart_effort_map.json",
    ".reports/dualscope_task_verdicts/*.json",
    "DUALSCOPE_MASTER_PLAN.md",
    "DUALSCOPE_TASK_QUEUE.md",
    "PLANS.md",
    "README.md",
    "requirements.txt",
]
DEFAULT_ALLOWED_OUTPUT_ARTIFACT_PATTERNS = [
    "outputs/dualscope_main_model_axis_upgrade_plan/default/*",
    "outputs/dualscope_main_model_axis_upgrade_plan_analysis/default/*",
    "outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/*",
    "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default/*",
    "outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default/*",
    "outputs/dualscope_qwen2p5_7b_first_slice_result_package/default/*",
    "outputs/dualscope_sci3_main_experiment_expansion_plan/default/*",
    "outputs/dualscope_cross_model_validation_plan/default/*",
    "outputs/dualscope_advbench_small_slice_response_generation_plan/default/*",
    "outputs/dualscope_advbench_small_slice_response_generation/default/*",
    "outputs/dualscope_advbench_small_slice_metric_computation/default/*",
    "outputs/dualscope_advbench_small_slice_result_package/default/*",
    "outputs/dualscope_jbb_small_slice_materialization/default/*",
    "outputs/dualscope_jbb_small_slice_response_generation_plan/default/*",
    "outputs/dualscope_jbb_small_slice_response_generation/default/*",
    "outputs/dualscope_jbb_small_slice_metric_computation/default/*",
    "outputs/dualscope_jbb_small_slice_result_package/default/*",
    "outputs/dualscope_sci3_expanded_result_synthesis_package/default/*",
]
DEFAULT_ALLOWED_PATTERNS.extend(DEFAULT_ALLOWED_OUTPUT_ARTIFACT_PATTERNS)
BENIGN_GATE_PATH_EXCEPTIONS = {
    "docs/dualscope_autorun_worktree_and_merge_gate.md",
    "docs/dualscope_experiment_execution_gate.md",
    "scripts/dualscope_experiment_execution_gate.py",
    "scripts/dualscope_safe_pr_merge_gate.py",
    "src/eval/dualscope_experiment_execution_gate_common.py",
}
DEFAULT_FORBIDDEN_PATTERNS = [
    ".env",
    ".env.*",
    "*secret*",
    "*credential*",
    "*token*",
    "*benchmark_truth*",
    "*benchmark-truth*",
    "*gate*",
    "*route_c*199*",
    "*route-c*199*",
    ".gitmodules",
    ".ssh/*",
]
CODEX_ACTOR_MARKERS = ("codex", "chatgpt-codex", "openai-codex")
CODEX_REVIEW_PHRASES = (
    "didn't find any major issues",
    "did not find any major issues",
    "no major issues",
)
ADV_BENCH_SMALL_SLICE_PATH = "data/advbench/small_slice/advbench_small_slice_source.jsonl"
ADV_BENCH_SMALL_SLICE_SOURCE_DATASET = "walledai/AdvBench"
ADV_BENCH_SMALL_SLICE_MAX_ROWS = 32
ADV_BENCH_SMALL_SLICE_REQUIRED_FIELDS = {
    "sample_id",
    "dataset_id",
    "instruction",
    "input",
    "source_dataset",
    "source_split",
    "source_index",
}
ADV_BENCH_SMALL_SLICE_RESPONSE_FIELDS = {"reference_response", "expected_behavior"}
JBB_SMALL_SLICE_PATH = "data/jbb/small_slice/jbb_small_slice_source.jsonl"
JBB_SMALL_SLICE_SOURCE_DATASET = "JailbreakBench/JBB-Behaviors"
JBB_SMALL_SLICE_MAX_ROWS = 32
JBB_SMALL_SLICE_REQUIRED_FIELDS = {
    "sample_id",
    "dataset_id",
    "source_dataset",
    "source_url",
    "source_split",
    "source_index",
    "behavior_category",
    "behavior_text",
    "trigger_family",
    "trigger_text",
    "target_family",
    "target_descriptor",
    "split",
    "license_status",
    "safety_notes",
    "readiness_notes",
}
JBB_SMALL_SLICE_FALSE_FIELDS = {
    "benchmark_truth_changed",
    "data_fabricated",
    "model_output_fabricated",
    "model_response_fabricated",
    "labels_fabricated",
    "logprobs_fabricated",
    "metrics_fabricated",
}
BENCHMARK_TRUTH_MUTATION_MARKERS = {
    "benchmark truth mutation",
    "benchmark_truth_mutation",
    "benchmark-truth-mutation",
    "benchmark truth mutated",
    "benchmark_truth_mutated",
    "benchmark-truth-mutated",
    "truth mutation",
    "truth_mutation",
    "truth-mutated",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def truncate(value: str | None, limit: int = 4000) -> str:
    text = value or ""
    return text if len(text) <= limit else text[:limit] + "..."


def proxy_env(proxy: str) -> dict[str, str]:
    env = os.environ.copy()
    env["HTTP_PROXY"] = proxy
    env["HTTPS_PROXY"] = proxy
    env["ALL_PROXY"] = proxy
    return env


def run_command(command: list[str], proxy: str, timeout: int = 120) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=proxy_env(proxy),
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except FileNotFoundError as exc:
        return {"command": command, "returncode": 127, "stdout": "", "stderr": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"Command timed out after {timeout}s.",
        }


def parse_csv_patterns(values: list[str] | None, defaults: list[str]) -> list[str]:
    if not values:
        return defaults
    patterns: list[str] = []
    for value in values:
        patterns.extend([item.strip() for item in value.split(",") if item.strip()])
    return patterns or defaults


def infer_repo_full_name(proxy: str) -> str | None:
    result = run_command(["git", "remote", "get-url", "origin"], proxy=proxy, timeout=60)
    if result["returncode"] != 0:
        return None
    remote = (result.get("stdout") or "").strip()
    https_match = re.search(r"github\.com[:/]([^/\s]+)/([^/\s]+?)(?:\.git)?$", remote)
    if not https_match:
        return None
    return f"{https_match.group(1)}/{https_match.group(2)}"


def is_benign_gate_path_exception(path: str) -> bool:
    return (
        path in BENIGN_GATE_PATH_EXCEPTIONS
        or fnmatch.fnmatch(path, ".plans/dualscope-safe-merge-gate-*.md")
        or path == ".plans/dualscope-experiment-execution-gate.md"
    )


def fetch_pr_file_json(path: str, head_ref: str | None, repo_full_name: str | None, proxy: str) -> dict[str, Any] | None:
    if not head_ref or not repo_full_name:
        return None
    result = run_command(
        ["gh", "api", f"repos/{repo_full_name}/contents/{path}", "--method", "GET", "-f", f"ref={head_ref}"],
        proxy=proxy,
        timeout=120,
    )
    if result["returncode"] != 0:
        return None
    try:
        payload = json.loads(result.get("stdout") or "{}")
        content = str(payload.get("content") or "").replace("\n", "")
        decoded = base64.b64decode(content).decode("utf-8")
        parsed = json.loads(decoded)
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else None


def fetch_pr_file_text(path: str, head_ref: str | None, repo_full_name: str | None, proxy: str) -> str | None:
    if not head_ref or not repo_full_name:
        return None
    result = run_command(
        ["gh", "api", f"repos/{repo_full_name}/contents/{path}", "--method", "GET", "-f", f"ref={head_ref}"],
        proxy=proxy,
        timeout=120,
    )
    if result["returncode"] != 0:
        return None
    try:
        payload = json.loads(result.get("stdout") or "{}")
        content = str(payload.get("content") or "").replace("\n", "")
        return base64.b64decode(content).decode("utf-8")
    except Exception:
        return None


def validate_verdict_registry_file(path: str, pr: dict[str, Any], repo_full_name: str | None, proxy: str) -> dict[str, Any]:
    row: dict[str, Any] = {"path": path, "valid": False, "reason": ""}
    if not fnmatch.fnmatch(path, ".reports/dualscope_task_verdicts/*.json"):
        row["reason"] = "not_allowed_verdict_registry_path"
        return row
    payload = fetch_pr_file_json(path, pr.get("headRefName"), repo_full_name, proxy)
    if not payload:
        row["reason"] = "unable_to_fetch_or_parse_json"
        return row
    missing = [key for key in ("task_id", "verdict", "validated") if key not in payload]
    if missing:
        row["reason"] = f"missing_required_fields:{','.join(missing)}"
        row["keys"] = sorted(payload)
        return row
    if not isinstance(payload.get("validated"), bool):
        row["reason"] = "validated_field_is_not_boolean"
        return row
    row.update(
        {
            "valid": True,
            "task_id": payload.get("task_id"),
            "verdict": payload.get("verdict"),
            "validated": payload.get("validated"),
        }
    )
    return row


def iter_json_string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        values: list[str] = []
        for key, item in value.items():
            values.append(str(key))
            values.extend(iter_json_string_values(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(iter_json_string_values(item))
        return values
    return []


def has_benchmark_truth_mutation_marker(row: dict[str, Any]) -> bool:
    for value in iter_json_string_values(row):
        lowered = value.lower()
        if any(marker in lowered for marker in BENCHMARK_TRUTH_MUTATION_MARKERS):
            return True
    return False


def validate_advbench_small_slice_file(
    path: str,
    pr: dict[str, Any],
    repo_full_name: str | None,
    proxy: str,
) -> dict[str, Any]:
    check: dict[str, Any] = {
        "path": path,
        "valid": False,
        "schema_valid": False,
        "reason": "",
        "row_count": 0,
        "max_rows": ADV_BENCH_SMALL_SLICE_MAX_ROWS,
        "source_dataset": None,
        "required_fields": sorted(ADV_BENCH_SMALL_SLICE_REQUIRED_FIELDS),
        "required_one_of_fields": sorted(ADV_BENCH_SMALL_SLICE_RESPONSE_FIELDS),
    }
    if path != ADV_BENCH_SMALL_SLICE_PATH:
        check["reason"] = "not_authorized_advbench_small_slice_path"
        return check
    if not path.endswith(".jsonl"):
        check["reason"] = "advbench_small_slice_not_jsonl"
        return check

    content = fetch_pr_file_text(path, pr.get("headRefName"), repo_full_name, proxy)
    if content is None:
        check["reason"] = "unable_to_fetch_advbench_small_slice"
        return check

    lines = content.splitlines()
    check["row_count"] = len(lines)
    if len(lines) > ADV_BENCH_SMALL_SLICE_MAX_ROWS:
        check["reason"] = "advbench_small_slice_row_count_exceeds_32"
        return check

    source_datasets: set[str] = set()
    row_errors: list[dict[str, Any]] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            row_errors.append({"line": index, "reason": "blank_line"})
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            row_errors.append({"line": index, "reason": "invalid_json", "detail": str(exc)})
            continue
        if not isinstance(parsed, dict):
            row_errors.append({"line": index, "reason": "json_row_not_object"})
            continue
        missing = sorted(ADV_BENCH_SMALL_SLICE_REQUIRED_FIELDS.difference(parsed))
        if missing:
            row_errors.append({"line": index, "reason": "missing_required_fields", "fields": missing})
        if not any(field in parsed for field in ADV_BENCH_SMALL_SLICE_RESPONSE_FIELDS):
            row_errors.append({"line": index, "reason": "missing_reference_response_or_expected_behavior"})
        source_dataset = parsed.get("source_dataset")
        source_datasets.add(str(source_dataset))
        if source_dataset != ADV_BENCH_SMALL_SLICE_SOURCE_DATASET:
            row_errors.append(
                {
                    "line": index,
                    "reason": "invalid_source_dataset",
                    "source_dataset": source_dataset,
                }
            )
        if has_benchmark_truth_mutation_marker(parsed):
            row_errors.append({"line": index, "reason": "benchmark_truth_mutation_marker_present"})

    check["source_dataset"] = ADV_BENCH_SMALL_SLICE_SOURCE_DATASET if source_datasets == {ADV_BENCH_SMALL_SLICE_SOURCE_DATASET} else sorted(source_datasets)
    if row_errors:
        check["reason"] = "advbench_small_slice_schema_invalid"
        check["row_errors"] = row_errors[:20]
        check["row_error_count"] = len(row_errors)
        return check

    check["valid"] = True
    check["schema_valid"] = True
    check["reason"] = "advbench_small_slice_valid"
    return check


def validate_jbb_small_slice_file(
    path: str,
    pr: dict[str, Any],
    repo_full_name: str | None,
    proxy: str,
) -> dict[str, Any]:
    check: dict[str, Any] = {
        "path": path,
        "valid": False,
        "schema_valid": False,
        "reason": "",
        "row_count": 0,
        "max_rows": JBB_SMALL_SLICE_MAX_ROWS,
        "source_dataset": None,
        "required_fields": sorted(JBB_SMALL_SLICE_REQUIRED_FIELDS),
        "false_fields": sorted(JBB_SMALL_SLICE_FALSE_FIELDS),
    }
    if path != JBB_SMALL_SLICE_PATH:
        check["reason"] = "not_authorized_jbb_small_slice_path"
        return check
    if not path.endswith(".jsonl"):
        check["reason"] = "jbb_small_slice_not_jsonl"
        return check

    content = fetch_pr_file_text(path, pr.get("headRefName"), repo_full_name, proxy)
    if content is None:
        check["reason"] = "unable_to_fetch_jbb_small_slice"
        return check

    lines = content.splitlines()
    check["row_count"] = len(lines)
    if len(lines) > JBB_SMALL_SLICE_MAX_ROWS:
        check["reason"] = "jbb_small_slice_row_count_exceeds_32"
        return check

    source_datasets: set[str] = set()
    row_errors: list[dict[str, Any]] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            row_errors.append({"line": index, "reason": "blank_line"})
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            row_errors.append({"line": index, "reason": "invalid_json", "detail": str(exc)})
            continue
        if not isinstance(parsed, dict):
            row_errors.append({"line": index, "reason": "json_row_not_object"})
            continue
        missing = sorted(JBB_SMALL_SLICE_REQUIRED_FIELDS.difference(parsed))
        if missing:
            row_errors.append({"line": index, "reason": "missing_required_fields", "fields": missing})
        source_dataset = parsed.get("source_dataset")
        source_datasets.add(str(source_dataset))
        if source_dataset != JBB_SMALL_SLICE_SOURCE_DATASET:
            row_errors.append(
                {
                    "line": index,
                    "reason": "invalid_source_dataset",
                    "source_dataset": source_dataset,
                }
            )
        true_flags = sorted(field for field in JBB_SMALL_SLICE_FALSE_FIELDS if parsed.get(field) is True)
        if true_flags:
            row_errors.append({"line": index, "reason": "forbidden_true_flag", "fields": true_flags})
        if has_benchmark_truth_mutation_marker(parsed):
            row_errors.append({"line": index, "reason": "benchmark_truth_mutation_marker_present"})

    check["source_dataset"] = JBB_SMALL_SLICE_SOURCE_DATASET if source_datasets == {JBB_SMALL_SLICE_SOURCE_DATASET} else sorted(source_datasets)
    if row_errors:
        check["reason"] = "jbb_small_slice_schema_invalid"
        check["row_errors"] = row_errors[:20]
        check["row_error_count"] = len(row_errors)
        return check

    check["valid"] = True
    check["schema_valid"] = True
    check["reason"] = "jbb_small_slice_valid"
    return check


def gh_pr_view(pr: int, repo: str | None, proxy: str) -> dict[str, Any]:
    command = ["gh", "pr", "view", str(pr), "--json", DETAIL_FIELDS]
    if repo:
        command.extend(["-R", repo])
    result = run_command(command, proxy=proxy, timeout=180)
    if result["returncode"] != 0:
        raise RuntimeError(result["stderr"] or result["stdout"] or f"Failed to read PR #{pr}")
    payload = json.loads(result["stdout"] or "{}")
    if not isinstance(payload, dict):
        raise RuntimeError(f"Unexpected gh pr view payload for PR #{pr}")
    return payload


def actor_login(item: dict[str, Any]) -> str:
    author = item.get("author")
    return str(author.get("login") or "") if isinstance(author, dict) else ""


def short_excerpt(value: str | None, limit: int = 240) -> str:
    text = " ".join((value or "").split())
    return text if len(text) <= limit else text[:limit] + "..."


def is_codex_actor(login: str) -> bool:
    lowered = login.lower()
    return any(marker in lowered for marker in CODEX_ACTOR_MARKERS)


def is_pure_codex_review_request(body: str) -> bool:
    normalized = " ".join(body.strip().lower().split())
    return normalized == "@codex review"


def codex_review_evidence_from_text(body: str) -> bool:
    lowered = body.lower()
    return any(phrase in lowered for phrase in CODEX_REVIEW_PHRASES)


def analyze_codex_review(pr: dict[str, Any]) -> dict[str, Any]:
    requested = False
    evidence_source = ""
    evidence_excerpt = ""

    for review in pr.get("reviews") or []:
        if not isinstance(review, dict):
            continue
        author = actor_login(review)
        body = str(review.get("body") or "")
        if is_codex_actor(author) or codex_review_evidence_from_text(body) or "codex review" in body.lower():
            evidence_source = f"review:{author or 'unknown'}"
            evidence_excerpt = short_excerpt(body)
            break

    if not evidence_source:
        for comment in pr.get("comments") or []:
            if not isinstance(comment, dict):
                continue
            author = actor_login(comment)
            body = str(comment.get("body") or "")
            lowered = body.lower()
            if "@codex review" in lowered:
                requested = True
            if is_pure_codex_review_request(body):
                continue
            if is_codex_actor(author) or codex_review_evidence_from_text(body) or "codex review" in lowered:
                evidence_source = f"comment:{author or 'unknown'}"
                evidence_excerpt = short_excerpt(body)
                break

    return {
        "codex_review_requested": requested,
        "codex_review_present": bool(evidence_source),
        "codex_review_evidence_source": evidence_source,
        "codex_review_evidence_excerpt": evidence_excerpt,
    }


def has_codex_review(pr: dict[str, Any]) -> bool:
    return bool(analyze_codex_review(pr)["codex_review_present"])


def infer_execution_task_id(pr: dict[str, Any]) -> str | None:
    for item in pr.get("files") or []:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "")
        prefix = ".reports/dualscope_task_verdicts/"
        suffix = ".json"
        if path.startswith(prefix) and path.endswith(suffix):
            return path[len(prefix) : -len(suffix)]
    for key in ("headRefName", "title"):
        text = str(pr.get(key) or "")
        for task_id in EXECUTION_REQUIRED_TASKS:
            if task_id in text:
                return task_id
    return None


def read_execution_gate_decision(path: Path, task_id: str | None) -> dict[str, Any]:
    if not task_id or task_id not in EXECUTION_REQUIRED_TASKS:
        return {
            "summary_status": "SKIPPED",
            "task_id": task_id,
            "gate_required": False,
            "execution_gate_passed": True,
            "merge_allowed_by_execution_gate": True,
            "reason": "task_not_execution_required",
            "decision_path": str(path),
        }
    if not path.exists():
        return {
            "summary_status": "FAIL",
            "task_id": task_id,
            "gate_required": True,
            "execution_gate_passed": False,
            "merge_allowed_by_execution_gate": False,
            "reason": "execution_gate_decision_missing",
            "decision_path": str(path),
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "summary_status": "FAIL",
            "task_id": task_id,
            "gate_required": True,
            "execution_gate_passed": False,
            "merge_allowed_by_execution_gate": False,
            "reason": f"execution_gate_decision_unreadable:{type(exc).__name__}",
            "decision_path": str(path),
        }
    if not isinstance(payload, dict):
        payload = {"summary_status": "FAIL", "reason": "execution_gate_decision_not_object"}
    expected_task = payload.get("task_id")
    if expected_task != task_id:
        payload = {
            **payload,
            "summary_status": "FAIL",
            "gate_required": True,
            "execution_gate_passed": False,
            "merge_allowed_by_execution_gate": False,
            "reason": f"execution_gate_task_mismatch:{expected_task!r}",
        }
    return {**payload, "decision_path": str(path)}


def count_requested_changes(pr: dict[str, Any]) -> int:
    count = 0
    if str(pr.get("reviewDecision") or "").upper() == "CHANGES_REQUESTED":
        count += 1
    for review in pr.get("reviews") or []:
        if isinstance(review, dict) and str(review.get("state") or "").upper() == "CHANGES_REQUESTED":
            count += 1
    return count


def has_requested_changes(pr: dict[str, Any]) -> bool:
    return count_requested_changes(pr) > 0


def summarize_checks(pr: dict[str, Any]) -> dict[str, Any]:
    rows = []
    failing = []
    pending = []
    for item in pr.get("statusCheckRollup") or []:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("context") or item.get("workflowName") or "unknown"
        status = str(item.get("status") or "UNKNOWN").upper()
        conclusion = str(item.get("conclusion") or "UNKNOWN").upper()
        row = {"name": name, "status": status, "conclusion": conclusion}
        rows.append(row)
        if conclusion in FAIL_CONCLUSIONS:
            failing.append(row)
        elif status in PENDING_STATUSES or conclusion == "UNKNOWN":
            pending.append(row)
    return {
        "summary_status": "PASS" if not failing else "FAIL",
        "checks": rows,
        "failing_checks": failing,
        "pending_checks": pending,
        "ci_state": "failing" if failing else ("pending" if pending else "passing_or_no_checks"),
    }


def check_file_scope(
    pr: dict[str, Any],
    allowed_patterns: list[str],
    forbidden_patterns: list[str],
    repo_full_name: str | None,
    proxy: str,
) -> dict[str, Any]:
    files = [str(item.get("path") or "") for item in pr.get("files") or [] if isinstance(item, dict)]
    rows = []
    forbidden = []
    not_allowed = []
    allowed_outputs_artifacts = []
    allowed_verdict_registry_files = []
    invalid_verdict_registry_files = []
    allowed_dualscope_docs = []
    allowed_advbench_small_slice_files = []
    advbench_small_slice_checks = []
    allowed_jbb_small_slice_files = []
    jbb_small_slice_checks = []
    for path in files:
        allowed = any(fnmatch.fnmatch(path, pattern) for pattern in allowed_patterns)
        matched_forbidden = [pattern for pattern in forbidden_patterns if fnmatch.fnmatch(path, pattern)]
        if is_benign_gate_path_exception(path):
            matched_forbidden = [pattern for pattern in matched_forbidden if pattern != "*gate*"]
        advbench_small_slice_check: dict[str, Any] | None = None
        jbb_small_slice_check: dict[str, Any] | None = None
        if path == ADV_BENCH_SMALL_SLICE_PATH:
            advbench_small_slice_check = validate_advbench_small_slice_file(path, pr, repo_full_name, proxy)
            advbench_small_slice_checks.append(advbench_small_slice_check)
            if advbench_small_slice_check["valid"]:
                allowed = True
                allowed_advbench_small_slice_files.append(path)
            else:
                matched_forbidden.append(advbench_small_slice_check["reason"])
        if path == JBB_SMALL_SLICE_PATH:
            jbb_small_slice_check = validate_jbb_small_slice_file(path, pr, repo_full_name, proxy)
            jbb_small_slice_checks.append(jbb_small_slice_check)
            if jbb_small_slice_check["valid"]:
                allowed = True
                allowed_jbb_small_slice_files.append(path)
            else:
                matched_forbidden.append(jbb_small_slice_check["reason"])
        verdict_registry_check: dict[str, Any] | None = None
        if path.startswith(".reports/"):
            verdict_registry_check = validate_verdict_registry_file(path, pr, repo_full_name, proxy)
            if verdict_registry_check["valid"]:
                allowed_verdict_registry_files.append(path)
            else:
                matched_forbidden.append(verdict_registry_check["reason"])
                invalid_verdict_registry_files.append(verdict_registry_check)
        if allowed and fnmatch.fnmatch(path, "docs/dualscope_*.md"):
            allowed_dualscope_docs.append(path)
        row = {
            "path": path,
            "allowed": allowed,
            "forbidden_patterns": matched_forbidden,
            "verdict_registry_check": verdict_registry_check,
            "advbench_small_slice_check": advbench_small_slice_check,
            "jbb_small_slice_check": jbb_small_slice_check,
        }
        rows.append(row)
        if allowed and path.startswith("outputs/"):
            allowed_outputs_artifacts.append(path)
        if matched_forbidden:
            forbidden.append(row)
        if not allowed:
            not_allowed.append(row)
    blocked_files = sorted({row["path"] for row in forbidden + not_allowed})
    file_scope_allowed = not forbidden and not not_allowed
    advbench_small_slice_check = advbench_small_slice_checks[0] if advbench_small_slice_checks else {}
    jbb_small_slice_check = jbb_small_slice_checks[0] if jbb_small_slice_checks else {}
    return {
        "summary_status": "PASS" if file_scope_allowed else "FAIL",
        "file_scope_allowed": file_scope_allowed,
        "allowed_patterns": allowed_patterns,
        "allowed_outputs_artifact_patterns": DEFAULT_ALLOWED_OUTPUT_ARTIFACT_PATTERNS,
        "allowed_outputs_artifacts": allowed_outputs_artifacts,
        "allowed_verdict_registry_files": allowed_verdict_registry_files,
        "invalid_verdict_registry_files": invalid_verdict_registry_files,
        "allowed_dualscope_docs": allowed_dualscope_docs,
        "allowed_advbench_small_slice_files": allowed_advbench_small_slice_files,
        "advbench_small_slice_checks": advbench_small_slice_checks,
        "advbench_small_slice_row_count": advbench_small_slice_check.get("row_count"),
        "advbench_small_slice_schema_valid": advbench_small_slice_check.get("schema_valid"),
        "advbench_small_slice_source_dataset": advbench_small_slice_check.get("source_dataset"),
        "allowed_jbb_small_slice_files": allowed_jbb_small_slice_files,
        "jbb_small_slice_checks": jbb_small_slice_checks,
        "jbb_small_slice_row_count": jbb_small_slice_check.get("row_count"),
        "jbb_small_slice_schema_valid": jbb_small_slice_check.get("schema_valid"),
        "jbb_small_slice_source_dataset": jbb_small_slice_check.get("source_dataset"),
        "forbidden_patterns": forbidden_patterns,
        "files": rows,
        "forbidden_files": forbidden,
        "not_allowed_files": not_allowed,
        "blocked_files": blocked_files,
        "blocked_data_files": sorted(path for path in blocked_files if path.startswith("data/")),
    }


def bool_arg(value: str) -> bool:
    lowered = value.lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected boolean, got {value!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safely check and optionally squash-merge one DualScope PR.")
    parser.add_argument("--pr", type=int, required=True, help="Pull request number to inspect.")
    parser.add_argument("--repo", help="Optional owner/repo for gh -R.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Artifact directory. Default: {DEFAULT_OUTPUT_DIR}")
    parser.add_argument("--check-only", action="store_true", help="Only check merge safety; do not merge.")
    parser.add_argument("--merge", action="store_true", help="Squash merge if all checks pass.")
    parser.add_argument("--merge-method", default="squash", choices=["squash", "merge", "rebase"], help="Merge method. Default: squash.")
    parser.add_argument("--delete-branch", type=bool_arg, default=False, help="Whether to delete branch. Default: false.")
    parser.add_argument("--allow-review-pending", action="store_true", help="Allow missing Codex review evidence.")
    parser.add_argument(
        "--allow-auto-merge-without-review",
        action="store_true",
        help="Allow merge without Codex review evidence when all hard safety checks pass. Default: disabled.",
    )
    parser.add_argument("--require-codex-review", type=bool_arg, default=True, help="Require Codex review evidence. Default: true.")
    parser.add_argument("--require-no-requested-changes", type=bool_arg, default=True, help="Require no requested changes. Default: true.")
    parser.add_argument("--require-no-failing-checks", type=bool_arg, default=True, help="Require no failing checks. Default: true.")
    parser.add_argument("--allowed-file-patterns", action="append", help="Comma-separated additional/replacement allowed file patterns.")
    parser.add_argument("--forbidden-file-patterns", action="append", help="Comma-separated additional/replacement forbidden file patterns.")
    parser.add_argument(
        "--execution-gate-decision",
        type=Path,
        default=DEFAULT_EXECUTION_GATE_DECISION_PATH,
        help=f"Experiment execution gate decision path. Default: {DEFAULT_EXECUTION_GATE_DECISION_PATH}",
    )
    parser.add_argument("--proxy", default=DEFAULT_PROXY, help=f"HTTP(S)/ALL proxy. Default: {DEFAULT_PROXY}")
    return parser


def render_report(decision: dict[str, Any], pr_status: dict[str, Any]) -> str:
    lines = [
        "# DualScope Safe PR Merge Gate Report",
        "",
        f"- PR: #{pr_status.get('number')} {pr_status.get('url')}",
        f"- Decision: `{decision.get('decision')}`",
        f"- Can merge: `{decision.get('can_merge')}`",
        f"- Merged: `{decision.get('merged')}`",
        "",
        "## Blockers",
    ]
    blockers = decision.get("blockers") or []
    if blockers:
        lines.extend(f"- {item.get('kind')}: {item.get('message')}" for item in blockers)
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = build_parser().parse_args()
    started = utc_now()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    allowed_patterns = parse_csv_patterns(args.allowed_file_patterns, DEFAULT_ALLOWED_PATTERNS)
    forbidden_patterns = parse_csv_patterns(args.forbidden_file_patterns, DEFAULT_FORBIDDEN_PATTERNS)
    scope = {
        "summary_status": "PASS",
        "schema_version": "dualscope/safe-pr-merge-gate-scope/v1",
        "started_at": started,
        "pr": args.pr,
        "repo": args.repo,
        "check_only": args.check_only,
        "merge_requested": args.merge,
        "merge_method": args.merge_method,
        "delete_branch": args.delete_branch,
        "require_codex_review": args.require_codex_review,
        "allow_auto_merge_without_review": args.allow_auto_merge_without_review,
        "require_no_requested_changes": args.require_no_requested_changes,
        "require_no_failing_checks": args.require_no_failing_checks,
        "allow_review_pending": args.allow_review_pending,
        "proxy": args.proxy,
    }
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_scope.json", scope)

    blockers: list[dict[str, Any]] = []
    try:
        pr_status = gh_pr_view(args.pr, args.repo, args.proxy)
    except Exception as exc:  # noqa: BLE001
        pr_status = {"number": args.pr, "summary_status": "FAIL", "error": str(exc)}
        blockers.append({"kind": "pr_read_failed", "message": str(exc)})

    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_pr_status.json", pr_status)
    repo_full_name = args.repo or infer_repo_full_name(args.proxy)
    file_scope = (
        check_file_scope(pr_status, allowed_patterns, forbidden_patterns, repo_full_name, args.proxy)
        if "files" in pr_status
        else {"summary_status": "FAIL"}
    )
    ci_check = summarize_checks(pr_status) if "statusCheckRollup" in pr_status else {"summary_status": "FAIL", "failing_checks": []}
    codex_review_analysis = analyze_codex_review(pr_status)
    codex_review_present = bool(codex_review_analysis["codex_review_present"])
    requested_changes = has_requested_changes(pr_status)
    requested_changes_count = count_requested_changes(pr_status)
    review_check = {
        "summary_status": "PASS" if codex_review_present and not requested_changes else "WARN",
        **codex_review_analysis,
        "codex_review_present": codex_review_present,
        "requested_changes": requested_changes,
        "requested_changes_count": requested_changes_count,
        "review_decision": pr_status.get("reviewDecision"),
    }
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_file_scope_check.json", file_scope)
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_review_check.json", review_check)
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_ci_check.json", ci_check)
    execution_task_id = infer_execution_task_id(pr_status)
    execution_gate = read_execution_gate_decision(args.execution_gate_decision, execution_task_id)
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_execution_gate_check.json", execution_gate)

    if args.pr == 14:
        blockers.append({"kind": "blocked_legacy_pr", "message": "PR #14 is explicitly excluded from unattended merge."})
    if pr_status.get("state") != "OPEN":
        blockers.append({"kind": "pr_not_open", "message": f"PR state is {pr_status.get('state')!r}."})
    if pr_status.get("baseRefName") != "main":
        blockers.append({"kind": "wrong_base", "message": f"PR base is {pr_status.get('baseRefName')!r}, expected 'main'."})
    if file_scope.get("summary_status") != "PASS":
        blockers.append({"kind": "file_scope_blocked", "message": "PR contains forbidden or not-allowed files."})
    if args.require_no_requested_changes and requested_changes:
        blockers.append({"kind": "requested_changes", "message": "PR has requested changes."})
    if args.require_no_failing_checks and ci_check.get("failing_checks"):
        blockers.append({"kind": "failing_checks", "message": "PR has failing CI checks."})
    if execution_gate.get("gate_required") and not execution_gate.get("merge_allowed_by_execution_gate"):
        blockers.append(
            {
                "kind": "experiment_execution_gate_failed",
                "message": str(execution_gate.get("reason") or "Experiment execution gate did not pass."),
            }
        )
    codex_review_required = args.require_codex_review and not args.allow_auto_merge_without_review
    review_missing_but_user_authorized = bool(
        args.allow_auto_merge_without_review
        and args.require_codex_review
        and not codex_review_present
    )
    if codex_review_required and not args.allow_review_pending and not codex_review_present:
        blockers.append({"kind": "codex_review_missing", "message": "Codex review evidence is missing or still pending."})
    if args.delete_branch:
        blockers.append({"kind": "branch_deletion_forbidden", "message": "--delete-branch=true is not allowed for this gate."})
    if args.merge_method != "squash":
        blockers.append({"kind": "non_squash_merge_forbidden", "message": "Only squash merge is allowed by default."})

    merge_result: dict[str, Any] | None = None
    can_merge = not blockers
    if args.merge and can_merge:
        command = ["gh", "pr", "merge", str(args.pr), "--squash", "--delete-branch=false"]
        if args.repo:
            command.extend(["-R", args.repo])
        merge_result = run_command(command, proxy=args.proxy, timeout=300)
        if merge_result["returncode"] != 0:
            blockers.append({"kind": "merge_failed", "message": merge_result["stderr"] or merge_result["stdout"]})
            can_merge = False

    decision = {
        "summary_status": "PASS" if not blockers else "WARN",
        "schema_version": "dualscope/safe-pr-merge-gate-decision/v1",
        "completed_at": utc_now(),
        "pr": args.pr,
        "url": pr_status.get("url"),
        "decision": "merge_allowed" if can_merge else "blocked",
        "can_merge": can_merge,
        "merge_allowed": can_merge,
        "check_only": args.check_only,
        "merge_requested": args.merge,
        "merged": bool(args.merge and can_merge and merge_result and merge_result.get("returncode") == 0),
        "merge_result": merge_result,
        "blockers": blockers,
        "merge_blockers": blockers,
        "codex_review_requested": review_check.get("codex_review_requested"),
        "codex_review_required": codex_review_required,
        "codex_review_present": review_check.get("codex_review_present"),
        "codex_review_evidence_source": review_check.get("codex_review_evidence_source"),
        "codex_review_evidence_excerpt": review_check.get("codex_review_evidence_excerpt"),
        "review_missing_but_user_authorized": review_missing_but_user_authorized,
        "merged_without_codex_review": bool(args.merge and can_merge and review_missing_but_user_authorized),
        "auto_merge_policy": "allow_without_review" if args.allow_auto_merge_without_review else "require_codex_review",
        "merge_allowed_reason": "all_hard_safety_checks_passed" if can_merge else "",
        "requested_changes": review_check.get("requested_changes"),
        "requested_changes_count": review_check.get("requested_changes_count", 0),
        "failing_checks_count": len(ci_check.get("failing_checks") or []),
        "failing_checks": ci_check.get("failing_checks") or [],
        "ci_state": ci_check.get("ci_state"),
        "file_scope_allowed": file_scope.get("file_scope_allowed"),
        "execution_task_id": execution_task_id,
        "experiment_execution_gate": execution_gate,
        "experiment_execution_gate_passed": execution_gate.get("execution_gate_passed"),
        "merge_allowed_by_execution_gate": execution_gate.get("merge_allowed_by_execution_gate"),
        "blocked_files": file_scope.get("blocked_files", []),
        "blocked_data_files": file_scope.get("blocked_data_files", []),
        "allowed_outputs_artifacts": file_scope.get("allowed_outputs_artifacts", []),
        "allowed_verdict_registry_files": file_scope.get("allowed_verdict_registry_files", []),
        "allowed_dualscope_docs": file_scope.get("allowed_dualscope_docs", []),
        "allowed_advbench_small_slice_files": file_scope.get("allowed_advbench_small_slice_files", []),
        "advbench_small_slice_row_count": file_scope.get("advbench_small_slice_row_count"),
        "advbench_small_slice_schema_valid": file_scope.get("advbench_small_slice_schema_valid"),
        "advbench_small_slice_source_dataset": file_scope.get("advbench_small_slice_source_dataset"),
        "allowed_jbb_small_slice_files": file_scope.get("allowed_jbb_small_slice_files", []),
        "jbb_small_slice_row_count": file_scope.get("jbb_small_slice_row_count"),
        "jbb_small_slice_schema_valid": file_scope.get("jbb_small_slice_schema_valid"),
        "jbb_small_slice_source_dataset": file_scope.get("jbb_small_slice_source_dataset"),
        "dangerous_actions": {
            "auto_merge_default": False,
            "force_push": False,
            "delete_branch": False,
            "remote_rewrite": False,
        },
    }
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_decision.json", decision)
    (args.output_dir / "dualscope_safe_pr_merge_gate_report.md").write_text(render_report(decision, pr_status), encoding="utf-8")
    print(json.dumps(decision, indent=2, ensure_ascii=True))
    print(f"Artifacts: {args.output_dir}")
    return 0 if decision["summary_status"] in {"PASS", "WARN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
