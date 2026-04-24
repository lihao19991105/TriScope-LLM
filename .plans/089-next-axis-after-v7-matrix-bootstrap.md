# 089 Next-Axis-After-v7 Matrix Bootstrap

## Purpose / Big Picture

088 如果已经明确 v7 之后最值得扩的方向，那么 089 的任务就是把这条 next-axis-after-v7 路线先 bootstrap 成一个真实存在的矩阵对象。

## Scope

### In Scope

- next-axis-after-v7 matrix definition
- readiness summary
- materialized inputs
- bootstrap artifact

### Out of Scope

- 直接执行完整下一轮矩阵
- 大规模模型 / dataset 轴跳跃

## Repository Context

本计划主要衔接：

- `outputs/post_v7_real_experiment_matrix_analysis/default/*`
- `outputs/next_axis_after_v6_matrix_execution/default/*`
- `outputs/next_axis_after_v6_matrix_bootstrap/default/*`

## Deliverables

- `.plans/089-next-axis-after-v7-matrix-bootstrap.md`
- `src/eval/next_axis_after_v7_matrix_bootstrap.py`
- `src/eval/next_axis_after_v7_matrix_bootstrap_checks.py`
- `scripts/build_next_axis_after_v7_matrix_bootstrap.py`
- `scripts/validate_next_axis_after_v7_matrix_bootstrap.py`
- `next_axis_after_v7_matrix_plan.json`
- `next_axis_after_v7_matrix_definition.json`
- `next_axis_after_v7_matrix_readiness_summary.json`
- `materialized_next_axis_after_v7_matrix/`
- `next_axis_after_v7_input_contract.json`
- `next_axis_after_v7_bootstrap_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define next-axis-after-v7 matrix
- [x] Milestone 2: materialize inputs and bootstrap artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 下一轮最自然的扩张并不是直接跳出 fusion 轴，而是对 `fusion_cell_refined_support_ablation` 自身做 residual-stability sweep。
- 现有 materialized inputs 可以直接复用，所以 089 仍然保持了低成本 bootstrap 节奏。

## Decision Log

- 决策：089 优先把下一步定义成 refined fusion support-residual stability 的下一层压力测试，而不是贸然跳到模型轴。
  - 原因：当前 repo reality 仍然缺少第二个 ready-local model；而 refined fusion 的 support-isolated residue 仍有继续被稳定性验证的空间。
  - 影响范围：routes、fusion mode、bootstrap notes。

## Plan of Work

先读取 088 的 recommendation 和当前 v7 matrix contract，再定义下一轮矩阵 routes 与 fusion mode。随后复制必要的 materialized inputs、写出 contract 和 bootstrap summary，最后完成 validator 与 README 收口。

## Concrete Steps

1. 创建 v8 bootstrap 实现与 CLI。
2. 定义 next-axis-after-v7 matrix definition / readiness。
3. materialize 输入目录并写出 input contract。
4. 跑 default / default_repeat 两次 bootstrap。
5. 跑 validator。
6. 更新 README 与计划进度。

## Validation and Acceptance

- `build_next_axis_after_v7_matrix_bootstrap.py --help` 可正常显示
- `validate_next_axis_after_v7_matrix_bootstrap.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v7_matrix_plan.json`
  - `next_axis_after_v7_matrix_definition.json`
  - `next_axis_after_v7_matrix_readiness_summary.json`
  - `materialized_next_axis_after_v7_matrix/`
  - `next_axis_after_v7_input_contract.json`
  - `next_axis_after_v7_bootstrap_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- bootstrap 可重复执行，覆盖目标输出目录中的同名文件。
- 若 build 失败，可直接重跑 build CLI。
- 若 validator 失败，可保留 run 目录并重跑 validator。

## Remaining Risks

- 下一轮矩阵仍然是小规模真实实验矩阵，不是最终论文矩阵。
- 继续扩 refined fusion coverage 依旧受 local curated split 和 lightweight model 限制。

## Outcome Summary

- `outputs/next_axis_after_v7_matrix_bootstrap/default/next_axis_after_v7_matrix_definition.json` 已定义 `next_axis_after_v7_real_experiment_matrix_v8`。
- `outputs/next_axis_after_v7_matrix_bootstrap/default/next_axis_after_v7_bootstrap_summary.json` 已确认下一轮矩阵 bootstrap ready，`route_count = 11`。
- `outputs/next_axis_after_v7_matrix_bootstrap/repeatability_default/artifact_acceptance.json` 已确认 acceptance / repeatability 为 `PASS`。

## Next Suggested Plan

若 089 完成，下一步应进入 next-axis-after-v7 matrix dry-run / execution，优先验证 refined fusion 的 support-residual stability 是否真的继续带来新判断信息。
