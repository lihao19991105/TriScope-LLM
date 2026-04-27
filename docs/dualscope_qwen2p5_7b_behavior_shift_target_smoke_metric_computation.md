# DualScope Qwen2.5-7B Behavior-Shift Target Smoke Metric Computation

This task computes only available metrics from bounded behavior-shift target smoke artifacts. It does not infer clean utility from free text and does not claim with-logprobs metrics when logprobs are unavailable.

Run:

```bash
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation.py
```

Outputs:

- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/available_metrics.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/readiness_matrix.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/detection_metrics.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/asr_metrics.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/metric_blockers.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/metric_report.md`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/metric_verdict.json`
