# 120 Route-C Refined Candidate Execution

## Purpose / Big Picture

119 已经说明：在当前 1.5B route_c 宇宙里，盲目扩 budget 不如先沿唯一正类 anchor 做 selection refinement。120 的目标就是把这版 refined candidate 从“paper plan / candidate summary”推进成真实 1.5B route_c execution，并验证它相对于 116 的原始 24-contract execution 是否真的提高了正类密度和可分析性。

## Scope

### In Scope

- 基于 119 的 refined selection registry 物化 refined execution inputs。
- 运行真实 1.5B route_c refined execution。
- 输出 refined execution selection / plan / readiness / run summary / metrics / summary / logistic summary。
- 显式比较 refined density 相对 116 是否提升。

### Out of Scope

- 3B / 7B。
- fusion 同轴。
- dataset 轴。
- 大规模 budget expansion。

## Repository Context

- `.plans/119-route-c-budget-expansion-or-selection-refinement.md`
- `src/eval/model_axis_1p5b_route_c_execution.py`
- `src/eval/model_axis_1p5b_route_c_stable_portability.py`
- `outputs/model_axis_1p5b_route_c_execution/default/*`
- `outputs/model_axis_1p5b_route_c_refinement/default/*`
- `outputs/model_axis_1p5b_route_c_stable_portability/default/materialized_route_c_stable_portability_inputs/*`

## Deliverables

- `.plans/120-route-c-refined-candidate-execution.md`
- `src/eval/model_axis_1p5b_route_c_refined_execution.py`
- `scripts/build_model_axis_1p5b_route_c_refined_execution.py`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/route_c_refined_execution_selection.json`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/route_c_refined_execution_plan.json`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/route_c_refined_execution_readiness_summary.json`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/route_c_refined_execution_run_summary.json`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/route_c_refined_execution_metrics.json`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/model_axis_1p5b_route_c_refined_summary.json`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/model_axis_1p5b_route_c_refined_logistic_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define refined execution path and materialize refined inputs
- [x] Milestone 2: run 1.5B route_c refined execution and compare density vs 116
- [x] Milestone 3: README / 收口

## Decision Log

- 决策：120 不重写 route_c pipeline，只在 115 的 stabilized inputs 上再裁出 119 的 refined base subset。
  - 原因：这样可以最大限度复用已稳定的 1.5B route_c contract，减少新变量。
- 决策：120 的 success criterion 包含“density 相对 116 提升”，而不是只要能跑。
  - 原因：本轮的价值就在于验证 refined selection 是否真的改善 route_c 的分析条件。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_refined_execution.py --help` 可正常显示。
- 必须输出 refined selection / plan / readiness / run summary / metrics / refined summary / refined logistic summary。
- summary 必须明确回答：两类是否保留、density 是否高于原始 1/24、是否继续 FULL_EXECUTE。

## Remaining Risks

- refined selection 仍然依赖单一正类 anchor，可能提升密度但不增加正类绝对数。
- 即便 refined execution 成功，也还不自动等于 refined candidate 稳定。

## Outcome Snapshot

- 120 已完成一次真实 1.5B route_c refined execution。
- 当前 refined execution 结果：
  - `summary_status = PASS`
  - `execution_status = FULL_EXECUTE`
  - `used_local_weights = true`
  - `entered_model_inference = true`
  - `class_balance = {label_0: 7, label_1: 1}`
  - `num_rows = 8`
  - `refined_density = 0.125`
  - `density_gain_vs_original = 3.0`
- 当前 refined execution 仍保留同一正类 anchor：
  - `csqa-pilot-021__targeted`
- 关键结果见：
  - `outputs/model_axis_1p5b_route_c_refined_execution/default/route_c_refined_execution_run_summary.json`
  - `outputs/model_axis_1p5b_route_c_refined_execution/default/route_c_refined_execution_metrics.json`
  - `outputs/model_axis_1p5b_route_c_refined_execution/default/model_axis_1p5b_route_c_refined_summary.json`
  - `outputs/model_axis_1p5b_route_c_refined_execution/default/model_axis_1p5b_route_c_refined_logistic_summary.json`

## Next Suggested Plan

若 120 确认 refined density 提升且 execution 继续成立，创建 `.plans/121-route-c-refined-candidate-stability.md`。
