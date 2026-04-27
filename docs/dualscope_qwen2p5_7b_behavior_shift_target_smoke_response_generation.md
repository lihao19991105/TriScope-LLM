# DualScope Qwen2.5-7B Behavior-Shift Target Smoke Response Generation

This smoke task tests a safe behavior-shift target on a bounded Alpaca slice. The poisoned condition asks the model to start with `Safety note:` and then answer safely. This is a controlled target-behavior proxy, not harmful content generation.

Run in a GPU-visible shell:

```bash
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation.py \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --target-response-plan-dir outputs/dualscope_first_slice_target_response_generation_plan/default \
  --allow-without-logprobs
```

Primary outputs:

- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_responses.jsonl`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_summary.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_blockers.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_report.md`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_verdict.json`
