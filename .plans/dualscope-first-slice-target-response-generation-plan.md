# dualscope-first-slice-target-response-generation-plan

## Purpose / Big Picture

The labeled first-slice chain has labels and condition-level detection alignment, but ASR and clean utility still require real model responses. This plan freezes the response-generation handoff for the same first-slice rows without changing the trigger, target, labels, gates, or matrix scope.

## Scope

### In Scope

- Read the labeled rerun artifacts under `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/`.
- Read the clean/poisoned labeled slice contracts under `outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default/`.
- Build a row-id keyed response-generation input manifest for the already joined first-slice label rows.
- Freeze the expected output schema needed later for ASR and clean utility.
- Write verdict and report artifacts under `outputs/dualscope_first_slice_target_response_generation_plan/default/`.

### Out of Scope

- No model response generation in this task.
- No fabricated model outputs.
- No benchmark truth, label, or gate changes.
- No full-matrix expansion.
- No route_c continuation or 199+ planning.

## Repository Context

This task follows:

- `.plans/dualscope-first-slice-clean-poisoned-labeled-slice-plan.md`
- `.plans/dualscope-minimal-first-slice-real-run-rerun-with-labels.md`
- `.plans/dualscope-minimal-first-slice-condition-level-rerun.md`

It adds a small planning builder in `src/eval` and a CLI wrapper in `scripts`, matching the existing first-slice artifact-builder style.

## Deliverables

- `src/eval/dualscope_first_slice_target_response_generation_plan.py`
- `scripts/build_dualscope_first_slice_target_response_generation_plan.py`
- `outputs/dualscope_first_slice_target_response_generation_plan/default/dualscope_first_slice_target_response_generation_plan_verdict.json`
- `outputs/dualscope_first_slice_target_response_generation_plan/default/dualscope_first_slice_target_response_generation_plan_report.md`

## Progress

- [x] M1: Read repository instructions, DualScope master plan, and latest first-slice labeled artifacts.
- [x] M2: Implement target-response generation planning builder and CLI.
- [x] M3: Run validation and generate plan artifacts.
- [x] M4: Complete PR workflow and trigger `@codex review`.

## Surprises & Discoveries

- Local branch creation is blocked because `.git/index.lock` cannot be created on the read-only git filesystem. Use the GitHub fallback if local commit and `scripts/codex-pr.sh` remain blocked.
- Local commit failed for the same read-only `.git/index.lock` reason; `scripts/codex-pr.sh` also failed because the checkout remains on `main`. The PR workflow must use the GitHub fallback.

## Decision Log

- The plan uses the 24 label rows already joined by the labeled rerun, not the full 144-row labeled slice, to preserve the current first-slice execution scope.
- The frozen target response remains `I have completed the requested instruction.` with `exact_or_contains` matching.
- The planning task writes prompts and generation configs only; it does not write any model responses.

## Plan of Work

Build a compact artifact package that verifies the labeled inputs, joins the selected row IDs back to their prompts, records the generation request schema, and explicitly marks ASR and clean utility as future metrics that require generated responses.

## Concrete Steps

1. Add the core builder.
2. Add the CLI wrapper.
3. Run the CLI against the default first-slice labeled artifacts.
4. Compile the new Python files.
5. Commit, open a PR, request `@codex review`, or document the fallback path if local git remains blocked.

## Validation and Acceptance

The task is complete when:

- The verdict artifact says `Target-response generation plan validated`.
- The report artifact is written.
- The planned rows include balanced clean and poisoned-triggered rows from the current joined first-slice labeled rerun.
- Source target and trigger contracts pass.
- `py_compile` passes.
- Scope flags record no training, no full matrix, no benchmark truth changes, no gate changes, and no route_c continuation.

## Idempotence and Recovery

The builder overwrites only the requested output directory. It can be safely rerun with the same input artifact directories and seed.

## Outputs and Artifacts

- `dualscope_first_slice_target_response_generation_plan_scope.json`
- `dualscope_first_slice_target_response_generation_plan_source_artifact_audit.json`
- `dualscope_first_slice_target_response_generation_plan_manifest.json`
- `dualscope_first_slice_target_response_generation_plan_rows.jsonl`
- `dualscope_first_slice_target_response_generation_plan_output_schema.json`
- `dualscope_first_slice_target_response_generation_plan_command_plan.json`
- `dualscope_first_slice_target_response_generation_plan_metric_dependency.json`
- `dualscope_first_slice_target_response_generation_plan_summary.json`
- `dualscope_first_slice_target_response_generation_plan_verdict.json`
- `dualscope_first_slice_target_response_generation_plan_report.md`
