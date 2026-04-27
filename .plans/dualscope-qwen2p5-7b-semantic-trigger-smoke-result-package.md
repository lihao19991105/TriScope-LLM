# DualScope Qwen2.5-7B Semantic Trigger Smoke Result Package

## Purpose / Big Picture

Package the bounded semantic trigger smoke response and metric artifacts without claiming full trigger-family or full-matrix performance.

## Scope

### In Scope

- Summarize real response count, detection metrics, ASR, fallback status, blockers, and limitations.
- Preserve clean utility and logprob blockers.
- Write a tracked verdict registry routing to behavior-shift smoke response generation.

### Out of Scope

- New response generation.
- Metric recomputation.
- Full trigger-family claims.
- Benchmark truth or gate changes.

## Validation

```bash
python3 -m py_compile src/eval/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package.py
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package.py --help
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package.py
```
