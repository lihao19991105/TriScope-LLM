# 128 Anchor-Aware Route-C Selection Deepening or Budget Decision

## Purpose / Big Picture

若 127 已明确 anchor-aware 路线成立，128 的目标就是在不 blind 扩 budget 的前提下，明确下一轮 route_c 更该做 anchor-aware deepening，还是才考虑更大 budget，并尽量物化一版 deepened candidate 供后续 execution 复用。

## Scope

### In Scope

- 比较 deepening vs budget。
- 输出 comparison / recommendation。
- 若条件允许，物化一版最小 deepened candidate。

### Out of Scope

- 3B / 7B。
- full execution rerun。
- dataset 轴扩张。
- 新 proxy substrate。

## Repository Context

- `.plans/123-anchor-aware-route-c-refined-followup.md`
- `.plans/124-anchor-aware-route-c-refined-execution.md`
- `.plans/126-confirm-anchor-aware-route-c-stability.md`
- `.plans/127-post-anchor-aware-route-c-stability-analysis.md`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_stability/default/*`

## Deliverables

- `.plans/128-anchor-aware-route-c-selection-deepening-or-budget-decision.md`
- `src/eval/model_axis_1p5b_route_c_anchor_deepening.py`
- `scripts/build_model_axis_1p5b_route_c_anchor_deepening.py`
- `outputs/model_axis_1p5b_route_c_anchor_deepening/default/route_c_anchor_deepening_options_comparison.json`
- `outputs/model_axis_1p5b_route_c_anchor_deepening/default/route_c_anchor_deepening_recommendation.json`
- `outputs/model_axis_1p5b_route_c_anchor_deepening/default/route_c_anchor_deepened_candidate_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_deepening/default/route_c_anchor_deepened_selection_registry.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: compare selection deepening vs budget
- [x] Milestone 2: materialize a minimal deepened candidate if warranted
- [x] Milestone 3: README / 收口

## Decision Log

- 决策：128 不做 blind budget expansion，而是先判断 deepening 是否还能保持不低于 refined baseline 的 density floor。
  - 原因：当前预算扩张的诚实性仍然很弱，而 selection deepening 至少可以复用已知 anchor-aware 邻域。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_anchor_deepening.py --help` 可正常显示。
- recommendation 必须明确回答：
  - 该继续 deepening 还是才考虑 budget
  - 依据是什么
  - 如物化 deepened candidate，其 density floor 是否仍高于或不低于 refined baseline

## Remaining Risks

- deepening candidate 很可能牺牲当前 1/6 的 density，换取更厚但更稀的 working slice。
- 若 deepening 后 density 立即掉回原始 sparse regime，则说明当前 anchor-aware 路线不适合再继续扩。

## Outcome Snapshot

- 128 已完成 selection deepening vs budget comparison，并物化一版最小 deepened candidate。
- 当前比较结论：
  - `recommended_next_step = selection_deepening_first`
  - blind budget expansion 仍不推荐
  - 当前 deepened candidate：
    - `selected_base_count = 4`
    - `selected_contract_count = 8`
    - `class_balance = {label_0:7,label_1:1}`
    - `deepened_density = 1/8 = 0.125`
    - `density_vs_anchor = 0.75`
    - `density_vs_refined_floor = 1.0`
- 当前结果快照见：
  - `outputs/model_axis_1p5b_route_c_anchor_deepening/default/route_c_anchor_deepening_options_comparison.json`
  - `outputs/model_axis_1p5b_route_c_anchor_deepening/default/route_c_anchor_deepening_recommendation.json`
  - `outputs/model_axis_1p5b_route_c_anchor_deepening/default/route_c_anchor_deepened_selection_registry.json`
  - `outputs/model_axis_1p5b_route_c_anchor_deepening/default/route_c_anchor_deepened_candidate_summary.json`

## Next Suggested Plan

若 128 recommendation 仍偏向 deepening，可在后续创建 deepened candidate execution / stability plan，但本轮不强求。
