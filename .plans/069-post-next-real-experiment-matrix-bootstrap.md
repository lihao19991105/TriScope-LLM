# 069 Post Next Real Experiment Matrix Bootstrap

## Purpose / Big Picture

068 如果已经明确 richer matrix v2 之后的下一步，那么 069 的任务就是把这条下一轮真实实验矩阵路线先 bootstrap 起步，而不是停在 recommendation 层。

## Scope

### In Scope

- next-next matrix definition
- readiness summary
- materialized next-next matrix inputs
- bootstrap artifact

### Out of Scope

- 直接执行完整 next-next matrix
- 大规模论文矩阵

## Repository Context

本计划主要衔接：

- `outputs/post_next_real_experiment_matrix_analysis/default/*`
- `outputs/next_real_experiment_matrix_execution/default/*`
- `outputs/next_real_experiment_matrix_bootstrap/default/*`

## Deliverables

- `.plans/069-post-next-real-experiment-matrix-bootstrap.md`
- `src/eval/post_next_real_experiment_matrix_bootstrap.py`
- `src/eval/post_next_real_experiment_matrix_bootstrap_checks.py`
- `scripts/build_post_next_real_experiment_matrix_bootstrap.py`
- `scripts/validate_post_next_real_experiment_matrix_bootstrap.py`
- `next_next_real_experiment_matrix_plan.json`
- `next_next_real_experiment_matrix_definition.json`
- `next_next_real_experiment_matrix_readiness_summary.json`
- `materialized_next_next_real_experiment_matrix/`
- `next_next_real_experiment_input_contract.json`
- `next_next_real_experiment_bootstrap_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define next-next matrix
- [x] Milestone 2: materialize next-next matrix inputs and bootstrap artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：069 把下一轮矩阵扩展轴定义为 `fusion_cell_coverage`。
  - 原因：068 已确认 richer routes 和 ablation 已带来增量，当前最大缺口是 fusion 仍然只是 summary，而不是独立矩阵 cell。
  - 影响范围：next-next matrix definition、route set、bootstrap contract。

## Validation and Acceptance

- `build_post_next_real_experiment_matrix_bootstrap.py --help` 可正常显示
- `validate_post_next_real_experiment_matrix_bootstrap.py --help` 可正常显示
- 至少生成：
  - `next_next_real_experiment_matrix_plan.json`
  - `next_next_real_experiment_matrix_definition.json`
  - `next_next_real_experiment_matrix_readiness_summary.json`
  - `materialized_next_next_real_experiment_matrix/`
  - `next_next_real_experiment_input_contract.json`
  - `next_next_real_experiment_bootstrap_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- next-next matrix 仍然是 small-scale real-experiment matrix，不是 full paper matrix。
- 新增 fusion cell 仍然会受到 local curated slice 与 lightweight model 的限制。

## Outcome Summary

- `outputs/post_next_real_experiment_matrix_bootstrap/default/next_next_real_experiment_matrix_definition.json` 已定义下一轮 richer matrix，加入显式 fusion cell coverage。
- `outputs/post_next_real_experiment_matrix_bootstrap/default/next_next_real_experiment_bootstrap_summary.json` 显示下一轮矩阵已 bootstrap ready。
- `outputs/post_next_real_experiment_matrix_bootstrap/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 069 完成，下一步应进入 next-next matrix dry-run / execution，优先验证新增 fusion cell coverage 是否能真正进入 execution 层。
