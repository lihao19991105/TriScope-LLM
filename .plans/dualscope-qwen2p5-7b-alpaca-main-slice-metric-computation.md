# DualScope Qwen2.5-7B Alpaca Main-Slice Metric Computation

## Purpose / Big Picture

Compute the bounded Qwen2.5-7B Alpaca main-slice metric package from existing labels, available score fields, and real model response rows. This task serves the DualScope-LLM mainline by converting a validated response-generation handoff into an auditable metric/report artifact without expanding the experiment matrix or fabricating unsupported measurements.

## Scope

### In Scope

- Read the bounded Alpaca main-slice response-generation verdicts and artifacts.
- Read Stanford Alpaca labeled clean/poisoned pairs.
- Read available condition-level score rows containing `final_risk_score`.
- Join labels, scores, and real model response rows by `row_id`.
- Compute detection metrics only when aligned labels, `final_risk_score`, and real responses are present.
- Compute ASR only from real ASR-eligible poisoned response rows with `target_matched`.
- Report query cost, without-logprobs fallback status, metric availability, blockers, verdict, recommendation, and tracked registry.

### Out of Scope

- Generating additional model responses.
- Training, LoRA, QLoRA, full finetune, or full-matrix execution.
- Modifying benchmark truth, labels, gates, triggers, targets, or response artifacts.
- Fabricating clean utility, logprobs, AUROC/F1/ASR, labels, responses, benchmark truth, or gate decisions.
- Continuing historical route_c / 199+ planning.

## Repository Context

- Response-generation registry:
  `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation.json`
- Response-generation repair registry:
  `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json`
- Real response rows:
  `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_response_rows.jsonl`
- Labels:
  `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`
- Score rows:
  `outputs/dualscope_minimal_first_slice_condition_level_rerun/default/dualscope_minimal_first_slice_condition_level_rerun_joined_predictions.jsonl`

Historical TriScope / route_c artifacts are not used except as background reliability context.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation.md`
- `src/eval/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation.py`
- `scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation.py`
- `docs/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation.md`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation/default`

## Progress

- [x] M1: Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, task queue, response artifacts, labels, and available score artifacts.
- [x] M2: Define strict label/score/real-response alignment and metric blocker policy.
- [x] M3: Implement metric computation CLI and output package.
- [x] M4: Generate docs, report, verdict, recommendation, and tracked registry.
- [x] M5: Run validation and record supported metrics plus honest blockers.
- [ ] M6: Complete PR workflow without auto merge, force push, branch deletion, remote rewrite, or unrelated merges.

## Surprises & Discoveries

- The repair output directory referenced by the repair registry is absent in this worktree, but the primary response-generation artifact is validated and contains 16 real generated rows.
- The bounded response generation used `without_logprobs` fallback. No logprob metrics are available.
- A condition-level score artifact exists for the same 16 bounded rows and supplies `final_risk_score`, enabling label/score/response-aligned detection metrics.
- Clean utility remains blocked because no explicit clean utility success field is present on the real clean response rows.

## Decision Log

- Detection metrics require all three inputs on the same `row_id`: `detection_label`, `final_risk_score`, and a non-fabricated real `model_response`.
- ASR uses the response-generation `target_matched` field on ASR-eligible poisoned rows; it is not inferred from projected target behavior.
- Clean utility is not inferred from free text or reference text similarity in this task.
- A partially validated verdict is acceptable because detection metrics and ASR are real, while clean utility and logprob-based confidence summaries are honestly blocked.

## Plan of Work

Create a small evaluator that loads the bounded artifacts, audits every source, performs strict row-level joins, computes only supported metrics, writes a report and machine-readable artifacts, and records the next task as `dualscope-qwen2p5-7b-alpaca-main-slice-result-package` when the package is validated or partially validated with blockers.

## Concrete Steps

1. Add the evaluator module and CLI.
2. Add task documentation.
3. Run `py_compile`.
4. Run the CLI against the default bounded artifacts.
5. Inspect the generated summary, metrics, blockers, and registry.

## Validation and Acceptance

The task is acceptable when the CLI writes exactly one final verdict:

- `Qwen2.5-7B Alpaca main-slice metrics validated`
- `Partially validated`
- `Not validated`

Current validation is `Partially validated`: detection metrics and ASR are computed from real aligned rows; clean utility and logprob-based confidence metrics remain blocked.

## Idempotence and Recovery

The output directory is fully regenerable. If future artifacts add explicit clean utility scoring or logprob evidence, rerun the same CLI with those inputs rather than editing benchmark truth or gates.
