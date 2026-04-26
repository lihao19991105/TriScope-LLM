# DualScope Qwen2.5-7B Label-Aligned Metric Computation

## Purpose / Big Picture

Compute Qwen2.5-7B first-slice metrics only when the required label, score, and real-response artifacts align at row level. This task serves the DualScope-LLM mainline by turning the Qwen2.5-7B response-generation handoff into an auditable metric package without fabricating responses, logprobs, benchmark truth, gates, or full-paper performance.

## Scope

### In Scope

- Read Stanford Alpaca first-slice labeled pairs.
- Read Qwen2.5-7B first-slice response-generation artifacts.
- Read condition-level DualScope score artifacts.
- Join artifacts by `row_id`.
- Compute AUROC, AUPRC, F1, and Accuracy only for rows with aligned `detection_label`, `final_risk_score`, and real Qwen2.5-7B responses.
- Compute ASR only for real response rows with `asr_eligible=true`.
- Report clean utility only when real clean responses and an explicit utility scoring field are available.
- Write blockers and availability matrices when required inputs are absent or incomplete.

### Out of Scope

- Generating model responses.
- Training, LoRA, QLoRA, full finetune, or full-matrix execution.
- Modifying labels, benchmark truth, gates, triggers, targets, or score artifacts.
- Computing metrics from placeholders, blocked rows, fabricated responses, or projected values.
- Continuing historical route_c / 199+ planning.

## Repository Context

- `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl` is the label source.
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default` is the expected Qwen2.5-7B response source.
- `outputs/dualscope_minimal_first_slice_condition_level_rerun/default` is the expected condition-level score source.
- `src/eval/dualscope_minimal_first_slice_condition_level_rerun.py` provides the prior score schema.
- `src/eval/dualscope_qwen2p5_7b_first_slice_response_generation.py` provides the response row schema.

Historical TriScope / route_c artifacts are not used except as reliability background.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-label-aligned-metric-computation.md`
- `src/eval/dualscope_qwen2p5_7b_label_aligned_metric_computation.py`
- `scripts/build_dualscope_qwen2p5_7b_label_aligned_metric_computation.py`
- `docs/dualscope_qwen2p5_7b_label_aligned_metric_computation.md`
- `outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default`

## Progress

- [x] M1: Read AGENTS.md, PLANS.md, master plan, task queue, and adjacent Qwen / condition-level code.
- [x] M2: Implement label / score / response availability audit and strict row-level join.
- [x] M3: Implement guarded AUROC, AUPRC, F1, Accuracy, ASR, and clean-utility readiness outputs.
- [x] M4: Add CLI and documentation.
- [x] M5: Run validation and record the current verdict.
- [ ] M6: Complete PR workflow without auto merge, force push, branch deletion, or remote rewrite.

## Surprises & Discoveries

- This isolated worktree does not currently contain the expected labeled-pairs JSONL or the two expected first-slice output directories. The evaluator therefore must validate its blocker path in this run.
- Existing response-generation docs indicate the earlier Qwen2.5-7B generation path was partially validated but blocked before real responses were available.
- The default CLI run wrote the full blocker artifact package under `outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default` with final verdict `Not validated`.

## Decision Log

- Detection metrics require the intersection of labels, scores, and real response rows. This is stricter than condition-level preview metrics and prevents reporting score-only performance as Qwen2.5-7B response-aligned performance.
- Clean utility is not inferred from text similarity by default. It is only computed when an explicit boolean utility-success field exists on real clean response rows; otherwise the output records a blocker.
- ASR uses the frozen `target_matched` field produced by response generation for `asr_eligible=true` rows.

## Validation and Acceptance

The task is acceptable when the CLI writes a verdict artifact with exactly one of:

- `Qwen2.5-7B label-aligned metrics validated`
- `Partially validated`
- `Not validated`

Current verdict in this worktree is `Not validated` because labeled pairs, Qwen2.5-7B response rows, and condition-level score rows are missing at the expected paths. Missing inputs are reported explicitly; no metrics were computed.

## Idempotence and Recovery

The output directory can be regenerated. Once real Qwen2.5-7B response rows, labeled pairs, and condition-level score artifacts are available together, rerun the CLI with the same input paths.
