# dualscope-minimal-first-slice-condition-level-rerun

## Purpose / Big Picture

The labeled rerun repair produced a clean/poisoned condition-level input slice keyed by `row_id`. This task reruns the minimal DualScope Stage 1 / Stage 2 / Stage 3 chain on that exact slice so the outputs are condition-row level instead of source-example level.

This closes the immediate alignment blocker for condition-level detection artifacts while preserving the existing dataset, model, trigger, target, and budget scope.

## Scope

### In Scope

- Consume `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair/default/condition_level_rerun_input_slice.jsonl`.
- Consume `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair/default/condition_level_rerun_input_manifest.json`.
- Run the existing minimal Stage 1, Stage 2, and Stage 3 entrypoints over the 24-row condition-level slice.
- Join Stage 3 decisions back to `row_id`, condition, and `detection_label`.
- Write condition-level rerun summary, verdict, report, command/status artifacts, joined prediction rows, and metric-readiness artifacts.

### Out of Scope

- No benchmark truth, label, or gate changes.
- No full-matrix expansion.
- No model training or full finetune.
- No route_c continuation or 199+ planning.
- No paper-level ASR / clean-utility claim without real generated model responses.

## Repository Context

This plan extends the DualScope minimal first-slice chain after:

- `.plans/dualscope-minimal-first-slice-real-run-rerun-with-labels-repair.md`
- `src/eval/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair.py`
- `scripts/run_dualscope_stage1_illumination.py`
- `scripts/run_dualscope_stage2_confidence.py`
- `scripts/run_dualscope_stage3_fusion.py`

It writes to:

- `outputs/dualscope_minimal_first_slice_condition_level_rerun/default/`

## Deliverables

- `src/eval/dualscope_minimal_first_slice_condition_level_rerun.py`
- `scripts/build_dualscope_minimal_first_slice_condition_level_rerun.py`
- Condition-level rerun artifacts under `outputs/dualscope_minimal_first_slice_condition_level_rerun/default/`

## Progress

- [x] M1: Read repository instructions, DualScope plan state, and repair artifacts.
- [x] M2: Implement minimal condition-level rerun builder and CLI.
- [x] M3: Run validation and generate expected artifacts.
- [ ] M4: Commit, open PR, trigger `@codex review`, and report PR/review status.

## Surprises & Discoveries

- Local `.git` refs are mounted read-only, so local branch creation failed before edits. If local commit remains blocked, use a GitHub API fallback for branch/commit/PR creation and report the local filesystem blocker explicitly.
- The condition-level rerun produced 24 joined row-id keyed predictions, matching the 24-row repair manifest.
- The stage entrypoints still run in protocol-compatible deterministic mode, so AUROC/F1 are recorded only as condition-level detection previews and not as paper performance.

## Decision Log

- Reuse the existing Stage 1 / Stage 2 / Stage 3 entrypoints to avoid changing gates or benchmark truth.
- Treat condition-level AUROC/F1 as contract-level detection previews only, because the current stage entrypoints still run in protocol-compatible deterministic mode.
- Keep ASR and clean utility unavailable until real generated model responses are present.

## Plan of Work

Run the condition-level input slice through the existing entrypoint chain, then build a small audit layer that checks the manifest, validates row-id alignment, joins labels to final decisions, computes transparent condition-level detection preview metrics, and writes a conservative verdict/report.

## Concrete Steps

1. Add a core builder in `src/eval`.
2. Add a CLI wrapper in `scripts`.
3. Run the CLI against the repair-produced input slice and default output directory.
4. Run `py_compile` and inspect key artifacts.
5. Complete the PR workflow using local git if possible; otherwise use the GitHub fallback and document the blocker.

## Validation and Acceptance

Accepted condition-level rerun requires:

- Input manifest is `PASS` and declares 24 rows.
- Stage 1 / Stage 2 / Stage 3 commands pass.
- Stage 3 outputs are keyed by all input `row_id` values.
- Joined condition-level rows include both clean and poisoned-triggered labels.
- Output verdict and report are written.
- Scope flags confirm no training, no full matrix, no benchmark truth changes, no gate changes, and no route_c continuation.

## Idempotence and Recovery

The builder overwrites only the requested output directory artifacts. It can be safely rerun with the same input slice, manifest, output directory, and seed.

## Outputs and Artifacts

- `dualscope_minimal_first_slice_condition_level_rerun_scope.json`
- `dualscope_minimal_first_slice_condition_level_rerun_command_plan.json`
- `dualscope_minimal_first_slice_condition_level_rerun_stage_status.json`
- `dualscope_minimal_first_slice_condition_level_rerun_joined_predictions.jsonl`
- `dualscope_minimal_first_slice_condition_level_rerun_metric_readiness.json`
- `dualscope_minimal_first_slice_condition_level_rerun_detection_metrics.json`
- `dualscope_minimal_first_slice_condition_level_rerun_summary.json`
- `dualscope_minimal_first_slice_condition_level_rerun_verdict.json`
- `dualscope_minimal_first_slice_condition_level_rerun_report.md`
