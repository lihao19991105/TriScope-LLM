# 124 Anchor-Aware Route-C Refined Execution

## Purpose / Big Picture

若 123 已经给出一版值得尝试的 anchor-aware follow-up candidate，124 的目标就是把它真正推进成 1.5B route_c execution，检验它相对 120 refined baseline 是否带来更高的正类密度或更强的可分析性。

## Scope

### In Scope

- 基于 123 的 anchor-aware selection registry 物化 execution inputs。
- 运行真实 1.5B route_c anchor-aware execution。
- 输出 selection / plan / readiness / run summary / metrics / summary / logistic summary。
- 显式比较 anchor-aware density 相对 120 是否提升。

### Out of Scope

- 3B / 7B。
- dataset 轴。
- blind budget expansion。
- 新 proxy substrate。

## Repository Context

- `.plans/123-anchor-aware-route-c-refined-followup.md`
- `.plans/120-route-c-refined-candidate-execution.md`
- `src/eval/model_axis_1p5b_route_c_refined_execution.py`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/*`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/*`
- `outputs/model_axis_1p5b_route_c_stable_portability/default/materialized_route_c_stable_portability_inputs/*`

## Deliverables

- `.plans/124-anchor-aware-route-c-refined-execution.md`
- `src/eval/model_axis_1p5b_route_c_anchor_execution.py`
- `scripts/build_model_axis_1p5b_route_c_anchor_execution.py`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/route_c_anchor_execution_selection.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/route_c_anchor_execution_plan.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/route_c_anchor_execution_readiness_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/route_c_anchor_execution_run_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/route_c_anchor_execution_metrics.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/model_axis_1p5b_route_c_anchor_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/model_axis_1p5b_route_c_anchor_logistic_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define anchor-aware execution path and materialize inputs
- [x] Milestone 2: run 1.5B route_c anchor-aware execution
- [x] Milestone 3: README / 收口

## Decision Log

- 决策：124 只在 123 的 anchor-aware candidate 上做一次最小 execution，而不是重新打开原始 24-contract 全量 selection。
  - 原因：本轮目标是验证 anchor-aware 路线是否真的优于 refined baseline，不是回到 blind expansion。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_anchor_execution.py --help` 可正常显示。
- run summary 必须明确回答：
  - `used_local_weights`
  - `entered_model_inference`
  - `class_balance`
  - `num_rows`
  - `anchor_density`
  - 相对 120 的 density 改变

## Remaining Risks

- 即便 density 提升，正类绝对数也可能仍然只有 1。
- anchor-aware candidate 可能是“更密但更脆”，需要后续单独做稳定性确认。

## Outcome Snapshot

- 124 已完成一次真实 1.5B route_c anchor-aware execution。
- 当前 anchor-aware execution 结果：
  - `summary_status = PASS`
  - `execution_status = FULL_EXECUTE`
  - `used_local_weights = true`
  - `entered_model_inference = true`
  - `class_balance = {label_0: 5, label_1: 1}`
  - `num_rows = 6`
  - `anchor_density = 0.166666...`
  - `density_gain_vs_original = 4.0`
  - `density_gain_vs_refined = 1.333333...`
  - `positive_support_sample_ids = ["csqa-pilot-021__targeted"]`
- 当前结论：
  - anchor-aware execution 真正落地了
  - 它相对 120 refined baseline 的确进一步提高了 density
  - 但新增值仍然来自更聪明的 selection，而不是新增正类锚点

## Next Suggested Plan

若 124 结果清晰，则创建 `.plans/125-post-route-c-refined-analysis.md`。
