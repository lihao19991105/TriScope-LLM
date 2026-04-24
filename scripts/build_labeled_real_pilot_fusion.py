#!/usr/bin/env python3
"""Materialize a labeled real-pilot fusion dataset."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.fusion.labeled_real_pilot_fusion import build_labeled_real_pilot_fusion_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Materialize a labeled real-pilot fusion dataset from the current fusion rows and labeled pilot rows.")
    parser.add_argument("--real-pilot-fusion-dataset", type=Path, default=Path("outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_dataset.jsonl"))
    parser.add_argument("--labeled-pilot-dataset", type=Path, default=Path("outputs/labeled_pilot_runs/default/labeled_pilot_dataset.jsonl"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--fusion-profile", default="labeled_real_pilot_default")
    parser.add_argument("--run-id", default="default")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_labeled_real_pilot_fusion_dataset(
            real_pilot_fusion_dataset_path=args.real_pilot_fusion_dataset,
            labeled_pilot_dataset_path=args.labeled_pilot_dataset,
            output_dir=args.output_dir,
            fusion_profile=args.fusion_profile,
            run_id=args.run_id,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "labeled_real_pilot_fusion_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"TriScope-LLM labeled real-pilot fusion materialization failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    print("TriScope-LLM labeled real-pilot fusion dataset complete")
    print(f"Rows: {result['summary']['num_rows']}")
    print(f"Label coverage: {result['summary']['label_coverage']}")
    print(f"Dataset: {result['output_paths']['dataset_jsonl']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
