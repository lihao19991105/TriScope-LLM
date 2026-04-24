# 065 Next Real Experiment Matrix Bootstrap

## Purpose / Big Picture

064 若已经明确下一步推荐路线，那么 065 的任务就是把“下一轮更像真实实验的矩阵”先 bootstrap 起步，而不是停留在分析层。

## Scope

### In Scope

- next real-experiment matrix definition
- readiness summary
- materialized next-matrix inputs
- bootstrap artifact

### Out of Scope

- 直接跑完整 next matrix execution
- benchmark-scale 主实验

## Repository Context

本计划主要衔接：

- `outputs/post_minimal_real_experiment_matrix_analysis/default/*`
- `outputs/first_minimal_real_experiment_matrix_execution/default/*`
- `outputs/minimal_real_experiment_matrix_bootstrap/default/*`

## Deliverables

- `.plans/065-next-real-experiment-matrix-bootstrap.md`
- `src/eval/next_real_experiment_matrix_bootstrap.py`
- `src/eval/next_real_experiment_matrix_bootstrap_checks.py`
- `scripts/build_next_real_experiment_matrix_bootstrap.py`
- `scripts/validate_next_real_experiment_matrix_bootstrap.py`
- `next_real_experiment_matrix_plan.json`
- `next_real_experiment_matrix_definition.json`
- `next_real_experiment_matrix_readiness_summary.json`
- `materialized_next_real_experiment_matrix/`
- `next_real_experiment_input_contract.json`
- `next_real_experiment_bootstrap_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define next real-experiment matrix
- [x] Milestone 2: materialize next matrix inputs and bootstrap artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：065 只做 next matrix bootstrap，不直接执行 full next matrix。
  - 原因：当前目标是把下一轮矩阵第一次做成具体可执行对象，而不是立即推到重型执行。
  - 影响范围：matrix definition、materialized inputs、bootstrap summary。

## Validation and Acceptance

- `build_next_real_experiment_matrix_bootstrap.py --help` 可正常显示
- `validate_next_real_experiment_matrix_bootstrap.py --help` 可正常显示
- 至少生成：
  - `next_real_experiment_matrix_plan.json`
  - `next_real_experiment_matrix_definition.json`
  - `next_real_experiment_matrix_readiness_summary.json`
  - `materialized_next_real_experiment_matrix/`
  - `next_real_experiment_input_contract.json`
  - `next_real_experiment_bootstrap_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- next matrix 仍然不是完整论文矩阵。
- 当前 next matrix 仍然会保留 small-scale / local / lightweight 属性。

## Outcome Summary

- `outputs/next_real_experiment_matrix_bootstrap/default/next_real_experiment_matrix_definition.json` 定义了 `next_real_experiment_matrix_v2`，并将 routes 扩到 `route_b / route_c / fusion_summary / route_b_only_ablation / route_c_only_ablation`。
- `outputs/next_real_experiment_matrix_bootstrap/default/next_real_experiment_bootstrap_summary.json` 显示 `route_count = 5`、`dataset_count = 1`、`model_count = 1`。
- `outputs/next_real_experiment_matrix_bootstrap/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 065 完成，下一步建议基于 `materialized_next_real_experiment_matrix/` 进入 next matrix dry-run 或 next matrix execution。
