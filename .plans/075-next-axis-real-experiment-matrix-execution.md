# 075 Next-Axis Real Experiment Matrix Execution

## Purpose / Big Picture

074 如果已经证明 v4 dry-run 可行，那么 075 的任务就是让 `fusion_cell_refined` 真正进入 execution 层，而不是继续停在 contract/readiness。

## Scope

### In Scope

- v4 matrix execution selection
- route / ablation / fusion summary / candidate / refined execution artifact
- structured execution outputs
- acceptance / repeatability

### Out of Scope

- 大规模模型矩阵
- 完整训练型 fusion classifier

## Repository Context

本计划主要衔接：

- `outputs/next_axis_real_experiment_matrix_dry_run/default/*`
- `outputs/post_next_real_experiment_matrix_execution/default/*`
- `outputs/next_axis_real_experiment_matrix_bootstrap/default/*`

## Deliverables

- `.plans/075-next-axis-real-experiment-matrix-execution.md`
- `src/eval/next_axis_real_experiment_matrix_execution.py`
- `src/eval/next_axis_real_experiment_matrix_execution_checks.py`
- `scripts/build_next_axis_real_experiment_matrix_execution.py`
- `scripts/validate_next_axis_real_experiment_matrix_execution.py`
- `next_axis_matrix_execution_selection.json`
- `next_axis_matrix_execution_plan.json`
- `next_axis_matrix_execution_readiness_summary.json`
- `next_axis_matrix_execution_run_summary.json`
- `next_axis_matrix_execution_registry.json`
- `next_axis_matrix_execution_metrics.json`
- `next_axis_matrix_cell_metrics.csv`
- `next_axis_matrix_fusion_cell_refined_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: choose v4 executable path
- [x] Milestone 2: execute v4 matrix
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：075 优先让 `fusion_cell_refined` 执行，而不是引入新的 dataset/model 轴。
  - 原因：当前最重要的问题是 refined fusion 是否真的比 candidate / summary 多提供信息。
  - 影响范围：selection、metrics、tradeoff context。

## Validation and Acceptance

- `build_next_axis_real_experiment_matrix_execution.py --help` 可正常显示
- `validate_next_axis_real_experiment_matrix_execution.py --help` 可正常显示
- 至少生成：
  - `next_axis_matrix_execution_run_summary.json`
  - `next_axis_matrix_execution_registry.json`
  - `next_axis_matrix_execution_metrics.json`
  - `next_axis_matrix_fusion_cell_refined_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- 075 的 refined execution 仍然是 lightweight contract refinement，不是训练得出的 fusion classifier。
- 仍然只有一个 dataset / 一个 model profile。

## Outcome Summary

- `outputs/next_axis_real_experiment_matrix_execution/default/next_axis_matrix_execution_run_summary.json` 显示 v4 execution 已完成。
- `outputs/next_axis_real_experiment_matrix_execution/default/next_axis_matrix_fusion_cell_refined_summary.json` 显示 `fusion_cell_refined` 已成为真实执行 artifact。
- `outputs/next_axis_real_experiment_matrix_execution/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 075 完成，下一步应进入 076，重点比较 `fusion_summary`、`fusion_cell_candidate`、`fusion_cell_refined` 三者的新增价值差异。
