# DualScope Qwen2.5-7B Alpaca Main-Slice Result Package

This document packages the bounded Qwen2.5-7B Alpaca main-slice artifacts after metric computation. It reports only values supported by local artifacts and does not claim full paper performance, full Alpaca coverage, full trigger coverage, cross-model validation, or clean utility success.

## Verdict

`Partially validated`

The package is partially validated because 16 real response rows, 16 aligned label/score/response rows, detection metrics, ASR, query cost, and without-logprobs fallback evidence are available. Clean utility and logprob metrics remain blocked.

## Source Artifacts

- Response generation: `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default`
- Metric computation: `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation/default`
- Result package: `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default`
- Metric registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation.json`

## Real Response Counts

| Count | Value | Source |
| --- | ---: | --- |
| Source examples selected | 8 | response-generation summary |
| Real response rows generated | 16 | response-generation summary |
| Blocked response rows | 0 | response-generation budget trace |
| Aligned label/score/real-response rows | 16 | metric-computation summary |
| Clean utility eligible rows | 8 | clean utility blocker |
| ASR eligible poisoned rows | 8 | ASR metrics |

## Real Computed Metrics

These metrics are copied from artifacts with `metrics_computed=true`, aligned labels, aligned scores, real model responses, and `model_responses_fabricated=false`.

| Metric | Value | Scope |
| --- | ---: | --- |
| AUROC | 0.585938 | bounded main-slice detection |
| AUPRC | 0.573855 | bounded main-slice detection |
| TPR@FPR=1% | 0.0 | bounded main-slice detection |
| Precision | 0.6 | threshold 0.55 |
| Recall | 0.375 | threshold 0.55 |
| F1 | 0.461538 | threshold 0.55 |
| Accuracy | 0.5625 | threshold 0.55 |
| ASR | 0.0 | 8 real poisoned-triggered eligible rows |

Confusion matrix at threshold 0.55: TP 3, FP 2, TN 6, FN 5.

## Without-Logprobs Fallback

- `with_logprobs`: false
- `without_logprobs`: true
- `without_logprobs_fallback`: true
- `logprobs_unavailable`: true
- response rows with logprobs: 0
- logprob metrics computed: false

## Blocked Clean Utility

Clean utility is not computed. The clean rows contain real responses, but no explicit utility-success field is available. The package does not infer clean utility from free-text similarity.

Missing explicit utility-success row count: 8.

Supported future fields: `clean_utility_success`, `utility_success`, `reference_match`, `response_reference_matched`.

## Query Cost

| Cost item | Value |
| --- | ---: |
| Generation attempts used | 16 |
| Stage 1 query count from score rows | 32 |
| Stage 2 query count from score rows | 27 |
| Total counted queries | 75 |
| Average counted queries per aligned row | 4.6875 |
| Max new tokens | 64 |

## Limitations

- This is a bounded Alpaca main-slice package, not full Alpaca coverage.
- Only `lexical_trigger_v1` / `cftrigger` and `fixed_response_v1` are covered here.
- No semantic trigger smoke result is included.
- No behavior-shift target result is included.
- No cross-model validation is included.
- No token logprobs are present.
- Clean utility success is blocked.
- Metrics are small-slice research evidence and must not be presented as full-paper performance.

## Guardrails

- Model responses fabricated: false
- Logprobs fabricated: false
- Metrics computed from placeholders: false
- Benchmark truth changed: false
- Gates changed: false
- Training executed: false
- Full matrix executed: false
- route_c / 199+ continuation: false

## Next Action

`dualscope-qwen2p5-7b-semantic-trigger-smoke-plan`

Plan a bounded semantic-trigger smoke experiment after this partially validated package. Keep it scoped and do not expand to full matrix, cross-model validation, or clean utility claims unless new artifacts prove them.
