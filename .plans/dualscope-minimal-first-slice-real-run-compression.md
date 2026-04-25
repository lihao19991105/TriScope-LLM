# dualscope-minimal-first-slice-real-run-compression

## Background

The minimal first-slice real run produced a complete artifact chain but ended as `Partially validated` because Stage 1 / Stage 2 remained protocol-compatible deterministic no-model-execution, Stage 2 used the without-logprobs fallback, and evaluation had only metric placeholders.

## Goal

Compress the partial state into concrete capability gaps and next actions without changing benchmark truth, gates, budgets, model axes, datasets, triggers, or targets.

## Non-goals

- No training
- No full matrix
- No label fabrication
- No fake logprobs
- No route_c recursion

## Milestones

- [x] M1: compression scope frozen
- [x] M2: blocker diagnostics and artifacts completed
- [x] M3: single verdict and recommendation completed

## Progress

- Rechecked the minimal first-slice real-run compression artifacts under `outputs/dualscope_minimal_first_slice_real_run_compression/default/`.
- Hardened compression probe discovery so reruns preserve already-copied root-level model/logprob probe artifacts and can still fall back to nested probe or enablement outputs.
- Kept the recommendation scoped to the next missing first-slice capability; no benchmark truth, gates, route_c chains, training, or full-matrix execution were changed.

## Exit criteria

Verdict is one of `Real-run compression validated`, `Partially validated`, `Not validated`.
