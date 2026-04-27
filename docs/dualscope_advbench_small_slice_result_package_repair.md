# DualScope AdvBench Small-Slice Result Package Repair

## Current Stage Goal

Compress the partially validated AdvBench result-package state into explicit evidence boundaries, blockers, and routing.

## Core Result

- Final verdict: `AdvBench small-slice result package repair validated`
- Source result-package verdict: `Partially validated`
- Metric repair verdict: `AdvBench small-slice metric computation repair validated`
- Real response rows: `0`
- Blocked response rows: `16`
- Reportable performance metrics: `0`
- Primary blocker: `torch_cuda_unavailable`
- Recommended next step: `dualscope-advbench-small-slice-response-generation-blocker-closure`
- Routing reason: `zero_real_responses_result_package_boundary_preserved`

## Reportable Evidence

- `materialization_status`: Prior result package and materialization registry preserve bounded AdvBench source status.
- `response_availability`: Response rows and metric repair support selected, blocked, and real-response counts.
- `cost_fallback_summary`: Fallback status is artifact-supported and does not imply behavior performance.

## Blocked Evidence

- `refusal_rate_or_safety_proxy`: No real model responses exist in the bounded AdvBench response artifacts.
- `target_success_or_asr`: No target-match fields over real response rows are available.
- `label_score_detection_metrics`: No aligned labels and risk scores over real AdvBench response rows are available.
- `clean_utility`: AdvBench harmful-prompt slice has no clean utility contract here.
- `with_logprobs_confidence_metrics`: No token logprobs are present; without-logprobs fallback is recorded.

## Blocker Compression

- Root cause: `zero_real_model_responses`
- Primary owner: `response_generation`

## Guardrails

- Model responses fabricated: `False`
- Logprobs fabricated: `False`
- Metrics fabricated: `False`
- Benchmark truth changed: `False`
- Gates changed: `False`
- Full matrix executed: `False`
- Training executed: `False`
- route_c continued: `False`
- 199+ generated: `False`

