# 046 Rerun Route C On Labeled Split V4

## Purpose / Big Picture

045 已经把 shared labeled substrate 从 `40 rows / 40 base samples` 提升到 `50 rows / 50 base samples`，并证明 route B / route C / fusion builder 仍然能附着在这个 v4 substrate 上。046 的目标是把 route C 真正 rerun 到 `larger_labeled_split_v4` 上，生成第一版 v4 条件下的 benchmark-truth-leaning supervised bootstrap artifact。

## Scope

### In Scope

- route C on v4 contract / label definition
- v4 route C inputs materialization
- route C on v4 rerun and logistic artifact
- acceptance / repeatability / README / 收口

### Out of Scope

- route B on v4 rerun
- v4 对称比较
- larger labeled split v5
- benchmark ground truth 或更大模型

## Repository Context

本计划主要衔接：

- `outputs/post_v3_next_step_bootstrap/default/*`
- `outputs/rerun_route_c_on_labeled_split_v3/default/*`
- `outputs/rerun_route_b_on_labeled_split_v3/default/*`
- `src/eval/rerun_route_c_on_labeled_split_v3.py`
- `src/fusion/benchmark_truth_leaning_label.py`
- `src/fusion/feature_alignment.py`

## Deliverables

- `.plans/046-rerun-route-c-on-labeled-split-v4.md`
- `src/eval/rerun_route_c_on_labeled_split_v4.py`
- `scripts/build_rerun_route_c_on_labeled_split_v4.py`
- `src/eval/rerun_route_c_on_labeled_split_v4_checks.py`
- `scripts/validate_rerun_route_c_on_labeled_split_v4.py`
- `route_c_v4_plan.json`
- `route_c_v4_label_definition.json`
- `route_c_v4_readiness_summary.json`
- `route_c_v4_dataset.jsonl`
- `route_c_v4_summary.json`
- `route_c_v4_logistic_predictions.jsonl`
- `route_c_v4_logistic_summary.json`
- `route_c_v4_model_metadata.json`
- `route_c_v4_run_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize route C on v4
- [x] Milestone 2: run route C on v4 rerun
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- v4 substrate 已经预先提供了 `50` 条 reasoning / confidence / illumination query contracts，以及 `100` 条 labeled illumination contracts，因此 046 不需要再发明新的 route C contract 语义。
- route C 在 v4 上的主要增量不是监督定义变化，而是 substrate 从 `40 base samples` 增长到 `50 base samples`，从而把 truth-leaning path 推到更大的 shared base。
- 046 仍然可以完整复用 042 的 stable orchestration，只需要切换到 v4 materialized inputs 与新的 artifact 命名。

## Decision Log

- 决策：046 继续使用 `task_answer_incorrect_label` 作为 route C supervision label。
  - 原因：这是当前最接近 task-truth 的低成本路径，并且与 v4 labeled illumination contracts 直接兼容。
  - 影响范围：route C v4 的 label definition、summary 与后续 comparison 语义。

## Plan of Work

先读取 045 的 `post_v3_next_step_plan.json` 和 `materialized_post_v3_inputs/`，确认当前 substrate 已经切到 `larger_labeled_split_v4`。然后把 v4 inputs 复制到 046 的 materialized inputs 目录，生成 route C v4 plan / label definition / readiness summary。接着复用 reasoning / confidence / illumination / labeled illumination 的 stable rerun 链路，在 v4 substrate 上跑出新的 fusion dataset，再用 benchmark-truth-leaning label builder 生成 contract-level supervised dataset，并完成 logistic bootstrap。最后补 acceptance、repeatability 与 README。

## Validation and Acceptance

- `build_rerun_route_c_on_labeled_split_v4.py --help` 可正常显示
- `validate_rerun_route_c_on_labeled_split_v4.py --help` 可正常显示
- 至少生成：
  - `route_c_v4_plan.json`
  - `route_c_v4_label_definition.json`
  - `route_c_v4_readiness_summary.json`
  - `route_c_v4_dataset.jsonl`
  - `route_c_v4_summary.json`
  - `route_c_v4_logistic_predictions.jsonl`
  - `route_c_v4_logistic_summary.json`
  - `route_c_v4_model_metadata.json`
  - `route_c_v4_run_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

046 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 probe 或 logistic 阶段中断，可直接重跑 build CLI。

## Remaining Risks

- route C v4 仍然只是 benchmark-truth-leaning proxy，不是 benchmark ground truth。
- 当前 rerun 仍然受 local curated split、轻量模型和 self-fit logistic 限制。

## Next Suggested Plan

若 046 完成，下一步建议创建 `.plans/047-rerun-route-b-on-labeled-split-v4.md`，把 route B 也 rerun 到同一个 v4 substrate 上，从而形成第一次真正的 v4 对称比较条件。
