#!/usr/bin/env python3
"""Validate execution evidence for DualScope experiment tasks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_experiment_execution_gate_common import (
    evaluate_experiment_execution_gate,
    render_execution_gate_report,
    required_artifact_rows,
    write_json,
)


DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_experiment_execution_gate/default")


def run_git_changed_files(worktree_dir: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(worktree_dir),
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    paths: list[str] = []
    for line in completed.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 else line.strip()
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[-1]
        paths.append(path.strip().strip('"'))
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check required execution artifacts for one DualScope experiment task.")
    parser.add_argument("--task-id", required=True, help="DualScope task id to check.")
    parser.add_argument("--worktree-dir", type=Path, required=True, help="Repository/worktree path containing task artifacts.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Output directory. Default: {DEFAULT_OUTPUT_DIR}")
    parser.add_argument(
        "--changed-path",
        action="append",
        default=[],
        help="Changed path to classify. May be supplied multiple times. Defaults to git status --porcelain paths.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    changed_paths = args.changed_path or run_git_changed_files(args.worktree_dir)
    decision = evaluate_experiment_execution_gate(
        task_id=args.task_id,
        worktree_dir=args.worktree_dir,
        changed_paths=changed_paths,
    )
    required = required_artifact_rows(args.task_id, args.worktree_dir)
    write_json(args.output_dir / "experiment_execution_gate_decision.json", decision)
    write_json(args.output_dir / "experiment_execution_gate_required_artifacts.json", required)
    (args.output_dir / "experiment_execution_gate_report.md").write_text(render_execution_gate_report(decision), encoding="utf-8")
    print(json.dumps(decision, indent=2, ensure_ascii=True))
    print(f"Artifacts: {args.output_dir}")
    return 0 if decision.get("execution_gate_passed") else 2


if __name__ == "__main__":
    raise SystemExit(main())
