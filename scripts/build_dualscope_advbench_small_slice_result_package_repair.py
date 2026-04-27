#!/usr/bin/env python3
"""Build AdvBench small-slice result-package repair artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_advbench_small_slice_result_package_repair import (  # noqa: E402
    DEFAULT_ANALYSIS_DIR,
    DEFAULT_METRIC_REPAIR_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REGISTRY_PATH,
    DEFAULT_RESPONSE_DIR,
    DEFAULT_RESULT_PACKAGE_DIR,
    FINAL_NOT_VALIDATED,
    build_advbench_small_slice_result_package_repair,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Repair/compress the partially validated AdvBench result-package state without "
            "fabricating unavailable behavior or performance metrics."
        )
    )
    parser.add_argument(
        "--result-package-dir",
        type=Path,
        default=DEFAULT_RESULT_PACKAGE_DIR,
        help="Prior AdvBench result-package artifact directory.",
    )
    parser.add_argument(
        "--metric-repair-dir",
        type=Path,
        default=DEFAULT_METRIC_REPAIR_DIR,
        help="AdvBench metric-computation repair artifact directory.",
    )
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=DEFAULT_RESPONSE_DIR,
        help="AdvBench response-generation artifact directory.",
    )
    parser.add_argument(
        "--result-package-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package.json"),
        help="Tracked prior AdvBench result-package verdict registry.",
    )
    parser.add_argument(
        "--metric-repair-registry",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation-repair.json"),
        help="Tracked AdvBench metric-computation repair verdict registry.",
    )
    parser.add_argument(
        "--response-generation-repair-registry",
        type=Path,
        default=Path(
            ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json"
        ),
        help="Tracked AdvBench response-generation repair verdict registry.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Repair output directory.")
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS_DIR, help="Analysis mirror directory.")
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help="Tracked task verdict registry path.",
    )
    parser.add_argument(
        "--docs-path",
        type=Path,
        default=Path("docs/dualscope_advbench_small_slice_result_package_repair.md"),
        help="Human-readable repair report path.",
    )
    parser.add_argument("--seed", type=int, default=20260427, help="Recorded seed for reproducibility.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_advbench_small_slice_result_package_repair(
        result_package_dir=args.result_package_dir,
        metric_repair_dir=args.metric_repair_dir,
        response_dir=args.response_dir,
        result_package_registry=args.result_package_registry,
        metric_repair_registry=args.metric_repair_registry,
        response_generation_repair_registry=args.response_generation_repair_registry,
        output_dir=args.output_dir,
        analysis_dir=args.analysis_dir,
        registry_path=args.registry_path,
        docs_path=args.docs_path,
        seed=args.seed,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Recommended next step: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 2 if summary["final_verdict"] == FINAL_NOT_VALIDATED else 0


if __name__ == "__main__":
    raise SystemExit(main())
