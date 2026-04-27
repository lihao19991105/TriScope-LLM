# DualScope Qwen2.5-7B Behavior-Shift Target Smoke Metric Computation

## Purpose / Big Picture

Compute available bounded behavior-shift target smoke metrics from real Qwen2.5-7B response rows. This validates the smoke evidence while preserving clean utility and logprob blockers.

## Scope

### In Scope

- Align behavior-shift smoke responses with labels and condition-level scores.
- Compute detection metrics and ASR/target-success readiness when fields are available.
- Record clean utility and logprob limitations honestly.

### Out of Scope

- Harmfulness scoring or unsafe target expansion.
- Full target-family or full-matrix claims.
- Benchmark truth or gate changes.

## Validation

```bash
python3 -m py_compile src/eval/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation.py
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation.py --help
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation.py
```
