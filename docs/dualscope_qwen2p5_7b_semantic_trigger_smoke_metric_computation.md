# DualScope Qwen2.5-7B Semantic Trigger Smoke Metric Computation

This task computes bounded semantic trigger smoke metrics from real Qwen2.5-7B response rows. It does not generate new responses, run a full trigger matrix, or infer unavailable utility/logprob metrics.

Run:

```bash
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation.py
```

Primary outputs:

- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/available_metrics.json`
- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/readiness_matrix.json`
- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/detection_metrics.json`
- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/asr_metrics.json`
- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/metric_blockers.json`
- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/metric_report.md`
- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/metric_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-computation.json`

Clean utility remains blocked unless explicit utility success fields are available. With-logprobs metrics remain blocked when response rows do not contain token logprobs.
