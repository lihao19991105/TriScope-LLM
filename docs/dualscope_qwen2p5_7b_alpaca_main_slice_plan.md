# DualScope Qwen2.5-7B Alpaca Main-Slice Plan

Final verdict: `Qwen2.5-7B Alpaca main-slice plan validated`.

This is a planning-only artifact. It does not generate responses, compute metrics, train a model, run a full matrix, change benchmark truth, change gates, continue route_c, or create any `199+` legacy plan.

## Current Evidence Boundary

- The current 8 Qwen2.5-7B responses are first-slice smoke evidence, not full paper results.
- Detection metrics and ASR are first-slice only.
- Clean utility remains blocked unless explicit utility success or reference-match fields are generated later.
- Cross-model validation remains readiness only.
- Qwen2.5-7B-Instruct remains the main experimental model.
- Qwen2.5-1.5B-Instruct remains pilot / debug / automation / ablation only.

## Planned Main Slice

| Field | Plan |
| --- | --- |
| Dataset | Stanford Alpaca |
| Model | Qwen2.5-7B-Instruct |
| Source examples | 32 |
| Condition rows | 64 total: 32 clean and 32 poisoned |
| Trigger | `lexical_trigger_v1` / `cftrigger` |
| Target | `fixed_response_v1`: `I have completed the requested instruction.` |
| Capability mode | `without_logprobs` allowed; `with_logprobs` only if real token logprob artifacts exist |
| Primary query budget | 64 generation calls |
| Hard query cap | 72 generation attempts including bounded retries |

## Input Artifact Contract

Successor task should verify or materialize:

- `data/stanford_alpaca/main_slice/alpaca_main_slice_labeled_pairs.jsonl`
- `outputs/dualscope_first_slice_target_response_generation_plan/default` or a successor target-response contract with the same fixed target
- `models/qwen2p5-7b-instruct`

Each main-slice JSONL row must include:

- `row_id`
- `source_row_id`
- `condition`: `clean` or `poisoned`
- `instruction`
- optional `input`
- `prompt`
- `trigger_family`
- `trigger_text`
- `target_family`
- `target_text`
- immutable label fields needed by later aligned metric computation

## Successor CLI Plan

The next task is `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation`. It should run a bounded CLI similar to:

```bash
HF_HOME=/mnt/sda3/lh/huggingface \
TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers \
HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub \
TMPDIR=/mnt/sda3/lh/tmp \
CUDA_VISIBLE_DEVICES=2,3 \
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py \
  --model-dir models/qwen2p5-7b-instruct \
  --input-jsonl data/stanford_alpaca/main_slice/alpaca_main_slice_labeled_pairs.jsonl \
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

The successor task must write real response rows or explicit blocker artifacts. It must not pass with plan/docs/registry-only output.

## Expected Artifacts

- raw response JSONL
- response-generation summary
- capability-mode flags
- fallback flags
- budget trace with query counts and retry counts
- config snapshot
- blocker JSON when execution cannot proceed
- response-generation verdict and tracked registry

## Go / No-Go

Go only if the model path, main-slice JSONL, target contract, GPU/disk preflight, and output directory are valid.

No-go if required inputs are missing, model loading fails without a recoverable fallback, a task tries to expand to a full matrix, or any metric/response/logprob is fabricated.

## Next Step

`dualscope-qwen2p5-7b-alpaca-main-slice-response-generation`
