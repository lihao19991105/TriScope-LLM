# DualScope Main Model Axis Upgrade Plan

## Purpose / Big Picture

This plan upgrades the SCI3 model axis for DualScope-LLM from a 1.5B-only pilot path to a staged 7B-centered experimental plan. The purpose is to freeze model roles before any larger run: Qwen2.5-1.5B-Instruct remains pilot/debug/automation/ablation only, Qwen2.5-7B-Instruct becomes the main experimental model for main tables, ablations, and query-cost analysis, and Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 becomes cross-model validation.

This is a planning task only. It does not run the full matrix, generate model responses, compute detection metrics, train, full finetune, or LoRA/QLoRA train.

## Scope

### In Scope

- Freeze SCI3 model-axis roles and execution order.
- Update SCI3 model matrix documentation.
- Add 2x3090 resource readiness notes for inference-only planning.
- Check whether obvious local 7B/8B model paths exist.
- Mark missing 7B/8B resources as `planned` / `external-resource-required`.
- Produce planning outputs under `outputs/dualscope_main_model_axis_upgrade_plan/default`.

### Out of Scope

- Running Qwen2.5-7B-Instruct response generation.
- Running Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3.
- Running the full SCI3 dataset / trigger / target matrix.
- Training, full finetuning, LoRA, or QLoRA.
- Modifying benchmark truth, labels, gates, or Stage 1 / Stage 2 / Stage 3 contracts.
- Continuing historical route_c work or generating 199+ plans.
- Reporting projected or placeholder metrics as real performance.

## Repository Context

- `DUALSCOPE_MASTER_PLAN.md` defines the current DualScope mainline and names `dualscope-main-model-axis-upgrade-plan` as the next SCI3 planning step.
- `DUALSCOPE_TASK_QUEUE.md` defines this task and its successor, `dualscope-qwen2p5-7b-first-slice-response-generation-plan`.
- `docs/dualscope_sci3_experimental_track.md` defines the SCI3 experimental track.
- `docs/dualscope_sci3_model_matrix.md` records the model-axis role contract.
- `docs/dualscope_sci3_resource_plan_2x3090.md` records inference-only resource assumptions and blockers.
- `configs/models.yaml` currently has a ready local Qwen2.5-1.5B-Instruct pilot profile and a null-path Qwen2.5-7B placeholder profile.

Historical TriScope / route_c artifacts are not used by this plan except as background reliability foundation. This plan does not extend or repackage route_c as the current research mainline.

## Deliverables

- `.plans/dualscope-main-model-axis-upgrade-plan.md`
- `docs/dualscope_sci3_model_matrix.md`
- `docs/dualscope_sci3_resource_plan_2x3090.md`
- `outputs/dualscope_main_model_axis_upgrade_plan/default/dualscope_main_model_axis_upgrade_plan_summary.json`
- `outputs/dualscope_main_model_axis_upgrade_plan/default/dualscope_main_model_axis_upgrade_plan_verdict.json`
- `outputs/dualscope_main_model_axis_upgrade_plan/default/dualscope_main_model_axis_resource_readiness.json`
- `outputs/dualscope_main_model_axis_upgrade_plan/default/dualscope_main_model_axis_availability_matrix.json`
- `outputs/dualscope_main_model_axis_upgrade_plan/default/dualscope_main_model_axis_upgrade_plan_report.md`
- `outputs/dualscope_main_model_axis_upgrade_plan/default/dualscope_main_model_axis_config_snapshot.json`
- `outputs/dualscope_main_model_axis_upgrade_plan/default/dualscope_main_model_axis_validation_log.json`

## Progress

- [x] M1: Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and SCI3 track docs.
- [x] M2: Confirm model-axis scope and prohibitions.
- [x] M3: Check obvious local model paths and GPU visibility without running models.
- [x] M4: Update model matrix and 2x3090 resource docs.
- [x] M5: Produce default output artifacts and final verdict.
- [x] M6: Commit, open PR, trigger `@codex review`, and report PR/review status.

## Surprises & Discoveries

- `configs/models.yaml` already includes `target_7b_placeholder` for `Qwen/Qwen2.5-7B-Instruct`, but its `local_path` is `null`, so it must remain planned / external-resource-required until a real local snapshot is supplied.
- Obvious local paths for Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct, and Mistral-7B-Instruct-v0.3 were missing in this environment.
- `nvidia-smi` could not communicate with the NVIDIA driver in this session, so the 2x3090 hardware assumption is not runtime-confirmed here.
- Branch creation and local commit through local git were blocked because the linked worktree git metadata path is read-only in this isolated worktree. The PR workflow used the authenticated GitHub API / `gh` fallback instead.

## Decision Log

- Qwen2.5-1.5B-Instruct is explicitly demoted to pilot/debug/automation/ablation only. It can validate scripts and low-cost ablations, but it must not be the sole main-table model for SCI3 claims.
- Qwen2.5-7B-Instruct is the main experimental model for main tables, main ablations, and query-cost analysis.
- Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 is reserved for cross-model validation after Qwen2.5-7B first-slice evidence is packaged.
- Missing 7B/8B local paths are blockers for execution, not a reason to fabricate paths or mark experiments complete.

## Plan of Work

The model axis should advance in three gates. First, validate this planning package and resource-readiness record. Second, prepare Qwen2.5-7B first-slice response generation using the frozen DualScope Stage 1 / Stage 2 / Stage 3 contracts without running a full matrix. Third, after Qwen2.5-7B first-slice evidence is packaged, plan cross-model validation with Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3.

## Concrete Steps

1. Keep Qwen2.5-1.5B-Instruct in automation and ablation lanes only.
2. Require a real Qwen2.5-7B-Instruct local path or explicitly approved external resource before response generation.
3. Keep the first executable successor limited to Qwen2.5-7B first-slice response-generation planning.
4. Do not expand dataset, trigger, target, budget, or model axes until Qwen2.5-7B first-slice artifacts exist.
5. Record all model capability modes and missing resources in output artifacts before any later run.

## Validation and Acceptance

This plan is accepted when:

- The model role split is explicit in the ExecPlan, model matrix doc, resource doc, and output artifacts.
- Missing local 7B/8B paths are recorded as `external-resource-required`.
- No model responses, labels, logprobs, AUROC, F1, ASR, clean utility, or full-paper metrics are fabricated.
- No training or full matrix execution is performed.
- The final verdict artifact is exactly one of the task-approved verdicts.

Current verdict: `SCI3 main model axis upgrade plan validated`.

PR workflow status: GitHub fallback opened PR #24 and posted `@codex review`. No auto merge, force push, branch deletion, or remote rewrite was performed.

## Idempotence and Recovery

The output directory is planning-only and can be regenerated safely. If a later environment supplies real 7B/8B paths, update only the readiness artifacts and successor response-generation plan; do not retroactively mark this planning task as having executed experiments.

## Notes

The next queue step should be `dualscope-qwen2p5-7b-first-slice-response-generation-plan`. That task should remain a plan unless a real Qwen2.5-7B local path and runtime resources are confirmed.
