# 047 Rerun Route B On Labeled Split V4

## Purpose / Big Picture

046 会先把 route C 推到 `larger_labeled_split_v4`。047 的目标是把 route B 也真正接到同一个 v4 substrate 上，使 route B / route C 在 `50-row / 50-base-sample` shared substrate 上达到第一次真正的对称状态。

## Scope

### In Scope

- route B on v4 contract / label definition
- v4 route B inputs materialization
- route B on v4 rerun and logistic artifact
- acceptance / repeatability / README / 收口

### Out of Scope

- v4 对称比较
- larger labeled split v5
- benchmark ground truth 或更大模型

## Repository Context

本计划主要衔接：

- `outputs/post_v3_next_step_bootstrap/default/*`
- `outputs/rerun_route_c_on_labeled_split_v4/default/*`
- `outputs/rerun_route_b_on_labeled_split_v3/default/*`
- `src/eval/rerun_route_b_on_labeled_split_v3.py`
- `src/fusion/more_natural_label_fusion.py`
- `src/fusion/feature_alignment.py`

## Deliverables

- `.plans/047-rerun-route-b-on-labeled-split-v4.md`
- `src/eval/rerun_route_b_on_labeled_split_v4.py`
- `scripts/build_rerun_route_b_on_labeled_split_v4.py`
- `src/eval/rerun_route_b_on_labeled_split_v4_checks.py`
- `scripts/validate_rerun_route_b_on_labeled_split_v4.py`
- `route_b_v4_plan.json`
- `route_b_v4_label_definition.json`
- `route_b_v4_readiness_summary.json`
- `route_b_v4_dataset.jsonl`
- `route_b_v4_summary.json`
- `route_b_v4_logistic_predictions.jsonl`
- `route_b_v4_logistic_summary.json`
- `route_b_v4_model_metadata.json`
- `route_b_v4_run_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize route B on v4
- [x] Milestone 2: run route B on v4 rerun
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- route B 在 v4 上不需要更复杂的 label semantics；它仍然是 sample-level task-correctness proxy，只是 substrate 从 `40` 行提升到 `50` 行。
- 047 的信息增量主要来自与 046 配对后的 shared-substrate symmetry，而不是 route B 自身定义变化。
- 047 可以直接沿用 043 的稳定链路，只需把 substrate 切换到 045 的 v4 inputs。

## Decision Log

- 决策：047 继续使用 `task_correctness_violation_label` 作为 route B supervision label。
  - 原因：这条 more-natural proxy 路线当前已经稳定，并且最适合与 route C v4 做对称比较。
  - 影响范围：route B v4 summary、comparison 和后续 recommendation 语义。

## Plan of Work

先读取 045 的 v4 substrate 和 046 的 route C v4 run summary，确认 route C v4 已经存在。然后把 v4 inputs materialize 到 047 目录，并生成 route B v4 plan / label definition / readiness summary。接着复用 reasoning / confidence / illumination rerun 链路和 more-natural label builder，在 v4 substrate 上跑出 route B v4 dataset 与 logistic artifact。最后补 acceptance、repeatability 与 README。

## Validation and Acceptance

- `build_rerun_route_b_on_labeled_split_v4.py --help` 可正常显示
- `validate_rerun_route_b_on_labeled_split_v4.py --help` 可正常显示
- 至少生成：
  - `route_b_v4_plan.json`
  - `route_b_v4_label_definition.json`
  - `route_b_v4_readiness_summary.json`
  - `route_b_v4_dataset.jsonl`
  - `route_b_v4_summary.json`
  - `route_b_v4_logistic_predictions.jsonl`
  - `route_b_v4_logistic_summary.json`
  - `route_b_v4_model_metadata.json`
  - `route_b_v4_run_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

047 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 rerun 过程失败，可直接重跑 build CLI。

## Remaining Risks

- route B v4 仍然只是 more-natural proxy supervision，不是更高等级真值。
- 当前 rerun 仍然受 local curated split、轻量模型和 self-fit logistic 限制。

## Next Suggested Plan

若 047 完成，下一步建议创建 `.plans/048-post-v4-symmetric-comparison.md`，把 B-v4 与 C-v4 放到同一层做第一次真正的 v4 对称比较。
