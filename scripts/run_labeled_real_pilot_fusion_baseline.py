#!/usr/bin/env python3
"""Run the first supervised real-pilot fusion bootstrap baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.fusion.labeled_real_pilot_fusion import run_labeled_real_pilot_logistic


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the first supervised labeled real-pilot fusion bootstrap baseline.")
    parser.add_argument("--fusion-dataset", type=Path, default=Path("outputs/labeled_real_pilot_fusion/default/labeled_real_pilot_fusion_dataset.jsonl"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--fusion-profile", default="labeled_real_pilot_default")
    parser.add_argument("--run-id", default="default")
    parser.add_argument("--label-threshold", type=float, default=0.5)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_labeled_real_pilot_logistic(
            labeled_real_pilot_fusion_dataset_path=args.fusion_dataset,
            output_dir=args.output_dir,
            fusion_profile=args.fusion_profile,
            run_id=args.run_id,
            label_threshold=args.label_threshold,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "labeled_real_pilot_fusion_run_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"TriScope-LLM labeled real-pilot fusion baseline failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    print("TriScope-LLM labeled real-pilot fusion baseline complete")
    print(f"Predictions: {result['output_paths']['predictions']}")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Run summary: {result['output_paths']['run_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
