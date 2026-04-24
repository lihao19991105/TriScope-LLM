# 066 Next Real Experiment Matrix Dry-Run

## Purpose / Big Picture

065 已经把 `next_real_experiment_matrix_v2` bootstrap 成一个 richer real-experiment matrix object，但它仍然只是 materialized object，还没有真正进入 matrix-level dry-run。066 的目标是把这个 richer matrix 从“可描述”推进到“可执行”。

## Scope

### In Scope

- v2 matrix dry-run contract 定义
- richer routes / ablation / fusion 的 cell 映射
- v2 matrix dry-run artifact
- acceptance / repeatability / README 收口

### Out of Scope

- full benchmark-scale matrix execution
- 扩回 proxy substrate

## Repository Context

本计划主要衔接：

- `outputs/next_real_experiment_matrix_bootstrap/default/*`
- `outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs/*`
- `src/eval/first_minimal_real_experiment_matrix_dry_run.py`

## Deliverables

- `.plans/066-next-real-experiment-matrix-dry-run.md`
- `src/eval/next_real_experiment_matrix_dry_run.py`
- `src/eval/next_real_experiment_matrix_dry_run_checks.py`
- `scripts/build_next_real_experiment_matrix_dry_run.py`
- `scripts/validate_next_real_experiment_matrix_dry_run.py`
- `next_matrix_dry_run_plan.json`
- `next_matrix_execution_contract.json`
- `next_matrix_readiness_summary.json`
- `next_matrix_dry_run_summary.json`
- `next_matrix_dry_run_registry.json`
- `next_matrix_module_status.json`
- `next_matrix_cell_status.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define v2 matrix dry-run contract
- [x] Milestone 2: run v2 matrix dry-run and emit structured artifacts
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- `next_real_experiment_matrix_v2` 虽然 route 数从 3 扩到了 5，但 materialized inputs 仍然沿用同一份 cutover dataset 和 v6 query contracts，所以 richer coverage 必须通过 cell mapping 而不是新数据源来表达。
- `route_b_only_ablation` 与 `route_c_only_ablation` 最自然的承载方式不是新数据集，而是和 full cell 并列的 ablation cells。

## Decision Log

- 决策：066 把 v2 matrix 映射为 3 个 cells：`full_routes_b_c_fusion`、`route_b_only_ablation`、`route_c_only_ablation`。
  - 原因：这样可以最小成本地把 richer route coverage 变成真实可执行对象，同时把 full cell 与 ablation cell 区分清楚。
  - 影响范围：dry-run contract、cell status、后续 067 execution selection。

## Plan of Work

先复用 062 的 dry-run 骨架，把 v2 matrix definition 从 route list 重写成明确的 cell contract；然后用现有 reasoning / confidence / illumination dry-run probe 做底层 readiness 验证，并把 richer routes 映射到 full cell 与 ablation cells。最后补 validator 和 README，确保 066 可以独立重跑。

## Concrete Steps

1. 新建 `src/eval/next_real_experiment_matrix_dry_run.py` 与校验模块。
2. 新建 `scripts/build_next_real_experiment_matrix_dry_run.py` 与 `scripts/validate_next_real_experiment_matrix_dry_run.py`。
3. 运行 build 脚本生成 `outputs/next_real_experiment_matrix_dry_run/default/`。
4. 再跑一轮 repeat run，并执行 validator。
5. 更新 README 与本计划进度。

## Validation and Acceptance

- `build_next_real_experiment_matrix_dry_run.py --help` 可正常显示
- `validate_next_real_experiment_matrix_dry_run.py --help` 可正常显示
- 至少生成：
  - `next_matrix_dry_run_plan.json`
  - `next_matrix_execution_contract.json`
  - `next_matrix_readiness_summary.json`
  - `next_matrix_dry_run_summary.json`
  - `next_matrix_dry_run_registry.json`
  - `next_matrix_module_status.json`
  - `next_matrix_cell_status.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- dry-run 输出固定落到 `outputs/next_real_experiment_matrix_dry_run/<run_name>/`
- 可以重复运行；重跑时覆盖同名输出目录中的同名文件
- 若中断，可直接重跑 build；validator 只依赖完整 run 目录和 repeat run 目录

## Remaining Risks

- v2 matrix 仍然只包含一个 dataset / model 组合。
- 当前 richer routes 仍然建立在 local curated split 与 lightweight model 上。

## Outcome Summary

- `outputs/next_real_experiment_matrix_dry_run/default/next_matrix_execution_contract.json` 已将 v2 matrix 明确映射为 full cell 与两个 ablation cells。
- `outputs/next_real_experiment_matrix_dry_run/default/next_matrix_dry_run_summary.json` 显示 richer routes 与 ablation cells 已进入 dry-run 层。
- `outputs/next_real_experiment_matrix_dry_run/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 066 完成，下一步应进入 `067-next-real-experiment-matrix-execution`，让 full cell 与新增 ablation cells 真实进入 execution 层。
