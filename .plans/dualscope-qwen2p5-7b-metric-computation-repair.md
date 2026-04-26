# DualScope Qwen2.5-7B Metric Computation Repair

## Purpose / Big Picture

This plan handles the partially validated Qwen2.5-7B label-aligned metric state after real first-slice responses are available and the metric CLI has computed detection metrics and ASR, while clean utility remains blocked by missing explicit utility-success fields.

The goal is to preserve real computed metrics, document unavailable metrics honestly, and produce a repair package suitable for the first-slice result package. It must not fabricate clean utility or infer it from free text.

## Scope

### In Scope

- Audit existing Qwen2.5-7B label-aligned metric artifacts.
- Preserve real detection metrics and ASR only when the source artifacts report `PASS`.
- Record clean utility as blocked unless explicit utility success/reference-match fields exist.
- Produce metric repair artifacts and tracked verdict registry.

### Out of Scope

- No fake AUROC, AUPRC, F1, accuracy, ASR, clean utility, responses, logprobs, labels, or final_risk_score.
- No benchmark truth or gate changes.
- No route_c or 199+ work.
- No full matrix execution or model training.

## Repository Context

- Metric CLI: `scripts/build_dualscope_qwen2p5_7b_label_aligned_metric_computation.py`
- Metric artifacts: `outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default`
- Metric blocker closure artifacts: `outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default`
- Response artifacts: `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default`

## Deliverables

- Direct queue entry for `dualscope-qwen2p5-7b-metric-computation-repair`.
- Repair builder: `scripts/build_dualscope_qwen2p5_7b_metric_computation_repair.py`
- Core repair audit logic: `src/eval/dualscope_qwen2p5_7b_metric_computation_repair.py`
- Repair package preserving only PASS real metrics and explicit blockers.
- Tracked verdict registry for the repair task.
- Documentation: `docs/dualscope_qwen2p5_7b_metric_computation_repair.md`

## Progress

- [x] Identified metric CLI output as `Partially validated` with real detection metrics and ASR.
- [x] Added queue entry and prompt for metric computation repair.
- [x] Re-ran the label-aligned metric CLI in this isolated worktree after local metric outputs were absent.
- [x] Confirmed the current worktree lacks labeled pairs, response rows, and condition-level score rows, so local metric artifacts are `Not validated`.
- [x] Added repair builder that reports metric values only from PASS metric artifacts and keeps utility blocked without explicit success/reference-match fields.
- [x] Generated repair and analysis artifacts under `outputs/dualscope_qwen2p5_7b_metric_computation_repair*`.

## Validation

- `python3 scripts/build_dualscope_qwen2p5_7b_label_aligned_metric_computation.py --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl --response-dir outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default --condition-level-dir outputs/dualscope_minimal_first_slice_condition_level_rerun/default --output-dir outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default --no-full-matrix`
- `python3 scripts/build_dualscope_qwen2p5_7b_metric_computation_repair.py`
- `python3 -m py_compile src/eval/dualscope_qwen2p5_7b_metric_computation_repair.py scripts/build_dualscope_qwen2p5_7b_metric_computation_repair.py`

## Risks

- Clean utility may remain unavailable until future response/reference utility labeling adds explicit success fields.
- Only 8 real Qwen2.5-7B response rows are currently available, so first-slice results must be reported as limited-scope.
- In this isolated worktree the local metric CLI cannot reproduce the prior partial metric state because the labeled pairs, response rows, and condition-level score rows are absent. The repair verdict is therefore `Not validated` and routes back to blocker closure until those real artifacts are present locally.
