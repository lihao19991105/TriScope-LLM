# dualscope-minimal-first-slice-real-run-preflight-rerun

## Purpose / Big Picture

Rerun the DualScope minimal first-slice real-run preflight after the real Stanford Alpaca first-slice JSONL has been materialized. This phase confirms whether the dataset, model, tokenizer, GPU, frozen Stage 1 / Stage 2 / Stage 3 artifacts, contracts, planned commands, dry-run config, and forbidden-expansion checks still pass in a replayable preflight package.

## Scope

### In Scope

- Reuse the frozen preflight implementation without changing benchmark truth or gate semantics.
- Produce independent rerun artifacts under `outputs/dualscope_first_slice_preflight_rerun/`.
- Run post-analysis and produce one final rerun verdict.
- Keep this phase preflight-only: no LoRA/QLoRA training and no full experiment matrix.

### Out of Scope

- Starting the minimal real run.
- Creating new datasets or expanding beyond the Stanford Alpaca first slice.
- Modifying Stage 1, Stage 2, or Stage 3 contracts.
- Continuing any old route_c recursive plan.

## Repository Context

This phase wraps the existing validated preflight implementation:

- `src/eval/dualscope_minimal_first_slice_real_run_preflight.py`
- `src/eval/post_dualscope_minimal_first_slice_real_run_preflight_analysis.py`

The wrapper exists so the 5-hour autonomous run has its own phase-level artifacts and verdict.

## Deliverables

- `src/eval/dualscope_first_slice_preflight_rerun.py`
- `src/eval/post_dualscope_first_slice_preflight_rerun_analysis.py`
- `scripts/build_dualscope_first_slice_preflight_rerun.py`
- `scripts/build_post_dualscope_first_slice_preflight_rerun_analysis.py`
- `docs/dualscope_first_slice_preflight_rerun.md`
- Independent preflight rerun outputs and analysis outputs.

## Progress

- [x] M1: rerun scope and contract frozen
- [x] M2: wrapper implementation / CLI / artifacts completed
- [x] M3: single verdict and recommendation completed

## Surprises & Discoveries

- The canonical preflight implementation is already usable as a rerun engine; the missing part was a standalone phase package for the autonomous run.

## Decision Log

- Reuse the canonical preflight implementation rather than forking the check logic. This avoids drift between preflight and rerun semantics.

## Plan of Work

Run the preflight into `outputs/dualscope_first_slice_preflight_rerun/default`, then analyze that directory into `outputs/dualscope_first_slice_preflight_rerun_analysis/default`.

## Concrete Steps

1. Run `scripts/build_dualscope_first_slice_preflight_rerun.py`.
2. Run `scripts/build_post_dualscope_first_slice_preflight_rerun_analysis.py`.
3. Compile newly added Python files.
4. Record verdict and next recommendation in the 5-hour run log/status.

## Validation and Acceptance

Accepted verdicts:

- `First slice preflight rerun validated`
- `Partially validated`
- `Not validated`

Validation requires all required rerun artifacts, a pass-through canonical preflight verdict, and no forbidden expansion.

## Idempotence and Recovery

The rerun is safe to repeat. It overwrites only the rerun output directories and does not modify data, labels, gates, model weights, or historical outputs.

## Outputs and Artifacts

- `outputs/dualscope_first_slice_preflight_rerun/default`
- `outputs/dualscope_first_slice_preflight_rerun_analysis/default`

## Remaining Risks

- GPU visibility depends on the active Python/CUDA environment. If CUDA is hidden, the rerun must record that honestly.

## Next Suggested Plan

If validated, continue to `dualscope-minimal-first-slice-real-run-readiness-package`.

