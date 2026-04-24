#!/usr/bin/env python3
"""Build the labeled-slice expansion bootstrap for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.labeled_slice_expansion import build_labeled_slice_expansion


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Expand the shared local labeled slice and emit bridge artifacts.")
    parser.add_argument(
        "--pilot-materialized-dir",
        type=Path,
        default=Path("outputs/pilot_materialization/pilot_csqa_reasoning_local"),
    )
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--reasoning-config", type=Path, default=Path("configs/reasoning.yaml"))
    parser.add_argument("--confidence-config", type=Path, default=Path("configs/confidence.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-bridge-dry-run", action="store_true")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_labeled_slice_expansion(
            pilot_materialized_dir=args.pilot_materialized_dir,
            output_dir=args.output_dir,
            models_config_path=args.models_config,
            reasoning_config_path=args.reasoning_config,
            confidence_config_path=args.confidence_config,
            illumination_config_path=args.illumination_config,
            seed=args.seed,
            run_bridge_dry_run=not args.skip_bridge_dry_run,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM labeled-slice expansion failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    print("TriScope-LLM labeled-slice expansion bootstrap complete")
    print(f"Expanded slice rows: {result['expanded_summary']['num_rows']}")
    print(f"Materialized inputs: {result['output_paths']['materialized_inputs_dir']}")
    if result["output_paths"]["bridge_summary"] is not None:
        print(f"Bridge summary: {result['output_paths']['bridge_summary']}")
    print(f"Expanded summary: {result['output_paths']['expanded_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
