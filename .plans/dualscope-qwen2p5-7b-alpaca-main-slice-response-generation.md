# DualScope Qwen2.5-7B Alpaca Main-Slice Response Generation

## Purpose / Big Picture

Execute the validated bounded Stanford Alpaca main-slice response-generation step for DualScope-LLM. This grows beyond the earlier 8-response first-slice smoke while preserving the current small-step SCI3 track: Qwen2.5-7B only, Stanford Alpaca only, lexical trigger baseline first, fixed target first, and no full matrix.

## Scope

### In Scope

- Generate or explicitly block 64 bounded response rows selected from 32 Alpaca source examples.
- Use `models/qwen2p5-7b-instruct`, bound to `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- Use lexical trigger `cftrigger` and fixed target `I have completed the requested instruction.`
- Record response JSONL, summary, capability/fallback flags, budget trace, blockers, report, verdict, and tracked registry.
- Preserve `without_logprobs` honesty unless real token logprob artifacts are produced.

### Out of Scope

- No training, LoRA, QLoRA, or full finetune.
- No full matrix, new model axis, semantic trigger execution, behavior-shift target execution, AdvBench, or JBB.
- No route_c continuation and no `199+` planning.
- No detection metric computation beyond availability summaries.
- No fabricated responses, logprobs, labels, benchmark truth, or paper-scale performance claims.

## Repository Context

- Validated predecessor registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json`
- Input labeled pairs: `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`
- Response-generation CLI: `scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py`
- Core implementation: `src/eval/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py`
- Output directory: `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default`
- Tracked registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation.json`

## Progress

- [x] M1: Read AGENTS, PLANS, master plan, task queue, and validated Alpaca main-slice plan.
- [x] M2: Add task-specific response-generation CLI and artifact writer.
- [x] M3: Compile and dry-check the blocker/artifact path.
- [x] M4: Execute bounded Qwen2.5-7B Alpaca main-slice response generation or write explicit blocker artifacts.
- [x] M5: Update docs, verdict registry, and final report.

## Decision Log

- The available tracked input is `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`, which contains enough clean/poisoned lexical-trigger rows to select the planned 32-source/64-row bounded main slice.
- The task records `without_logprobs` capability because this response-generation step does not claim token logprob extraction.
- The hard generation attempt cap remains 72, matching the validated plan.

## Validation

Run:

```bash
python3 -m py_compile \
  src/eval/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py \
  scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py
```

Then run the bounded CLI with:

```bash
HF_HOME=/mnt/sda3/lh/huggingface \
TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers \
HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub \
TMPDIR=/mnt/sda3/lh/tmp \
CUDA_VISIBLE_DEVICES=2,3 \
python3 scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py \
  --model-dir models/qwen2p5-7b-instruct \
  --input-jsonl data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --output-dir outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default \
  --max-source-examples 32 \
  --expected-response-rows 64 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --max-generation-attempts 72 \
  --load-in-4bit \
  --allow-without-logprobs \
  --seed 2025
```

Validated only if real generated rows exist for the bounded main slice and the final verdict is `Qwen2.5-7B Alpaca main-slice response generation validated`. Runtime blockers must produce explicit blocker artifacts and a partial or not-validated verdict.

## Result

The task is `Partially validated`. The CLI selected 32 source examples and 64 response rows, wrote response JSONL rows with explicit blocked status, and produced summary, capability, fallback, budget, blocker, report, verdict, and tracked registry artifacts. Real generation did not run because CUDA was unavailable in this worktree runtime: `nvidia-smi` could not communicate with the NVIDIA driver and PyTorch selected CPU, while CPU generation is disabled for this 7B task. A 4-bit attempt was also blocked because `bitsandbytes` is unavailable.
