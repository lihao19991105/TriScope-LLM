# 131 Post Deepened Route-C Analysis And Baseline Decision

## Purpose / Big Picture

130 已给出 deepened 稳定性结论。131 的目标是把 original / refined / anchor-aware / deepened 四层结果统一比较，明确当前 route_c 的 working baseline，并给出下一步入口。

## Scope

### In Scope

- 聚合 116 / 120 / 121 / 124 / 126 / 129 / 130 关键 artifact。
- 输出 progression summary / four-way comparison / next-step recommendation。
- 明确当前 working baseline 与后续动作。

### Out of Scope

- 3B / 7B。
- dataset 轴扩张。
- blind budget expansion。
- fusion 同轴扩张。

## Repository Context

- `.plans/126-confirm-anchor-aware-route-c-stability.md`
- `.plans/129-deepened-route-c-candidate-execution.md`
- `.plans/130-confirm-deepened-route-c-stability.md`
- `src/eval/post_route_c_anchor_stability_analysis.py`
- `outputs/model_axis_1p5b_route_c_anchor_stability/default/*`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/*`
- `outputs/model_axis_1p5b_route_c_deepened_stability/default/*`

## Deliverables

- `.plans/131-post-deepened-route-c-analysis-and-baseline-decision.md`
- `src/eval/post_route_c_deepened_analysis.py`
- `scripts/build_post_route_c_deepened_analysis.py`
- `outputs/model_axis_1p5b_route_c_deepened_analysis/default/route_c_deepened_analysis_summary.json`
- `outputs/model_axis_1p5b_route_c_deepened_analysis/default/route_c_original_refined_anchor_deepened_comparison.json`
- `outputs/model_axis_1p5b_route_c_deepened_analysis/default/route_c_deepened_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: build original/refined/anchor/deepened progression summary
- [x] Milestone 2: recommendation / README / 收口

## Surprises & Discoveries

- deepened 的稳定性并不自动等价于 baseline 升级价值；在本轮证据下，anchor-aware 仍是更优工作基线。

## Decision Log

- 决策：131 以 baseline 选择为核心，不以“单次分数波动”作为升级依据。
  - 原因：当前路线重点是稳定且可分析的工作态，而不是追逐一次性高分。

## Plan of Work

先聚合四层 baseline 的 execution/stability 结果，构建统一 comparison。再输出 summary 与 recommendation，明确当前 working baseline 是 anchor-aware 还是 deepened，以及后续是否继续 deepening 或先保持 anchor baseline。

## Concrete Steps

1. 新增 post deepened analysis 模块与 CLI。
2. 运行分析脚本生成 comparison / summary / recommendation。
3. 依据结果更新 README 恢复点和下一步边界。

## Validation and Acceptance

- `python3 scripts/build_post_route_c_deepened_analysis.py --help` 正常显示。
- 必须输出 comparison / summary / recommendation 三个文件。
- 必须明确回答：
  - 当前 working baseline 是 original / refined / anchor-aware / deepened 哪一个
  - 下一步是继续 deepening、保持 anchor-aware baseline，还是才考虑 budget
  - route_c 是否进入更适合分析的稳定工作态

## Idempotence and Recovery

- 可重复运行；同一输出目录会覆盖摘要文件。
- 若中断可直接重跑同一命令恢复。

## Outputs and Artifacts

- `outputs/model_axis_1p5b_route_c_deepened_analysis/default/*`

## Remaining Risks

- deepened 可能长期停留在 refined floor，难以替代 anchor baseline。
- 当前正类支持仍然高度集中于单锚点。

## Outcome Snapshot

- 131 已完成四层 route_c 对比并给出 baseline 决策。
- 当前比较结果：
  - original：`density = 1/24 = 0.041666...`
  - refined：`density = 1/8 = 0.125`（stable）
  - anchor-aware：`density = 1/6 = 0.166666...`（stable）
  - deepened：`density = 1/8 = 0.125`（stable but fallback decision）
- 当前工作结论：
  - `working_baseline = anchor-aware`
  - `recommended_next_step = keep_anchor_aware_baseline_and_only_consider_more_deepening`
  - `route_c_stable_working_state = true`

## Next Suggested Plan

- 若仍保持 anchor baseline，可继续受控 deepening；暂不进入 budget / 3B / 7B / fusion 扩张。