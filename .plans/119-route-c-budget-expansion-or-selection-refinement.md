# 119 Route-C Budget Expansion Or Selection Refinement

## Purpose / Big Picture

若 117/118 已经明确 route_c 当前“可执行但正类过稀”，119 的目标不是立刻再跑一轮 full execution，而是先用结构化比较决定：下一步到底更应该先扩 budget，还是先改 selection。

## Scope

### In Scope

- 比较 budget expansion 与 selection refinement 两条路线。
- 给出当前资源约束下更优的 route_c 稀疏修复建议。
- 若条件允许，额外生成一版最小 refined/expanded candidate summary，供后续 execution 使用。

### Out of Scope

- 3B / 7B。
- dataset 轴。
- fusion 同轴。
- 新训练主线。

## Repository Context

- `.plans/117-analyze-model-axis-1p5b-route-c-sparsity.md`
- `.plans/118-confirm-model-axis-1p5b-route-c-stability.md`
- `outputs/model_axis_1p5b_route_c_sparsity/default/*`
- `outputs/model_axis_1p5b_route_c_stability/default/*`

## Deliverables

- `.plans/119-route-c-budget-expansion-or-selection-refinement.md`
- `src/eval/model_axis_1p5b_route_c_refinement.py`
- `scripts/build_model_axis_1p5b_route_c_refinement.py`
- `outputs/model_axis_1p5b_route_c_refinement/default/route_c_refinement_options_comparison.json`
- `outputs/model_axis_1p5b_route_c_refinement/default/route_c_refinement_recommendation.json`
- 若条件允许：
  - `outputs/model_axis_1p5b_route_c_refinement/default/route_c_refined_candidate_summary.json`
  - 或 `outputs/model_axis_1p5b_route_c_refinement/default/route_c_expanded_budget_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: compare budget expansion vs selection refinement
- [x] Milestone 2: materialize one minimal refinement-oriented candidate summary
- [x] Milestone 3: README / 收口

## Decision Log

- 决策：119 先做路线比较，再决定是否 materialize 一版最小增强。
  - 原因：当前 route_c 的关键不是“立刻多跑一点”，而是避免把大量负类继续堆进来。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_refinement.py --help` 可正常显示。
- comparison 与 recommendation 必须明确回答：当前更该先扩 budget，还是先改 selection。

## Remaining Risks

- 当前即便生成 refined candidate，也还没有自动完成下一次 execution。
- selection refinement 若过度收缩，可能让结论更依赖单个正类 anchor。

## Outcome Snapshot

- 119 已明确比较两条路线：
  - `budget_expansion`：在当前 140-contract 宇宙里预期主要新增负类，不是当前最优
  - `selection_refinement`：不能创造新正类，但能保留唯一正类 anchor 并提高正类密度
- 当前 recommendation：
  - `recommended_next_step = selection_refinement_first`
- 已 materialize 一版最小 refined candidate：
  - `selected_base_count = 4`
  - `selected_contract_count = 8`
  - `class_balance = {label_0: 7, label_1: 1}`
  - `refined_positive_density = 0.125`
- 关键结果见：
  - `outputs/model_axis_1p5b_route_c_refinement/default/route_c_refinement_options_comparison.json`
  - `outputs/model_axis_1p5b_route_c_refinement/default/route_c_refinement_recommendation.json`
  - `outputs/model_axis_1p5b_route_c_refinement/default/route_c_refined_selection_registry.json`
  - `outputs/model_axis_1p5b_route_c_refinement/default/route_c_refined_candidate_summary.json`

## Next Suggested Plan

若 119 recommendation 明确，可在后续创建 route_c refined execution / route_c expanded-budget execution 计划，但本轮不强求。
