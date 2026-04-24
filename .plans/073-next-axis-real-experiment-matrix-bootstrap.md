# 073 Next-Axis Real Experiment Matrix Bootstrap

## Purpose / Big Picture

072 如果已经明确 fusion-cell-aware v3 之后的下一步，那么 073 的任务就是把这条下一轴真实实验矩阵路线先 bootstrap 起步，而不是停在 recommendation 层。

## Scope

### In Scope

- next-axis matrix definition
- readiness summary
- materialized next-axis matrix inputs
- bootstrap artifact

### Out of Scope

- 直接执行完整 next-axis matrix
- 大规模论文矩阵

## Repository Context

本计划主要衔接：

- `outputs/post_v3_real_experiment_matrix_analysis/default/*`
- `outputs/post_next_real_experiment_matrix_execution/default/*`
- `outputs/post_next_real_experiment_matrix_bootstrap/default/*`

## Deliverables

- `.plans/073-next-axis-real-experiment-matrix-bootstrap.md`
- `src/eval/next_axis_real_experiment_matrix_bootstrap.py`
- `src/eval/next_axis_real_experiment_matrix_bootstrap_checks.py`
- `scripts/build_next_axis_real_experiment_matrix_bootstrap.py`
- `scripts/validate_next_axis_real_experiment_matrix_bootstrap.py`
- `next_axis_real_experiment_matrix_plan.json`
- `next_axis_real_experiment_matrix_definition.json`
- `next_axis_real_experiment_matrix_readiness_summary.json`
- `materialized_next_axis_real_experiment_matrix/`
- `next_axis_real_experiment_input_contract.json`
- `next_axis_real_experiment_bootstrap_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define next-axis matrix
- [x] Milestone 2: materialize next-axis matrix inputs and bootstrap artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：073 把下一轴定义为 `fusion_cell_refinement`，而不是直接跳到模型轴或数据轴。
  - 原因：当前没有第二个 ready-local 模型，dataset 轴也缺少同等成熟的新对象；fusion cell refinement 是当前最有现实推进价值的下一步。
  - 影响范围：next-axis matrix definition、route set、fusion mode。

## Validation and Acceptance

- `build_next_axis_real_experiment_matrix_bootstrap.py --help` 可正常显示
- `validate_next_axis_real_experiment_matrix_bootstrap.py --help` 可正常显示
- 至少生成：
  - `next_axis_real_experiment_matrix_plan.json`
  - `next_axis_real_experiment_matrix_definition.json`
  - `next_axis_real_experiment_matrix_readiness_summary.json`
  - `materialized_next_axis_real_experiment_matrix/`
  - `next_axis_real_experiment_input_contract.json`
  - `next_axis_real_experiment_bootstrap_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- next-axis matrix 仍然是 small-scale real-experiment matrix，不是 full paper matrix。
- 当前下一轴依旧没有跳出 local curated split 与 lightweight model 的限制。

## Outcome Summary

- `outputs/next_axis_real_experiment_matrix_bootstrap/default/next_axis_real_experiment_matrix_definition.json` 已定义下一轮矩阵，并把重点放在 fusion cell refinement 上。
- `outputs/next_axis_real_experiment_matrix_bootstrap/default/next_axis_real_experiment_bootstrap_summary.json` 显示 next-axis matrix 已 bootstrap ready。
- `outputs/next_axis_real_experiment_matrix_bootstrap/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 073 完成，下一步应进入 next-axis matrix dry-run / execution，优先验证 refined fusion cell coverage 是否能进一步提升分析价值。
