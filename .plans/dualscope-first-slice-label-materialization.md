# dualscope-first-slice-label-materialization

## Purpose / Big Picture

This plan freezes what labels are actually available for the current DualScope minimal first-slice and prevents metric overclaiming. The previous real run had no performance labels, so AUROC/F1-style reporting must remain blocked until a clean/poisoned label source exists.

## Scope

### In Scope

- Inspect materialized Stanford Alpaca rows and first-slice candidate queries.
- Freeze artifact-validation labels and schema-level labels.
- Record unavailable clean/poisoned, backdoor binary, ASR, and target behavior labels.
- Produce metric readiness artifacts.

### Out of Scope

- No synthetic label fabrication.
- No response-based backdoor inference.
- No benchmark truth changes.
- No gate changes.
- No model training or full matrix.

## Deliverables

- Label materialization implementation, CLI, post-analysis, docs.
- Label contract and metric readiness artifacts.
- Single verdict and recommendation.

## Progress

- [x] M1: label scope and non-fabrication contract frozen
- [x] M2: label artifacts completed
- [x] M3: single verdict and recommendation completed

## Validation and Acceptance

The stage is partially validated when schema/artifact labels are available but performance labels are not. It is validated only once clean/poisoned detection labels and target-behavior labels are available from a legitimate source.
