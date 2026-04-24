# dualscope-first-slice-data-source-intake-package

## Purpose / Big Picture

Create a user-facing intake package that states exactly what real Alpaca source file is needed, accepted formats, import commands, schema expectations, and next actions.

## Scope

### In Scope
- Source-file requirements.
- Accepted JSON/JSONL schemas.
- Import and schema-check command examples.
- User action items.

### Out of Scope
- Downloading or fabricating data.
- Training or real-run execution.

## Repository Context

This follows partially validated dataset materialization when no real source is available.

## Deliverables

Implementation, CLI, docs, artifacts, report, verdict, recommendation.

## Progress

- [x] M1: intake requirements frozen.
- [x] M2: intake package artifacts completed.
- [x] M3: single verdict and recommendation completed.

## Surprises & Discoveries

- No local real Alpaca source file was found.

## Decision Log

- The package recommends dataset materialization as the next concrete action.

## Plan of Work

Generate source requirements, format examples, command examples, schema expectation, and user action items.

## Validation and Acceptance

All required intake artifacts exist and py_compile passes.

## Idempotence and Recovery

The package is static and safe to regenerate.

## Outputs and Artifacts

`outputs/dualscope_first_slice_data_source_intake_package/default`

## Remaining Risks

Requires user-provided real data.

## Next Suggested Plan

Run dry-run config and contract validator.
