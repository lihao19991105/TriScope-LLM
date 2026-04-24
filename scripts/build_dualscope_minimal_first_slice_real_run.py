#!/usr/bin/env python3
"""Build DualScope minimal first-slice real-run artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_minimal_first_slice_real_run import build_dualscope_minimal_first_slice_real_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the DualScope minimal first-slice artifact chain.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--capability-mode", choices=["auto", "with_logprobs", "without_logprobs"], default="auto")
    parser.add_argument("--allow-fallback-without-logprobs", action="store_true")
    parser.add_argument("--stop-on-missing-artifact", action="store_true")
    parser.add_argument("--no-full-matrix", action="store_true", default=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = build_dualscope_minimal_first_slice_real_run(
            output_dir=args.output_dir,
            seed=args.seed,
            capability_mode=args.capability_mode,
            allow_fallback_without_logprobs=args.allow_fallback_without_logprobs,
            stop_on_missing_artifact=args.stop_on_missing_artifact,
            no_full_matrix=args.no_full_matrix,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"DualScope minimal first-slice real run failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1
    print("DualScope minimal first-slice real run complete")
    print(f"Verdict: {result['verdict']['final_verdict']}")
    print(f"Recommendation: {result['recommendation']['recommended_next_step']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

