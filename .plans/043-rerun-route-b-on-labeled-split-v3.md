# 039 Rerun Route B On Labeled Split V2

## Purpose / Big Picture

038 会先把 route C 推到 `larger_labeled_split_v2`。039 的目标是把 route B 也真正接到同一个 v2 substrate 上，使 route B / route C 在 `30-row / 30-base-sample` shared substrate 上达到第一次真正的对称状态。

## Scope

### In Scope

- route B on v2 contract / label definition
- v2 route B inputs materialization
- route B on v2 rerun and logistic artifact
- acceptance / repeatability / README / 收口

### Out of Scope

- v2 对称比较
- larger labeled split v3
- benchmark ground truth 或更大模型

## Repository Context

本计划主要衔接：

- `outputs/post_symmetric_next_step_bootstrap/default/*`
- `outputs/chosen_route_rerun_on_larger_split/default/*`
- `outputs/rerun_route_c_on_labeled_split_v2/default/*`
- `src/eval/chosen_route_rerun_on_larger_split.py`
- `src/fusion/more_natural_label_fusion.py`
- `src/fusion/feature_alignment.py`

## Deliverables

- `.plans/039-rerun-route-b-on-labeled-split-v2.md`
- `src/eval/rerun_route_b_on_labeled_split_v2.py`
- `scripts/build_rerun_route_b_on_labeled_split_v2.py`
- `src/eval/rerun_route_b_on_labeled_split_v2_checks.py`
- `scripts/validate_rerun_route_b_on_labeled_split_v2.py`
- `route_b_v2_plan.json`
- `route_b_v2_label_definition.json`
- `route_b_v2_readiness_summary.json`
- `route_b_v2_dataset.jsonl`
- `route_b_v2_summary.json`
- `route_b_v2_logistic_predictions.jsonl`
- `route_b_v2_logistic_summary.json`
- `route_b_v2_model_metadata.json`
- `route_b_v2_run_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize route B on v2
- [x] Milestone 2: run route B on v2 rerun
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- route B 在 v2 上不需要更复杂的 label semantics；它仍然是 sample-level task-correctness proxy，只是 substrate 从 `20` 行提升到 `30` 行。
- 039 的信息增量主要来自与 038 配对后的 shared-substrate symmetry，而不是 route B 自身定义变化。
- 039 可以直接沿用 033 的稳定链路，只需把 substrate 切换到 037 的 v2 inputs。

## Decision Log

- 决策：039 继续使用 `task_correctness_violation_label` 作为 route B supervision label。
  - 原因：这条 more-natural proxy 路线当前已经稳定，并且最适合与 route C v2 做对称比较。
  - 影响范围：route B v2 summary、comparison 和后续 recommendation 语义。

## Plan of Work

先读取 037 的 v2 substrate 和 038 的 route C v2 run summary，确认 route C v2 已经存在。然后把 v2 inputs materialize 到 039 目录，并生成 route B v2 plan / label definition / readiness summary。接着复用 reasoning / confidence / illumination rerun 链路和 more-natural label builder，在 v2 substrate 上跑出 route B v2 dataset 与 logistic artifact。最后补 acceptance、repeatability 与 README。

## Validation and Acceptance

- `build_rerun_route_b_on_labeled_split_v2.py --help` 可正常显示
- `validate_rerun_route_b_on_labeled_split_v2.py --help` 可正常显示
- 至少生成：
  - `route_b_v2_plan.json`
  - `route_b_v2_label_definition.json`
  - `route_b_v2_readiness_summary.json`
  - `route_b_v2_dataset.jsonl`
  - `route_b_v2_summary.json`
  - `route_b_v2_logistic_predictions.jsonl`
  - `route_b_v2_logistic_summary.json`
  - `route_b_v2_model_metadata.json`
  - `route_b_v2_run_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

039 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 rerun 过程失败，可直接重跑 build CLI。

## Remaining Risks

- route B v2 仍然只是 more-natural proxy supervision，不是更高等级真值。
- 当前 rerun 仍然受 local curated split、轻量模型和 self-fit logistic 限制。

## Next Suggested Plan

若 039 完成，下一步建议创建 `.plans/040-post-v2-symmetric-comparison.md`，把 B-v2 与 C-v2 放到同一层做第一次真正的 v2 对称比较。
