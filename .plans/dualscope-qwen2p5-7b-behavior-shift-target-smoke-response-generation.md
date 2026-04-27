# DualScope Qwen2.5-7B Behavior-Shift Target Smoke Response Generation

## Purpose / Big Picture

Run a bounded behavior-shift target smoke with Qwen2.5-7B. The target is a safe response-format shift, not harmful content generation.

## Scope

### In Scope

- Use Stanford Alpaca labeled pairs.
- Generate at most 8 source examples / 16 condition rows.
- Use Qwen2.5-7B from `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- Require real response JSONL rows or explicit blocker JSON.
- Record without-logprobs fallback.

### Out of Scope

- Full target family expansion.
- AdvBench or JBB execution.
- Harmful output elicitation.
- Training, full matrix, benchmark truth changes, or gate changes.

## Validation

```bash
python3 -m py_compile src/eval/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation.py
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation.py --help
```

Real generation should run only in the GPU-visible shell environment.
