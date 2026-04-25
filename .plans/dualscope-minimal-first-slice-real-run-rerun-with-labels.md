# dualscope-minimal-first-slice-real-run-rerun-with-labels

## Purpose / Big Picture

This plan reruns the minimal first-slice chain with the clean/poisoned label contract attached. It records whether labels are merely aligned to source-level Stage 3 outputs or are ready for honest clean-vs-poisoned performance metrics.

## Scope

### In Scope

- Run the existing minimal first-slice rerun into a nested artifact directory.
- Read clean/poisoned first-slice labels.
- Join labels to available Stage 3 outputs.
- Export alignment, metric-readiness, report, summary, and verdict artifacts.

### Out of Scope

- No training.
- No full matrix.
- No benchmark truth or gate changes.
- No fabricated model responses.
- No route_c continuation.

## Repository Context

This task consumes `outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default/` and writes `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/`.

## Deliverables

- `src/eval/dualscope_minimal_first_slice_real_run_rerun_with_labels.py`
- `scripts/build_dualscope_minimal_first_slice_real_run_rerun_with_labels.py`
- labeled rerun artifacts under `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/`

## Progress

- [x] M1: Scope and artifact contract frozen.
- [x] M2: Labeled rerun builder restored.
- [x] M3: Existing run honestly remains partially validated due source-level predictions.

## Validation and Acceptance

Validated only when condition-row-level predictions and required model responses are aligned. Partially validated when labels join only to source-level outputs.

## Next Suggested Plan

If partially validated, continue to `dualscope-minimal-first-slice-real-run-rerun-with-labels-repair`.
