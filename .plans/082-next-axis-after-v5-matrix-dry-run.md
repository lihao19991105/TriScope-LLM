# 082 Next-Axis-After-v5 Matrix Dry Run

## Purpose / Big Picture

081 已经把 `next_axis_after_v5_real_experiment_matrix_v6` bootstrap 出来，082 的任务是把这个 refined-fusion-support-sweep-aware v6 对象第一次推进成真正可执行的 matrix dry-run。

## Scope

### In Scope

- v6 matrix dry-run contract
- route / ablation / fusion summary / candidate / refined / refined-ablation / refined-support-sweep cell mapping
- structured dry-run artifact
- acceptance / repeatability

### Out of Scope

- 完整论文级矩阵
- 大规模模型 / dataset 轴扩张

## Repository Context

本计划主要衔接：

- `outputs/next_axis_after_v5_matrix_bootstrap/default/*`
- `outputs/next_axis_after_v4_matrix_execution/default/*`
- `outputs/post_v5_real_experiment_matrix_analysis/default/*`

## Deliverables

- `.plans/082-next-axis-after-v5-matrix-dry-run.md`
- `src/eval/next_axis_after_v5_matrix_dry_run.py`
- `src/eval/next_axis_after_v5_matrix_dry_run_checks.py`
- `scripts/build_next_axis_after_v5_matrix_dry_run.py`
- `scripts/validate_next_axis_after_v5_matrix_dry_run.py`
- `next_axis_after_v5_matrix_dry_run_plan.json`
- `next_axis_after_v5_matrix_execution_contract.json`
- `next_axis_after_v5_matrix_readiness_summary.json`
- `next_axis_after_v5_matrix_dry_run_summary.json`
- `next_axis_after_v5_matrix_dry_run_registry.json`
- `next_axis_after_v5_matrix_dry_run.log`
- `next_axis_after_v5_matrix_module_status.json`
- `next_axis_after_v5_matrix_cell_status.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define v6 matrix dry-run contract
- [x] Milestone 2: run v6 matrix dry-run
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 复用 v6 substrate 的 query contracts 依然足够支撑新的 support-sweep matrix dry-run，因此 082 不需要再引入新的 prompt/query 物化层。

## Decision Log

- 决策：082 保持 dataset/model 固定，只把重点放在 `fusion_cell_refined_support_sweep` 相对 `fusion_cell_refined_ablation` / `fusion_cell_refined` / `fusion_cell_candidate` / `fusion_summary` 的 contract 差异上。
  - 原因：当前新增问题不是继续扩轴，而是证明 refined-fusion stability sweep 已经成为可执行对象。
  - 影响范围：cell design、readiness summary、module status。

## Plan of Work

先读取 081 的 matrix definition、bootstrap summary 和 materialized inputs，建立 v6 的 cell mapping 与 execution contract。随后运行一次真实的 matrix-level dry-run，确认 support sweep cell 与已有的 summary / candidate / refined / refined-ablation cells 能同时进入结构化 dry-run 层。最后补 acceptance、repeatability 与 README 收口。

## Concrete Steps

1. 创建 v6 dry-run 实现与 CLI。
2. 物化 contract、readiness 和 dry-run registry。
3. 跑 default / default_repeat 两次 dry-run。
4. 跑 validator 并检查 `fusion_cell_refined_support_sweep` cell 是否通过。
5. 更新 README 与计划进度。

## Validation and Acceptance

- `build_next_axis_after_v5_matrix_dry_run.py --help` 可正常显示
- `validate_next_axis_after_v5_matrix_dry_run.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v5_matrix_dry_run_plan.json`
  - `next_axis_after_v5_matrix_execution_contract.json`
  - `next_axis_after_v5_matrix_readiness_summary.json`
  - `next_axis_after_v5_matrix_dry_run_summary.json`
  - `next_axis_after_v5_matrix_dry_run_registry.json`
  - `next_axis_after_v5_matrix_module_status.json`
  - `next_axis_after_v5_matrix_cell_status.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- dry-run 可以重复执行，覆盖目标输出目录中的同名文件。
- 若单次 run 失败，可直接重跑 build CLI。
- 若 build 成功但 validator 失败，可保留现有 run 目录并单独重跑 validator。

## Remaining Risks

- v6 仍然只是 small-scale real-experiment matrix，不是正式主实验矩阵。
- `fusion_cell_refined_support_sweep` 即使 dry-run 成功，也还不是训练得出的 fusion classifier。

## Outcome Summary

- `outputs/next_axis_after_v5_matrix_dry_run/default/next_axis_after_v5_matrix_dry_run_summary.json` 显示 v6 dry-run 已完成。
- `outputs/next_axis_after_v5_matrix_dry_run/default/next_axis_after_v5_matrix_cell_status.json` 显示 `fusion_summary`、`fusion_cell_candidate`、`fusion_cell_refined`、`fusion_cell_refined_ablation`、`fusion_cell_refined_support_sweep` 都已进入 dry-run cell 结构。
- `outputs/next_axis_after_v5_matrix_dry_run/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 082 完成，下一步应进入 083，优先验证 `fusion_cell_refined_support_sweep` 能否真正进入 execution 层。
