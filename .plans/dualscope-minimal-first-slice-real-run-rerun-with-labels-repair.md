# dualscope-minimal-first-slice-real-run-rerun-with-labels-repair

## Purpose / Big Picture

The labeled rerun is partially validated because Stage 3 predictions are source-example level while labels are condition-row level. This repair compresses the blocker into a reproducible condition-level rerun input slice without changing labels, benchmark truth, gates, budgets, or model scope.

## Scope

### In Scope

- Read the labeled rerun artifacts and clean/poisoned label JSONL.
- Detect source-level repeated predictions.
- Materialize a small `row_id` keyed condition-level rerun input slice.
- Write blocker-compression, input-manifest, summary, verdict, and next-step artifacts.
- Register the repair task in the local queue so future orchestrator runs can emit a direct prompt.

### Out of Scope

- No condition-level model execution yet.
- No AUROC/F1/ASR/utility metric reporting.
- No model training, full matrix, benchmark-truth changes, gate changes, or route_c continuation.

## Repository Context

This plan consumes:

- `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/`
- `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`

It writes:

- `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair/default/`

## Deliverables

- `src/eval/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair.py`
- `scripts/build_dualscope_minimal_first_slice_real_run_rerun_with_labels_repair.py`
- Queue/orchestrator handling for validated repair tasks.
- Repair/compression artifacts and a condition-level rerun input JSONL.

## Progress

- [x] M1: Repair scope and blocker compression contract frozen.
- [x] M2: Repair builder and CLI implemented.
- [x] M3: Queue/orchestrator direct repair handling implemented.
- [x] M4: Validation completed.

## Validation and Acceptance

Accepted verdict:

- `Repair/compression package validated`

Validation requires a condition-level input slice with equal clean and poisoned-triggered rows, no model-output fabrication, explicit performance-metric blockers, and a next-step recommendation to run a condition-level rerun.

## Next Suggested Plan

Continue to `dualscope-minimal-first-slice-condition-level-rerun`.
