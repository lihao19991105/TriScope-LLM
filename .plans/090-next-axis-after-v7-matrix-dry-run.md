# 090 Next-Axis-After-v7 Matrix Dry Run

## Purpose / Big Picture

089 已经把 `next_axis_after_v7_real_experiment_matrix_v8` bootstrap 出来，090 的任务是把这个 refined-fusion-support-ablation-sweep-aware v8 对象第一次推进成真正可执行的 matrix dry-run。

## Scope

### In Scope

- v8 matrix dry-run contract
- route / ablation / fusion summary / candidate / refined / refined-ablation / support-sweep / support-ablation / support-ablation-sweep cell mapping
- structured dry-run artifact
- acceptance / repeatability

### Out of Scope

- 完整论文级矩阵
- 大规模模型 / dataset 轴扩张

## Repository Context

本计划主要衔接：

- `outputs/next_axis_after_v7_matrix_bootstrap/default/*`
- `outputs/next_axis_after_v6_matrix_execution/default/*`
- `outputs/post_v7_real_experiment_matrix_analysis/default/*`

## Deliverables

- `.plans/090-next-axis-after-v7-matrix-dry-run.md`
- `src/eval/next_axis_after_v7_matrix_dry_run.py`
- `src/eval/next_axis_after_v7_matrix_dry_run_checks.py`
- `scripts/build_next_axis_after_v7_matrix_dry_run.py`
- `scripts/validate_next_axis_after_v7_matrix_dry_run.py`
- `next_axis_after_v7_matrix_dry_run_plan.json`
- `next_axis_after_v7_matrix_execution_contract.json`
- `next_axis_after_v7_matrix_readiness_summary.json`
- `next_axis_after_v7_matrix_dry_run_summary.json`
- `next_axis_after_v7_matrix_dry_run_registry.json`
- `next_axis_after_v7_matrix_dry_run.log`
- `next_axis_after_v7_matrix_module_status.json`
- `next_axis_after_v7_matrix_cell_status.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define v8 matrix dry-run contract
- [x] Milestone 2: run v8 matrix dry-run
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- v8 仍然不需要新的 query-contract 物化层；沿用已有 materialized inputs 就足以支撑 dry-run。
- `fusion_cell_refined_support_ablation_sweep` 可以自然作为新增 explicit cell 接入现有 dry-run schema，不需要重构 registry / module-status 结构。

## Decision Log

- 决策：090 保持 dataset/model 固定，只把重点放在 `fusion_cell_refined_support_ablation_sweep` 相对 `fusion_cell_refined_support_ablation` / `fusion_cell_refined_support_sweep` / `fusion_cell_refined_ablation` / `fusion_cell_refined` / `fusion_cell_candidate` / `fusion_summary` 的 contract 差异上。
  - 原因：当前新增问题不是继续扩轴，而是证明 support-isolated residual stability 已经成为可执行对象。
  - 影响范围：cell design、readiness summary、module status、preview。

## Plan of Work

先读取 089 的 matrix definition、bootstrap summary 和 materialized inputs，建立 v8 的 cell mapping 与 execution contract。随后运行一次真实的 matrix-level dry-run，确认 support-ablation-sweep cell 与已有的 summary / candidate / refined / refined-ablation / support-sweep / support-ablation cells 能同时进入结构化 dry-run 层。最后补 acceptance、repeatability 与 README 收口。

## Concrete Steps

1. 创建 v8 dry-run 实现与 CLI。
2. 物化 contract、readiness 和 dry-run registry。
3. 跑 default / default_repeat 两次 dry-run。
4. 跑 validator 并检查 `fusion_cell_refined_support_ablation_sweep` cell 是否通过。
5. 更新 README 与计划进度。

## Validation and Acceptance

- `build_next_axis_after_v7_matrix_dry_run.py --help` 可正常显示
- `validate_next_axis_after_v7_matrix_dry_run.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v7_matrix_dry_run_plan.json`
  - `next_axis_after_v7_matrix_execution_contract.json`
  - `next_axis_after_v7_matrix_readiness_summary.json`
  - `next_axis_after_v7_matrix_dry_run_summary.json`
  - `next_axis_after_v7_matrix_dry_run_registry.json`
  - `next_axis_after_v7_matrix_module_status.json`
  - `next_axis_after_v7_matrix_cell_status.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- dry-run 可以重复执行，覆盖目标输出目录中的同名文件。
- 若单次 run 失败，可直接重跑 build CLI。
- 若 build 成功但 validator 失败，可保留现有 run 目录并单独重跑 validator。

## Remaining Risks

- v8 仍然只是 small-scale real-experiment matrix，不是正式主实验矩阵。
- `fusion_cell_refined_support_ablation_sweep` 即使 dry-run 成功，也还不是训练得出的 fusion classifier。

## Outcome Summary

- `outputs/next_axis_after_v7_matrix_dry_run/default/next_axis_after_v7_matrix_dry_run_summary.json` 已确认 v8 dry-run 为 `PASS`。
- `outputs/next_axis_after_v7_matrix_dry_run/default/next_axis_after_v7_matrix_cell_status.json` 已确认 10 个 cells 全部通过，其中包含 `fusion_cell_refined_support_ablation_sweep`。
- `outputs/next_axis_after_v7_matrix_dry_run/repeatability_default/artifact_acceptance.json` 已确认 acceptance / repeatability 为 `PASS`。

## Next Suggested Plan

若 090 完成，下一步应进入 091，优先验证 `fusion_cell_refined_support_ablation_sweep` 能否真正进入 execution 层。
