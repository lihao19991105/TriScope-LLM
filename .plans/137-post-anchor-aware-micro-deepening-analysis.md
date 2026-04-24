# 137 Post Anchor-Aware Micro-Deepening Analysis

## Purpose / Big Picture

136 产出 micro-deepening 执行证据后，137 的目标是统一比较 refined / anchor-aware / deepened / anchor-v2 / micro 五层结果，明确 route_c 当前 working baseline 与下一步动作。

## Scope

### In Scope

- 聚合 131/134/135/136 关键产物。
- 输出 micro analysis summary / comparison / recommendation。
- 明确 baseline 是否更新。

### Out of Scope

- 3B / 7B。
- blind budget expansion。
- dataset 轴扩张。
- fusion 同轴扩张。

## Repository Context

- `.plans/134-post-anchor-aware-baseline-preserving-analysis.md`
- `.plans/135-diagnose-anchor-aware-v2-label-collapse.md`
- `.plans/136-anchor-aware-micro-deepening-stable-execution.md`
- `outputs/model_axis_1p5b_route_c_anchor_v2_analysis/default/*`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/*`

## Deliverables

- `.plans/137-post-anchor-aware-micro-deepening-analysis.md`
- `src/eval/post_route_c_micro_analysis.py`
- `scripts/build_post_route_c_micro_analysis.py`
- `outputs/model_axis_1p5b_route_c_micro_analysis/default/route_c_micro_analysis_summary.json`
- `outputs/model_axis_1p5b_route_c_micro_analysis/default/route_c_anchor_vs_micro_comparison.json`
- `outputs/model_axis_1p5b_route_c_micro_analysis/default/route_c_micro_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: compare anchor-aware/v2/micro evidence and produce baseline decision
- [x] Milestone 2: recommendation / README / 收口

## Decision Log

- 决策：137 以 baseline decision 为核心，不将 micro 路径默认视为升级。
  - 原因：当前核心目标是稳定可分析，而非激进扩厚。

## Validation and Acceptance

- `python3 scripts/build_post_route_c_micro_analysis.py --help` 可正常显示。
- 必须显式回答：
  - 当前 working baseline。
  - micro 是否解决 labels collapse。
  - 下一步是否继续 micro 修复或保持 anchor baseline。

## Remaining Risks

- 若 labels path 仍不稳定，route_c 可能长期停留在单锚点局部最优态。

## Outcome Snapshot

- 137 已完成 anchor-aware/v2/micro 统一比较。
- 当前关键结果：
  - `working_baseline = anchor-aware`
  - `micro_summary_status = BLOCKED`
  - `micro_deepening_assessment = still_label_fragile`
  - `labels_collapse_avoided = false`
- 当前 recommendation：
  - `keep_anchor_aware_baseline_and_fix_label_path_before_next_micro_attempt`

