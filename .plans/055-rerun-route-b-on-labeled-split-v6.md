# 055 Rerun Route B On Labeled Split V6

## Purpose / Big Picture

054 会先把 route C 推到 `larger_labeled_split_v6`。055 的目标是把 route B 也真正接到同一个 v6 substrate 上，使 route B / route C 在 `70-row / 70-base-sample` shared substrate 上达到第一次真正的对称状态。

## Scope

### In Scope

- route B on v6 contract / label definition
- v6 route B inputs materialization
- route B on v6 rerun and logistic artifact
- acceptance / repeatability / README / 收口

### Out of Scope

- v6 对称比较
- benchmark ground truth 接入
- 更大模型 / 更大数据规模

## Repository Context

本计划主要衔接：

- `outputs/rerun_route_c_on_labeled_split_v6/default/*`
- `outputs/post_v5_next_step_bootstrap/default/*`
- `src/eval/rerun_route_b_on_labeled_split_v5.py`
- `src/fusion/more_natural_label_fusion.py`
- `src/probes/*.py`
- `src/features/*.py`

## Deliverables

- `.plans/055-rerun-route-b-on-labeled-split-v6.md`
- `src/eval/rerun_route_b_on_labeled_split_v6.py`
- `scripts/build_rerun_route_b_on_labeled_split_v6.py`
- `src/eval/rerun_route_b_on_labeled_split_v6_checks.py`
- `scripts/validate_rerun_route_b_on_labeled_split_v6.py`
- `route_b_v6_plan.json`
- `route_b_v6_label_definition.json`
- `route_b_v6_readiness_summary.json`
- `route_b_v6_dataset.jsonl`
- `route_b_v6_summary.json`
- `route_b_v6_logistic_predictions.jsonl`
- `route_b_v6_logistic_summary.json`
- `route_b_v6_model_metadata.json`
- `route_b_v6_run_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize route B on v6
- [x] Milestone 2: run route B on v6 rerun
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- route B 在 v6 上不需要更复杂的 label semantics；它仍然是 sample-level task-correctness proxy，只是 substrate 从 `60` 行提升到 `70` 行。
- 055 可以直接沿用 051 的稳定链路，只需把 substrate 切换到 053 的 v6 inputs。
- route B v6 最终稳定产出 `70` 条 sample-level rows、`70` 个 base samples，logistic `mean_prediction_score = 0.1436550875416965`，acceptance / repeatability 都为 `PASS`。

## Decision Log

- 决策：055 继续沿用 more-natural supervision proxy 语义，只切换 substrate 到 v6。
  - 原因：当前最重要的是与 route C v6 形成严格对称条件，而不是改动 route B 的监督定义。
  - 影响范围：route B v6 summary、comparison 和后续 recommendation 语义。

## Plan of Work

先读取 053 的 v6 substrate 和 054 的 route C v6 run summary，确认 route C v6 已经存在。然后把 v6 inputs materialize 到 055 目录，并生成 route B v6 plan / label definition / readiness summary。接着复用 reasoning / confidence / illumination rerun 链路和 more-natural label builder，在 v6 substrate 上跑出 route B v6 dataset 与 logistic artifact。最后补 acceptance、repeatability 与 README。

## Concrete Steps

1. 更新 `src/eval/rerun_route_b_on_labeled_split_v6.py` 与配套 CLI / validator。
2. 运行 `build_rerun_route_b_on_labeled_split_v6.py` 生成 route B v6 artifact。
3. 运行 repeat run 与 validator。
4. 更新 README 与 plan 进度。

## Validation and Acceptance

- `build_rerun_route_b_on_labeled_split_v6.py --help` 可正常显示
- `validate_rerun_route_b_on_labeled_split_v6.py --help` 可正常显示
- 至少生成：
  - `route_b_v6_plan.json`
  - `route_b_v6_label_definition.json`
  - `route_b_v6_readiness_summary.json`
  - `route_b_v6_dataset.jsonl`
  - `route_b_v6_summary.json`
  - `route_b_v6_logistic_predictions.jsonl`
  - `route_b_v6_logistic_summary.json`
  - `route_b_v6_model_metadata.json`
  - `route_b_v6_run_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

055 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 rerun 中断，可直接重跑 build CLI。

## Remaining Risks

- route B v6 仍然只是 more-natural proxy supervision，不是更高等级真值。
- route B v6 仍受 local curated split、`pilot_distilgpt2_hf` 和 self-fit logistic 限制。

## Next Suggested Plan

若 055 完成，下一步建议创建 `.plans/056-post-v6-symmetric-comparison.md`，把 B-v6 与 C-v6 放到同一层做第一次真正的 v6 对称比较。
