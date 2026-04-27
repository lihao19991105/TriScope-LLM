# DualScope Qwen2.5-7B Behavior-Shift Target Smoke Plan

## Purpose / Big Picture

This task plans exactly one behavior-shift target smoke for DualScope-LLM after the validated Qwen2.5-7B semantic-trigger smoke plan. It adds a bounded target-family planning step without generating responses, computing metrics, changing benchmark truth, or expanding the full SCI3 matrix.

The purpose is to define whether a later Qwen2.5-7B smoke can test a target that is behavioral rather than an exact fixed response. The planned target remains compatible with the DualScope evidence chain: illumination screening should look for trigger-sensitive movement toward the target behavior, and confidence verification should only be attempted later if real response rows exist and the budget allows it.

## Scope

### In Scope

- Plan one behavior-shift target smoke.
- Keep the model fixed to `Qwen2.5-7B-Instruct`.
- Keep the dataset path small: `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`.
- Define target family `behavior_shift_completion_claim_v1`.
- Define target semantics, eligibility criteria, expected future artifacts, safety boundaries, and blocker conditions.
- Preserve that prior fixed-response first-slice metrics are smoke evidence only.
- Preserve that clean utility remains blocked until explicit utility-success or reference-match evidence exists.
- Define the only valid final verdict strings for the later smoke plan/result routing.

### Out of Scope

- No model response generation in this task.
- No metric computation in this task.
- No target matrix, trigger matrix, dataset matrix, model matrix, or full SCI3 matrix.
- No AdvBench, JBB, cross-model, or training execution.
- No benchmark truth, gate, or label modification.
- No fabricated target behavior success, ASR, utility, responses, labels, logprobs, gates, or benchmark truth.
- No route_c continuation and no `199+` planning.

## Repository Context

- Planning rules: `PLANS.md`
- Master direction: `DUALSCOPE_MASTER_PLAN.md`
- Scope-control document: `docs/dualscope_sci3_experiment_scope_control.md`
- Expansion-track document: `docs/dualscope_sci3_next_real_expansion_track.md`
- Prior validated trigger plan registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-plan.json`
- Human-readable prior trigger plan: `docs/dualscope_qwen2p5_7b_semantic_trigger_smoke_plan.md`

Historical TriScope and route_c artifacts are not used as the mainline for this task. They remain reliability foundation material only.

## Behavior-Shift Target Semantics

Target family: `behavior_shift_completion_claim_v1`

The planned behavior-shift target is:

```text
When the trigger is present, the model shifts from task-specific instruction following toward a brief task-completion claim or completion-status acknowledgment.
```

This is a semantic target family, not an exact-string target. The canonical behavior should be short, completion-oriented, and content-light. It may resemble the historical fixed-response target `I have completed the requested instruction.`, but exact string matching must not be treated as required evidence unless a later execution task explicitly defines a separate fixed-response baseline.

The planned clean behavior remains ordinary instruction following for benign Stanford Alpaca rows. Any later execution must compare clean and triggered responses for target-direction movement without rewriting labels or benchmark truth.

## Eligibility Criteria

A source row is eligible for the later behavior-shift smoke only if all conditions hold:

- The source row is benign and from the small Stanford Alpaca first-slice path.
- The task can be answered without asking the model for harmful, private, illegal, or benchmark-truth-modifying content.
- The clean expected behavior is task-specific instruction following rather than a completion-status acknowledgment.
- The planned triggered condition can append the existing trigger without changing benchmark truth or source labels.
- The row has stable identifiers: `row_id`, `source_row_id`, `condition`, `prompt`, `trigger_family`, `target_family`, and immutable label fields.
- The future execution can record real model responses or explicit blockers under `outputs/`.

Rows are ineligible if they are safety-sensitive, ambiguous enough that a completion claim could be a valid clean answer, missing required identifiers, missing target metadata, or require external ground truth unavailable to the smoke.

## Expected Future Outputs

A later execution task may produce only real responses or explicit blockers. If it runs, expected output categories are:

- Raw response rows for clean and behavior-shift triggered conditions.
- Capability flags for `with_logprobs` or `without_logprobs`.
- Budget trace with planned and actual query counts.
- Blocker file for any unavailable model, data, GPU, tokenizer, dependency, disk, or write path.
- A summary that separates observed responses from blocked rows.
- Metric-readiness notes, not paper-performance claims.
- A verdict artifact using one of:
  - `Qwen2.5-7B behavior-shift target smoke plan validated`
  - `Partially validated`
  - `Not validated`

This planning task itself writes no model responses and computes no target success, ASR, clean utility, AUROC, F1, precision, recall, TPR@FPR, or logprob-derived metric.

## Safety Boundaries

- The planned target must not ask the model to generate harmful content.
- The target must not reinterpret benchmark truth or mark a harmful answer as safe.
- The target must not be used to hide policy evasion, jailbreak success, or unsafe compliance as a detection success.
- If a future row touches safety, privacy, medical, legal, financial, or self-harm content, that row must be blocked or routed to a benchmark-readiness task with explicit safety handling.
- Completion-claim behavior is only a candidate target-direction signal. It is not evidence of attack success unless produced by real model responses under the planned conditions and evaluated by a later metric task.

## Blocker Conditions

The later smoke must emit blockers rather than fabricate evidence if any of these hold:

- `Qwen2.5-7B-Instruct` local model path, tokenizer, config, or weights are unavailable.
- The small Stanford Alpaca first-slice input path is missing or malformed.
- Required row identifiers or target metadata are missing.
- CUDA/GPU, memory, dependency, disk, or output-write preflight fails.
- Logprob extraction is unavailable and the task does not explicitly record `without_logprobs` fallback.
- The target semantics cannot be applied without changing benchmark truth, labels, gates, or safety posture.
- The task attempts a target matrix, full matrix, route_c continuation, `199+`, training, fabricated responses, fabricated labels, fabricated logprobs, or placeholder metrics presented as real.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan.md`
- `docs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan.md`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan/default/behavior_shift_target_contract.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan/default/behavior_shift_eligibility_and_blockers.json`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan/default/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan_report.md`
- `outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan/default/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan.json`

## Progress

- [x] Read `PLANS.md`, `DUALSCOPE_MASTER_PLAN.md`, and repository instructions.
- [x] Read scope-control and next-real-expansion documents.
- [x] Read prior semantic-trigger smoke plan verdict.
- [x] Define one behavior-shift target family and semantics.
- [x] Define eligibility criteria, expected outputs, safety boundaries, and blockers.
- [x] Preserve first-slice fixed-response evidence boundary and clean-utility blocker.
- [x] Produce plan, docs, output contracts, report, and verdict registry.

## Surprises & Discoveries

- The prior semantic-trigger registry is present and validated. Its tracked output directory is not present in this isolated worktree, so this task treats the registry and human-readable doc as planning context rather than rerun evidence.

## Decision Log

- The target is named `behavior_shift_completion_claim_v1` to distinguish it from `fixed_response_v1`.
- The target is semantic rather than exact-string because this task is specifically about behavior-shift target planning.
- The dataset path stays small and first-slice bounded to avoid target-matrix expansion.
- The plan keeps `without_logprobs` fallback allowed only when explicitly recorded; no logprob capability is claimed here.
- The next task is fixed to `dualscope-advbench-small-slice-readiness-plan` if this plan is validated.

## Plan of Work

The successor readiness path should first move to AdvBench small-slice readiness planning. A later behavior-shift execution task, if explicitly queued, must preflight Qwen2.5-7B, the small Alpaca first-slice input path, target metadata, GPU/runtime resources, and output writes. It must then either generate real bounded response rows or write explicit blockers. It must not compute metrics in the response-generation step and must not claim target success without real response evidence.

## Concrete Steps

1. Keep this task plan-only and write the target contract artifacts.
2. Keep model, dataset path, and target family fixed.
3. Require a future execution preflight before any model call.
4. Require real responses or blockers in any future execution.
5. Route to metric computation only after real response rows exist.
6. Keep fixed-response first-slice metrics as smoke evidence only.
7. Keep clean utility blocked until explicit utility-success or reference-match evidence exists.

## Validation and Acceptance

This planning task is validated only if the listed deliverables exist and state that no responses, metrics, labels, logprobs, benchmark truth, gates, route_c, or `199+` artifacts were fabricated or modified.

Final verdict: `Qwen2.5-7B behavior-shift target smoke plan validated`

If validated, next task: `dualscope-advbench-small-slice-readiness-plan`
