# 108 Post Model-Axis 1.5B Analysis

## Purpose / Big Picture

107 已让 `pilot_small_hf -> Qwen/Qwen2.5-1.5B-Instruct` 真正进入本地推理。108 的目标不是比较性能输赢，而是判断这次 1.5B 引入是否已经打开了“模型轴外推性验证入口”，以及下一步应先稳住 1.5B 还是继续扩更大模型。

## Scope

### In Scope

- 对比 lightweight baseline 与 1.5B route_b execution 的 contract / execution / artifact
- 总结 1.5B 当前已打通的部分与剩余 blocker
- 形成下一步 recommendation
- acceptance / README / 收口

### Out of Scope

- 继续 fusion 同轴扩张
- 直接引入 3B / 7B
- 多模型矩阵
- 新训练主线

## Repository Context

- `.plans/107-model-axis-1p5b-minimal-execution.md`
- `outputs/model_axis_1p5b_bootstrap/default/*`
- `outputs/model_axis_1p5b_dry_run/default/*`
- `outputs/model_axis_1p5b_execution/default/*`
- `outputs/rerun_route_b_on_labeled_split_v6/default/*`

## Deliverables

- `.plans/108-post-model-axis-1p5b-analysis.md`
- `src/eval/post_model_axis_1p5b_analysis.py`
- `src/eval/post_model_axis_1p5b_analysis_checks.py`
- `scripts/build_post_model_axis_1p5b_analysis.py`
- `scripts/validate_post_model_axis_1p5b_analysis.py`
- `outputs/model_axis_1p5b_analysis/default/model_axis_1p5b_analysis_summary.json`
- `outputs/model_axis_1p5b_analysis/default/model_axis_1p5b_vs_lightweight_comparison.json`
- `outputs/model_axis_1p5b_analysis/default/model_axis_1p5b_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: compare lightweight baseline and 1.5B execution lineage
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Decision Log

- 决策：108 以 `route_b` 为主比较对象。
  - 原因：107 只执行了一个最小但真实的 1.5B cell，analysis 应忠实围绕这一条已打通路径展开。
- 决策：即使 107 是 `PARTIAL`，仍进入 108。
  - 原因：107 已满足“真读本地 1.5B 权重并进入推理”，已经具备分析模型轴入口是否被打开的价值。

## Validation and Acceptance

- `build_post_model_axis_1p5b_analysis.py --help` 可正常显示
- `validate_post_model_axis_1p5b_analysis.py --help` 可正常显示
- `outputs/model_axis_1p5b_analysis/default/model_axis_1p5b_analysis_summary.json` 已生成
- `outputs/model_axis_1p5b_analysis/default/model_axis_1p5b_next_step_recommendation.json` 已生成
- `outputs/model_axis_1p5b_analysis/repeatability_default/artifact_acceptance.json` 为 `PASS`

## Outcome Summary

- 108 已确认模型轴入口已经真正打开：
  - `Qwen/Qwen2.5-1.5B-Instruct` 本地快照已被接入
  - 1.5B route_b 已真实进入本地推理
- 但当前 1.5B minimal execution 仍以 `PARTIAL_SINGLE_CLASS_LABEL_COLLAPSE` 收口，因此当前价值主要是“证明 contract 可迁移并能执行”，而不是形成稳定可比的 route_b logistic 结果。
- 当前 recommendation 已明确为：
  - `stabilize_model_axis_1p5b_route_b_label_balance`
- repeatability validation 已为 `PASS`。

## Next Suggested Plan

下一步应优先稳住 1.5B 上的 `route_b` 标签可分性，再决定是否扩 `route_c`、`fusion_summary` 或更大模型。
