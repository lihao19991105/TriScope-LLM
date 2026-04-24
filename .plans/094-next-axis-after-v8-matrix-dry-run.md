# 094 Next-Axis-After-v8 Matrix Dry Run

## Purpose / Big Picture

093 已经把 `next_axis_after_v8_real_experiment_matrix_v9` bootstrap 出来。094 的目标是把这个 refined-fusion-support-floor-probe-aware v9 对象第一次推进成真正可执行的 matrix dry-run，并把 `fusion_cell_refined_support_ablation_floor_probe` 从 bootstrap object 推进成 explicit dry-run cell。

## Scope

### In Scope

- v9 matrix dry-run contract
- route / ablation / fusion summary / candidate / refined / refined-ablation / support-sweep / support-ablation / support-ablation-sweep / floor-probe mapping
- structured dry-run artifact
- acceptance / repeatability

### Out of Scope

- 模型轴和数据轴扩张
- 训练型 fusion classifier

## Repository Context

- `outputs/next_axis_after_v8_matrix_bootstrap/default/*`
- `outputs/next_axis_after_v7_matrix_execution/default/*`
- `outputs/post_v8_real_experiment_matrix_analysis/default/*`

## Deliverables

- `.plans/094-next-axis-after-v8-matrix-dry-run.md`
- `src/eval/next_axis_after_v8_matrix_dry_run.py`
- `src/eval/next_axis_after_v8_matrix_dry_run_checks.py`
- `scripts/build_next_axis_after_v8_matrix_dry_run.py`
- `scripts/validate_next_axis_after_v8_matrix_dry_run.py`
- `outputs/next_axis_after_v8_matrix_dry_run/default/next_axis_after_v8_matrix_dry_run_summary.json`
- `outputs/next_axis_after_v8_matrix_dry_run/default/next_axis_after_v8_matrix_cell_status.json`
- `outputs/next_axis_after_v8_matrix_dry_run/repeatability_default/artifact_acceptance.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define v9 matrix dry-run contract
- [x] Milestone 2: run v9 matrix dry-run
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：094 保持 dataset/model 固定，只把新增重点放在 `fusion_cell_refined_support_ablation_floor_probe` 相对 `fusion_cell_refined_support_ablation_sweep` / `fusion_cell_refined_support_ablation` / `fusion_cell_refined_support_sweep` / `fusion_cell_refined` / `fusion_cell_candidate` / `fusion_summary` 的 contract 差异上。
  - 原因：当前新增问题不是继续扩轴，而是先把 swept support-isolated floor 变成显式可执行对象。

## Validation and Acceptance

- `build_next_axis_after_v8_matrix_dry_run.py --help` 可正常显示
- `validate_next_axis_after_v8_matrix_dry_run.py --help` 可正常显示
- `outputs/next_axis_after_v8_matrix_dry_run/default/next_axis_after_v8_matrix_dry_run_summary.json` 为 `PASS`
- `outputs/next_axis_after_v8_matrix_dry_run/default/next_axis_after_v8_matrix_cell_status.json` 包含 `fusion_cell_refined_support_ablation_floor_probe`
- `outputs/next_axis_after_v8_matrix_dry_run/repeatability_default/artifact_acceptance.json` 为 `PASS`

## Outcome Summary

- v9 dry-run 已完成，`matrix_name = next_axis_after_v8_real_experiment_matrix_v9`，`route_count = 12`，`cell_count = 11`。
- `fusion_cell_refined_support_ablation_floor_probe` 已作为 `dataset0_model0_fusion_cell_refined_support_ablation_floor_probe_explicit` 进入 dry-run。
- repeatability 已通过，说明 v9 dry-run contract 稳定。

## Next Suggested Plan

若 094 完成，下一步应进入 095，优先验证 `fusion_cell_refined_support_ablation_floor_probe` 能否真正进入 execution 层。
