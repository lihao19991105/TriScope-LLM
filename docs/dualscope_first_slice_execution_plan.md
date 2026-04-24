# DualScope First Slice Execution Plan

The first slice is the smallest executable DualScope setting derived from the frozen experimental matrix.

## Frozen Slice

- Dataset: Stanford Alpaca
- Model: Qwen2.5-1.5B-Instruct
- Trigger: lexical trigger
- Target: fixed response / refusal-bypass
- Capability mode: without-logprobs by default; with-logprobs if available
- Baselines: illumination-only and DualScope budget-aware two-stage fusion

## Purpose

The first slice validates artifact shape and stage compatibility before any full matrix run. It should produce Stage 1, Stage 2, and Stage 3 artifacts plus budget and metric placeholders.

## Boundaries

This slice must not become a full matrix sweep, model-axis expansion, budget expansion, or route_c continuation.

