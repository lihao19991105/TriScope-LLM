# 107 Model-Axis-1.5B Minimal Execution

## Purpose / Big Picture

106 已把 `pilot_small_hf -> Qwen/Qwen2.5-1.5B-Instruct` 推进到 `ready_local / ready_run`。107 的目标是在不扩成多模型矩阵的前提下，完成第一次真实的 1.5B 本地 minimal execution，并证明当前 real-experiment matrix contract 不只属于 `pilot_distilgpt2_hf`。

## Scope

### In Scope

- 选择一个最小但真实的 1.5B executable cell
- materialize 一份低成本 execution 输入
- 复用现有 route B 执行语义跑 1.5B 本地推理
- execution summary / metrics / acceptance / README

### Out of Scope

- 3B / 7B 模型扩张
- 多模型矩阵
- route C / fusion 全矩阵 execution
- 新训练主线

## Repository Context

- `.plans/106-model-axis-1p5b-dry-run.md`
- `outputs/model_axis_1p5b_dry_run/default/*`
- `outputs/model_axis_1p5b_bootstrap/default/*`
- `outputs/rerun_route_b_on_labeled_split_v6/default/*`
- `src/eval/rerun_route_b_on_labeled_split_v6.py`

## Deliverables

- `.plans/107-model-axis-1p5b-minimal-execution.md`
- `src/eval/model_axis_1p5b_execution.py`
- `src/eval/model_axis_1p5b_execution_checks.py`
- `scripts/build_model_axis_1p5b_execution.py`
- `scripts/validate_model_axis_1p5b_execution.py`
- `outputs/model_axis_1p5b_execution/default/model_axis_1p5b_execution_selection.json`
- `outputs/model_axis_1p5b_execution/default/model_axis_1p5b_execution_plan.json`
- `outputs/model_axis_1p5b_execution/default/model_axis_1p5b_execution_readiness_summary.json`
- `outputs/model_axis_1p5b_execution/default/model_axis_1p5b_execution_run_summary.json`
- `outputs/model_axis_1p5b_execution/default/model_axis_1p5b_execution_metrics.json`
- `outputs/model_axis_1p5b_execution/default/model_axis_1p5b_route_b_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: select first executable 1.5B cell and materialize execution inputs
- [x] Milestone 2: run 1.5B minimal execution
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：107 默认选择 `route_b` 作为 first executable cell。
  - 原因：它已经在 105/106 中被明确为最小 executable candidate，并且比 route_c / fusion 更小、更直接。
- 决策：107 允许先用一份克制的 route_b 子集执行，再在必要时 fallback 到更大的 route_b 子集。
  - 原因：既满足“最小 execution”，又避免因为单类标签导致 route_b logistic 无法完成。

## Validation and Acceptance

- `build_model_axis_1p5b_execution.py --help` 可正常显示
- `validate_model_axis_1p5b_execution.py --help` 可正常显示
- `outputs/model_axis_1p5b_execution/default/model_axis_1p5b_execution_run_summary.json` 已生成
- `outputs/model_axis_1p5b_execution/default/model_axis_1p5b_execution_metrics.json` 已生成
- `outputs/model_axis_1p5b_execution/repeatability_default/artifact_acceptance.json` 为 `PASS`

## Outcome Summary

- `route_b` 已作为 first executable cell 真正进入 1.5B 本地推理。
- `pilot_small_hf -> Qwen/Qwen2.5-1.5B-Instruct` 已真实读到本地权重，`used_local_weights = true`、`entered_model_inference = true`。
- 107 当前以 `PARTIAL_SINGLE_CLASS_LABEL_COLLAPSE` 收口：
  - 三路 probe 和 fusion 对齐都已完成
  - route_b dataset 已真实落盘
  - 但当前 32-row minimal execution 的 more-natural 标签分布塌成单类，导致 logistic fitting 被诚实阻塞
- repeatability validation 已为 `PASS`。

## Next Suggested Plan

进入 108，对 lightweight baseline 与 1.5B 的 contract / execution / artifact 做模型轴分析，并判断下一步应先稳住 1.5B route_b 标签可分性，还是再扩 route_c / 更大模型。
