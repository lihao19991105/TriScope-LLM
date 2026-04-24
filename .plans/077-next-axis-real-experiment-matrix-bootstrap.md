# 077 Next-Axis Real Experiment Matrix Bootstrap

## Purpose / Big Picture

076 如果已经明确 v4 之后最值得扩的方向，那么 077 的任务就是把这条 next-axis-after-v4 路线先 bootstrap 成一个真实存在的矩阵对象。

## Scope

### In Scope

- next-axis-after-v4 matrix definition
- readiness summary
- materialized inputs
- bootstrap artifact

### Out of Scope

- 直接执行完整下一轮矩阵
- 大规模模型 / dataset 轴跳跃

## Repository Context

本计划主要衔接：

- `outputs/post_v4_real_experiment_matrix_analysis/default/*`
- `outputs/next_axis_real_experiment_matrix_execution/default/*`
- `outputs/next_axis_real_experiment_matrix_bootstrap/default/*`

## Deliverables

- `.plans/077-next-axis-real-experiment-matrix-bootstrap.md`
- `src/eval/next_axis_after_v4_real_experiment_matrix_bootstrap.py`
- `src/eval/next_axis_after_v4_real_experiment_matrix_bootstrap_checks.py`
- `scripts/build_next_axis_after_v4_real_experiment_matrix_bootstrap.py`
- `scripts/validate_next_axis_after_v4_real_experiment_matrix_bootstrap.py`
- `next_axis_after_v4_matrix_plan.json`
- `next_axis_after_v4_matrix_definition.json`
- `next_axis_after_v4_matrix_readiness_summary.json`
- `materialized_next_axis_after_v4_matrix/`
- `next_axis_after_v4_input_contract.json`
- `next_axis_after_v4_bootstrap_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define next-axis-after-v4 matrix
- [x] Milestone 2: materialize inputs and bootstrap artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：077 优先把下一步定义成 refined fusion coverage 的下一层隔离/验证，而不是贸然跳到模型轴。
  - 原因：当前 repo reality 仍然缺少第二个 ready-local model；而 refined fusion 仍有继续被隔离验证的空间。
  - 影响范围：routes、fusion mode、bootstrap notes。

## Validation and Acceptance

- `build_next_axis_after_v4_real_experiment_matrix_bootstrap.py --help` 可正常显示
- `validate_next_axis_after_v4_real_experiment_matrix_bootstrap.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v4_matrix_plan.json`
  - `next_axis_after_v4_matrix_definition.json`
  - `next_axis_after_v4_matrix_readiness_summary.json`
  - `materialized_next_axis_after_v4_matrix/`
  - `next_axis_after_v4_input_contract.json`
  - `next_axis_after_v4_bootstrap_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- 下一轮矩阵仍然是小规模真实实验矩阵，不是最终论文矩阵。
- 继续扩 refined fusion coverage 依旧受 local curated split 和 lightweight model 限制。

## Outcome Summary

- `outputs/next_axis_after_v4_real_experiment_matrix_bootstrap/default/next_axis_after_v4_matrix_definition.json` 已定义下一轮矩阵。
- `outputs/next_axis_after_v4_real_experiment_matrix_bootstrap/default/next_axis_after_v4_bootstrap_summary.json` 显示下一轮矩阵已 bootstrap ready。
- `outputs/next_axis_after_v4_real_experiment_matrix_bootstrap/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 077 完成，下一步应进入 next-axis-after-v4 matrix dry-run / execution，优先验证 refined fusion 的进一步隔离覆盖是否真的带来新判断信息。
