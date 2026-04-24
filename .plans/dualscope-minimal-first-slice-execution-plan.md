# dualscope-minimal-first-slice-execution-plan

## Background

`dualscope-experimental-matrix-freeze` validated the paper-facing experiment matrix and recommended a minimal executable first slice. This plan turns that frozen slice into an execution contract without running the full matrix.

## Goal

Define a small, resource-safe first slice that can validate the DualScope Stage 1 -> Stage 2 -> Stage 3 artifact flow.

## Non-goals

- No full matrix run.
- No model-axis expansion.
- No budget expansion.
- No prompt-family expansion.
- No route_c continuation.
- No benchmark truth or gate changes.

## First-slice setting

- Dataset: Stanford Alpaca
- Model: Qwen2.5-1.5B-Instruct
- Trigger: lexical trigger
- Target: fixed response / refusal-bypass
- Capability: without-logprobs by default; with-logprobs only if local inference exposes token scores
- Baselines: illumination-only and DualScope budget-aware two-stage fusion

## Required artifacts

- first slice definition
- run contract
- expected artifact list
- validation criteria
- resource contract
- failure fallback plan
- summary, details, report, verdict, recommendation

## Validation criteria

The plan is valid if it reads the frozen matrix, keeps the slice inside the matrix boundary, defines all expected artifacts, and does not require a full experiment, training, or model expansion.

## Milestones

- M1: first-slice dataset / model / trigger / target / capability / baseline scope frozen
- M2: run contract / artifact / validation / resource / fallback contracts completed
- M3: single verdict and single recommendation completed

## Exit criteria

- Post-analysis returns one verdict.
- If validated, the only next step is `dualscope-minimal-first-slice-smoke-run`.

## Progress

- [x] M1: first-slice dataset / model / trigger / target / capability / baseline scope frozen
- [x] M2: run contract / artifact / validation / resource / fallback contracts completed
- [x] M3: single verdict and single recommendation completed

