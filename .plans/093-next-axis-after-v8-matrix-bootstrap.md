# 093 Next-Axis-After-v8 Matrix Bootstrap

## Purpose / Big Picture

092 已经把 `next_axis_after_v7_real_experiment_matrix_v8` 的新增价值明确下来，093 的任务是把推荐的下一步 `fusion_support_floor_invariance_coverage` 路线 bootstrap 成可继续执行的真实实验矩阵对象。

## Scope

### In Scope

- next-axis-after-v8 matrix definition / readiness
- materialized inputs
- bootstrap summary / contract
- acceptance / repeatability

### Out of Scope

- 直接运行 v9 完整 dry-run / execution
- 大规模模型 / dataset 轴扩张

## Repository Context

本计划主要衔接：

- `outputs/post_v8_real_experiment_matrix_analysis/default/*`
- `outputs/next_axis_after_v7_matrix_bootstrap/default/*`
- `outputs/next_axis_after_v7_matrix_execution/default/*`

## Deliverables

- `.plans/093-next-axis-after-v8-matrix-bootstrap.md`
- `src/eval/next_axis_after_v8_matrix_bootstrap.py`
- `src/eval/next_axis_after_v8_matrix_bootstrap_checks.py`
- `scripts/build_next_axis_after_v8_matrix_bootstrap.py`
- `scripts/validate_next_axis_after_v8_matrix_bootstrap.py`
- `next_axis_after_v8_matrix_plan.json`
- `next_axis_after_v8_matrix_definition.json`
- `next_axis_after_v8_matrix_readiness_summary.json`
- `materialized_next_axis_after_v8_matrix/`
- `next_axis_after_v8_input_contract.json`
- `next_axis_after_v8_bootstrap_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define next-axis-after-v8 matrix
- [x] Milestone 2: materialize next-axis-after-v8 inputs
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 由于 v8 已经把 support-isolated floor 是否继续变化这件事显式化，下一轮最自然的增量不是继续扩 route 数，而是把这个 floor 本身变成 direct probe 对象。
- 因此 v9 的新增对象更适合作为 `fusion_cell_refined_support_ablation_floor_probe`，而不是急着切到模型轴或数据轴。

## Decision Log

- 决策：093 将下一轮矩阵定义为 `next_axis_after_v8_real_experiment_matrix_v9`，扩张轴为 `fusion_support_floor_invariance_coverage`。
  - 原因：这是当前最诚实、最低风险、最能直接复用 v8 结论的下一步。
  - 影响范围：matrix definition、input contract、README 后续恢复点。

## Plan of Work

先读取 092 recommendation 和当前 v8 matrix definition / contract / materialized inputs，生成 v9 matrix plan、definition 和 readiness summary。随后 materialize v9 inputs，写出 input contract、bootstrap summary 和 repeatability artifacts，最后更新 README 与计划进度。

## Concrete Steps

1. 创建 v9 bootstrap 实现与 CLI。
2. 生成 matrix plan、definition、readiness。
3. 物化 `materialized_next_axis_after_v8_matrix/`。
4. 跑 default / default_repeat 两次 bootstrap。
5. 跑 validator 并确认 route / fusion mode / matrix name 稳定。
6. 更新 README 与计划进度。

## Validation and Acceptance

- `build_next_axis_after_v8_matrix_bootstrap.py --help` 可正常显示
- `validate_next_axis_after_v8_matrix_bootstrap.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v8_matrix_plan.json`
  - `next_axis_after_v8_matrix_definition.json`
  - `next_axis_after_v8_matrix_readiness_summary.json`
  - `materialized_next_axis_after_v8_matrix/`
  - `next_axis_after_v8_input_contract.json`
  - `next_axis_after_v8_bootstrap_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- bootstrap 可以重复执行，覆盖目标输出目录中的同名文件。
- 若单次 run 失败，可直接重跑 build CLI。
- 若 build 成功但 validator 失败，可保留 run 目录并单独重跑 validator。

## Remaining Risks

- v9 仍然会延续当前 single-dataset / single-model 的轻量级真实实验设定。
- floor-probe 仍然属于 explicit contract-level cell，不是训练出来的 fusion classifier。

## Outcome Summary

- `outputs/next_axis_after_v8_matrix_bootstrap/default/next_axis_after_v8_matrix_definition.json` 已定义 `next_axis_after_v8_real_experiment_matrix_v9`。
- `outputs/next_axis_after_v8_matrix_bootstrap/default/next_axis_after_v8_bootstrap_summary.json` 已确认下一轮矩阵 bootstrap ready，包含新增 `fusion_cell_refined_support_ablation_floor_probe`。
- `outputs/next_axis_after_v8_matrix_bootstrap/repeatability_default/artifact_acceptance.json` 已确认 acceptance / repeatability 为 `PASS`。

## Next Suggested Plan

若 093 完成，下一步应进入 094，优先验证 `fusion_cell_refined_support_ablation_floor_probe` 能否进入 dry-run / execution 层。
