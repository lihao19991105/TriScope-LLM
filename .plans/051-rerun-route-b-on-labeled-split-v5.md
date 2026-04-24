# 051 Rerun Route B On Labeled Split V5

## Purpose / Big Picture

050 会先把 route C 推到 `larger_labeled_split_v5`。051 的目标是把 route B 也真正接到同一个 v5 substrate 上，使 route B / route C 在 `60-row / 60-base-sample` shared substrate 上达到第一次真正的对称状态。

## Scope

### In Scope

- route B on v5 contract / label definition
- v5 route B inputs materialization
- route B on v5 rerun and logistic artifact
- acceptance / repeatability / README / 收口

### Out of Scope

- v5 对称比较
- benchmark ground truth 接入
- 更大模型 / 更大数据规模

## Repository Context

本计划主要衔接：

- `outputs/rerun_route_c_on_labeled_split_v5/default/*`
- `outputs/post_v4_next_step_bootstrap/default/*`
- `src/eval/rerun_route_b_on_labeled_split_v4.py`
- `src/fusion/more_natural_label_fusion.py`
- `src/probes/*.py`
- `src/features/*.py`

## Deliverables

- `.plans/051-rerun-route-b-on-labeled-split-v5.md`
- `src/eval/rerun_route_b_on_labeled_split_v5.py`
- `scripts/build_rerun_route_b_on_labeled_split_v5.py`
- `src/eval/rerun_route_b_on_labeled_split_v5_checks.py`
- `scripts/validate_rerun_route_b_on_labeled_split_v5.py`
- `route_b_v5_plan.json`
- `route_b_v5_label_definition.json`
- `route_b_v5_readiness_summary.json`
- `route_b_v5_dataset.jsonl`
- `route_b_v5_summary.json`
- `route_b_v5_logistic_predictions.jsonl`
- `route_b_v5_logistic_summary.json`
- `route_b_v5_model_metadata.json`
- `route_b_v5_run_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize route B on v5
- [x] Milestone 2: run route B on v5 rerun
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- route B 在 v5 上不需要更复杂的 label semantics；它仍然是 sample-level task-correctness proxy，只是 substrate 从 `50` 行提升到 `60` 行。
- 051 可以直接沿用 047 的稳定链路，只需把 substrate 切换到 049 的 v5 inputs。
- route B v5 已稳定产出 `60` 条 sample-level rows / `60` 个 base samples，repeatability validator 为 `PASS`，因此 v5 条件下的 B/C 对称比较输入已经完整。

## Decision Log

- 决策：051 继续沿用 more-natural supervision proxy 语义，只切换 substrate 到 v5。
  - 原因：当前最重要的是与 route C v5 形成严格对称条件，而不是改动 route B 的监督定义。
  - 影响范围：route B v5 summary、comparison 和后续 recommendation 语义。

## Plan of Work

先读取 049 的 v5 substrate 和 050 的 route C v5 run summary，确认 route C v5 已经存在。然后把 v5 inputs materialize 到 051 目录，并生成 route B v5 plan / label definition / readiness summary。接着复用 reasoning / confidence / illumination rerun 链路和 more-natural label builder，在 v5 substrate 上跑出 route B v5 dataset 与 logistic artifact。最后补 acceptance、repeatability 与 README。

## Concrete Steps

1. 更新 `src/eval/rerun_route_b_on_labeled_split_v5.py` 与配套 CLI / validator。
2. 运行 `build_rerun_route_b_on_labeled_split_v5.py` 生成 route B v5 artifact。
3. 运行 repeat run 与 validator。
4. 更新 README 与 plan 进度。

## Validation and Acceptance

- `build_rerun_route_b_on_labeled_split_v5.py --help` 可正常显示
- `validate_rerun_route_b_on_labeled_split_v5.py --help` 可正常显示
- 至少生成：
  - `route_b_v5_plan.json`
  - `route_b_v5_label_definition.json`
  - `route_b_v5_readiness_summary.json`
  - `route_b_v5_dataset.jsonl`
  - `route_b_v5_summary.json`
  - `route_b_v5_logistic_predictions.jsonl`
  - `route_b_v5_logistic_summary.json`
  - `route_b_v5_model_metadata.json`
  - `route_b_v5_run_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

051 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 rerun 中断，可直接重跑 build CLI。

## Remaining Risks

- route B v5 仍然只是 more-natural proxy supervision，不是更高等级真值。
- route B v5 仍受 local curated split、`pilot_distilgpt2_hf` 和 self-fit logistic 限制。

## Next Suggested Plan

若 051 完成，下一步建议创建 `.plans/052-post-v5-symmetric-comparison.md`，把 B-v5 与 C-v5 放到同一层做第一次真正的 v5 对称比较。
