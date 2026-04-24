# dualscope-minimal-first-slice-real-run-rerun-with-model-or-fallback

## Purpose / Big Picture

This plan reruns the minimal first-slice pipeline after model execution and local logits capability have been enabled. It keeps a strict distinction between capability probes and Stage 1/Stage 2 entrypoint integration.

## Scope

### In Scope

- Rerun the existing minimal first-slice artifact chain.
- Attach model generation and local logits/logprob capability evidence.
- Record whether Stage 1/Stage 2 entrypoints still use protocol-compatible deterministic mode.
- Preserve metric placeholder limitations when performance labels remain unavailable.

### Out of Scope

- No training.
- No full matrix.
- No benchmark truth or gate changes.
- No fake model-execution or logprob claims.

## Progress

- [x] M1: rerun scope and capability evidence contract frozen
- [x] M2: rerun artifacts completed
- [x] M3: verdict and recommendation completed

## Acceptance

The rerun is validated only if Stage 1/Stage 2 consume model/logprob evidence directly and performance labels are available. Otherwise it is partially validated if the artifact chain runs and capability probes are attached honestly.
