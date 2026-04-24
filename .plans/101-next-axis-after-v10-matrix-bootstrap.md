# 101 Next-Axis-After-v10 Matrix Bootstrap

## Purpose / Big Picture

100 已明确推荐继续扩 `fusion_support_floor_stress_invariance_coverage`。101 的目标是把这个 recommendation 物化成下一轮真实实验矩阵对象，而不是停在分析层。

## Scope

### In Scope

- v11 matrix plan / definition / readiness
- materialized next-axis-after-v10 inputs
- input contract / bootstrap summary
- acceptance / repeatability

### Out of Scope

- v11 dry-run / execution
- 模型轴和数据轴扩张

## Repository Context

- `outputs/post_v10_real_experiment_matrix_analysis/default/*`
- `outputs/next_axis_after_v9_matrix_bootstrap/default/*`
- `outputs/next_axis_after_v9_matrix_execution/default/*`

## Deliverables

- `.plans/101-next-axis-after-v10-matrix-bootstrap.md`
- `src/eval/next_axis_after_v10_matrix_bootstrap.py`
- `src/eval/next_axis_after_v10_matrix_bootstrap_checks.py`
- `scripts/build_next_axis_after_v10_matrix_bootstrap.py`
- `scripts/validate_next_axis_after_v10_matrix_bootstrap.py`
- `outputs/next_axis_after_v10_matrix_bootstrap/default/next_axis_after_v10_matrix_definition.json`
- `outputs/next_axis_after_v10_matrix_bootstrap/default/next_axis_after_v10_bootstrap_summary.json`
- `outputs/next_axis_after_v10_matrix_bootstrap/default/materialized_next_axis_after_v10_matrix/`
- `outputs/next_axis_after_v10_matrix_bootstrap/repeatability_default/artifact_acceptance.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define next-axis-after-v10 matrix
- [x] Milestone 2: materialize next-axis-after-v10 matrix inputs
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：101 继续保持 dataset/model 固定，只新增 `fusion_cell_refined_support_ablation_floor_stress_sweep`。
  - 原因：当前瓶颈仍是 ready-local dataset/model 稀缺，因此 support-floor-stress invariance coverage 比跨轴扩张更诚实、更可执行。

## Validation and Acceptance

- `build_next_axis_after_v10_matrix_bootstrap.py --help` 可正常显示
- `validate_next_axis_after_v10_matrix_bootstrap.py --help` 可正常显示
- `outputs/next_axis_after_v10_matrix_bootstrap/default/next_axis_after_v10_matrix_definition.json` 已生成
- `outputs/next_axis_after_v10_matrix_bootstrap/default/next_axis_after_v10_bootstrap_summary.json` 为 `PASS`
- `outputs/next_axis_after_v10_matrix_bootstrap/repeatability_default/artifact_acceptance.json` 为 `PASS`

## Outcome Summary

- 已 bootstrap 出 `next_axis_after_v10_real_experiment_matrix_v11`。
- 新矩阵 `route_count = 14`，新增 `fusion_cell_refined_support_ablation_floor_stress_sweep`。
- repeatability 已通过，说明下一轮 v11 bootstrap artifact 可稳定恢复。

## Next Suggested Plan

若 101 完成，下一步应进入 v11 dry-run / execution，优先验证 explicit support-floor-stress 结论在继续 sweep 后是否仍保持 invariance。
