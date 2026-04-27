# DualScope Qwen2.5-7B Behavior-Shift Target Smoke Result Package

## Purpose / Big Picture

Package bounded behavior-shift target smoke responses and metrics, separating real evidence from fallback and blocked metrics.

## Scope

### In Scope

- Summarize response rows, detection metrics, behavior target success/ASR, fallback status, and limitations.
- Preserve clean utility and logprob blockers.
- Route to AdvBench small-slice materialization after validated packaging.

### Out of Scope

- Full target-family claims.
- Unsafe behavior generation.
- New metric computation.
- Benchmark truth or gate changes.

## Validation

```bash
python3 -m py_compile src/eval/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package.py
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package.py --help
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package.py
```
