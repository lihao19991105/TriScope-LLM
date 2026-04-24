"""Standalone rerun wrapper for DualScope first-slice real-run preflight."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_minimal_first_slice_real_run_preflight import (
    build_dualscope_minimal_first_slice_real_run_preflight,
)


def build_dualscope_first_slice_preflight_rerun(
    real_run_plan_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    """Run the canonical preflight checks into the rerun-specific output dir."""

    return build_dualscope_minimal_first_slice_real_run_preflight(
        real_run_plan_dir=real_run_plan_dir,
        output_dir=output_dir,
        seed=seed,
    )

