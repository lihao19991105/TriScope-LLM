# DualScope Qwen2.5-7B First-Slice Response Generation Plan

This document is the handoff plan for Qwen2.5-7B-Instruct first-slice response generation. It is not a response artifact and does not report model outputs or metrics.

## Frozen Scope

| Axis | Frozen value |
| --- | --- |
| Project mainline | DualScope-LLM |
| Dataset | Stanford Alpaca first-slice |
| Model role | Qwen2.5-7B-Instruct as main experimental model |
| Trigger | Lexical trigger `cftrigger` |
| Target | Fixed target text: `I have completed the requested instruction.` |
| Protocol | Frozen Stage 1 illumination, Stage 2 confidence verification, Stage 3 budget-aware fusion |
| Execution mode | Planning only |

## Current Readiness

| Check | Status | Note |
| --- | --- | --- |
| SCI3 model-axis plan | ready | `outputs/dualscope_main_model_axis_upgrade_plan/default` exists |
| Alpaca labeled pairs | blocked | `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl` is missing in this worktree |
| Target-response plan | blocked | `outputs/dualscope_first_slice_target_response_generation_plan/default` is missing in this worktree |
| Qwen2.5-7B local path | partially ready | Mounted snapshot observed at `/mnt/sda3/lh/models/qwen2p5-7b-instruct`; repo-local `models/qwen2p5-7b-instruct` binding is absent |
| GPU visibility | blocked | Fresh `nvidia-smi` check failed to communicate with the NVIDIA driver; prior SCI3 artifacts record earlier visibility but do not make this session executable |
| Disk for fresh 7B materialization | partially ready | `/mnt/sda3/lh` has sufficient space and already contains the mounted model snapshot; the worktree filesystem has about 19 GB free and should not be used for fresh materialization |

## Execution Guardrails

- Do not use Qwen2.5-1.5B as a substitute for Qwen2.5-7B main-model evidence.
- Do not generate or write model responses until a real Qwen2.5-7B model path or approved external resource is supplied.
- Do not report logprobs, AUROC, F1, ASR, clean utility, latency, or cost metrics from this planning task.
- Do not alter labels, benchmark truth, gates, trigger definitions, target definitions, or Stage 1 / Stage 2 / Stage 3 protocol contracts.
- Do not expand to AdvBench, JBB, semantic triggers, contextual triggers, behavior-shift targets, or cross-model validation in this task.

## Successor Command Shape

The successor execution task may add a real generation entrypoint after blockers are cleared. The intended command shape is:

```bash
python3 scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py \
  --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --target-response-plan-dir outputs/dualscope_first_slice_target_response_generation_plan/default \
  --model-path /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --output-dir outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default \
  --seed 2025 \
  --trigger-text cftrigger \
  --target-text "I have completed the requested instruction." \
  --no-full-matrix
```

This command is a planned shape only. It has not been executed in this task.

## Verdict

Final verdict: `Partially validated`.

The plan is validated as a planning and blocker package, but actual Qwen2.5-7B first-slice response generation remains blocked by missing first-slice inputs, missing target-response plan outputs, absent repo-local model binding/config wiring, and failed current GPU visibility. A mounted Qwen2.5-7B snapshot exists at `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, but this task did not load it or generate responses.
