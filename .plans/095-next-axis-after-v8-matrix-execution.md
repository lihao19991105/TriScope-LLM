# 095 Next-Axis-After-v8 Matrix Execution

## Purpose / Big Picture

094 已确认 `next_axis_after_v8_real_experiment_matrix_v9` 可以作为 refined-fusion-support-floor-probe-aware matrix 进入 dry-run。095 的目标是把 `fusion_cell_refined_support_ablation_floor_probe` 真正推进到 execution 层，并与 summary / candidate / refined / refined-ablation / support-sweep / support-ablation / support-ablation-sweep 并列比较。

## Scope

### In Scope

- v9 matrix execution selection / plan / readiness
- explicit floor-probe execution artifact
- execution metrics / preview / registry
- acceptance / repeatability

### Out of Scope

- 重跑昂贵底层 route substrate
- 模型轴与数据轴扩张

## Repository Context

- `outputs/next_axis_after_v8_matrix_dry_run/default/*`
- `outputs/next_axis_after_v7_matrix_execution/default/*`
- `outputs/next_axis_after_v8_matrix_bootstrap/default/*`

## Deliverables

- `.plans/095-next-axis-after-v8-matrix-execution.md`
- `src/eval/next_axis_after_v8_matrix_execution.py`
- `src/eval/next_axis_after_v8_matrix_execution_checks.py`
- `scripts/build_next_axis_after_v8_matrix_execution.py`
- `scripts/validate_next_axis_after_v8_matrix_execution.py`
- `outputs/next_axis_after_v8_matrix_execution/default/next_axis_after_v8_matrix_execution_run_summary.json`
- `outputs/next_axis_after_v8_matrix_execution/default/next_axis_after_v8_matrix_execution_metrics.json`
- `outputs/next_axis_after_v8_matrix_execution/default/next_axis_after_v8_matrix_fusion_cell_refined_support_ablation_floor_probe_summary.json`
- `outputs/next_axis_after_v8_matrix_execution/repeatability_default/artifact_acceptance.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: select first executable v9 path
- [x] Milestone 2: run v9 matrix execution
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：095 采用“基于已通过验收的 v8 execution 产物做 matrix-level promotion”的降本路线，并显式构造 floor-probe cell。
  - 原因：当前最重要的是诚实回答 swept support-isolated floor 是否 invariant，而不是做一轮昂贵 rerun。

## Validation and Acceptance

- `build_next_axis_after_v8_matrix_execution.py --help` 可正常显示
- `validate_next_axis_after_v8_matrix_execution.py --help` 可正常显示
- `outputs/next_axis_after_v8_matrix_execution/default/next_axis_after_v8_matrix_execution_run_summary.json` 为 `PASS`
- `outputs/next_axis_after_v8_matrix_execution/default/next_axis_after_v8_matrix_fusion_cell_refined_support_ablation_floor_probe_summary.json` 已存在
- `outputs/next_axis_after_v8_matrix_execution/repeatability_default/artifact_acceptance.json` 为 `PASS`

## Outcome Summary

- v9 execution 已完成，`executed_cell_count = 11`。
- `fusion_cell_refined_support_ablation_floor_probe` 已真实进入 execution，`floor_probe_signal_score = 0.0`，`support_floor_invariant = true`。
- repeatability 已通过，表明 floor-probe metrics 在当前 contract 下稳定可复现。

## Next Suggested Plan

若 095 完成，下一步应进入 096，优先把 floor-probe 与 support-ablation-sweep / support-ablation / support-sweep / refined / candidate / summary 的关系写成结构化比较。
