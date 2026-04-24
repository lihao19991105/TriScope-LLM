# 127 Post Anchor-Aware Route-C Stability Analysis

## Purpose / Big Picture

若 126 已完成，127 的目标是把 original / refined / anchor-aware / anchor-aware-stable 四层结果统一比较，判断当前 anchor-aware 改进到底是稳定优势还是一次性优势，并据此给出下一步 recommendation。

## Scope

### In Scope

- 对比 116 / 120 / 121 / 124 / 126 的关键 artifact。
- 输出 progression summary / comparison / next-step recommendation。
- 同步 README 恢复点。

### Out of Scope

- 3B / 7B。
- blind budget expansion。
- dataset 轴。
- fusion 同轴。

## Repository Context

- `.plans/120-route-c-refined-candidate-execution.md`
- `.plans/121-route-c-refined-candidate-stability.md`
- `.plans/124-anchor-aware-route-c-refined-execution.md`
- `.plans/126-confirm-anchor-aware-route-c-stability.md`
- `outputs/model_axis_1p5b_route_c_execution/default/*`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/*`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_stability/default/*`

## Deliverables

- `.plans/127-post-anchor-aware-route-c-stability-analysis.md`
- `src/eval/post_route_c_anchor_stability_analysis.py`
- `scripts/build_post_route_c_anchor_stability_analysis.py`
- `outputs/model_axis_1p5b_route_c_anchor_stability_analysis/default/route_c_anchor_stability_analysis_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_stability_analysis/default/route_c_refined_vs_anchor_stability_comparison.json`
- `outputs/model_axis_1p5b_route_c_anchor_stability_analysis/default/route_c_anchor_stability_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: compare original / refined / anchor-aware / anchor-aware-stable
- [x] Milestone 2: recommendation / README / 收口

## Decision Log

- 决策：127 重点判断“更密的 anchor-aware 是否已经稳定成立”，而不是只看单次 execution 的 density。
  - 原因：当前是否继续 deepening，取决于 anchor-aware 改进是不是稳定可依赖。

## Validation and Acceptance

- `python3 scripts/build_post_route_c_anchor_stability_analysis.py --help` 可正常显示。
- summary 必须明确回答：
  - anchor-aware 是否真的优于 refined baseline
  - 这种优势是否稳定
  - 下一步更该继续 selection deepening，还是才考虑 budget

## Remaining Risks

- 即便 anchor-aware 稳定，它也可能仍然只围绕 1 个正类锚点工作。
- 下一步 deepening 仍要避免变成隐性 budget expansion。

## Outcome Snapshot

- 127 已完成 original / refined / anchor-aware / anchor-aware-stable 的四层对比。
- 当前比较结论：
  - original route_c：
    - `density = 1/24 = 0.041666...`
    - `characterization = stable_but_sparse`
  - refined route_c：
    - `density = 1/8 = 0.125`
    - `stability_characterization = better_and_stable`
  - anchor-aware route_c：
    - `density = 1/6 = 0.166666...`
    - `anchor_stability_established = true`
    - `anchor_beats_refined_on_density = true`
- 当前 recommendation：
  - `selection_deepening_before_any_budget_expansion`

## Next Suggested Plan

若 127 recommendation 倾向 selection deepening，则创建 `.plans/128-anchor-aware-route-c-selection-deepening-or-budget-decision.md`。
