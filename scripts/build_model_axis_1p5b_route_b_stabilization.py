#!/usr/bin/env python3
"""Build 1.5B route_b label-balance stabilization artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build model-axis 1.5B route_b label-balance stabilization artifacts.")
    parser.add_argument(
        "--execution-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_execution/default"),
        help="Directory containing 107 model-axis 1.5B execution artifacts.",
    )
    parser.add_argument(
        "--reference-route-b-dataset-path",
        type=Path,
        default=Path("outputs/rerun_route_b_on_labeled_split_v6/default/route_b_v6_dataset.jsonl"),
        help="Reference route_b v6 dataset used for sample-selection diagnosis.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory for 109 stabilization artifacts.",
    )
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.model_axis_1p5b_route_b_stabilization import build_model_axis_1p5b_route_b_stabilization

    try:
        result = build_model_axis_1p5b_route_b_stabilization(
            execution_dir=args.execution_dir,
            reference_route_b_dataset_path=args.reference_route_b_dataset_path,
            output_dir=args.output_dir,
            seed=args.seed,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM model-axis 1.5B route_b stabilization failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM model-axis 1.5B route_b stabilization complete")
    print(f"Diagnosis: {result['output_paths']['diagnosis']}")
    print(f"Candidate summary: {result['output_paths']['candidate_summary']}")
    print(f"Precheck: {result['output_paths']['precheck']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
