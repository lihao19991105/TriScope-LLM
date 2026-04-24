#!/usr/bin/env python3
"""CLI for stage-156 route_c frozen semantic minimal light expansion validation."""

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
        help="Stable real execution run directory used as light-expansion anchor.",
    )
    parser.add_argument(
        "--stage-153-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_minimal_real_continuous_execution/default"),
        help="Directory containing stage-153 minimal real continuous execution artifacts.",
    )
    parser.add_argument(
        "--stage-154-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_minimal_real_batched_continuous_regression/default"),
        help="Directory containing stage-154 minimal real batched continuous regression artifacts.",
    )
    parser.add_argument(
        "--stage-155-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_minimal_batched_continuous_stability_recheck/default"),
        help="Directory containing stage-155 minimal batched continuous stability recheck artifacts.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label-threshold", type=float, default=0.5)
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write stage-156 artifacts.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.route_c_frozen_semantic_minimal_light_expansion_validation import (
        build_route_c_frozen_semantic_minimal_light_expansion_validation,
    )

    try:
        result = build_route_c_frozen_semantic_minimal_light_expansion_validation(
            real_run_dir=args.real_run_dir,
            stage_153_dir=args.stage_153_dir,
            stage_154_dir=args.stage_154_dir,
            stage_155_dir=args.stage_155_dir,
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
        print(f"TriScope-LLM stage-156 minimal light expansion validation failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("stage-156 route_c frozen semantic minimal light expansion validation artifacts written to:")
    for key, value in result["output_paths"].items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
