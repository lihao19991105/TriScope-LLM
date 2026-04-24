# 122 Post Route-C Refined Analysis

## Purpose / Big Picture

若 120/121 已经完成，122 的目标就是系统比较原始 route_c execution 与 refined candidate execution，判断 refined selection 是否已经把 route_c 推到了“更适合分析”的版本，以及下一步是继续 refined selection 还是再考虑 budget expansion。

## Scope

### In Scope

- 对比 116 / 118 / 120 / 121 的 route_c execution / stability artifact。
- 输出 progression summary / original-vs-refined comparison / next-step recommendation。
- 同步 README 恢复点。

### Out of Scope

- 3B / 7B。
- dataset 轴。
- fusion 同轴。
- 新 proxy substrate。

## Repository Context

- `.plans/116-model-axis-1p5b-route-c-minimal-execution.md`
- `.plans/118-confirm-model-axis-1p5b-route-c-stability.md`
- `.plans/120-route-c-refined-candidate-execution.md`
- `.plans/121-route-c-refined-candidate-stability.md`
- `outputs/model_axis_1p5b_route_c_execution/default/*`
- `outputs/model_axis_1p5b_route_c_stability/default/*`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/*`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/*`

## Deliverables

- `.plans/122-post-route-c-refined-analysis.md`
- `src/eval/post_route_c_refined_analysis.py`
- `scripts/build_post_route_c_refined_analysis.py`
- `outputs/model_axis_1p5b_route_c_refined_analysis/default/route_c_refined_analysis_summary.json`
- `outputs/model_axis_1p5b_route_c_refined_analysis/default/route_c_original_vs_refined_comparison.json`
- `outputs/model_axis_1p5b_route_c_refined_analysis/default/route_c_refined_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: compare original vs refined route_c execution/stability
- [x] Milestone 2: recommendation / README / 收口

## Decision Log

- 决策：122 重点评估 density、稳定性和可分析性，不把“分数高低”当核心目标。
  - 原因：当前 route_c 的研究价值主要在于从 sparse route_c 推进到 analyzable route_c。

## Validation and Acceptance

- `python3 scripts/build_post_route_c_refined_analysis.py --help` 可正常显示。
- summary 必须明确回答：refined selection 是否真实优于原始 execution，以及下一步该继续 refined selection 还是回到 budget。

## Remaining Risks

- 即便 refined baseline 更好，当前 route_c 仍然是 thin positive-support regime。
- 下一步若继续 refinement，仍需避免过度围绕单个 anchor 过拟合。

## Outcome Snapshot

- 122 已完成原始 route_c 与 refined route_c 的 progression 对比。
- 当前比较结论：
  - 原始 route_c：
    - `class_balance = {label_0: 23, label_1: 1}`
    - `density = 1/24 = 0.041666...`
    - `stability_characterization = stable_but_sparse`
  - refined route_c：
    - `class_balance = {label_0: 7, label_1: 1}`
    - `density = 1/8 = 0.125`
    - `stability_characterization = better_and_stable`
  - `density_gain_ratio = 3.0`
- 当前 recommendation：
  - `continue_refined_selection_before_any_budget_expansion`
- 关键结果见：
  - `outputs/model_axis_1p5b_route_c_refined_analysis/default/route_c_refined_analysis_summary.json`
  - `outputs/model_axis_1p5b_route_c_refined_analysis/default/route_c_original_vs_refined_comparison.json`
  - `outputs/model_axis_1p5b_route_c_refined_analysis/default/route_c_refined_next_step_recommendation.json`

## Next Suggested Plan

若 122 recommendation 明确，可在后续创建 refined route_c follow-up execution / refinement plan，但本轮不强求。
