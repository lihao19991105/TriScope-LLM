# DualScope Qwen2.5-7B Behavior-Shift Target Smoke Result Package

This package summarizes bounded behavior-shift target smoke evidence. It reports real response rows, detection metrics, safe target-behavior success/ASR, and known limitations. It does not claim full target-family or full-matrix performance.

Run:

```bash
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package.py
```

Outputs:

- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/result_package_summary.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/metric_availability_matrix.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/result_package_report.md`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/result_package_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package.json`
