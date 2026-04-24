# 063 First Minimal Real Experiment Matrix Execution

## Purpose / Big Picture

062 会证明 `minimal_real_experiment_matrix_v1` 的执行映射已经成立。063 的任务是在这个基础上选择第一轮最小但真实的 matrix-level execution path，让矩阵级真实执行真正发生。

## Scope

### In Scope

- first executable matrix path selection
- matrix execution input materialization
- first matrix execution artifact
- acceptance / repeatability / README / 收口

### Out of Scope

- 更大模型矩阵
- benchmark-grade主实验宣称
- 大规模真实实验

## Repository Context

本计划主要衔接：

- `outputs/first_minimal_real_experiment_matrix_dry_run/default/*`
- `outputs/minimal_real_experiment_matrix_bootstrap/default/*`
- `src/eval/first_real_experiment_execution.py`

## Deliverables

- `.plans/063-first-minimal-real-experiment-matrix-execution.md`
- `src/eval/first_minimal_real_experiment_matrix_execution.py`
- `src/eval/first_minimal_real_experiment_matrix_execution_checks.py`
- `scripts/build_first_minimal_real_experiment_matrix_execution.py`
- `scripts/validate_first_minimal_real_experiment_matrix_execution.py`
- `first_matrix_execution_selection.json`
- `first_matrix_execution_plan.json`
- `first_matrix_execution_readiness_summary.json`
- `first_matrix_execution_run_summary.json`
- `first_matrix_execution_registry.json`
- `first_matrix_execution_outputs/`
- `first_matrix_route_b_summary.json`
- `first_matrix_route_c_summary.json`
- `first_matrix_fusion_summary.json`
- `first_matrix_execution_metrics.json`
- `first_matrix_cell_metrics.csv`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: select first executable matrix path and materialize inputs
- [x] Milestone 2: run first matrix execution and emit artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：063 优先让 matrix 中唯一的 dataset/model cell 同时执行 `route_b + route_c + fusion_summary`。
  - 原因：当前矩阵规模很小，没有必要把 first matrix execution 退化成 route-only partial demo。
  - 影响范围：selection、metrics、cell-level summary。

## Validation and Acceptance

- `build_first_minimal_real_experiment_matrix_execution.py --help` 可正常显示
- `validate_first_minimal_real_experiment_matrix_execution.py --help` 可正常显示
- 至少生成：
  - `first_matrix_execution_selection.json`
  - `first_matrix_execution_plan.json`
  - `first_matrix_execution_readiness_summary.json`
  - `first_matrix_execution_run_summary.json`
  - `first_matrix_execution_registry.json`
  - `first_matrix_execution_outputs/`
  - `first_matrix_cell_metrics.csv`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- 即使 063 成功，当前 matrix 仍然只是 minimal matrix v1，而不是更丰富的真实实验矩阵。
- fusion 仍可能先以 summary/integration 形态落地，而不是完整独立 classifier path。

## Outcome Summary

- `outputs/first_minimal_real_experiment_matrix_execution/default/first_matrix_execution_run_summary.json` 显示 `executed_layers = ["route_b", "route_c", "fusion_summary"]`、`executed_cell_count = 1`。
- `outputs/first_minimal_real_experiment_matrix_execution/default/first_matrix_execution_metrics.json` 显示 `route_b_rows = 70`、`route_c_rows = 140`、`shared_base_samples = 70`。
- `outputs/first_minimal_real_experiment_matrix_execution/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 063 完成，下一步建议创建 `.plans/064-post-minimal-real-experiment-matrix-analysis.md`，分析 matrix execution 相比 single-cutover execution 增加了什么。
