# 132 Anchor-Aware Baseline-Preserving Deepening Follow-up

## Purpose / Big Picture

131 已确认 route_c 的 working baseline 是 anchor-aware（1/6）而非 deepened（1/8）。132 的目标是在不破坏 anchor-aware baseline 优势的前提下，构造一版更保守的 baseline-preserving follow-up v2 candidate，并先用 precheck 判断其是否值得进入真实 execution。

## Scope

### In Scope

- 读取 124/126/128/129/130/131 的关键 artifact。
- 明确 anchor-aware baseline 的不可破坏约束。
- 物化 baseline-preserving follow-up v2 candidate。
- 输出 precheck 与 readiness，判断是否值得进入 133 execution。

### Out of Scope

- 3B / 7B。
- blind budget expansion。
- dataset 轴扩张。
- fusion 同轴扩张。

## Repository Context

- `.plans/124-anchor-aware-route-c-refined-execution.md`
- `.plans/126-confirm-anchor-aware-route-c-stability.md`
- `.plans/128-anchor-aware-route-c-selection-deepening-or-budget-decision.md`
- `.plans/129-deepened-route-c-candidate-execution.md`
- `.plans/130-confirm-deepened-route-c-stability.md`
- `.plans/131-post-deepened-route-c-analysis-and-baseline-decision.md`
- `src/eval/model_axis_1p5b_route_c_anchor_followup.py`
- `src/eval/model_axis_1p5b_route_c_anchor_deepening.py`

## Deliverables

- `.plans/132-anchor-aware-baseline-preserving-deepening-followup.md`
- `src/eval/model_axis_1p5b_route_c_anchor_followup_v2.py`
- `scripts/build_model_axis_1p5b_route_c_anchor_followup_v2.py`
- `outputs/model_axis_1p5b_route_c_anchor_followup_v2/default/route_c_anchor_preservation_constraints.json`
- `outputs/model_axis_1p5b_route_c_anchor_followup_v2/default/route_c_anchor_followup_v2_strategy.json`
- `outputs/model_axis_1p5b_route_c_anchor_followup_v2/default/route_c_anchor_followup_v2_selection_registry.json`
- `outputs/model_axis_1p5b_route_c_anchor_followup_v2/default/route_c_anchor_followup_v2_candidate_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_followup_v2/default/route_c_anchor_followup_v2_precheck.json`
- `outputs/model_axis_1p5b_route_c_anchor_followup_v2/default/route_c_anchor_followup_v2_readiness_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define baseline-preserving constraints and materialize follow-up v2 candidate
- [x] Milestone 2: run follow-up v2 precheck and readiness decision
- [x] Milestone 3: acceptance / README / 收口

## Decision Log

- 决策：132 采用 baseline-preserving 的“替换式保守扩厚”，而不是继续增加 base count。
  - 原因：128 的 deepened candidate 从 1/6 回落到 1/8，核心原因是新增了一个仅含负类的 base，使分母从 6 增至 8，而正类仍是 1。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_anchor_followup_v2.py --help` 可正常显示。
- 必须显式回答：
  - 128 为何掉回 1/8。
  - 132 如何避免重复该问题。
  - v2 candidate 是否至少两类。
  - density 是否仍 >= 1/6。
  - 是否值得进入真实 execution。

## Remaining Risks

- 当前正类仍集中于单锚点，baseline-preserving 可能只得到“可执行但无实质增益”的结论。
- 若 v2 只实现 baseline preservation 而无扩展价值，133 需要明确回退条件。

## Outcome Snapshot

- 132 已完成并产出 v2 follow-up artifacts。
- 当前关键结果：
  - `strategy_mode = swap_second_neighbor_for_conservative_probe`
  - `selected_base_ids = [csqa-pilot-021, csqa-pilot-002, csqa-pilot-006]`
  - `row_count = 6`
  - `class_balance = {label_0:5,label_1:1}`
  - `candidate_density = 1/6 = 0.166666...`
  - `density_preserved_vs_anchor = true`
  - `precheck_logistic_pass = true`
  - `worth_executing = true`
- 132 显式记录了 128 掉回 1/8 的原因：新增负类 base 使分母从 6 增至 8，而正类仍为 1。

