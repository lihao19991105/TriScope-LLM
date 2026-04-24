# 071 Post Next Real Experiment Matrix Execution

## Purpose / Big Picture

070 如果已经让 `post_next_real_experiment_matrix_v3` 进入 dry-run 层，那么 071 的任务就是让 `fusion_cell_candidate` 真正进入 execution，而不是继续停在 candidate / readiness 状态。

## Scope

### In Scope

- v3 matrix execution selection
- core route cells、ablation cells、fusion summary、fusion_cell_candidate 的最小真实执行
- execution artifact、metrics、registry
- acceptance / repeatability / README 收口

### Out of Scope

- 大规模多模型矩阵
- benchmark-scale fusion classifier

## Repository Context

本计划主要衔接：

- `outputs/post_next_real_experiment_matrix_dry_run/default/*`
- `outputs/next_real_experiment_matrix_execution/default/*`
- `src/eval/next_real_experiment_matrix_execution.py`

## Deliverables

- `.plans/071-post-next-real-experiment-matrix-execution.md`
- `src/eval/post_next_real_experiment_matrix_execution.py`
- `src/eval/post_next_real_experiment_matrix_execution_checks.py`
- `scripts/build_post_next_real_experiment_matrix_execution.py`
- `scripts/validate_post_next_real_experiment_matrix_execution.py`
- `post_next_matrix_execution_selection.json`
- `post_next_matrix_execution_plan.json`
- `post_next_matrix_execution_readiness_summary.json`
- `post_next_matrix_execution_run_summary.json`
- `post_next_matrix_execution_registry.json`
- `post_next_matrix_execution_metrics.json`
- `post_next_matrix_cell_metrics.csv`
- v3 route / ablation / fusion summaries

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: select executable v3 matrix path
- [x] Milestone 2: run v3 matrix execution and emit artifacts
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：071 采用“rehydrate v2 execution artifacts + explicit fusion candidate construction”的执行模式。
  - 原因：当前最关键的是让 `fusion_cell_candidate` 进入 execution 层，而不是为同一 substrate 重复做昂贵 rerun。
  - 影响范围：execution metrics、fusion candidate summary、072 analysis。

## Validation and Acceptance

- `build_post_next_real_experiment_matrix_execution.py --help` 可正常显示
- `validate_post_next_real_experiment_matrix_execution.py --help` 可正常显示
- 至少生成：
  - `post_next_matrix_execution_run_summary.json`
  - `post_next_matrix_execution_registry.json`
  - `post_next_matrix_execution_metrics.json`
  - `post_next_matrix_route_b_summary.json`
  - `post_next_matrix_route_c_summary.json`
  - `post_next_matrix_route_b_only_ablation_summary.json`
  - `post_next_matrix_route_c_only_ablation_summary.json`
  - `post_next_matrix_fusion_summary.json`
  - `post_next_matrix_fusion_cell_candidate_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- `fusion_cell_candidate` 仍然是基于已执行 route artifacts 构造的 explicit fusion candidate，不是独立训练出的 fusion classifier。
- v3 execution 仍然基于 local curated split 与 lightweight model。

## Outcome Summary

- `outputs/post_next_real_experiment_matrix_execution/default/post_next_matrix_execution_run_summary.json` 显示 v3 matrix execution 已完成，并包含 `fusion_cell_candidate`。
- `outputs/post_next_real_experiment_matrix_execution/default/post_next_matrix_fusion_cell_candidate_summary.json` 提供了 explicit fusion candidate 的执行级 artifact。
- `outputs/post_next_real_experiment_matrix_execution/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 071 完成，下一步应进入 `072-post-v3-real-experiment-matrix-analysis`，判断 `fusion_cell_candidate` 相比 `fusion_summary` 是否带来了新的判断信息。
