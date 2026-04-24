#!/usr/bin/env python3
"""CLI for the 1.5B model-axis dry-run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.model_axis_1p5b_dry_run import build_model_axis_1p5b_dry_run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the 1.5B model-axis dry-run.")
    parser.add_argument("--bootstrap-summary-path", type=Path, default=Path("outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_bootstrap_summary.json"))
    parser.add_argument("--matrix-definition-path", type=Path, default=Path("outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_matrix_definition.json"))
    parser.add_argument("--readiness-summary-path", type=Path, default=Path("outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_readiness_summary.json"))
    parser.add_argument("--blocker-diagnosis-path", type=Path, default=Path("outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_blocker_diagnosis.json"))
    parser.add_argument("--recovery-options-path", type=Path, default=Path("outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_recovery_options.json"))
    parser.add_argument("--minimal-execution-candidate-path", type=Path, default=Path("outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_minimal_execution_candidate.json"))
    parser.add_argument("--materialized-inputs-dir", type=Path, default=Path("outputs/model_axis_1p5b_bootstrap/default/materialized_model_axis_1p5b_inputs"))
    parser.add_argument("--base-v11-inputs-dir", type=Path, default=Path("outputs/next_axis_after_v10_matrix_dry_run/default/materialized_next_axis_after_v10_matrix_inputs"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_model_axis_1p5b_dry_run(
            bootstrap_summary_path=args.bootstrap_summary_path,
            matrix_definition_path=args.matrix_definition_path,
            readiness_summary_path=args.readiness_summary_path,
            blocker_diagnosis_path=args.blocker_diagnosis_path,
            recovery_options_path=args.recovery_options_path,
            minimal_execution_candidate_path=args.minimal_execution_candidate_path,
            materialized_inputs_dir=args.materialized_inputs_dir,
            base_v11_inputs_dir=args.base_v11_inputs_dir,
            output_dir=args.output_dir,
            seed=args.seed,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "build_failure.json").write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM model-axis 1.5B dry-run failed: {exc}")
        return 1
    print("TriScope-LLM model-axis 1.5B dry-run complete")
    print(f"Summary: {result['output_paths']['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
