# DualScope Qwen2.5-7B Semantic Trigger Smoke Result Package

This package summarizes bounded semantic trigger smoke evidence. It separates real detection and ASR metrics from blocked clean utility and unavailable logprob metrics.

Run:

```bash
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package.py
```

Outputs:

- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/result_package_summary.json`
- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/metric_availability_matrix.json`
- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/result_package_report.md`
- `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/result_package_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-result-package.json`
