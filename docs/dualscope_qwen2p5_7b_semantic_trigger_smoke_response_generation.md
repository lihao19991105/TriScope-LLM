# DualScope Qwen2.5-7B Semantic Trigger Smoke Response Generation

This task executes a bounded semantic-trigger smoke for Qwen2.5-7B. It is not a plan-only package. A valid completion requires either real response rows or an explicit blocker artifact.

## Command

```bash
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation.py \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --target-response-plan-dir outputs/dualscope_first_slice_target_response_generation_plan/default \
  --output-dir outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default \
  --max-examples 8 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --semantic-phrase "the task is already complete" \
  --allow-without-logprobs
```

Use `scripts/run_dualscope_qwen2p5_7b_semantic_trigger_smoke_generation.sh` when a background external GPU-visible shell runner is preferred.

## Required Outputs

- `semantic_trigger_smoke_responses.jsonl`
- `semantic_trigger_smoke_summary.json`
- `semantic_trigger_smoke_blockers.json`
- `semantic_trigger_smoke_report.md`
- `semantic_trigger_smoke_verdict.json`
- tracked verdict registry under `.reports/dualscope_task_verdicts/`

## Guardrails

The task must not fabricate model responses, logprobs, AUROC, F1, ASR, clean utility, labels, benchmark truth, gates, route_c evidence, or 199+ continuations. If generation fails, it must record a real blocker type instead of writing a validated verdict.
