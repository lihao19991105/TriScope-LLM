#!/usr/bin/env python3
"""Run the bounded Alpaca main-slice response-generation repair path."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_alpaca_main_slice_response_generation import (  # noqa: E402
    build_qwen2p5_7b_alpaca_main_slice_response_generation,
)


REPAIR_TASK_ID = "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair"
REPAIR_VALIDATED = "Qwen2.5-7B Alpaca main-slice response generation repaired"
PARTIAL = "Partially validated"
NOT_VALIDATED = "Not validated"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def has_real_response(row: dict[str, Any]) -> bool:
    if row.get("blocked") is True or row.get("generation_blocked") is True:
        return False
    if str(row.get("status") or "").strip().lower() in {"blocked", "failed", "error"}:
        return False
    if str(row.get("response_generation_status") or "").strip().lower() == "blocked":
        return False
    for key in ("model_response", "response", "generated_text", "output_text", "text"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return True
    return False


def blocker_type_from_summary(summary: dict[str, Any]) -> str:
    blockers = summary.get("blockers")
    if isinstance(blockers, list) and blockers:
        first = blockers[0]
        if isinstance(first, str) and first.strip():
            return first.strip()
    mode = summary.get("response_generation_mode")
    if isinstance(mode, dict) and int(mode.get("row_count_generated") or 0) <= 0:
        return "runtime_error"
    return ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Repair bounded Qwen2.5-7B Stanford Alpaca main-slice response generation."
    )
    parser.add_argument("--model-dir", type=Path, default=Path("/mnt/sda3/lh/models/qwen2p5-7b-instruct"))
    parser.add_argument(
        "--input-jsonl",
        type=Path,
        default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"),
    )
    parser.add_argument(
        "--plan-verdict",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default"),
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(
            ".reports/dualscope_task_verdicts/"
            "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json"
        ),
    )
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--max-source-examples", type=int, default=4)
    parser.add_argument("--expected-response-rows", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=32)
    parser.add_argument("--max-generation-attempts", type=int, default=8)
    parser.add_argument("--min-free-gpu-memory-mib", type=int, default=0)
    parser.add_argument("--load-in-4bit", action="store_true")
    parser.add_argument("--low-memory", action="store_true", default=True)
    parser.add_argument("--allow-without-logprobs", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_qwen2p5_7b_alpaca_main_slice_response_generation(
        output_dir=args.output_dir,
        input_jsonl=args.input_jsonl,
        model_dir=args.model_dir,
        plan_verdict=args.plan_verdict,
        registry_path=args.registry_path,
        seed=args.seed,
        max_source_examples=args.max_source_examples,
        expected_response_rows=args.expected_response_rows,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
        max_generation_attempts=args.max_generation_attempts,
        min_free_gpu_memory_mib=args.min_free_gpu_memory_mib,
        load_in_4bit=args.load_in_4bit,
        low_memory=args.low_memory,
        allow_without_logprobs=args.allow_without_logprobs,
        trigger_text="cftrigger",
        target_text="I have completed the requested instruction.",
        dry_run=args.dry_run,
    )
    response_rows = read_jsonl(args.output_dir / "qwen2p5_7b_alpaca_main_slice_response_rows.jsonl")
    real_rows = [row for row in response_rows if has_real_response(row)]
    write_jsonl(
        args.output_dir / "qwen2p5_7b_alpaca_main_slice_response_generation_repair_responses.jsonl",
        real_rows,
    )
    blocker_type = blocker_type_from_summary(summary)
    if blocker_type:
        write_json(
            args.output_dir / "qwen2p5_7b_alpaca_main_slice_response_generation_repair_blockers.json",
            {
                "summary_status": "BLOCKED",
                "task_id": REPAIR_TASK_ID,
                "blocker_type": blocker_type,
                "blockers": summary.get("blockers", []),
                "generated_rows": len(real_rows),
                "model_response_fabricated": False,
                "logprobs_fabricated": False,
                "metrics_computed": False,
            },
        )

    verdict = REPAIR_VALIDATED if real_rows else PARTIAL if blocker_type else NOT_VALIDATED
    next_task = (
        "dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation"
        if verdict == REPAIR_VALIDATED
        else "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure"
    )
    repair_summary = {
        **summary,
        "task_id": REPAIR_TASK_ID,
        "final_verdict": verdict,
        "recommended_next_step": next_task,
        "repair_source_task_id": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation",
        "real_response_rows": len(real_rows),
        "blocker_type": blocker_type,
    }
    write_json(args.output_dir / "dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair_summary.json", repair_summary)
    write_json(
        args.output_dir / "dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair_verdict.json",
        {
            "summary_status": "PASS" if verdict == REPAIR_VALIDATED else "PARTIAL" if verdict == PARTIAL else "FAIL",
            "task_id": REPAIR_TASK_ID,
            "final_verdict": verdict,
            "recommended_next_step": next_task,
            "response_rows": len(real_rows),
            "blocker_type": blocker_type,
        },
    )
    write_json(
        args.registry_path,
        {
            "task_id": REPAIR_TASK_ID,
            "verdict": verdict,
            "source_output_dir": str(args.output_dir),
            "validated": verdict == REPAIR_VALIDATED,
            "repair_for": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation",
            "next_task": next_task,
            "generated_rows": len(real_rows),
            "blocker_type": blocker_type,
            "model_response_fabricated": False,
            "logprobs_fabricated": False,
            "metrics_computed": False,
        },
    )
    print(f"Repair verdict: {verdict}")
    print(f"Real response rows: {len(real_rows)}")
    print(f"Blocker type: {blocker_type or '<none>'}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if verdict != NOT_VALIDATED else 2


if __name__ == "__main__":
    raise SystemExit(main())
