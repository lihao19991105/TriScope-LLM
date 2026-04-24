# 125 Post Anchor-Aware Route-C Analysis

## Purpose / Big Picture

若 124 已完成，125 的目标是系统比较 original route_c、refined route_c、anchor-aware route_c 三层结果，判断 anchor-aware follow-up 是否真正优于 refined baseline，以及下一步是继续 anchor-aware refinement，还是应回到更保守的 refined baseline。

## Scope

### In Scope

- 对比 116 / 120 / 121 / 123 / 124 的关键 artifact。
- 输出 progression summary / three-way comparison / next-step recommendation。
- 同步 README 恢复点。

### Out of Scope

- 3B / 7B。
- dataset 轴。
- fusion 同轴。
- blind budget expansion。

## Repository Context

- `.plans/120-route-c-refined-candidate-execution.md`
- `.plans/121-route-c-refined-candidate-stability.md`
- `.plans/123-anchor-aware-route-c-refined-followup.md`
- `.plans/124-anchor-aware-route-c-refined-execution.md`
- `outputs/model_axis_1p5b_route_c_execution/default/*`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/*`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/*`

## Deliverables

- `.plans/125-post-route-c-refined-analysis.md`
- `src/eval/post_route_c_anchor_analysis.py`
- `scripts/build_post_route_c_anchor_analysis.py`
- `outputs/model_axis_1p5b_route_c_anchor_analysis/default/route_c_anchor_analysis_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_analysis/default/route_c_original_refined_anchor_comparison.json`
- `outputs/model_axis_1p5b_route_c_anchor_analysis/default/route_c_anchor_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: compare original / refined / anchor-aware route_c
- [x] Milestone 2: recommendation / README / 收口

## Decision Log

- 决策：125 把“是否新增正类支持”和“是否只是通过进一步裁剪负类抬高 density”区分开来。
  - 原因：anchor-aware 路线如果只是更密，但没有新增正类支持，下一步策略会不同。

## Validation and Acceptance

- `python3 scripts/build_post_route_c_anchor_analysis.py --help` 可正常显示。
- summary 必须明确回答：
  - anchor-aware 是否真实优于 refined baseline
  - refined baseline 是否仍是更稳妥工作基线
  - 下一步更该继续 anchor-aware refinement 还是再考虑 budget

## Remaining Risks

- 即便 anchor-aware 更优，也可能仍然只有 1 个正类锚点。
- 如果 124 尚未做稳定性确认，125 的 recommendation 需要把这一点写清楚。

## Outcome Snapshot

- 125 已完成 original / refined / anchor-aware route_c 的三层对比。
- 当前比较结论：
  - original route_c：
    - `density = 1/24 = 0.041666...`
    - `characterization = stable_but_sparse`
  - refined route_c：
    - `density = 1/8 = 0.125`
    - `stability_characterization = better_and_stable`
  - anchor-aware route_c：
    - `density = 1/6 = 0.166666...`
    - `density_gain_vs_refined = 1.333333...`
    - `anchor_adds_new_positive_support = false`
- 当前 recommendation：
  - `confirm_anchor_aware_route_c_stability_before_any_budget_expansion`

## Next Suggested Plan

若 125 recommendation 清晰，可在后续创建 anchor-aware stability / second follow-up plan，但本轮不强求。
