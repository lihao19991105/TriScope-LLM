# 123 Anchor-Aware Route-C Refined Follow-up

## Purpose / Big Picture

122 已经把 route_c 推到 refined working baseline，但当前唯一稳定正类锚点仍然只有 `csqa-pilot-021__targeted`。123 的目标是围绕这个锚点做一轮更克制的 anchor-aware follow-up：不盲扩 budget、不打开新轴，而是分析锚点邻域、挑选最接近该锚点的负类，判断是否能在不破坏稳定性的前提下进一步提高正类密度或至少找到更值得执行的 follow-up candidate。

## Scope

### In Scope

- 读取 120/121/122 的 refined execution / stability / analysis artifact。
- 分析 `csqa-pilot-021__targeted` 的 anchor profile 与邻域负类。
- 物化一版 anchor-aware follow-up candidate。
- 在不跑 full execution 的前提下做轻量 precheck，判断是否值得进入 124。

### Out of Scope

- 3B / 7B。
- fusion 同轴扩张。
- proxy substrate 扩容。
- blind budget expansion。
- dataset 轴扩张。

## Repository Context

- `.plans/120-route-c-refined-candidate-execution.md`
- `.plans/121-route-c-refined-candidate-stability.md`
- `.plans/122-post-route-c-refined-analysis.md`
- `src/eval/model_axis_1p5b_route_c_execution.py`
- `src/eval/model_axis_1p5b_route_c_refined_execution.py`
- `outputs/model_axis_1p5b_route_c_execution/default/*`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/*`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/*`
- `outputs/model_axis_1p5b_route_c_refined_analysis/default/*`

## Deliverables

- `.plans/123-anchor-aware-route-c-refined-followup.md`
- `src/eval/model_axis_1p5b_route_c_anchor_followup.py`
- `scripts/build_model_axis_1p5b_route_c_anchor_followup.py`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_profile.json`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_neighbor_analysis.json`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_selection_strategy.json`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_followup_selection_registry.json`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_followup_candidate_dataset.jsonl`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_followup_candidate_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_followup_precheck.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: analyze anchor neighborhood and define anchor-aware selection strategy
- [x] Milestone 2: materialize follow-up candidate and run light precheck
- [x] Milestone 3: README / 收口

## Decision Log

- 决策：123 不打开新样本宇宙，先只在 116 的原始 24-contract route_c execution 宇宙里做 anchor-aware refinement。
  - 原因：当前用户明确禁止 blind budget expansion，本轮更需要验证“围绕唯一正类锚点的更聪明 selection”有没有价值。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_anchor_followup.py --help` 可正常显示。
- candidate summary / precheck 必须明确回答：
  - 新 candidate 的 row_count / class_balance
  - 相对 120 refined baseline 的 density 变化
  - 是否值得进入真实 execution

## Remaining Risks

- anchor-aware follow-up 很可能仍然无法创造第二个正类，只能在保持同一正类锚点的前提下继续压缩负类。
- 如果候选集过小，后续 execution 虽然更密，但也可能更脆。

## Outcome Snapshot

- 123 已完成一次真实 anchor-aware follow-up materialization。
- 当前 anchor-aware candidate 结果：
  - `anchor_base_sample_id = csqa-pilot-021`
  - `selected_neighbor_base_ids = ["csqa-pilot-002", "csqa-pilot-005"]`
  - `selected_contract_count = 6`
  - `class_balance = {label_0: 5, label_1: 1}`
  - `anchor_followup_density = 1/6 = 0.166666...`
  - `density_gain_vs_refined = 1.333333...`
  - `precheck_logistic_pass = true`
  - `worth_executing = true`
- 当前结论：
  - anchor-aware follow-up 没有产生新增正类支持
  - 但它在保持同一正类锚点的前提下，把 density 从 refined baseline 的 `1/8` 进一步抬高到了 `1/6`

## Next Suggested Plan

若 123 precheck 表明该 follow-up candidate 值得进入真实 execution，则创建 `.plans/124-anchor-aware-route-c-refined-execution.md`。
