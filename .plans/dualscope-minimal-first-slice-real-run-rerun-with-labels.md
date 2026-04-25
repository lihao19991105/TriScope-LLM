# dualscope-minimal-first-slice-real-run-rerun-with-labels

## Purpose / Big Picture

This plan reruns the minimal first-slice chain with the clean/poisoned labeled slice contract attached to metric readiness. It advances DualScope-LLM by connecting the first-slice real-run artifacts to explicit detection / ASR / utility label contracts while preserving the current dataset, model, trigger, target, and budget scope.

## Scope

### In Scope

- Rerun the existing minimal first-slice real-run rerun command.
- Read clean/poisoned labeled first-slice artifacts from `outputs/dualscope_first_slice_clean_poisoned_labeled_slice/`.
- Align available Stage 3 source-level outputs with clean/poisoned label rows.
- Export labeled metric readiness, alignment, summary, verdict, and report artifacts.

### Out of Scope

- No training.
- No full experiment matrix.
- No benchmark truth changes.
- No gate changes.
- No fabricated model responses.
- No route_c continuation or `199+` planning.

## Repository Context

- Reuses `scripts/build_dualscope_minimal_first_slice_real_run_rerun.py`.
- Reuses `src/eval/dualscope_minimal_first_slice_real_run_rerun.py`.
- Consumes local ignored artifacts from:
  - `outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default/`
  - `outputs/dualscope_first_slice_clean_poisoned_labeled_slice_analysis/default/`
- Writes new ignored artifacts under:
  - `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/`

This plan serves the DualScope mainline by tightening the first-slice metric contract. It does not continue historical TriScope / route_c chains.

## Deliverables

- `scripts/build_dualscope_minimal_first_slice_real_run_rerun_with_labels.py`
- `src/eval/dualscope_minimal_first_slice_real_run_rerun_with_labels.py`
- `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/dualscope_minimal_first_slice_real_run_rerun_with_labels_verdict.json`
- `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/dualscope_minimal_first_slice_real_run_rerun_with_labels_report.md`

## Progress

- [x] M1: Scope and artifact contract frozen.
- [x] M2: Labeled rerun builder implemented.
- [x] M3: Local validation completed.
- [x] M4: PR workflow completed.

## Surprises & Discoveries

- The current Stage 3 output is source-example level, while the clean/poisoned labeled slice is condition-row level. The rerun can therefore attach and validate label readiness, but cannot honestly compute final clean-vs-poisoned performance metrics until Stage 3 emits row-level predictions or model responses for both conditions.

## Decision Log

- Keep the verdict `Partially validated` when label artifacts are valid but row-level predictions are not available. This avoids overstating performance readiness.
- Write an explicit alignment artifact so the next task can close the remaining row-level output gap without changing benchmark truth.

## Plan of Work

Run the existing minimal first-slice rerun into a nested artifact directory, then read labeled slice contracts and row data. Join labels to Stage 3 outputs by `source_example_id`, record the condition-level mismatch, and write metric readiness artifacts that separate label readiness from performance metric readiness.

## Concrete Steps

1. Implement a CLI wrapper with input/output/seed/config-style arguments.
2. Implement the core builder.
3. Run py_compile.
4. Run the labeled rerun builder.
5. Verify required output artifacts.

## Validation and Acceptance

Required checks:

- `python3 -m py_compile scripts/build_dualscope_minimal_first_slice_real_run_rerun_with_labels.py`
- `python3 -m py_compile src/eval/dualscope_minimal_first_slice_real_run_rerun_with_labels.py`
- `scripts/build_dualscope_minimal_first_slice_real_run_rerun_with_labels.py --output-dir outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default --no-full-matrix`

## Idempotence and Recovery

The builder overwrites only its own output directory. It can be rerun safely after upstream labeled-slice or rerun artifacts change. It never changes benchmark truth, gates, branch history, remotes, or local datasets.

## Outputs and Artifacts

- `dualscope_minimal_first_slice_real_run_rerun_with_labels_scope.json`
- `dualscope_minimal_first_slice_real_run_rerun_with_labels_alignment.json`
- `dualscope_minimal_first_slice_real_run_rerun_with_labels_metric_readiness.json`
- `dualscope_minimal_first_slice_real_run_rerun_with_labels_summary.json`
- `dualscope_minimal_first_slice_real_run_rerun_with_labels_verdict.json`
- `dualscope_minimal_first_slice_real_run_rerun_with_labels_report.md`

## Remaining Risks

- Performance metrics remain unavailable until Stage 3 emits aligned clean/poisoned row-level predictions and model-response evidence.

## Next Suggested Plan

If this remains partially validated, the next step should repair row-level Stage 3 output alignment before artifact validation or result packaging.
