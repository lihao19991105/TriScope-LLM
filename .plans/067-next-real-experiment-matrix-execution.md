# 067 Next Real Experiment Matrix Execution

## Purpose / Big Picture

066 如果已经让 `next_real_experiment_matrix_v2` 进入 dry-run 层，那么 067 的任务就是让 richer routes 真正进入 matrix-level execution，而不是继续停留在 contract/readiness 层。

## Scope

### In Scope

- richer matrix execution selection
- full cell 与 ablation cells 的最小真实执行
- execution artifact、metrics、registry
- acceptance / repeatability / README 收口

### Out of Scope

- 大规模多模型矩阵
- 新 benchmark 接入

## Repository Context

本计划主要衔接：

- `outputs/next_real_experiment_matrix_dry_run/default/*`
- `outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs/*`
- `src/eval/rerun_route_b_on_labeled_split_v6.py`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`

## Deliverables

- `.plans/067-next-real-experiment-matrix-execution.md`
- `src/eval/next_real_experiment_matrix_execution.py`
- `src/eval/next_real_experiment_matrix_execution_checks.py`
- `scripts/build_next_real_experiment_matrix_execution.py`
- `scripts/validate_next_real_experiment_matrix_execution.py`
- `next_matrix_execution_selection.json`
- `next_matrix_execution_plan.json`
- `next_matrix_execution_readiness_summary.json`
- `next_matrix_execution_run_summary.json`
- `next_matrix_execution_registry.json`
- `next_matrix_execution_metrics.json`
- `next_matrix_cell_metrics.csv`
- richer route summaries / ablation summaries

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: select executable richer matrix path
- [x] Milestone 2: run richer matrix execution and emit artifacts
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：067 执行 3 个 cells：full cell + `route_b_only_ablation` + `route_c_only_ablation`。
  - 原因：当前最重要的是让 richer coverage 中新增的 ablation routes 真正进入 execution，而不是仅保留 full cell。
  - 影响范围：execution registry、metrics、后续 068 richer matrix analysis。

## Validation and Acceptance

- `build_next_real_experiment_matrix_execution.py --help` 可正常显示
- `validate_next_real_experiment_matrix_execution.py --help` 可正常显示
- 至少生成：
  - `next_matrix_execution_run_summary.json`
  - `next_matrix_execution_registry.json`
  - `next_matrix_execution_metrics.json`
  - `next_matrix_route_b_summary.json`
  - `next_matrix_route_c_summary.json`
  - `next_matrix_route_b_only_ablation_summary.json`
  - `next_matrix_route_c_only_ablation_summary.json`
  - `next_matrix_fusion_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- richer matrix execution 仍然基于单 dataset / 单 model。
- ablation cells 当前仍然复用同一批真实 route outputs 做隔离解释，还不是全新模型/数据条件下的独立实验。

## Outcome Summary

- `outputs/next_real_experiment_matrix_execution/default/next_matrix_execution_run_summary.json` 显示 full cell 与两个 ablation cells 已进入 execution。
- `outputs/next_real_experiment_matrix_execution/default/next_matrix_cell_metrics.csv` 提供 richer route coverage 的 cell-level metrics。
- `outputs/next_real_experiment_matrix_execution/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 067 完成，下一步应进入 `068-post-next-real-experiment-matrix-analysis`，判断 richer routes 与 ablation cells 是否真的带来新增信息。
