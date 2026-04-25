# dualscope-first-slice-real-run-artifact-validation-repair

## Purpose / Big Picture

The previous first-slice real-run artifact validation is only partially validated because it validates an older source-level rerun view and does not separate artifact completeness from condition-row alignment, capability fallback flags, and full model-response performance readiness.

This repair produces a minimal audit package for DualScope-LLM that explains the partial verdict without rerunning the matrix or fabricating AUROC, F1, ASR, utility, labels, or model outputs.

## Scope

### In Scope

- Read the prior artifact-validation output and post-analysis output.
- Read the latest labeled rerun, condition-level rerun, target-response-generation plan, and frozen Stage 1/2/3 contract artifacts.
- Separate the partial verdict into missing artifacts, schema mismatch, granularity mismatch, projected metric versus full metric confusion, capability/fallback flag status, and report/verdict/recommendation artifact status.
- Generate repair-only JSON, JSONL, Markdown, verdict, and recommendation artifacts.
- Run py_compile and both repair CLIs.

### Out of Scope

- No full matrix rerun.
- No dataset, model, trigger, target, or budget expansion.
- No benchmark-truth, label, gate, or model-output modification.
- No AUROC/F1/ASR/utility fabrication.
- No route_c continuation or 199+ planning.
- No claim that detection preview metrics are full model performance metrics.

## Repository Context

Inputs:

- `outputs/dualscope_first_slice_real_run_artifact_validation/default/`
- `outputs/dualscope_first_slice_real_run_artifact_validation_analysis/default/`
- `outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/`
- `outputs/dualscope_minimal_first_slice_condition_level_rerun/default/`
- `outputs/dualscope_first_slice_condition_row_level_fusion_alignment/default/`
- `outputs/dualscope_first_slice_target_response_generation_plan/default/`
- `outputs/dualscope_illumination_screening_freeze/default/`
- `outputs/dualscope_confidence_verification_with_without_logprobs/default/`
- `outputs/dualscope_budget_aware_two_stage_fusion_design/default/`

Outputs:

- `outputs/dualscope_first_slice_real_run_artifact_validation_repair/default/`
- `outputs/dualscope_first_slice_real_run_artifact_validation_repair_analysis/default/`

This task serves the DualScope mainline only. It does not continue historical route_c work.

## Deliverables

- `src/eval/dualscope_first_slice_real_run_artifact_validation_repair.py`
- `src/eval/post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py`
- `scripts/build_dualscope_first_slice_real_run_artifact_validation_repair.py`
- `scripts/build_post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py`
- `docs/dualscope_first_slice_real_run_artifact_validation_repair.md`
- Repair and post-analysis output directories.

## Progress

- [x] M1: Prior partial verdict and latest first-slice artifacts inspected.
- [x] M2: Repair builder and CLI implemented.
- [x] M3: Post-analysis builder and CLI implemented.
- [x] M4: Repair artifacts generated and validation commands completed.

## Surprises & Discoveries

- Git branch creation failed because Git could not create a ref lock in `.git/refs/heads/codex`.
- `outputs/dualscope_first_slice_condition_row_level_fusion_alignment/default/` is absent, but `dualscope_minimal_first_slice_condition_level_rerun_alignment.json` exists and records condition-row alignment.
- The condition-level rerun provides preview detection metrics with `real_performance_claimed: false`; ASR and clean utility remain blocked by missing real generated model responses.
- Repair and post-analysis CLIs both returned `First-slice real-run artifact validation repair validated`.

## Decision Log

- Treat repair validation as validation of the repair/audit package, not as a claim that full paper performance metrics are ready.
- Use condition-level rerun artifacts as the current row-level evidence source without materializing a new alignment directory or rerunning Stage 1/2/3.
- Keep the next recommendation on model-response metrics, because full ASR and clean utility require real model responses.

## Validation and Acceptance

Required commands:

- `python3 -m py_compile src/eval/dualscope_first_slice_real_run_artifact_validation_repair.py src/eval/post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py scripts/build_dualscope_first_slice_real_run_artifact_validation_repair.py scripts/build_post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py`
- `python3 scripts/build_dualscope_first_slice_real_run_artifact_validation_repair.py --output-dir outputs/dualscope_first_slice_real_run_artifact_validation_repair/default --seed 42`
- `python3 scripts/build_post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py --repair-dir outputs/dualscope_first_slice_real_run_artifact_validation_repair/default --output-dir outputs/dualscope_first_slice_real_run_artifact_validation_repair_analysis/default --seed 42`

Accepted final verdicts:

- `First-slice real-run artifact validation repair validated`
- `Partially validated`
- `Not validated`
