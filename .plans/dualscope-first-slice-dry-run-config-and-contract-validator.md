# dualscope-first-slice-dry-run-config-and-contract-validator

## Purpose / Big Picture

Validate a CPU-only dry-run first-slice configuration and ensure Stage 1 / Stage 2 / Stage 3 contracts join correctly without data, GPU inference, training, or full experiment execution.

## Scope

### In Scope
- Dry-run config.
- Stage contract join map.
- Artifact path plan.
- Capability fallback and budget config.
- Forbidden expansion check.

### Out of Scope
- Training.
- Inference.
- Dataset fabrication.

## Repository Context

Uses frozen Stage 1 / Stage 2 / Stage 3 artifacts and first-slice plans.

## Deliverables

Implementation, CLI, docs, artifacts, report, verdict, recommendation.

## Progress

- [x] M1: dry-run validation scope frozen.
- [x] M2: dry-run artifacts completed.
- [x] M3: single verdict and recommendation completed.

## Validation and Acceptance

All contract joins pass and no forbidden expansion is detected.

## Outputs and Artifacts

`outputs/dualscope_first_slice_dry_run_config_validator/default`

## Next Suggested Plan

Run artifact validator hardening.
