# 134 Post Anchor-Aware Baseline-Preserving Analysis

## Purpose / Big Picture

133 已完成 follow-up v2 execution，并给出可用于 baseline 决策的新证据。134 的目标是统一比较 refined / anchor-aware / deepened / anchor-followup-v2 四层 route_c 结果，明确当前 working baseline 是否仍为 anchor-aware。

## Scope

### In Scope

- 聚合 120/124/126/129/130/131/132/133 关键 artifact。
- 输出 v2 比较 summary / comparison / recommendation。
- 明确当前 baseline 决策与下一步入口。

### Out of Scope

- 3B / 7B。
- dataset 轴扩张。
- blind budget expansion。
- fusion 同轴扩张。

## Repository Context

- `.plans/131-post-deepened-route-c-analysis-and-baseline-decision.md`
- `.plans/132-anchor-aware-baseline-preserving-deepening-followup.md`
- `.plans/133-anchor-aware-baseline-preserving-execution.md`
- `src/eval/post_route_c_deepened_analysis.py`
- `outputs/model_axis_1p5b_route_c_deepened_analysis/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_execution_v2/default/*`

## Deliverables

- `.plans/134-post-anchor-aware-baseline-preserving-analysis.md`
- `src/eval/post_route_c_anchor_v2_analysis.py`
- `scripts/build_post_route_c_anchor_v2_analysis.py`
- `outputs/model_axis_1p5b_route_c_anchor_v2_analysis/default/route_c_anchor_v2_analysis_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_v2_analysis/default/route_c_anchor_v2_comparison.json`
- `outputs/model_axis_1p5b_route_c_anchor_v2_analysis/default/route_c_anchor_v2_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: compare refined/anchor/deepened/anchor-v2 and produce progression summary
- [x] Milestone 2: recommendation / README / 收口

## Decision Log

- 决策：134 以 baseline decision 为核心，不把 v2 的单次候选运行自动视为 baseline 升级。
  - 原因：131 已给出 anchor-aware working baseline，134 需要在同一证据标准下比较 v2 新结果。

## Validation and Acceptance

- `python3 scripts/build_post_route_c_anchor_v2_analysis.py --help` 可正常显示。
- 必须显式回答：
  - 当前 working baseline 是 refined / anchor-aware / deepened / anchor-followup-v2 哪个。
  - 下一步应继续受控 deepening，还是保持 anchor-aware baseline。
  - 当前是否进入“局部最优但单锚点”工作态。

## Remaining Risks

- 即使 baseline 决策清晰，正类仍可能长期集中在单锚点，导致扩展空间受限。

## Outcome Snapshot

- 134 已完成四层对比（refined / anchor-aware / deepened / anchor-followup-v2）。
- 当前关键结果：
  - `working_baseline = anchor-aware`
  - `v2_execution_status = PARTIAL`
  - `v2_baseline_preservation_assessment = should_fall_back_to_anchor_baseline`
  - `route_c_local_optimal_single_anchor = true`
- 当前 recommendation：
  - `keep_anchor_aware_baseline_and_only_controlled_micro_deepening`

