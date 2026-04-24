# 070 Post Next Real Experiment Matrix Dry-Run

## Purpose / Big Picture

069 已经把 `post_next_real_experiment_matrix_v3` bootstrap 成一个 fusion-cell-aware matrix object，但它还没有真正进入 dry-run。070 的任务是把 v3 matrix 从“有 fusion_cell_candidate 定义”推进成“有 fusion-cell-aware dry-run artifact”。

## Scope

### In Scope

- v3 matrix dry-run contract 定义
- route / ablation / fusion_summary / fusion_cell_candidate 的 cell 映射
- v3 matrix dry-run artifact
- acceptance / repeatability / README 收口

### Out of Scope

- full benchmark-scale execution
- 回退去 proxy substrate 扩容

## Repository Context

本计划主要衔接：

- `outputs/post_next_real_experiment_matrix_bootstrap/default/*`
- `outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs/*`
- `src/eval/next_real_experiment_matrix_dry_run.py`

## Deliverables

- `.plans/070-post-next-real-experiment-matrix-dry-run.md`
- `src/eval/post_next_real_experiment_matrix_dry_run.py`
- `src/eval/post_next_real_experiment_matrix_dry_run_checks.py`
- `scripts/build_post_next_real_experiment_matrix_dry_run.py`
- `scripts/validate_post_next_real_experiment_matrix_dry_run.py`
- `post_next_matrix_dry_run_plan.json`
- `post_next_matrix_execution_contract.json`
- `post_next_matrix_readiness_summary.json`
- `post_next_matrix_dry_run_summary.json`
- `post_next_matrix_dry_run_registry.json`
- `post_next_matrix_module_status.json`
- `post_next_matrix_cell_status.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define v3 matrix dry-run contract
- [x] Milestone 2: run v3 matrix dry-run and emit structured artifacts
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- v3 的新增价值不在于新数据源，而在于把 `fusion_summary` 与 `fusion_cell_candidate` 明确分成 inherited summary style cell 和 explicit candidate style cell。
- 当前最小 honest 映射是 5 个 cells：`route_b_c_core`、两个 ablation cells、`fusion_summary` cell、`fusion_cell_candidate` cell。

## Decision Log

- 决策：070 把 v3 matrix 建模为 5 个 cells，而不是把 `fusion_summary` 塞回 full route bundle 里。
  - 原因：本轮的核心问题是比较 `fusion_summary` 与 `fusion_cell_candidate`，所以它们必须是明确分开的 cells。
  - 影响范围：dry-run contract、cell status、后续 071 execution selection。

## Validation and Acceptance

- `build_post_next_real_experiment_matrix_dry_run.py --help` 可正常显示
- `validate_post_next_real_experiment_matrix_dry_run.py --help` 可正常显示
- 至少生成：
  - `post_next_matrix_dry_run_plan.json`
  - `post_next_matrix_execution_contract.json`
  - `post_next_matrix_readiness_summary.json`
  - `post_next_matrix_dry_run_summary.json`
  - `post_next_matrix_dry_run_registry.json`
  - `post_next_matrix_module_status.json`
  - `post_next_matrix_cell_status.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- v3 matrix 仍然只有一个 dataset / model 组合。
- `fusion_cell_candidate` 还只是 explicit candidate style，不等于 benchmark-grade fusion classifier。

## Outcome Summary

- `outputs/post_next_real_experiment_matrix_dry_run/default/post_next_matrix_execution_contract.json` 已把 v3 matrix 明确映射为 core route cells、ablation cells、fusion summary cell 和 fusion candidate cell。
- `outputs/post_next_real_experiment_matrix_dry_run/default/post_next_matrix_dry_run_summary.json` 显示 `fusion_cell_candidate` 已进入 dry-run 层。
- `outputs/post_next_real_experiment_matrix_dry_run/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 070 完成，下一步应进入 `071-post-next-real-experiment-matrix-execution`，让 `fusion_cell_candidate` 真正进入 execution 层。
