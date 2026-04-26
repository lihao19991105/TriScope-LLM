# DualScope Qwen2.5-7B Result Package Repair

- Final verdict: `Qwen2.5-7B result package repair validated`
- Recommended next step: `dualscope-sci3-main-experiment-expansion-plan`
- Prior result-package registry verdict: `Partially validated`
- Prior result-package directory exists: `False`
- Response-generation verdict: `Qwen2.5-7B first-slice response generation validated`
- Metric-computation verdict: `Partially validated`
- Metric-repair verdict: `Qwen2.5-7B metric computation repair validated`
- Real Qwen2.5-7B response rows: `8`
- Aligned metric rows: `8`
- Detection metrics reportable: `True`
- AUROC: `0.46875`
- AUPRC: `0.525`
- F1: `0.285714`
- Accuracy: `0.375`
- ASR reportable: `True`
- ASR: `0.0`
- Clean utility reportable: `False`
- Clean utility explicitly blocked: `True`
- Capability mode: `without_logprobs=True`, `with_logprobs=False`
- Clean utility is not inferred from free text.
- This package is first-slice evidence only; it is not full-paper performance.
- Benchmark truth changed: `False`
- Gates changed: `False`
- route_c / 199+ continuation: `False`
- Full matrix executed: `False`
- Training executed: `False`

## Regenerate

```bash
python3 scripts/build_dualscope_qwen2p5_7b_result_package_repair.py --seed 2025
```

