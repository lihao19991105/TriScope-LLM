# 062 First Minimal Real Experiment Matrix Dry-Run

## Purpose / Big Picture

061 已经把 `minimal_real_experiment_matrix_v1` 变成了一个可执行的矩阵对象。062 的任务是把它从“已 materialize 的矩阵输入”推进成“第一轮真正会动起来的 matrix-level dry-run”，明确矩阵单元、route 映射、module status 与输出契约。

## Scope

### In Scope

- matrix dry-run contract definition
- matrix cell / route / module mapping
- first matrix dry-run execution
- acceptance / repeatability / README / 收口

### Out of Scope

- first matrix full execution
- 更大模型矩阵
- benchmark-scale主实验

## Repository Context

本计划主要衔接：

- `outputs/minimal_real_experiment_matrix_bootstrap/default/*`
- `outputs/real_experiment_cutover_bootstrap/default/*`
- `outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs/*`
- `src/eval/real_experiment_first_dry_run.py`

## Deliverables

- `.plans/062-first-minimal-real-experiment-matrix-dry-run.md`
- `src/eval/first_minimal_real_experiment_matrix_dry_run.py`
- `src/eval/first_minimal_real_experiment_matrix_dry_run_checks.py`
- `scripts/build_first_minimal_real_experiment_matrix_dry_run.py`
- `scripts/validate_first_minimal_real_experiment_matrix_dry_run.py`
- `first_matrix_dry_run_plan.json`
- `first_matrix_execution_contract.json`
- `first_matrix_readiness_summary.json`
- `first_matrix_dry_run_summary.json`
- `first_matrix_dry_run_registry.json`
- `first_matrix_module_status.json`
- `first_matrix_cell_status.json`
- `first_matrix_dry_run_preview.jsonl`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define matrix dry-run contract and readiness
- [x] Milestone 2: run first matrix dry-run and emit structured artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：062 不重新生成 query contract，而是复用稳定的 v6 query contracts，并把它们映射到 `minimal_real_experiment_matrix_v1` 的单个 matrix cell。
  - 原因：当前矩阵对象的目标是从 single-cutover execution 进入 matrix envelope，而不是发明新的 query substrate。
  - 影响范围：execution contract、cell status、dry-run registry。

## Validation and Acceptance

- `build_first_minimal_real_experiment_matrix_dry_run.py --help` 可正常显示
- `validate_first_minimal_real_experiment_matrix_dry_run.py --help` 可正常显示
- 至少生成：
  - `first_matrix_dry_run_plan.json`
  - `first_matrix_execution_contract.json`
  - `first_matrix_readiness_summary.json`
  - `first_matrix_dry_run_summary.json`
  - `first_matrix_dry_run_registry.json`
  - `first_matrix_module_status.json`
  - `first_matrix_cell_status.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- 当前 matrix 仍然是单 dataset / 单 model / 小规模 local curated 对象。
- dry-run 证明的是 matrix execution mapping，而不是 full matrix 结论。

## Outcome Summary

- `outputs/first_minimal_real_experiment_matrix_dry_run/default/first_matrix_dry_run_summary.json` 显示 `dry_run_completed = true`、`cell_count = 1`、`dataset_rows = 70`。
- `outputs/first_minimal_real_experiment_matrix_dry_run/default/first_matrix_cell_status.json` 显示当前唯一 cell `dataset0_model0_routes_b_c_fusion` 的 `route_b / route_c / fusion_summary` 全部 PASS。
- `outputs/first_minimal_real_experiment_matrix_dry_run/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 062 完成，下一步建议创建 `.plans/063-first-minimal-real-experiment-matrix-execution.md`，基于 dry-run 结果完成 first matrix execution。
