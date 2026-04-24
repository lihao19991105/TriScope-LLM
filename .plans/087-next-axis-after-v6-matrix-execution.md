# 087 Next-Axis-After-v6 Matrix Execution

## Purpose / Big Picture

086 如果已经证明 v7 dry-run 可行，那么 087 的任务就是让 `fusion_cell_refined_support_ablation` 真正进入 execution 层，而不是继续停在 contract / readiness。

## Scope

### In Scope

- v7 matrix execution selection
- route / ablation / fusion summary / candidate / refined / refined-ablation / support-sweep / support-ablation execution artifact
- structured execution outputs
- acceptance / repeatability

### Out of Scope

- 大规模模型矩阵
- 完整训练型 fusion classifier

## Repository Context

本计划主要衔接：

- `outputs/next_axis_after_v6_matrix_dry_run/default/*`
- `outputs/next_axis_after_v5_matrix_execution/default/*`
- `outputs/next_axis_after_v6_matrix_bootstrap/default/*`

## Deliverables

- `.plans/087-next-axis-after-v6-matrix-execution.md`
- `src/eval/next_axis_after_v6_matrix_execution.py`
- `src/eval/next_axis_after_v6_matrix_execution_checks.py`
- `scripts/build_next_axis_after_v6_matrix_execution.py`
- `scripts/validate_next_axis_after_v6_matrix_execution.py`
- `next_axis_after_v6_matrix_execution_selection.json`
- `next_axis_after_v6_matrix_execution_plan.json`
- `next_axis_after_v6_matrix_execution_readiness_summary.json`
- `next_axis_after_v6_matrix_execution_run_summary.json`
- `next_axis_after_v6_matrix_execution_registry.json`
- `next_axis_after_v6_matrix_execution_metrics.json`
- `next_axis_after_v6_matrix_cell_metrics.csv`
- `next_axis_after_v6_matrix_fusion_cell_refined_support_ablation_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: choose v7 executable path
- [x] Milestone 2: execute v7 matrix
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- `fusion_cell_refined_support_ablation` 可以用“从 support-sweep 中移除 support-retained residual”的 contract-level promotion 诚实构造，不需要重新 rerun routes。
- support-focused ablation 之后的 signal 恰好回落到 refined-ablation / candidate floor，这让 v7 的比较语义更清楚。

## Decision Log

- 决策：087 优先让 `fusion_cell_refined_support_ablation` 执行，而不是引入新的 dataset/model 轴。
  - 原因：当前最重要的问题是 refined fusion 在 support-focused ablation 后还剩多少信息。
  - 影响范围：selection、metrics、tradeoff context。

## Plan of Work

先读取 086 的 dry-run contract 与 083 的 executed v6 artifacts，确定 v7 的最小可执行路径。随后生成 support-ablation execution summary，并保留 summary / candidate / refined / refined-ablation / support-sweep 作为比较基线。最后完成 validator 与 README 收口。

## Concrete Steps

1. 创建 v7 execution 实现与 CLI。
2. 将 v6 route / fusion summaries 提升到 v7 matrix execution outputs。
3. 显式构造 `fusion_cell_refined_support_ablation` summary。
4. 跑 default / default_repeat 两次 execution。
5. 跑 validator 并核对 support-ablation 指标。
6. 更新 README 与计划进度。

## Validation and Acceptance

- `build_next_axis_after_v6_matrix_execution.py --help` 可正常显示
- `validate_next_axis_after_v6_matrix_execution.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v6_matrix_execution_run_summary.json`
  - `next_axis_after_v6_matrix_execution_registry.json`
  - `next_axis_after_v6_matrix_execution_metrics.json`
  - `next_axis_after_v6_matrix_fusion_cell_refined_support_ablation_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- execution 可以重复执行，覆盖目标输出目录中的同名文件。
- 若 execution build 失败，可直接重跑 build CLI。
- 若 build 成功但 validator 失败，可保留 run 目录并重跑 validator。

## Remaining Risks

- 087 的 support-ablation execution 仍然是 lightweight contract perturbation，不是训练得出的 fusion classifier。
- 仍然只有一个 dataset / 一个 model profile。

## Outcome Summary

- `outputs/next_axis_after_v6_matrix_execution/default/next_axis_after_v6_matrix_execution_run_summary.json` 已确认 v7 execution 为 `PASS`，`executed_cell_count = 9`。
- `outputs/next_axis_after_v6_matrix_execution/default/next_axis_after_v6_matrix_fusion_cell_refined_support_ablation_summary.json` 已确认 `fusion_cell_refined_support_ablation` 真正进入 execution 层。
- `outputs/next_axis_after_v6_matrix_execution/repeatability_default/artifact_acceptance.json` 已确认 acceptance / repeatability 为 `PASS`。

## Next Suggested Plan

若 087 完成，下一步应进入 088，重点比较 `fusion_summary`、`fusion_cell_candidate`、`fusion_cell_refined`、`fusion_cell_refined_ablation`、`fusion_cell_refined_support_sweep`、`fusion_cell_refined_support_ablation` 六者的新增价值差异。
