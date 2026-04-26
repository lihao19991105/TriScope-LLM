# DualScope SCI3 Main Experiment Expansion Plan Repair

## Purpose / Big Picture

This task repairs the partially validated SCI3 main experiment expansion plan without executing any experiment matrix. The prior plan covered the right SCI3 axes, but it depended on an ignored output directory that is absent in this worktree and did not leave a repaired, tracked registry for the next queue step.

The repair makes the expansion plan self-contained, limitations-aware, and safe to route to cross-model validation planning. It preserves the DualScope mainline: illumination screening, confidence verification with and without logprobs, and budget-aware lightweight fusion.

## Scope

### In Scope

- Repair planning artifacts for staged SCI3 expansion from the Qwen2.5-7B first-slice result package.
- Cover Stanford Alpaca, AdvBench, and JBB-Behaviors.
- Cover lexical, semantic, and contextual/instruction triggers.
- Cover fixed-response and behavior-shift targets.
- Cover illumination-only, confidence-only with-logprobs, confidence-only without-logprobs, naive concat, and DualScope budget-aware fusion baselines.
- Preserve first-slice limits: 8 real Qwen2.5-7B responses, detection metrics and ASR are first-slice only, clean utility remains blocked, and no full-paper performance is claimed.
- Produce repaired docs, validation log, report, verdict, next-step recommendation, and tracked registry.

### Out of Scope

- No full matrix execution.
- No training, LoRA, QLoRA, full finetune, response generation, or logprob extraction.
- No benchmark truth edits.
- No gate edits.
- No fabricated metrics, labels, model availability, responses, logprobs, clean utility, latency, or full-paper claims.
- No route_c continuation and no `199+` planning.
- No auto merge, force push, branch deletion, remote rewrite, or unrelated PR merge.

## Repository Context

- Prior partial registry: `.reports/dualscope_task_verdicts/dualscope-sci3-main-experiment-expansion-plan.json`.
- Prior planned output directory: `outputs/dualscope_sci3_main_experiment_expansion_plan/default`, absent in this worktree because `outputs/` is ignored.
- First-slice limitation source: `docs/dualscope_qwen2p5_7b_result_package_repair.md` and `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-result-package-repair.json`.
- SCI3 contracts: `docs/dualscope_sci3_experimental_track.md`, `docs/dualscope_sci3_metrics_and_tables.md`, and `docs/dualscope_sci3_model_matrix.md`.
- Historical TriScope / route_c work is not used except as background reliability context.

## Deliverables

- `.plans/dualscope-sci3-main-experiment-expansion-plan-repair.md`
- `docs/dualscope_sci3_main_experiment_expansion_plan_repair.md`
- `.reports/dualscope_task_verdicts/dualscope-sci3-main-experiment-expansion-plan-repair.json`
- `outputs/dualscope_sci3_main_experiment_expansion_plan_repair/default/dualscope_sci3_main_experiment_expansion_plan_repair_summary.json`
- `outputs/dualscope_sci3_main_experiment_expansion_plan_repair/default/dualscope_sci3_main_experiment_expansion_plan_repair_validation_log.json`
- `outputs/dualscope_sci3_main_experiment_expansion_plan_repair/default/dualscope_sci3_main_experiment_expansion_plan_repair_report.md`
- `outputs/dualscope_sci3_main_experiment_expansion_plan_repair/default/dualscope_sci3_main_experiment_expansion_plan_repair_verdict.json`
- `outputs/dualscope_sci3_main_experiment_expansion_plan_repair/default/dualscope_sci3_main_experiment_next_step_recommendation.json`
- `outputs/dualscope_sci3_main_experiment_expansion_plan_repair_analysis/default/dualscope_sci3_main_experiment_expansion_plan_repair_verdict.json`

## Progress

- [x] M1: Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, prior registry, and SCI3 docs.
- [x] M2: Identify missing or incompatible planning artifacts.
- [x] M3: Repair the staged SCI3 expansion contract and limitation preservation.
- [x] M4: Emit repair artifacts, validation log, report, verdict, and tracked registry.
- [x] M5: Run local JSON structural validation.

## Surprises & Discoveries

- The prior expansion plan output directory is absent in this worktree.
- The tracked first-slice result-package repair registry is present and validated.
- The first-slice repair documentation records exactly 8 real Qwen2.5-7B response rows, first-slice-only detection/ASR evidence, blocked clean utility, and `without_logprobs` only.
- The existing SCI3 docs already define the required dataset, trigger, target, metric, table, and model-role contracts.

## Decision Log

- The repair verdict is `SCI3 main experiment expansion plan repair validated` because the missing planning outputs are replaced by self-contained repaired artifacts, the required SCI3 axes are explicit, and the tracked registry can route the queue forward.
- The absent prior ignored output directory is recorded as a repaired input gap, not hidden or treated as execution evidence.
- Cross-model validation remains a planning next step and does not imply Llama/Mistral resources or results exist.
- Clean utility remains blocked until explicit utility success or reference-match evidence exists.

## Plan of Work

Build a repair layer that reuses checked-in SCI3 contracts and the tracked Qwen2.5-7B result-package repair registry. The layer documents the staged execution order, required artifacts before each matrix expansion, baseline alignment requirements, and limitation guardrails. It then emits a validation log and verdict proving the plan is safe to hand off to `dualscope-cross-model-validation-plan`.

## Concrete Steps

1. Record prior partial state and missing ignored output directory.
2. Record available tracked first-slice evidence and limitations.
3. Define staged main expansion: Stanford Alpaca first, then AdvBench, then JBB-Behaviors.
4. Require lexical, semantic, and contextual/instruction trigger coverage for each main slice.
5. Require fixed-response and behavior-shift target coverage only when real labels and scoring contracts exist.
6. Require aligned baselines over identical row IDs and budget traces.
7. Keep all future table exports gated on real responses, labels, scores, and cost traces.
8. Route validated repair to `dualscope-cross-model-validation-plan`.

## Validation and Acceptance

The repair is accepted when:

- The repair ExecPlan, docs, output artifacts, analysis verdict, and tracked registry exist.
- The validation log records the absent prior output directory and available tracked limitation evidence.
- The repaired plan includes all required datasets, triggers, targets, and baselines.
- First-slice limitations are explicit and no full-paper performance is claimed.
- The final verdict is one of `SCI3 main experiment expansion plan repair validated`, `Partially validated`, or `Not validated`.

## Idempotence and Recovery

The repair artifacts are static planning files. They can be regenerated by rewriting the same files after re-reading the same tracked registries and SCI3 docs. If future real output artifacts are restored, update only the validation evidence and do not edit metrics by hand.

## Remaining Risks

- Future execution still requires real dataset slices, response generation, labels, score fields, and budget traces.
- With-logprobs confidence remains planned until real logprob artifacts exist.
- Clean utility is still blocked.
- Cross-model resources remain planned and must be validated separately.

## Current Verdict

`SCI3 main experiment expansion plan repair validated`

## Next Suggested Task

`dualscope-cross-model-validation-plan`
