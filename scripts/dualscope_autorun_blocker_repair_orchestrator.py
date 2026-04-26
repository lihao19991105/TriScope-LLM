#!/usr/bin/env python3
"""Classify DualScope autorun blockers and generate a safe repair task."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_autorun_blocker_classifier import classify_autorun_blockers  # noqa: E402
from src.eval.dualscope_autorun_repair_task_generator import generate_repair_task  # noqa: E402


DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_autorun_blocker_repair/default")


def read_json_if_exists(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def render_report(classification: dict[str, Any], repair_task: dict[str, Any], decision: dict[str, Any]) -> str:
    lines = [
        "# DualScope Autorun Blocker Repair Report",
        "",
        f"- Primary blocker class: `{classification.get('primary_blocker_class')}`",
        f"- Repairable: `{classification.get('repairable')}`",
        f"- Repair task: `{repair_task.get('repair_task_id')}`",
        f"- Decision: `{decision.get('decision')}`",
        f"- Return target: `{repair_task.get('return_to_task_if_validated')}`",
        "",
        "## Classified Evidence",
    ]
    for item in classification.get("classified_blockers") or []:
        lines.append(f"- {item.get('source')}: `{item.get('blocker_class')}` - {item.get('evidence')}")
    if not classification.get("classified_blockers"):
        lines.append("- None")
    lines.extend(["", "## Safety Constraints"])
    for key, value in (classification.get("safety_constraints") or {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Next Action", decision.get("next_action") or "No next action recorded."])
    return "\n".join(lines) + "\n"


def build_repair_artifacts(
    autorun_summary: dict[str, Any],
    autorun_blockers: dict[str, Any],
    task_selection: dict[str, Any],
    output_dir: Path,
    dry_run: bool,
    failed_task_id: str | None = None,
) -> dict[str, Any]:
    classification = classify_autorun_blockers(
        autorun_summary=autorun_summary,
        autorun_blockers=autorun_blockers,
        task_selection=task_selection,
    )
    repair_task = generate_repair_task(classification, task_selection=task_selection, failed_task_id=failed_task_id)
    decision = {
        "summary_status": "PASS" if classification.get("repairable") else "WARN",
        "schema_version": "dualscope/autorun-blocker-repair-decision/v1",
        "dry_run": dry_run,
        "decision": "generate_repair_task" if classification.get("repairable") else "stop_unrepairable",
        "blocker_class": classification.get("primary_blocker_class"),
        "repairable": classification.get("repairable"),
        "repair_task_id": repair_task.get("repair_task_id"),
        "return_to_mainline_task": repair_task.get("return_to_task_if_validated"),
        "stop_reason_if_not_repairable": repair_task.get("stop_reason_if_not_repairable"),
        "next_action": (
            "Run the generated repair task in a task worktree, then rerun the original queue selection."
            if classification.get("repairable")
            else "Stop and resolve the unrepairable blocker manually."
        ),
    }
    attempts = [
        {
            "attempt": 1,
            "dry_run": dry_run,
            "blocker_class": classification.get("primary_blocker_class"),
            "repair_task_id": repair_task.get("repair_task_id"),
            "repairable": classification.get("repairable"),
            "status": "planned" if classification.get("repairable") else "not_planned",
        }
    ]
    summary = {
        "summary_status": decision["summary_status"],
        "schema_version": "dualscope/autorun-blocker-repair-summary/v1",
        "blocker_class": classification.get("primary_blocker_class"),
        "repairable": classification.get("repairable"),
        "repair_task_id": repair_task.get("repair_task_id"),
        "return_to_mainline_task": repair_task.get("return_to_task_if_validated"),
        "dry_run": dry_run,
        "artifacts": {
            "classification": str(output_dir / "dualscope_autorun_blocker_classification.json"),
            "decision": str(output_dir / "dualscope_autorun_blocker_repair_decision.json"),
            "generated_repair_task": str(output_dir / "dualscope_autorun_generated_repair_task.json"),
            "attempts": str(output_dir / "dualscope_autorun_repair_attempts.jsonl"),
            "report": str(output_dir / "dualscope_autorun_repair_report.md"),
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "dualscope_autorun_blocker_classification.json", classification)
    write_json(output_dir / "dualscope_autorun_blocker_repair_decision.json", decision)
    write_json(output_dir / "dualscope_autorun_generated_repair_task.json", repair_task)
    write_jsonl(output_dir / "dualscope_autorun_repair_attempts.jsonl", attempts)
    write_json(output_dir / "dualscope_autorun_repair_summary.json", summary)
    (output_dir / "dualscope_autorun_repair_report.md").write_text(render_report(classification, repair_task, decision), encoding="utf-8")
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Classify autorun blockers and generate a safe repair task.")
    parser.add_argument("--autorun-summary", type=Path, required=True, help="Path to dualscope_autorun_loop_summary.json")
    parser.add_argument("--autorun-blockers", type=Path, required=True, help="Path to dualscope_autorun_loop_blockers.json")
    parser.add_argument("--task-selection", type=Path, required=True, help="Path to dualscope_next_task_selection.json")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Output directory. Default: {DEFAULT_OUTPUT_DIR}")
    parser.add_argument("--failed-task-id", default=None, help="Optional explicit failed task id.")
    parser.add_argument("--dry-run", action="store_true", help="Generate repair decision artifacts without executing repair.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_repair_artifacts(
        autorun_summary=read_json_if_exists(args.autorun_summary),
        autorun_blockers=read_json_if_exists(args.autorun_blockers),
        task_selection=read_json_if_exists(args.task_selection),
        output_dir=args.output_dir,
        dry_run=args.dry_run,
        failed_task_id=args.failed_task_id,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    print(f"Artifacts: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
