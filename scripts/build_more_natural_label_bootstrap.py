#!/usr/bin/env python3
"""Materialize and optionally run the first more-natural-label supervised fusion bootstrap."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.fusion.more_natural_label_fusion import (
    build_more_natural_labeled_dataset,
    run_more_natural_logistic,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the first more-natural-label supervised fusion bootstrap.")
    parser.add_argument(
        "--real-pilot-fusion-dataset",
        type=Path,
        default=Path("outputs/controlled_supervision_expansion/default/expanded_real_pilot_fusion/fusion_dataset.jsonl"),
    )
    parser.add_argument(
        "--reasoning-raw-results",
        type=Path,
        default=Path("outputs/controlled_supervision_expansion/default/expanded_reasoning/reasoning_probe/raw_results.jsonl"),
    )
    parser.add_argument(
        "--confidence-raw-results",
        type=Path,
        default=Path("outputs/controlled_supervision_expansion/default/expanded_confidence/confidence_probe/raw_results.jsonl"),
    )
    parser.add_argument(
        "--illumination-raw-results",
        type=Path,
        default=Path("outputs/controlled_supervision_expansion/default/expanded_illumination/illumination_probe/raw_results.jsonl"),
    )
    parser.add_argument(
        "--pilot-slice",
        type=Path,
        default=Path("outputs/pilot_materialization/pilot_csqa_reasoning_local/csqa_reasoning_pilot_slice.jsonl"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label-threshold", type=float, default=0.5)
    parser.add_argument("--skip-logistic", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        dataset_result = build_more_natural_labeled_dataset(
            real_pilot_fusion_dataset_path=args.real_pilot_fusion_dataset,
            reasoning_raw_results_path=args.reasoning_raw_results,
            confidence_raw_results_path=args.confidence_raw_results,
            illumination_raw_results_path=args.illumination_raw_results,
            pilot_slice_path=args.pilot_slice,
            output_dir=args.output_dir,
            fusion_profile="more_natural_label_real_pilot",
            run_id="default",
        )
        logistic_result = None
        if not args.skip_logistic:
            logistic_result = run_more_natural_logistic(
                dataset_path=args.output_dir / "more_natural_labeled_dataset.jsonl",
                output_dir=args.output_dir,
                fusion_profile="more_natural_label_real_pilot",
                run_id="default",
                label_threshold=args.label_threshold,
                random_seed=args.seed,
            )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM more-natural-label bootstrap failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM more-natural-label bootstrap complete")
    print(f"Rows: {dataset_result['summary']['num_rows']}")
    print(f"Class balance: {dataset_result['summary']['class_balance']}")
    if logistic_result is not None:
        print(f"Logistic status: {logistic_result['summary']['summary_status']}")
    print(f"Output dir: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
