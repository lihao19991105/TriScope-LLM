# 079 Next-Axis-After-v4 Matrix Execution

## Purpose / Big Picture

078 如果已经证明 v5 dry-run 可行，那么 079 的任务就是让 `fusion_cell_refined_ablation` 真正进入 execution 层，而不是继续停在 contract/readiness。

## Scope

### In Scope

- v5 matrix execution selection
- route / ablation / fusion summary / candidate / refined / refined-ablation execution artifact
- structured execution outputs
- acceptance / repeatability

### Out of Scope

- 大规模模型矩阵
- 完整训练型 fusion classifier

## Repository Context

本计划主要衔接：

- `outputs/next_axis_after_v4_matrix_dry_run/default/*`
- `outputs/next_axis_real_experiment_matrix_execution/default/*`
- `outputs/next_axis_after_v4_real_experiment_matrix_bootstrap/default/*`

## Deliverables

- `.plans/079-next-axis-after-v4-matrix-execution.md`
- `src/eval/next_axis_after_v4_matrix_execution.py`
- `src/eval/next_axis_after_v4_matrix_execution_checks.py`
- `scripts/build_next_axis_after_v4_matrix_execution.py`
- `scripts/validate_next_axis_after_v4_matrix_execution.py`
- `next_axis_after_v4_matrix_execution_selection.json`
- `next_axis_after_v4_matrix_execution_plan.json`
- `next_axis_after_v4_matrix_execution_readiness_summary.json`
- `next_axis_after_v4_matrix_execution_run_summary.json`
- `next_axis_after_v4_matrix_execution_registry.json`
- `next_axis_after_v4_matrix_execution_metrics.json`
- `next_axis_after_v4_matrix_cell_metrics.csv`
- `next_axis_after_v4_matrix_fusion_cell_refined_ablation_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: choose v5 executable path
- [x] Milestone 2: execute v5 matrix
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：079 优先让 `fusion_cell_refined_ablation` 执行，而不是引入新的 dataset/model 轴。
  - 原因：当前最重要的问题是 refined fusion 在显式消融后还剩多少信息。
  - 影响范围：selection、metrics、tradeoff context。

## Validation and Acceptance

- `build_next_axis_after_v4_matrix_execution.py --help` 可正常显示
- `validate_next_axis_after_v4_matrix_execution.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v4_matrix_execution_run_summary.json`
  - `next_axis_after_v4_matrix_execution_registry.json`
  - `next_axis_after_v4_matrix_execution_metrics.json`
  - `next_axis_after_v4_matrix_fusion_cell_refined_ablation_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- 079 的 refined-ablation execution 仍然是 lightweight contract ablation，不是训练得出的 fusion classifier。
- 仍然只有一个 dataset / 一个 model profile。

## Outcome Summary

- `outputs/next_axis_after_v4_matrix_execution/default/next_axis_after_v4_matrix_execution_run_summary.json` 显示 v5 execution 已完成。
- `outputs/next_axis_after_v4_matrix_execution/default/next_axis_after_v4_matrix_fusion_cell_refined_ablation_summary.json` 显示 `fusion_cell_refined_ablation` 已成为真实执行 artifact。
- `outputs/next_axis_after_v4_matrix_execution/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 079 完成，下一步应进入 080，重点比较 `fusion_summary`、`fusion_cell_candidate`、`fusion_cell_refined`、`fusion_cell_refined_ablation` 四者的新增价值差异。
