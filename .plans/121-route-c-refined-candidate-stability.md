# 121 Route-C Refined Candidate Stability

## Purpose / Big Picture

120 若确认 refined selection 在单次 execution 上确实优于 116，121 的目标就是判断这不是一次性偶然成功，而是轻量复跑下仍保持改进方向的 refined baseline。

## Scope

### In Scope

- 定义 refined stability protocol / success criteria / run plan。
- 在固定 refined subset 上做轻量 1.5B rerun。
- 输出 run registry / JSONL results / summary / comparison CSV。

### Out of Scope

- 3B / 7B。
- dataset 轴。
- full matrix。
- 新训练主线。

## Repository Context

- `.plans/120-route-c-refined-candidate-execution.md`
- `src/eval/model_axis_1p5b_route_c_refined_execution.py`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/*`
- `outputs/model_axis_1p5b_route_c_execution/default/*`

## Deliverables

- `.plans/121-route-c-refined-candidate-stability.md`
- `src/eval/model_axis_1p5b_route_c_refined_stability.py`
- `scripts/build_model_axis_1p5b_route_c_refined_stability.py`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_protocol.json`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_success_criteria.json`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_run_plan.json`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_run_registry.json`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_results.jsonl`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_summary.json`
- `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_comparison.csv`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define refined stability protocol and success criteria
- [x] Milestone 2: run refined stability confirmation and aggregate results
- [x] Milestone 3: README / 收口

## Decision Log

- 决策：121 继承 118 的轻量 rerun 思路，但 success criteria 增加“density 持续高于原始 116”。
  - 原因： refined candidate 的价值不只是继续两类存在，而是要保持改进方向。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_refined_stability.py --help` 可正常显示。
- summary 必须明确回答：refined candidate 是“更好且稳定”，还是“更好但脆弱”。

## Remaining Risks

- refined density 可能稳定提升，但正类绝对数仍然只有 1。
- 当前结论仍受限于 benchmark-truth-leaning proxy 语义。

## Outcome Snapshot

- 121 已完成 3 个轻量 refined rerun 场景（seed=42/43/44）。
- 所有 run 均保持：
  - `used_local_weights=true`
  - `entered_model_inference=true`
  - `class_balance={label_0:7,label_1:1}`
  - `refined_density=0.125`
  - `density_improved_vs_116=true`
  - `logistic PASS`
  - `csqa-pilot-021__targeted` 作为 refined anchor 持续保留
- 当前结论：
  - `stability_established=true`
  - `stability_characterization=better_and_stable`
- 当前结果快照见：
  - `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_summary.json`
  - `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_run_registry.json`
  - `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_results.jsonl`
  - `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_comparison.csv`

## Next Suggested Plan

若 121 结论清晰，创建 `.plans/122-post-route-c-refined-analysis.md`。
