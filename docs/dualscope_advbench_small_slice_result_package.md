# DualScope AdvBench Small-Slice Result Package

## Current Stage Goal

Package the bounded AdvBench small-slice status from existing materialization, response-generation, and metric-computation artifacts without fabricating behavior or performance evidence.

## Core Result

- Final verdict: `Partially validated`
- Recommended next step: `dualscope-advbench-small-slice-response-generation-blocker-closure`
- Materialized source rows: `32`
- Selected response rows: `16`
- Real model responses: `0`
- Blocked response rows: `16`
- Primary blocker: `torch_cuda_unavailable`
- Without-logprobs fallback: `True`

## Metric Availability

- `materialization`: status=`available`, reportable=`True`, blocker=``
- `response_availability`: status=`available`, reportable=`True`, blocker=``
- `cost_fallback_summary`: status=`available`, reportable=`True`, blocker=``
- `refusal_rate`: status=`not_applicable`, reportable=`False`, blocker=`No real model_response rows are available; blocked empty rows cannot support refusal or safety behavior metrics.`
- `safety_behavior_proxy`: status=`not_applicable`, reportable=`False`, blocker=`No real model_response rows are available; blocked empty rows cannot support refusal or safety behavior metrics.`
- `target_behavior_status`: status=`not_applicable`, reportable=`False`, blocker=`No target definitions or target_matched values are present in the bounded response rows.`
- `label_score_aligned_detection_metrics`: status=`not_applicable`, reportable=`False`, blocker=`No real response rows are available for label/score-aligned detection metrics.`
- `asr`: status=`not_applicable`, reportable=`False`, blocker=`No target definitions and no real target_matched response rows.`
- `clean_utility`: status=`not_applicable`, reportable=`False`, blocker=`AdvBench harmful-prompt slice has no clean utility contract here.`
- `with_logprobs_metrics`: status=`not_applicable`, reportable=`False`, blocker=`No logprobs are present in the bounded artifacts.`
- `full_paper_performance`: status=`not_applicable`, reportable=`False`, blocker=`This is a blocked bounded small-slice artifact package, not full-matrix evidence.`

## Limitations

- Bounded AdvBench small-slice only: 32 materialized rows and 16 selected response rows, not full AdvBench.
- Response generation produced zero real model responses in this worktree because CUDA was unavailable and CPU generation was disabled.
- Refusal rate, safety behavior proxy, target success, ASR, clean utility, and label/score detection metrics are not reportable without real model responses and required fields.
- The runner is in without-logprobs mode; with-logprobs confidence metrics are unavailable.
- This package makes no full-matrix, cross-model, full-paper performance, benchmark-truth, or gate claim.

## Non-Fabrication Guardrails

- Model responses fabricated: `False`
- Logprobs fabricated: `False`
- Metrics fabricated: `False`
- Benchmark truth changed: `False`
- Gates changed: `False`
- Full matrix executed: `False`
- Full paper performance claimed: `False`
- route_c / 199+ continued: `False`

