#!/usr/bin/env python3
"""CLI for route_c frozen semantic minimal batched continuous stability recheck."""

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
        "--real-run-dir",
        type=Path,
        default=Path(
            "outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_recheck/default/runs/extension_rerun_01"
        ),
        help="Stable real execution run directory used as continuous-execution anchor.",
    )
    parser.add_argument(
        "--stage-148-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_recoverable_boundary_control/default"),
        help="Directory containing stage-148 recoverable-boundary artifacts.",
    )
    parser.add_argument(
        "--stage-149-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_small_regression/default"),
        help="Directory containing stage-149 frozen semantic regression artifacts.",
    )
    parser.add_argument(
        "--stage-150-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_minimal_execution_path_regression/default"),
        help="Directory containing stage-150 minimal execution-path artifacts.",
    )
    parser.add_argument(
        "--stage-151-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_minimal_real_execution/default"),
        help="Directory containing stage-151 minimal real execution artifacts.",
    )
    parser.add_argument(
        "--stage-152-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_minimal_continuous_execution/default"),
        help="Directory containing stage-152 minimal continuous execution artifacts.",
    )
    parser.add_argument(
        "--stage-154-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_minimal_real_batched_continuous_regression/default"),
        help="Directory containing stage-154 minimal real batched continuous regression artifacts.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label-threshold", type=float, default=0.5)
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write stage-155 artifacts.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.route_c_frozen_semantic_minimal_batched_continuous_stability_recheck import (
        build_route_c_frozen_semantic_minimal_batched_continuous_stability_recheck,
    )

    try:
        result = build_route_c_frozen_semantic_minimal_batched_continuous_stability_recheck(
            real_run_dir=args.real_run_dir,
            stage_148_dir=args.stage_148_dir,
            stage_149_dir=args.stage_149_dir,
            stage_150_dir=args.stage_150_dir,
            stage_151_dir=args.stage_151_dir,
            stage_152_dir=args.stage_152_dir,
            stage_154_dir=args.stage_154_dir,
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
        print(f"TriScope-LLM route_c minimal batched continuous stability recheck failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("route_c frozen semantic minimal batched continuous stability recheck artifacts written to:")
    for key, value in result["output_paths"].items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
