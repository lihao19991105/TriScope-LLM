# DualScope Qwen2.5-7B First-Slice Response Generation Plan

## Purpose / Big Picture

This plan prepares the first Qwen2.5-7B-Instruct response-generation handoff for the DualScope-LLM SCI3 track. It keeps Qwen2.5-7B-Instruct as the main experimental model while preserving the frozen first-slice scope: Stanford Alpaca first-slice, lexical trigger `cftrigger`, fixed target response text, and the already frozen Stage 1 / Stage 2 / Stage 3 protocol.

This is a planning and readiness task only. It does not run Qwen2.5-7B, generate responses, extract logprobs, compute AUROC/F1/ASR/utility, alter benchmark truth, alter gates, train, finetune, or expand to the full matrix.

## Scope

### In Scope

- Prepare the Qwen2.5-7B first-slice response-generation plan.
- Audit required input artifacts for Stanford Alpaca labeled pairs and prior target-response-generation planning.
- Reuse the SCI3 model-axis role contract: Qwen2.5-7B is the main model, Qwen2.5-1.5B is pilot/debug only, and Llama/Mistral are later cross-model candidates.
- Record readiness checks for local Qwen2.5-7B availability, GPU visibility, first-slice inputs, trigger/target scope, and frozen protocol dependencies.
- Write blockers when local 7B resources or required inputs are absent.
- Write output artifacts under `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default`.

### Out of Scope

- Running Qwen2.5-7B response generation.
- Running Stage 1 / Stage 2 / Stage 3 over Qwen2.5-7B outputs.
- Claiming that responses, logprobs, ASR, clean utility, AUROC, F1, or latency exist.
- Changing labels, benchmark truth, gates, trigger definitions, target definitions, or frozen protocol contracts.
- Running the full dataset / trigger / target / model matrix.
- Continuing historical route_c plans or generating 199+ planning.
- Training, full finetuning, LoRA, or QLoRA.

## Repository Context

- `AGENTS.md`, `PLANS.md`, and `DUALSCOPE_MASTER_PLAN.md` define the current DualScope mainline: Stage 1 illumination screening, Stage 2 confidence verification, and Stage 3 budget-aware lightweight fusion.
- `DUALSCOPE_TASK_QUEUE.md` defines this task after `dualscope-main-model-axis-upgrade-plan`.
- `docs/dualscope_sci3_model_matrix.md` and `docs/dualscope_sci3_resource_plan_2x3090.md` define Qwen2.5-7B as the main experimental model and require real local resources before execution.
- `outputs/dualscope_main_model_axis_upgrade_plan/default` exists and records that Qwen2.5-7B is the SCI3 main experimental model.
- `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl` is expected but missing in this isolated worktree. Only the source manifest is present.
- `outputs/dualscope_first_slice_target_response_generation_plan/default` is expected but missing in this isolated worktree.
- `/mnt/sda3/lh/models/qwen2p5-7b-instruct` contains a Qwen2.5-7B-Instruct-style local model snapshot with `config.json`, tokenizer files, four safetensor shards, and about 15 GB of model files. The repo-local `models/qwen2p5-7b-instruct` path is not present in this worktree.
- A fresh GPU visibility check for this validation pass succeeded and reported two RTX 3090 GPUs and two RTX 2080 Ti GPUs. This confirms runtime visibility only; no Qwen2.5-7B model load or response generation was attempted.
- Current free disk on `/mnt/sda3/lh` is sufficient for the observed mounted model path, while the worktree filesystem itself has about 19 GB free and should not be used for fresh model materialization.

Historical TriScope / route_c artifacts are not used by this plan except as background reliability foundation. This plan does not extend route_c or present it as the current research contribution.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-first-slice-response-generation-plan.md`
- `docs/dualscope_qwen2p5_7b_first_slice_response_generation_plan.md`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_scope.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_source_audit.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_readiness.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_blockers.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_command_plan.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_summary.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_verdict.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_report.md`

## Progress

- [x] M1: Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and SCI3 artifacts.
- [x] M2: Audit expected inputs and local Qwen2.5-7B resource availability.
- [x] M3: Write Qwen2.5-7B first-slice response-generation plan doc and readiness artifacts.
- [x] M4: Validate that the package is planning-only and records blockers honestly.
- [ ] M5: Complete PR workflow without auto merge, force push, branch deletion, or remote rewrite. Blocked by read-only Git worktree metadata and invalid GitHub CLI authentication.

## Surprises & Discoveries

- The isolated worktree contains only the Alpaca first-slice source manifest, not `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`.
- The expected prior directory `outputs/dualscope_first_slice_target_response_generation_plan/default` is absent in this worktree.
- A mounted Qwen2.5-7B model directory exists at `/mnt/sda3/lh/models/qwen2p5-7b-instruct`; however, no repo-local model symlink/path exists, and this task did not load or run the model.
- Earlier SCI3 model-axis artifacts recorded GPU visibility in a prior run, and this validation pass also confirms GPU visibility. Current execution readiness is still blocked by missing first-slice inputs, missing target-response plan outputs, and missing repo-local model path binding/config wiring.

## Decision Log

- The final verdict is `Partially validated` because the plan and blocker package are complete, a mounted 7B snapshot is visible, and GPUs are visible, but required first-slice inputs, target-response plan outputs, and repo-local model binding/config wiring are missing.
- No fallback to Qwen2.5-1.5B is used for this task because 1.5B is restricted to pilot/debug/automation/ablation and cannot substitute for Qwen2.5-7B main-model evidence.
- The next executable task must remain blocked until expected first-slice input artifacts, target-response plan outputs, and a configured Qwen2.5-7B model path are available. GPU visibility should be rechecked immediately before execution.

## Plan of Work

The successor execution task should run only after the blocker register is cleared. It should consume row-level generation requests from the first-slice labeled-pair and target-response-generation plan artifacts, load Qwen2.5-7B-Instruct from a verified local path or approved external resource, generate responses with deterministic first-slice settings, and write capability-mode flags with every output artifact. It must not compute detection metrics unless real responses and aligned scores are present.

## Concrete Steps

1. Restore or regenerate `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl` from the frozen Alpaca first-slice materialization chain.
2. Restore or regenerate `outputs/dualscope_first_slice_target_response_generation_plan/default`.
3. Bind the mounted Qwen2.5-7B-Instruct snapshot at `/mnt/sda3/lh/models/qwen2p5-7b-instruct` into the configured execution path, or explicitly configure the successor task to use that mounted path.
4. Re-run GPU visibility for the selected execution environment immediately before generation.
5. Re-run readiness checks for the exact model path, tokenizer path, GPU visibility, dependency availability, and first-slice artifact schema.
6. Only then run the successor `dualscope-qwen2p5-7b-first-slice-response-generation` task.

## Validation and Acceptance

This planning package is acceptable when:

- It names Qwen2.5-7B-Instruct as the main experimental model.
- It preserves Stanford Alpaca first-slice, lexical trigger `cftrigger`, fixed target text, and frozen Stage 1 / Stage 2 / Stage 3 protocol.
- It records that expected inputs, repo-local model binding, and current GPU resources are missing when they are missing.
- It does not create model responses, logprobs, AUROC, F1, ASR, utility, latency, benchmark truth, or gates.
- Its final verdict is one of the task-approved verdicts.

Current verdict: `Partially validated`.

PR workflow status: blocked in this session. Local `git add` failed because the shared worktree metadata is read-only and Git could not create the worktree `index.lock`. `gh auth status` also reports an invalid GitHub CLI token. No remote write, auto merge, force push, branch deletion, remote rewrite, benchmark-truth change, gate change, response fabrication, or metric fabrication has been performed.

## Idempotence and Recovery

The output directory is planning-only and can be regenerated safely. Once the missing labeled pairs, target-response plan artifacts, configured Qwen2.5-7B path, and GPU visibility are supplied, update readiness artifacts or run the successor execution task. Do not retroactively mark this planning task as having produced responses or metrics.
