#!/usr/bin/env python3
"""Build a unified smoke-level analysis report for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.smoke_reporting import build_smoke_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a unified smoke-level run registry, artifact registry, and compact report "
            "from existing TriScope-LLM module and fusion artifacts."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where the smoke report artifacts will be written.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_smoke_report(args.output_dir)
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "report_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "output_dir": str(args.output_dir),
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM smoke report build failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    summary = result["smoke_report_summary"]
    output_paths = result["output_paths"]
    print("TriScope-LLM smoke report build complete")
    print(f"Registered runs: {summary['num_registered_runs']}")
    print(f"Registered artifacts: {summary['num_registered_artifacts']}")
    print(f"Run registry: {output_paths['run_registry']}")
    print(f"Artifact registry: {output_paths['artifact_registry']}")
    print(f"Smoke summary: {output_paths['smoke_report_summary']}")
    print(f"Baseline comparison: {output_paths['baseline_comparison']}")
    print(f"Error analysis dataset: {output_paths['error_analysis_jsonl']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
