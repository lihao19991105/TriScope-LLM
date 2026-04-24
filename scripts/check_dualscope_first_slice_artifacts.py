#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_artifact_validator import check_first_slice_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DualScope first-slice real-run artifacts.")
    parser.add_argument("--run-dir", type=Path, default=Path("outputs/dualscope_minimal_first_slice_real_run"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    summary = check_first_slice_artifacts(args.run_dir, args.output_dir)
    print(f"Artifact check verdict: {summary['verdict']}")
    return 0 if summary["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
