# DualScope AdvBench Small-Slice Metric Computation

## Current Stage Goal

Compute only metrics supported by the bounded AdvBench response artifacts and explicitly block unsupported performance claims.

## Core Result

- Final verdict: `Partially validated`
- Response rows: `16`
- Real response rows: `0`
- Blocked rows: `16`
- Response availability rate: `0.0`
- Blocker type: `torch_cuda_unavailable`

## Available Metrics

- Response availability and blocked-row rate are available.
- Cost/fallback summary is available.
- Refusal rate status: `NOT_APPLICABLE`
- Target behavior status: `NOT_APPLICABLE`
- Detection metrics status: `NOT_APPLICABLE`

## Metric Blockers

- Real model responses are unavailable: `blocked`.
- Logprobs are unavailable: `not_applicable`.
- Label/score-aligned detection metrics are unavailable: `not_applicable`.
- ASR and clean utility are unavailable: `not_applicable`, `not_applicable`.

## Readiness Matrix

- `response_availability`: `available` - Response JSONL exists and exposes generated versus blocked row counts.
- `blocker_fallback_summary`: `available` - Blocker and without-logprobs fallback fields are present.
- `refusal_rate`: `not_applicable` - No real model_response rows are available; blocked empty rows cannot support refusal or safety behavior metrics.
- `safety_behavior_proxy`: `not_applicable` - No real model_response rows are available; blocked empty rows cannot support refusal or safety behavior metrics.
- `target_behavior_status`: `not_applicable` - No target definitions or target_matched values are present in the bounded response rows.
- `detection_metrics`: `not_applicable` - No real response rows are available for label/score-aligned detection metrics.
- `cost_fallback_summary`: `available` - Computed from response row capability and blocker fields.
- `full_matrix_or_training`: `not_run` - Hard constraint: this task does not run full matrix or training.

## Verdict

This package is partially validated because artifact-level availability and blocker/fallback summaries are real, but performance metrics are blocked by zero generated model responses.

