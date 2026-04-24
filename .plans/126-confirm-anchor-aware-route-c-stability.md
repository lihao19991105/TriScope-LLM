# 126 Confirm Anchor-Aware Route-C Stability

## Purpose / Big Picture

124 已经把 anchor-aware route_c 推进到真实 1.5B execution，并把 density 从 refined baseline 的 `1/8` 提高到 `1/6`。126 的目标是确认这不是一次性偶然成功，而是在轻量复跑 / 小扰动下仍保持“更高密度 + 至少两类 + execution/logistic 继续成立”的稳定路径。

## Scope

### In Scope

- 读取 123/124/125 的关键 artifact。
- 定义 anchor-aware stability protocol / success criteria / run plan。
- 在固定 anchor-aware subset 上做轻量 rerun。
- 输出 run registry / JSONL results / summary / comparison CSV。

### Out of Scope

- 3B / 7B。
- dataset 轴。
- blind budget expansion。
- 新 proxy substrate。

## Repository Context

- `.plans/123-anchor-aware-route-c-refined-followup.md`
- `.plans/124-anchor-aware-route-c-refined-execution.md`
- `.plans/125-post-route-c-refined-analysis.md`
- `src/eval/model_axis_1p5b_route_c_anchor_execution.py`
- `outputs/model_axis_1p5b_route_c_anchor_followup/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_analysis/default/*`

## Deliverables

- `.plans/126-confirm-anchor-aware-route-c-stability.md`
- `src/eval/model_axis_1p5b_route_c_anchor_stability.py`
- `scripts/build_model_axis_1p5b_route_c_anchor_stability.py`
- `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_protocol.json`
- `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_success_criteria.json`
- `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_run_plan.json`
- `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_run_registry.json`
- `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_results.jsonl`
- `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_comparison.csv`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define anchor-aware stability protocol and success criteria
- [x] Milestone 2: run anchor-aware stability confirmation and aggregate results
- [x] Milestone 3: README / 收口

## Decision Log

- 决策：126 继承 121 的轻量 rerun 结构，但 success criteria 升级为“anchor density 不能退回 refined baseline 的 1/8”。
  - 原因：当前 anchor-aware 的价值就在于它比 refined baseline 更密，如果复跑后退回 1/8，就不能算稳定增益。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_anchor_stability.py --help` 可正常显示。
- summary 必须明确回答：
  - `all_two_classes`
  - `all_logistic_pass`
  - `anchor_density_preserved_all_runs`
  - `reference_anchor_preserved_all_runs`
  - 当前 anchor-aware 是“better_and_stable”，还是“denser_but_fragile”

## Remaining Risks

- anchor-aware 路线即便稳定，也可能仍然只有同一个正类锚点。
- 若 rerun 结果分化，下一步就不能直接继续 deepening，必须先回到更保守基线。

## Outcome Snapshot

- 126 已完成 3 个轻量 anchor-aware rerun 场景（seed=42/43/44）。
- 所有 run 均保持：
  - `used_local_weights=true`
  - `entered_model_inference=true`
  - `class_balance={label_0:5,label_1:1}`
  - `anchor_density=1/6=0.166666...`
  - `density_not_worse_than_refined_floor=true`
  - `reference_anchor_preserved=true`
  - `logistic PASS`
- 当前结论：
  - `stability_established=true`
  - `stability_characterization=better_and_stable`
- 当前结果快照见：
  - `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_summary.json`
  - `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_run_registry.json`
  - `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_results.jsonl`
  - `outputs/model_axis_1p5b_route_c_anchor_stability/default/route_c_anchor_stability_comparison.csv`

## Next Suggested Plan

若 126 结果清晰，则创建 `.plans/127-post-anchor-aware-route-c-stability-analysis.md`。
