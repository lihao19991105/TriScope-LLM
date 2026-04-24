# 091 Next-Axis-After-v7 Matrix Execution

## Purpose / Big Picture

090 已经把 `next_axis_after_v7_real_experiment_matrix_v8` 推进到 dry-run 成立，091 的任务是把这个 refined-fusion-support-ablation-sweep-aware v8 对象第一次推进成真正的 matrix execution。

## Scope

### In Scope

- v8 matrix execution selection / plan / readiness
- route / ablation / fusion summary / candidate / refined / refined-ablation / support-sweep / support-ablation / support-ablation-sweep execution artifacts
- execution metrics / preview / registry
- acceptance / repeatability

### Out of Scope

- 大规模模型 / dataset 轴扩张
- 重新训练完整 fusion classifier

## Repository Context

本计划主要衔接：

- `outputs/next_axis_after_v7_matrix_dry_run/default/*`
- `outputs/next_axis_after_v6_matrix_execution/default/*`
- `outputs/next_axis_after_v7_matrix_bootstrap/default/*`

## Deliverables

- `.plans/091-next-axis-after-v7-matrix-execution.md`
- `src/eval/next_axis_after_v7_matrix_execution.py`
- `src/eval/next_axis_after_v7_matrix_execution_checks.py`
- `scripts/build_next_axis_after_v7_matrix_execution.py`
- `scripts/validate_next_axis_after_v7_matrix_execution.py`
- `next_axis_after_v7_matrix_execution_selection.json`
- `next_axis_after_v7_matrix_execution_plan.json`
- `next_axis_after_v7_matrix_execution_readiness_summary.json`
- `next_axis_after_v7_matrix_execution_run_summary.json`
- `next_axis_after_v7_matrix_execution_registry.json`
- `next_axis_after_v7_matrix_execution_metrics.json`
- `next_axis_after_v7_matrix_cell_metrics.csv`
- `next_axis_after_v7_matrix_fusion_cell_refined_support_ablation_sweep_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: select v8 execution path
- [x] Milestone 2: run v8 matrix execution
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 当前最诚实的低成本执行方式仍然是 rehydrate 既有 route / fusion artifacts，并显式构造新的 `fusion_cell_refined_support_ablation_sweep` cell。
- support-ablation floor 在现有 lightweight setting 下已经接近 candidate floor，因此 v8 更像“把 residual stability 显式化”，而不是制造一个更高的新分数。

## Decision Log

- 决策：091 以“最小但能真正回答 support-isolated residual 在继续 sweep 后还剩多少信息”为优先，保留所有对照 cell 并新增 `fusion_cell_refined_support_ablation_sweep`。
  - 原因：当前研究增量在于显式化 residual stability，而不是再扩 route 数量。
  - 影响范围：execution metrics、comparison-ready summaries、preview。

## Plan of Work

先基于 090 的 dry-run 结果确定全部 v8 cells 均可执行，再把 v7 execution 的 route / fusion artifacts rehydrate 到 v8 matrix 层，并构造新的 support-ablation-sweep summary。随后生成 metrics、cell metrics、preview、run summary 和 repeatability artifacts，最后更新 README 与计划收口。

## Concrete Steps

1. 创建 v8 execution 实现与 CLI。
2. 写出 selection、plan、readiness。
3. 物化 route / fusion / support-ablation-sweep outputs。
4. 跑 default / default_repeat 两次 execution。
5. 跑 validator 并检查 `fusion_cell_refined_support_ablation_sweep` 是否执行成功。
6. 更新 README 与计划进度。

## Validation and Acceptance

- `build_next_axis_after_v7_matrix_execution.py --help` 可正常显示
- `validate_next_axis_after_v7_matrix_execution.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v7_matrix_execution_run_summary.json`
  - `next_axis_after_v7_matrix_execution_registry.json`
  - `next_axis_after_v7_matrix_execution_metrics.json`
  - `next_axis_after_v7_matrix_fusion_cell_refined_support_ablation_sweep_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- execution 可以重复执行，覆盖目标输出目录中的同名文件。
- 若单次 run 失败，可直接重跑 build CLI。
- 若 build 成功但 validator 失败，可保留 run 目录并单独重跑 validator。

## Remaining Risks

- v8 execution 仍然是 contract-level artifact promotion，不是全新 end-to-end rerun。
- `fusion_cell_refined_support_ablation_sweep` 仍然不是训练得出的 fusion classifier。

## Outcome Summary

- `outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_execution_run_summary.json` 已确认 v8 execution 为 `PASS`。
- `outputs/next_axis_after_v7_matrix_execution/default/next_axis_after_v7_matrix_fusion_cell_refined_support_ablation_sweep_summary.json` 已确认 `fusion_cell_refined_support_ablation_sweep` 真正进入 execution 层。
- `outputs/next_axis_after_v7_matrix_execution/repeatability_default/artifact_acceptance.json` 已确认 acceptance / repeatability 为 `PASS`。

## Next Suggested Plan

若 091 完成，下一步应进入 092，优先分析 support-isolated residual 在继续 sweep 后还剩多少稳定性。
