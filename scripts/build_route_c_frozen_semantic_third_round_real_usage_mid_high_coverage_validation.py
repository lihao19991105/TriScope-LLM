#!/usr/bin/env python3
"""CLI for stage-185 route_c frozen semantic third round real usage mid high coverage validation."""

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
        help="Stable real execution run directory used as stage-185 anchor.",
    )
    parser.add_argument(
        "--stage-182-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_third_round_real_usage_cadence_stability_recheck/default"),
        help="Directory containing stage-182 artifacts.",
    )
    parser.add_argument(
        "--stage-183-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_third_round_real_usage_batched_cadence_combo_validation/default"),
        help="Directory containing stage-183 artifacts.",
    )
    parser.add_argument(
        "--stage-184-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_third_round_real_usage_batched_cadence_combo_stability_recheck/default"),
        help="Directory containing stage-184 artifacts.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label-threshold", type=float, default=0.5)
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write stage-185 artifacts.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.route_c_frozen_semantic_third_round_real_usage_mid_high_coverage_validation import build_route_c_frozen_semantic_third_round_real_usage_mid_high_coverage_validation

    try:
        result = build_route_c_frozen_semantic_third_round_real_usage_mid_high_coverage_validation(
            real_run_dir=args.real_run_dir,
            stage_182_dir=args.stage_182_dir,
            stage_183_dir=args.stage_183_dir,
            stage_184_dir=args.stage_184_dir,
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
        print(f"TriScope-LLM stage-185 third round real usage mid high coverage validation failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("stage-185 route_c frozen semantic third round real usage mid high coverage validation artifacts written to:")
    for key, value in result["output_paths"].items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
