# 083 Next-Axis-After-v5 Matrix Execution

## Purpose / Big Picture

082 如果已经证明 v6 dry-run 可行，那么 083 的任务就是让 `fusion_cell_refined_support_sweep` 真正进入 execution 层，而不是继续停在 contract / readiness。

## Scope

### In Scope

- v6 matrix execution selection
- route / ablation / fusion summary / candidate / refined / refined-ablation / refined-support-sweep execution artifact
- structured execution outputs
- acceptance / repeatability

### Out of Scope

- 大规模模型矩阵
- 完整训练型 fusion classifier

## Repository Context

本计划主要衔接：

- `outputs/next_axis_after_v5_matrix_dry_run/default/*`
- `outputs/next_axis_after_v4_matrix_execution/default/*`
- `outputs/next_axis_after_v5_matrix_bootstrap/default/*`

## Deliverables

- `.plans/083-next-axis-after-v5-matrix-execution.md`
- `src/eval/next_axis_after_v5_matrix_execution.py`
- `src/eval/next_axis_after_v5_matrix_execution_checks.py`
- `scripts/build_next_axis_after_v5_matrix_execution.py`
- `scripts/validate_next_axis_after_v5_matrix_execution.py`
- `next_axis_after_v5_matrix_execution_selection.json`
- `next_axis_after_v5_matrix_execution_plan.json`
- `next_axis_after_v5_matrix_execution_readiness_summary.json`
- `next_axis_after_v5_matrix_execution_run_summary.json`
- `next_axis_after_v5_matrix_execution_registry.json`
- `next_axis_after_v5_matrix_execution_metrics.json`
- `next_axis_after_v5_matrix_cell_metrics.csv`
- `next_axis_after_v5_matrix_fusion_cell_refined_support_sweep_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: choose v6 executable path
- [x] Milestone 2: execute v6 matrix
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- `fusion_cell_refined_support_sweep` 可以用 v5 已执行的 refined / ablation artifacts 做低成本、可解释的 contract-level promotion，而不需要昂贵 rerun。

## Decision Log

- 决策：083 优先让 `fusion_cell_refined_support_sweep` 执行，而不是引入新的 dataset/model 轴。
  - 原因：当前最重要的问题是 refined fusion 在 support / stability 扰动下还能保留多少信息。
  - 影响范围：selection、metrics、tradeoff context。

## Plan of Work

先读取 082 的 dry-run contract 与 079 的 executed v5 artifacts，确定 v6 的最小可执行路径。随后生成 support-sweep execution summary，并保留 summary / candidate / refined / refined-ablation 作为比较基线。最后完成 validator 与 README 收口。

## Concrete Steps

1. 创建 v6 execution 实现与 CLI。
2. 将 v5 route / fusion summaries 提升到 v6 matrix execution outputs。
3. 显式构造 `fusion_cell_refined_support_sweep` summary。
4. 跑 default / default_repeat 两次 execution。
5. 跑 validator 并核对 support-sweep 指标。
6. 更新 README 与计划进度。

## Validation and Acceptance

- `build_next_axis_after_v5_matrix_execution.py --help` 可正常显示
- `validate_next_axis_after_v5_matrix_execution.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v5_matrix_execution_run_summary.json`
  - `next_axis_after_v5_matrix_execution_registry.json`
  - `next_axis_after_v5_matrix_execution_metrics.json`
  - `next_axis_after_v5_matrix_fusion_cell_refined_support_sweep_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- execution 可以重复执行，覆盖目标输出目录中的同名文件。
- 若 execution build 失败，可直接重跑 build CLI。
- 若 build 成功但 validator 失败，可保留 run 目录并重跑 validator。

## Remaining Risks

- 083 的 support-sweep execution 仍然是 lightweight contract perturbation，不是训练得出的 fusion classifier。
- 仍然只有一个 dataset / 一个 model profile。

## Outcome Summary

- `outputs/next_axis_after_v5_matrix_execution/default/next_axis_after_v5_matrix_execution_run_summary.json` 显示 v6 execution 已完成。
- `outputs/next_axis_after_v5_matrix_execution/default/next_axis_after_v5_matrix_fusion_cell_refined_support_sweep_summary.json` 显示 `fusion_cell_refined_support_sweep` 已成为真实执行 artifact。
- `outputs/next_axis_after_v5_matrix_execution/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 083 完成，下一步应进入 084，重点比较 `fusion_summary`、`fusion_cell_candidate`、`fusion_cell_refined`、`fusion_cell_refined_ablation`、`fusion_cell_refined_support_sweep` 五者的新增价值差异。
