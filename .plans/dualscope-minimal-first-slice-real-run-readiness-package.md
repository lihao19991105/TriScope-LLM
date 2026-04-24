# dualscope-minimal-first-slice-real-run-readiness-package

## Purpose / Big Picture

Prepare the final go/no-go bundle immediately before the DualScope minimal first-slice real run. This phase does not execute training or inference. It confirms whether the dataset, GPU, model, scope, planned commands, and required command entrypoints are ready for a minimal, non-expanded real run.

## Scope

### In Scope

- Read materialization, preflight rerun, readiness-after-materialization, and real-run plan artifacts.
- Confirm dataset path, model path, GPU capability, and first-slice scope.
- Check whether planned real-run command entrypoints are present.
- Produce a final go/no-go recommendation.

### Out of Scope

- Running LoRA/QLoRA training.
- Running Stage 1 / Stage 2 / Stage 3 real inference.
- Expanding the matrix, model axis, budget, trigger family, or datasets.
- Changing benchmark truth or gate semantics.

## Repository Context

This phase follows:

- `dualscope-first-slice-dataset-materialization`
- `dualscope-minimal-first-slice-real-run-preflight-rerun`

It prepares, but does not execute, `dualscope-minimal-first-slice-real-run`.

## Deliverables

- `src/eval/dualscope_minimal_first_slice_real_run_readiness_package.py`
- `src/eval/post_dualscope_minimal_first_slice_real_run_readiness_package_analysis.py`
- `scripts/build_dualscope_minimal_first_slice_real_run_readiness_package.py`
- `scripts/build_post_dualscope_minimal_first_slice_real_run_readiness_package_analysis.py`
- `docs/dualscope_minimal_first_slice_real_run_readiness_package.md`
- readiness package outputs and post-analysis outputs.

## Progress

- [x] M1: go/no-go scope frozen
- [x] M2: readiness checks and artifacts completed
- [x] M3: single verdict and recommendation completed

## Surprises & Discoveries

- The data and preflight checks are ready, but the command plan references some minimal real-run entrypoints that are not yet present in the repository.

## Decision Log

- Treat missing real-run entrypoints as a readiness blocker rather than pretending the real run can safely start.

## Plan of Work

Build a readiness package that records the current go/no-go state and gives exactly one next recommendation.

## Concrete Steps

1. Load plan, materialization, and preflight rerun artifacts.
2. Check dataset/model/GPU readiness.
3. Check command entrypoint availability.
4. Produce summary, checklist, report, verdict, and recommendation.
5. Run py_compile for added files.

## Validation and Acceptance

Accepted verdicts:

- `Minimal real run readiness validated`
- `Partially validated`
- `Not validated`

`Minimal real run readiness validated` requires data, GPU, preflight, and required real-run entrypoint checks to pass.

## Idempotence and Recovery

The package is safe to rerun. It writes only readiness artifacts and does not modify data, model weights, labels, gates, or historical outputs.

## Outputs and Artifacts

- `outputs/dualscope_minimal_first_slice_real_run_readiness_package/default`
- `outputs/dualscope_minimal_first_slice_real_run_readiness_package_analysis/default`

## Remaining Risks

- Minimal real-run command entrypoints must be implemented before actual execution if they remain missing.

## Next Suggested Plan

If validated, enter `dualscope-minimal-first-slice-real-run`. If partially validated due to missing entrypoints, implement the minimal real-run command-entrypoint package first.

