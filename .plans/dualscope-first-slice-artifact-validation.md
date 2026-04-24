# dualscope-first-slice-artifact-validation

## Background

The minimal first-slice smoke run emitted controlled Stage 1, Stage 2, Stage 3, baseline, metric-placeholder, budget, and manifest artifacts. This stage validates those artifacts against the frozen first-slice and experimental-matrix contracts.

## Goal

Verify artifact existence, field compatibility, capability-mode markers, budget fields, metrics placeholders, and report readability.

## Non-goals

- No new experiment execution.
- No model or budget expansion.
- No benchmark truth or gate changes.
- No route_c continuation.

## Validation scope

- Stage 1 illumination artifacts
- Stage 2 confidence artifacts
- Stage 3 fusion artifacts
- Baseline fields
- Metrics placeholder
- Cost / budget fields
- With-logprobs / without-logprobs markers
- Naming and report readability

## Milestones

- M1: artifact checklist and contract criteria frozen
- M2: artifact validation and compatibility analysis completed
- M3: single verdict and single recommendation completed

## Exit criteria

If validated, the only next step is `dualscope-first-slice-report-skeleton`.

## Progress

- [x] M1: artifact checklist and contract criteria frozen
- [x] M2: artifact validation and compatibility analysis completed
- [x] M3: single verdict and single recommendation completed

