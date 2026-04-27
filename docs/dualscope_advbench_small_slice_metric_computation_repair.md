# DualScope AdvBench Small-Slice Metric Computation Repair

## Current Stage Goal

Compress the partially validated AdvBench metric-computation state into explicit metric availability, blockers, and next-step routing.

## Core Result

- Final verdict: `AdvBench small-slice metric computation repair validated`
- Source metric verdict: `Partially validated`
- Real response rows: `0`
- Blocked response rows: `16`
- Source blocker type: `torch_cuda_unavailable`
- Recommended next step: `dualscope-advbench-small-slice-response-generation-blocker-closure`
- Routing reason: `zero_real_responses_upstream_generation_blocker_preserved`

## Availability

- `response_availability`: reportable=`True`, source_status=`PASS`
- `cost_fallback_summary`: reportable=`True`, source_status=`PASS`
- `refusal_rate`: reportable=`False`, source_status=`NOT_APPLICABLE`
- `target_behavior_status`: reportable=`False`, source_status=`NOT_APPLICABLE`
- `label_score_aligned_detection_metrics`: reportable=`False`, source_status=`NOT_APPLICABLE`
- `attack_success_rate`: reportable=`False`, source_status=`NOT_APPLICABLE`
- `clean_utility`: reportable=`False`, source_status=`NOT_APPLICABLE`
- `with_logprobs_metrics`: reportable=`False`, source_status=`NOT_APPLICABLE`

## Blocked Metrics

- `refusal_rate`: No real model_response rows are available; blocked empty rows cannot support refusal or safety behavior metrics.
- `target_behavior_status`: No target definitions or target_matched values are present in the bounded response rows.
- `label_score_aligned_detection_metrics`: No real response rows are available for label/score-aligned detection metrics.
- `attack_success_rate`: No real target_matched response rows are available.
- `clean_utility`: AdvBench harmful-prompt slice has no clean utility contract in this task.
- `with_logprobs_metrics`: No token logprobs are present in bounded AdvBench artifacts.

## Guardrails

- Model responses fabricated: `False`
- Logprobs fabricated: `False`
- Benchmark truth changed: `False`
- Gates changed: `False`
- Full matrix executed: `False`
- Training executed: `False`
- route_c continued: `False`
- 199+ generated: `False`

