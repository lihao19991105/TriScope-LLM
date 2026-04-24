# 024 More Natural Label Bootstrap

## Purpose / Big Picture

023 会说明：在 current controlled supervision 已跑满当前 local slice 之后，下一步最值得启动的是第一条 more-natural-label 路线。024 的目标是在不引入新模型、新数据和外部标注的前提下，把这条路线最小成本地 materialize，并让它第一次产出可执行 artifact。

## Scope

### In Scope

- more-natural-label selection / definition / readiness
- more-natural labeled fusion dataset materialization
- 最小 supervised logistic bootstrap
- acceptance / repeatability / README / 计划收口

### Out of Scope

- benchmark ground truth
- 更大数据切片
- 更重模型
- 研究级监督评估

## Repository Context

本计划将衔接：

- `outputs/more_natural_label_analysis/*`
- `outputs/controlled_supervision_expansion/*`
- `outputs/real_pilot_fusion_readiness/*`
- `outputs/pilot_materialization/*`
- `src/fusion/`
- `scripts/`

## Deliverables

- `.plans/024-more-natural-label-bootstrap.md`
- `src/fusion/more_natural_label_fusion.py`
- `scripts/build_more_natural_label_bootstrap.py`
- `src/fusion/more_natural_label_fusion_checks.py`
- `scripts/validate_more_natural_label_bootstrap.py`
- `more_natural_label_selection.json`
- `more_natural_label_definition.json`
- `more_natural_label_readiness_summary.json`
- `more_natural_labeled_dataset.jsonl`
- `more_natural_label_summary.json`
- `more_natural_supervised_readiness_summary.json`
- `more_natural_logistic_predictions.jsonl`
- `more_natural_logistic_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize more-natural-label route
- [x] Milestone 2: runnable more-natural supervised bootstrap
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 当前 more-natural 候选无需新 benchmark 或外部标签：直接复用 local slice 里的 `answerKey` 即可在 base-sample 层定义 task-correctness proxy。
- expanded real-pilot fusion 已经具备完整 `5` 行 full intersection，因此 more-natural label 可以直接映射到 sample-level fusion row，而不再需要 `contract_variant` 扩展。
- 当前候选标签分布为 `3 / 2`，这已经足够支撑第一版 bootstrap logistic。
- 这条路线的关键价值不是“更大”，而是“标签语义更自然”，因为它不再依赖 `control / targeted` contract row。

## Decision Log

- 决策：024 选择 `task_correctness_violation_label` 作为第一条 more-natural label。
  - 原因：它基于 local slice 的 `answerKey` 与 observed multi-modal pilot outputs，是当前最可审计、最轻量、最自然的候选。
  - 影响范围：dataset schema、summary、README。

- 决策：024 在 base-sample 层 materialize dataset，不再沿用 `contract_variant` row expansion。
  - 原因：当前 label 是 sample-level task correctness proxy，而不是 contract-level controlled label。
  - 影响范围：`more_natural_labeled_dataset.jsonl`、logistic prediction schema。

## Plan of Work

先把 route B 的 selection / definition / readiness 写成结构化 artifact，明确 label 来自 `answerKey + observed outputs`。然后利用 022 的 expanded real-pilot fusion 与三路原始结果，在 base-sample 层 materialize 一份 more-natural labeled fusion dataset，并在这份 dataset 上跑一版最小 logistic bootstrap。最后补 acceptance / repeatability 和 README。

## Concrete Steps

1. 创建 `.plans/024-more-natural-label-bootstrap.md`。
2. 实现 `src/fusion/more_natural_label_fusion.py`。
3. 实现 `scripts/build_more_natural_label_bootstrap.py`。
4. 生成 selection / definition / readiness / dataset / summary artifacts。
5. 运行最小 logistic bootstrap。
6. 实现 validator 与 repeatability。
7. 更新 README 与计划状态。

## Validation and Acceptance

- `build_more_natural_label_bootstrap.py --help` 可正常显示
- `validate_more_natural_label_bootstrap.py --help` 可正常显示
- M1 至少成功生成：
  - `more_natural_label_selection.json`
  - `more_natural_label_definition.json`
  - `more_natural_label_readiness_summary.json`
- M2 至少成功生成：
  - `more_natural_labeled_dataset.jsonl`
  - `more_natural_label_summary.json`
  - `more_natural_supervised_readiness_summary.json`
- 若 logistic 可行，则继续生成：
  - `more_natural_logistic_predictions.jsonl`
  - `more_natural_logistic_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

### Validation Snapshot

- `outputs/more_natural_label_bootstrap/default/more_natural_label_summary.json`
  - `num_rows = 5`
  - `label_name = task_correctness_violation_label`
  - `class_balance = {label_0: 3, label_1: 2}`
- `outputs/more_natural_label_bootstrap/default/more_natural_logistic_summary.json`
  - `summary_status = PASS`
  - `num_predictions = 5`
  - `mean_prediction_score = 0.44282765928624446`
- `outputs/more_natural_label_bootstrap/repeatability_default/repeatability_summary.json`
  - `all_key_metrics_match = true`

## Idempotence and Recovery

- 输出写入独立 `output_dir`
- 可重复运行
- 若上游 artifact 缺失，应写出结构化 failure summary

## Outputs and Artifacts

- `outputs/more_natural_label_bootstrap/*`

## Remaining Risks

- 当前 more-natural label 仍然只是 pilot-level proxy，而不是 benchmark ground truth。
- 当前 dataset 仍然只覆盖 5-row local slice 和轻量模型。
- illumination 的 task correctness 由 response 中的 option label 与 `query_answer_key` 做近似匹配，因此仍然是 lightweight proxy。

## Next Suggested Plan

若 024 完成，下一步建议分析 more-natural label 与 current controlled supervision 的边际价值差异，并决定是否需要引入更接近 benchmark truth 的监督源。
