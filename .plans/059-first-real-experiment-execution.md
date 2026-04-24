# 059 First Real Experiment Execution

## Purpose / Big Picture

058 会证明 `small_real_labeled_csqa_triscope_cutover_v1` 的执行映射已经成立。059 的任务是在这个基础上选择一条最小但真实的执行路径，让第一轮 real-experiment-style execution 真正发生，而不是继续停留在 dry-run。

## Scope

### In Scope

- first executable path selection
- execution input materialization
- first real execution artifact
- acceptance / repeatability / README / 收口

### Out of Scope

- 大规模实验矩阵
- benchmark-grade 结果宣称
- 更大模型 / 更大数据规模

## Repository Context

本计划主要衔接：

- `outputs/real_experiment_first_dry_run/default/*`
- `outputs/real_experiment_cutover_bootstrap/default/*`
- `outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs/*`
- `src/eval/rerun_route_b_on_labeled_split_v6.py`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`

## Deliverables

- `.plans/059-first-real-experiment-execution.md`
- `src/eval/first_real_experiment_execution.py`
- `scripts/build_first_real_experiment_execution.py`
- `src/eval/first_real_experiment_execution_checks.py`
- `scripts/validate_first_real_experiment_execution.py`
- `first_real_execution_selection.json`
- `first_real_execution_plan.json`
- `first_real_execution_readiness_summary.json`
- `first_real_execution_run_summary.json`
- `first_real_execution_registry.json`
- `first_real_execution_outputs/`
- `first_real_route_b_summary.json`
- `first_real_route_c_summary.json`
- `first_real_fusion_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: select first executable path and materialize inputs
- [x] Milestone 2: run first real execution and emit artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 当前仓库里已经有稳定的 route B / route C execution函数，因此 059 的关键不是重新实现 route logic，而是把这些稳定链路包成 first real-experiment execution 对象。
- 只要 route B 与 route C 都能在同一个 cutover contract 上重跑，059 就已经比 readiness-only 阶段前进了一大步。
- 实际结果表明两条 route 都能在同一个 cutover envelope 下 full execute，而 fusion 可以先以 integrated cross-route summary 的方式诚实落地，不需要在第一轮真实执行里就强行引入更重的 classifier path。

## Decision Log

- 决策：059 优先选择“最小但真实”的执行路径，而不是追求一口气 full matrix。
  - 原因：当前更需要 first execution existence，而不是更重的覆盖面。
  - 影响范围：selection、execution registry、后续分析。

## Plan of Work

先读取 058 的 module status，确认哪些链路可以 full execute。然后选择最小但收益最大的 first executable path，并 materialize execution inputs。接着真正运行 route B / route C，并在两者都成功时生成一个 honest 的 fusion-level execution summary。最后补 validator、repeatability 与 README。

## Concrete Steps

1. 实现 `src/eval/first_real_experiment_execution.py` 与配套 CLI / validator。
2. 运行 build CLI 生成 first execution artifact。
3. 运行 repeat run 与 validator。
4. 更新 README 与 plan 进度。

## Validation and Acceptance

- `build_first_real_experiment_execution.py --help` 可正常显示
- `validate_first_real_experiment_execution.py --help` 可正常显示
- 至少生成：
  - `first_real_execution_selection.json`
  - `first_real_execution_plan.json`
  - `first_real_execution_readiness_summary.json`
  - `first_real_execution_run_summary.json`
  - `first_real_execution_registry.json`
  - `first_real_execution_outputs/`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

059 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 first execution 中断，可直接重跑 build CLI。

## Remaining Risks

- 即使 059 成功，当前结果仍然不是 benchmark 主实验。
- first execution 仍可能包含 honest fallback 或 partial fusion，而不是完整论文级 execution matrix。

## Outcome Summary

- `outputs/first_real_experiment_execution/default/first_real_execution_run_summary.json` 显示 `executed_layers = ["route_b", "route_c", "fusion_summary"]`。
- `outputs/first_real_experiment_execution/default/first_real_execution_metrics.json` 显示 `route_b_rows = 70`、`route_c_rows = 140`、`shared_base_samples = 70`。
- `outputs/first_real_experiment_execution/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 059 完成，下一步建议创建 `.plans/060-post-first-real-experiment-analysis.md`，分析 first execution 到底成立到什么程度，以及下一轮应该优先补什么。
