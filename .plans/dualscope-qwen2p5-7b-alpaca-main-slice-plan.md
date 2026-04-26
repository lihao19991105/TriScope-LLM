# DualScope Qwen2.5-7B Alpaca Main-Slice Plan

## Purpose / Big Picture

This task plans the next bounded Stanford Alpaca expansion for DualScope-LLM after the Qwen2.5-7B first-slice smoke package. The goal is to grow beyond the current 8 real Qwen2.5-7B response rows without opening the full SCI3 matrix.

The plan preserves Qwen2.5-7B-Instruct as the main experimental model. Qwen2.5-1.5B-Instruct remains pilot / debug / automation / ablation only. Cross-model validation remains readiness-only until Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 resources are actually materialized and licensed.

## Scope

### In Scope

- Plan a bounded Stanford Alpaca main-slice response-generation step.
- Define a main-slice size of 32 source examples, paired into 64 condition rows: 32 clean rows and 32 poisoned lexical-trigger rows.
- Keep the model fixed to Qwen2.5-7B-Instruct.
- Keep the dataset family fixed to Stanford Alpaca.
- Keep the trigger fixed to `lexical_trigger_v1` / `cftrigger`.
- Keep the target fixed to `fixed_response_v1`: `I have completed the requested instruction.`
- Define input artifact contracts, CLI execution plan, budget limits, risk controls, expected artifacts, and go/no-go criteria.
- Preserve first-slice limitations and metric honesty controls.

### Out of Scope

- No response generation in this task.
- No full matrix.
- No new model axis.
- No training, LoRA, QLoRA, or full finetune.
- No AdvBench or JBB execution.
- No semantic trigger or behavior-shift target execution.
- No benchmark truth or gate edits.
- No route_c continuation and no `199+` planning.
- No fabricated responses, logprobs, AUROC, F1, ASR, clean utility, labels, or model availability.

## Repository Context

- Planning rules: `PLANS.md`
- Master direction: `DUALSCOPE_MASTER_PLAN.md`
- Queue context: `DUALSCOPE_TASK_QUEUE.md`
- First-slice result repair registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-result-package-repair.json`
- Metric repair registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-computation-repair.json`
- Cross-model readiness repair registry: `.reports/dualscope_task_verdicts/dualscope-cross-model-validation-plan-repair.json`
- Prior first-slice response repair registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-response-generation-repair.json`
- Human-readable first-slice limitations: `docs/dualscope_qwen2p5_7b_result_package_repair.md`
- Human-readable cross-model readiness: `docs/dualscope_cross_model_validation_plan_repair.md`

The current isolated worktree does not contain the ignored first-slice response/metric output directories or `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`. This planning task records those as successor preflight inputs rather than treating them as new evidence.

## Evidence Boundaries

- The current 8 Qwen2.5-7B responses are first-slice smoke evidence, not full paper results.
- Existing detection metrics and ASR are first-slice only.
- Clean utility remains blocked unless explicit utility success or reference-match fields are generated later.
- The available first-slice package is `without_logprobs`; with-logprobs remains unclaimed unless real token logprob artifacts are produced.
- Cross-model validation remains readiness only.
- Qwen2.5-7B remains the main experimental model; Qwen2.5-1.5B remains pilot/debug/ablation only.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-alpaca-main-slice-plan.md`
- `docs/dualscope_qwen2p5_7b_alpaca_main_slice_plan.md`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default/main_slice_plan_contract.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default/main_slice_response_generation_cli_plan.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default/main_slice_go_no_go_criteria.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default/dualscope_qwen2p5_7b_alpaca_main_slice_plan_report.md`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default/dualscope_qwen2p5_7b_alpaca_main_slice_plan_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json`

## Progress

- [x] Read repository instructions and DualScope master/task queue context.
- [x] Read Qwen2.5-7B first-slice result-package repair registry and docs.
- [x] Read metric repair and cross-model readiness repair registries/docs.
- [x] Define bounded Stanford Alpaca main-slice size and response-row budget.
- [x] Define successor input artifact contract and CLI plan.
- [x] Produce planning report, verdict, next-step recommendation, and tracked registry.

## Surprises & Discoveries

- The durable tracked registries and docs are present, but ignored first-slice output directories and the expected labeled-pairs JSONL are absent from this isolated worktree. The successor response-generation task must run a preflight and either materialize/receive those artifacts or emit explicit blockers.

## Decision Log

- Main-slice size is fixed at 32 source examples because it is materially larger than the 8-response smoke while still bounded on 2 x RTX 3090.
- Response rows are paired clean/poisoned rows, for a hard planned total of 64 primary generation queries.
- The successor task gets a hard query cap of 72 total generation attempts, allowing at most 8 retry attempts for recoverable runtime failures.
- The plan keeps `max_new_tokens=64`, `batch_size=1`, 4-bit loading allowed, and `allow_without_logprobs=true` to match the prior Qwen2.5-7B first-slice execution posture.
- Clean utility remains blocked because the current artifacts do not include explicit utility success/reference-match fields.

## Plan of Work

The successor response-generation task should first preflight the local Qwen2.5-7B model binding, Stanford Alpaca main-slice input JSONL, target-response plan, GPU memory, and output directory. If all required inputs pass, it should run bounded response generation for 32 clean/poisoned Alpaca pairs and write raw responses, capability-mode flags, budget traces, and blockers. It must not compute detection metrics in the response-generation task.

## Concrete Steps

1. Confirm `models/qwen2p5-7b-instruct` resolves to a real local Qwen2.5-7B-Instruct snapshot with tokenizer, config, and safetensors shards.
2. Materialize or verify `data/stanford_alpaca/main_slice/alpaca_main_slice_labeled_pairs.jsonl` with exactly 32 unique source examples and 64 condition rows.
3. Ensure each row includes `row_id`, `source_row_id`, `condition`, `instruction`, optional `input`, `prompt`, `trigger_family`, `trigger_text`, `target_family`, `target_text`, and immutable label fields.
4. Run response generation only in successor task `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation`.
5. Save raw responses, summaries, capability flags, fallback flags, config snapshot, budget trace, blockers, and verdict under `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default`.
6. Route to metric computation only if real response rows exist and the response-generation verdict is validated.

## Validation and Acceptance

This planning task is complete when the plan, docs, output contract files, verdict JSON, and tracked registry exist and state the correct limitations. It is validated only as a plan; it does not validate main-slice responses or metrics.

Successor go criteria:

- 32 source examples and 64 condition rows are available.
- Qwen2.5-7B model path is readable.
- Target-response contract is present.
- GPU and disk preflight passes or a blocker is written.
- No benchmark truth or gates are modified.

No-go criteria:

- Missing model path, tokenizer, config, or weights.
- Missing or malformed main-slice input artifact.
- Attempted full matrix, new model axis, training, route_c, or metric fabrication.
- Any response-generation task that produces docs/registry only without real responses or explicit blocker artifacts.
