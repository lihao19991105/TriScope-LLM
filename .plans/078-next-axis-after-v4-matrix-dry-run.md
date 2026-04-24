# 078 Next-Axis-After-v4 Matrix Dry Run

## Purpose / Big Picture

077 已经把 `next_axis_after_v4_real_experiment_matrix_v5` bootstrap 出来，078 的任务是把这个 refined-fusion-ablation-aware v5 对象第一次推进成真正可执行的 matrix dry-run。

## Scope

### In Scope

- v5 matrix dry-run contract
- route / ablation / fusion summary / candidate / refined / refined-ablation cell mapping
- structured dry-run artifact
- acceptance / repeatability

### Out of Scope

- 完整论文级矩阵
- 大规模模型/数据轴扩张

## Repository Context

本计划主要衔接：

- `outputs/next_axis_after_v4_real_experiment_matrix_bootstrap/default/*`
- `outputs/next_axis_real_experiment_matrix_execution/default/*`
- `outputs/post_v4_real_experiment_matrix_analysis/default/*`

## Deliverables

- `.plans/078-next-axis-after-v4-matrix-dry-run.md`
- `src/eval/next_axis_after_v4_matrix_dry_run.py`
- `src/eval/next_axis_after_v4_matrix_dry_run_checks.py`
- `scripts/build_next_axis_after_v4_matrix_dry_run.py`
- `scripts/validate_next_axis_after_v4_matrix_dry_run.py`
- `next_axis_after_v4_matrix_dry_run_plan.json`
- `next_axis_after_v4_matrix_execution_contract.json`
- `next_axis_after_v4_matrix_readiness_summary.json`
- `next_axis_after_v4_matrix_dry_run_summary.json`
- `next_axis_after_v4_matrix_dry_run_registry.json`
- `next_axis_after_v4_matrix_dry_run.log`
- `next_axis_after_v4_matrix_module_status.json`
- `next_axis_after_v4_matrix_cell_status.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define v5 matrix dry-run contract
- [x] Milestone 2: run v5 matrix dry-run
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：078 保持 dataset/model 固定，只把重点放在 `fusion_cell_refined_ablation` 与 `fusion_cell_refined` / `fusion_cell_candidate` / `fusion_summary` 的 contract 差异上。
  - 原因：当前最关键的新问题不是扩轴，而是证明 refined-fusion-ablation 已经成为可执行对象。
  - 影响范围：cell design、readiness summary、module status。

## Validation and Acceptance

- `build_next_axis_after_v4_matrix_dry_run.py --help` 可正常显示
- `validate_next_axis_after_v4_matrix_dry_run.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v4_matrix_dry_run_plan.json`
  - `next_axis_after_v4_matrix_execution_contract.json`
  - `next_axis_after_v4_matrix_readiness_summary.json`
  - `next_axis_after_v4_matrix_dry_run_summary.json`
  - `next_axis_after_v4_matrix_dry_run_registry.json`
  - `next_axis_after_v4_matrix_module_status.json`
  - `next_axis_after_v4_matrix_cell_status.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- v5 仍然只是 small-scale real-experiment matrix，不是正式主实验矩阵。
- `fusion_cell_refined_ablation` 即使 dry-run 成功，也还不是训练得出的 fusion classifier。

## Outcome Summary

- `outputs/next_axis_after_v4_matrix_dry_run/default/next_axis_after_v4_matrix_dry_run_summary.json` 显示 v5 dry-run 已完成。
- `outputs/next_axis_after_v4_matrix_dry_run/default/next_axis_after_v4_matrix_cell_status.json` 显示 `fusion_summary`、`fusion_cell_candidate`、`fusion_cell_refined`、`fusion_cell_refined_ablation` 都已进入 dry-run cell 结构。
- `outputs/next_axis_after_v4_matrix_dry_run/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 078 完成，下一步应进入 079，优先验证 `fusion_cell_refined_ablation` 能否真正进入 execution 层。
