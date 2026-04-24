# 061 Minimal Real Experiment Matrix Bootstrap

## Purpose / Big Picture

060 若已经明确下一步推荐路线，那么 061 的任务就是把“下一轮更像真实实验的最小矩阵”先 bootstrap 起步，而不是停留在分析层。

## Scope

### In Scope

- minimal real-experiment matrix definition
- readiness summary
- materialized matrix inputs
- bootstrap artifact

### Out of Scope

- 直接跑完整真实实验矩阵
- benchmark-scale main run
- 更大模型矩阵

## Repository Context

本计划主要衔接：

- `outputs/post_first_real_experiment_analysis/default/*`
- `outputs/first_real_experiment_execution/default/*`
- `outputs/real_experiment_cutover_bootstrap/default/*`

## Deliverables

- `.plans/061-minimal-real-experiment-matrix-bootstrap.md`
- `src/eval/minimal_real_experiment_matrix_bootstrap.py`
- `scripts/build_minimal_real_experiment_matrix_bootstrap.py`
- `src/eval/minimal_real_experiment_matrix_bootstrap_checks.py`
- `scripts/validate_minimal_real_experiment_matrix_bootstrap.py`
- `minimal_real_experiment_matrix_plan.json`
- `minimal_real_experiment_matrix_definition.json`
- `minimal_real_experiment_matrix_readiness_summary.json`
- `materialized_minimal_real_experiment_matrix/`
- `minimal_real_experiment_input_contract.json`
- `minimal_real_experiment_bootstrap_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define minimal real-experiment matrix
- [x] Milestone 2: materialize matrix inputs and bootstrap artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 当前最值得 bootstrap 的不一定是更大规模，而是更清晰的最小矩阵边界：哪些 dataset / labels / model / routes 已经足够作为下一轮真实实验对象。
- 060 的 recommendation 可以非常轻量地落成 061：当前最小矩阵保持单一 dataset、单一 model，但已经把 `route_b / route_c / fusion_summary` 三条输出期望统一到了同一个真实实验矩阵对象里。

## Decision Log

- 决策：061 只做 minimal matrix bootstrap，不直接执行 full matrix。
  - 原因：当前目标是把下一轮真实实验扩张第一次做成可执行对象，而不是立刻推到重型阶段。
  - 影响范围：matrix definition、materialized inputs、bootstrap summary。

## Plan of Work

先读取 060 recommendation，明确最小真实实验矩阵应该包含哪些 dataset / labels / model / routes。然后输出 matrix plan、definition 与 readiness summary，并 materialize 一份最小矩阵输入。最后补 validator、repeatability 与 README。

## Concrete Steps

1. 实现 `src/eval/minimal_real_experiment_matrix_bootstrap.py` 与配套 CLI / validator。
2. 运行 build CLI 生成 minimal matrix bootstrap artifact。
3. 运行 repeat run 与 validator。
4. 更新 README 与 plan 进度。

## Validation and Acceptance

- `build_minimal_real_experiment_matrix_bootstrap.py --help` 可正常显示
- `validate_minimal_real_experiment_matrix_bootstrap.py --help` 可正常显示
- 至少生成：
  - `minimal_real_experiment_matrix_plan.json`
  - `minimal_real_experiment_matrix_definition.json`
  - `minimal_real_experiment_matrix_readiness_summary.json`
  - `materialized_minimal_real_experiment_matrix/`
  - `minimal_real_experiment_input_contract.json`
  - `minimal_real_experiment_bootstrap_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

061 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 matrix bootstrap 中断，可直接重跑 build CLI。

## Remaining Risks

- minimal matrix 仍然不是完整主实验。
- 当前 matrix 的 label / model / dataset 仍然带有 small-scale cutover 属性。

## Outcome Summary

- `outputs/minimal_real_experiment_matrix_bootstrap/default/minimal_real_experiment_matrix_definition.json` 定义了 dataset=`larger_labeled_split_v6_local_curated_csqa_style`、model=`pilot_distilgpt2_hf`、routes=`route_b/route_c/fusion_summary`。
- `outputs/minimal_real_experiment_matrix_bootstrap/default/minimal_real_experiment_bootstrap_summary.json` 显示 `matrix_name = minimal_real_experiment_matrix_v1`，并已 materialize matrix inputs。
- `outputs/minimal_real_experiment_matrix_bootstrap/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 061 完成，下一步建议基于 `materialized_minimal_real_experiment_matrix/` 进入 first matrix dry-run 或 first matrix execution。
