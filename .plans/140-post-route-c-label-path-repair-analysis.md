# 140 Post Route-C Label Path Repair Analysis

## Purpose / Big Picture

139 完成一致性复检后，140 的目标是统一比较 135/137 与 138/139 的结论，明确 route_c 下一步应继续 gate-first 修复，还是回到受保护 execution 尝试。

## Scope

### In Scope

- 汇总 collapse diagnosis、micro decision、label health gating、consistency recheck。
- 输出修复后分析 summary / comparison / recommendation。
- 明确 working baseline 与下一步 guarded path。

### Out of Scope

- 3B / 7B。
- blind budget expansion。
- dataset 轴扩张。
- fusion 同轴扩张。

## Repository Context

- `.plans/135-diagnose-anchor-aware-v2-label-collapse.md`
- `.plans/137-post-anchor-aware-micro-deepening-analysis.md`
- `.plans/138-route-c-label-path-health-gating-and-instrumentation.md`
- `.plans/139-route-c-label-path-consistency-recheck.md`

## Deliverables

- `.plans/140-post-route-c-label-path-repair-analysis.md`
- `src/eval/post_route_c_label_path_repair_analysis.py`
- `scripts/build_post_route_c_label_path_repair_analysis.py`
- `outputs/model_axis_1p5b_route_c_label_repair_analysis/default/route_c_label_repair_analysis_summary.json`
- `outputs/model_axis_1p5b_route_c_label_repair_analysis/default/route_c_label_repair_vs_collapse_comparison.json`
- `outputs/model_axis_1p5b_route_c_label_repair_analysis/default/route_c_label_repair_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: compare collapse-era and repair-era evidence
- [x] Milestone 2: recommendation / README / 收口

## Decision Log

- 决策：140 首先判断“失败模式是否已从不可见转为可见可控”，再决定是否恢复 execution 尝试。
  - 原因：当前阶段核心是路径可信度，而非立即提升分数。

## Validation and Acceptance

- `python3 scripts/build_post_route_c_label_path_repair_analysis.py --help` 可正常显示。
- 必须明确回答：
  - label path 是否仍是主阻塞。
  - working baseline 是否变化。
  - 下一步是继续修 path 还是恢复 guarded execution。

## Remaining Risks

- 即使 gate 可解释，若模型输出仍持续退化，短期仍无法恢复两类 execution。

## Outcome Snapshot

- 140 已完成修复后分析与 recommendation。
- 当前关键结果：
  - `working_baseline = anchor-aware`
  - `label_path_still_primary_blocker = true`
  - `label_health_gate_status = BLOCKED`
  - `consistency_restored = false`
- 当前 recommendation：
  - `continue_label_path_instrumentation_and_parser_repair_before_next_execution_attempt`

