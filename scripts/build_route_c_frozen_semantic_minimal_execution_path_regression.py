#!/usr/bin/env python3
"""CLI for route_c frozen semantic minimal execution-path regression validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--regression-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_small_regression/default"),
        help="Directory containing stage-149 regression artifacts.",
    )
    parser.add_argument(
        "--stage-143-run-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_recheck/default/runs/extension_rerun_01"),
        help="Representative stage-143 stable run directory.",
    )
    parser.add_argument(
        "--stage-144-run-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_stable_baseline_time_separated_replay/default/runs/time_replay_01"),
        help="Representative stage-144 replay-regression run directory.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label-threshold", type=float, default=0.5)
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write stage-150 artifacts.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.route_c_frozen_semantic_minimal_execution_path_regression import (
        build_route_c_frozen_semantic_minimal_execution_path_regression,
    )

    try:
        result = build_route_c_frozen_semantic_minimal_execution_path_regression(
            regression_dir=args.regression_dir,
            stage_143_run_dir=args.stage_143_run_dir,
            stage_144_run_dir=args.stage_144_run_dir,
            output_dir=args.output_dir,
            seed=args.seed,
            label_threshold=args.label_threshold,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM route_c minimal execution-path regression failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("route_c frozen semantic minimal execution-path regression artifacts written to:")
    for key, value in result["output_paths"].items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
