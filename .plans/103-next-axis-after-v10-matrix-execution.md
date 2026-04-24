# 103 Next-Axis-After-v10 Matrix Execution

## Purpose / Big Picture

102 已确认 `next_axis_after_v10_real_experiment_matrix_v11` 可以作为 refined-fusion-support-floor-stress-sweep-aware matrix 进入 dry-run。103 的目标是把 `fusion_cell_refined_support_ablation_floor_stress_sweep` 真正推进到 execution 层，并与更早的 floor-stress / floor-probe / support-ablation-sweep 等显式 cell 并列比较。

## Scope

### In Scope

- v11 matrix execution selection / plan / readiness
- explicit floor-stress-sweep execution artifact
- execution metrics / preview / registry
- acceptance / repeatability / README

### Out of Scope

- 新开更大模型
- 数据轴扩张

## Repository Context

- `outputs/next_axis_after_v10_matrix_dry_run/default/*`
- `outputs/next_axis_after_v9_matrix_execution/default/*`
- `outputs/next_axis_after_v10_matrix_bootstrap/default/*`

## Deliverables

- `.plans/103-next-axis-after-v10-matrix-execution.md`
- `src/eval/next_axis_after_v10_matrix_execution.py`
- `src/eval/next_axis_after_v10_matrix_execution_checks.py`
- `scripts/build_next_axis_after_v10_matrix_execution.py`
- `scripts/validate_next_axis_after_v10_matrix_execution.py`
- `outputs/next_axis_after_v10_matrix_execution/default/next_axis_after_v10_matrix_execution_run_summary.json`
- `outputs/next_axis_after_v10_matrix_execution/default/next_axis_after_v10_matrix_execution_metrics.json`
- `outputs/next_axis_after_v10_matrix_execution/default/next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_floor_stress_sweep_summary.json`
- `outputs/next_axis_after_v10_matrix_execution/repeatability_default/artifact_acceptance.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: select first executable v11 path
- [x] Milestone 2: run v11 matrix execution
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：103 继续使用“基于已通过验收的 v10 execution 产物做 matrix-level promotion”的路线，显式构造 floor-stress-sweep cell。
  - 原因：本轮的诚实目标是判断 direct-stress 结论在继续 sweep 后是否仍保持 invariant，而不是重做昂贵底层执行。

## Validation and Acceptance

- `build_next_axis_after_v10_matrix_execution.py --help` 可正常显示
- `validate_next_axis_after_v10_matrix_execution.py --help` 可正常显示
- `outputs/next_axis_after_v10_matrix_execution/default/next_axis_after_v10_matrix_execution_run_summary.json` 为 `PASS`
- `outputs/next_axis_after_v10_matrix_execution/default/next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_floor_stress_sweep_summary.json` 已存在
- `outputs/next_axis_after_v10_matrix_execution/repeatability_default/artifact_acceptance.json` 为 `PASS`

## Outcome Summary

- v11 execution 已完成，`executed_cell_count = 13`。
- `fusion_cell_refined_support_ablation_floor_stress_sweep` 已真实进入 execution，且继续表现为 invariance-confirming signal。
- repeatability 已通过，说明 v11 execution metrics 在当前 contract 下稳定可复现。

## Next Suggested Plan

若 103 完成，下一步应进入 104，优先判断当前 fusion 同轴细化是否已经接近边际收益上限，并决定是否切向 1.5B 模型轴。
