#!/usr/bin/env python3
"""Build DualScope first-slice real-run artifact-validation repair artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_real_run_artifact_validation_repair import (  # noqa: E402
    build_real_run_artifact_validation_repair,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build repair-only audit artifacts for first-slice real-run artifact validation."
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for repair artifacts.")
    parser.add_argument(
        "--validation-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_real_run_artifact_validation/default"),
        help="Previous artifact-validation output directory.",
    )
    parser.add_argument(
        "--validation-analysis-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_real_run_artifact_validation_analysis/default"),
        help="Previous artifact-validation post-analysis output directory.",
    )
    parser.add_argument(
        "--labeled-rerun-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default"),
        help="Labeled rerun artifact directory.",
    )
    parser.add_argument(
        "--condition-rerun-dir",
        type=Path,
        default=Path("outputs/dualscope_minimal_first_slice_condition_level_rerun/default"),
        help="Condition-level rerun artifact directory.",
    )
    parser.add_argument(
        "--row-level-fusion-alignment-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_condition_row_level_fusion_alignment/default"),
        help="Optional standalone row-level fusion-alignment artifact directory.",
    )
    parser.add_argument(
        "--target-response-dir",
        type=Path,
        default=Path("outputs/dualscope_first_slice_target_response_generation_plan/default"),
        help="Target-response-generation plan artifact directory.",
    )
    parser.add_argument(
        "--illumination-freeze-dir",
        type=Path,
        default=Path("outputs/dualscope_illumination_screening_freeze/default"),
        help="Frozen Stage 1 artifact directory.",
    )
    parser.add_argument(
        "--confidence-freeze-dir",
        type=Path,
        default=Path("outputs/dualscope_confidence_verification_with_without_logprobs/default"),
        help="Frozen Stage 2 artifact directory.",
    )
    parser.add_argument(
        "--fusion-freeze-dir",
        type=Path,
        default=Path("outputs/dualscope_budget_aware_two_stage_fusion_design/default"),
        help="Frozen Stage 3 artifact directory.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed recorded in repair artifacts.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_real_run_artifact_validation_repair(
        output_dir=args.output_dir,
        validation_dir=args.validation_dir,
        validation_analysis_dir=args.validation_analysis_dir,
        labeled_rerun_dir=args.labeled_rerun_dir,
        condition_rerun_dir=args.condition_rerun_dir,
        row_level_fusion_alignment_dir=args.row_level_fusion_alignment_dir,
        target_response_dir=args.target_response_dir,
        illumination_freeze_dir=args.illumination_freeze_dir,
        confidence_freeze_dir=args.confidence_freeze_dir,
        fusion_freeze_dir=args.fusion_freeze_dir,
        seed=args.seed,
    )
    print(f"Verdict: {summary['final_verdict']}")
    print(f"Recommendation: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
