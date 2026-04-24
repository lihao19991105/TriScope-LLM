# 139 Route-C Label Path Consistency Recheck

## Purpose / Big Picture

138 已将 label health gate 做成执行路径能力。139 的目标是复检 precheck 与 execution 的一致性，确认是否从“隐式单类失败”转成“显式 gate 阻断且可解释”。

## Scope

### In Scope

- 输出 recheck protocol、fix applied、readiness。
- 输出 precheck vs execution recheck 对照与指标。
- 给出一致性是否恢复的结论。

### Out of Scope

- 3B / 7B。
- blind budget expansion。
- dataset 轴扩张。
- fusion 同轴扩张。

## Repository Context

- `.plans/138-route-c-label-path-health-gating-and-instrumentation.md`
- `outputs/model_axis_1p5b_route_c_label_health/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_followup_v2/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_execution_recheck/default/*`

## Deliverables

- `.plans/139-route-c-label-path-consistency-recheck.md`
- `src/eval/route_c_label_path_consistency_recheck.py`
- `scripts/build_route_c_label_path_consistency_recheck.py`
- `outputs/model_axis_1p5b_route_c_label_recheck/default/route_c_label_recheck_protocol.json`
- `outputs/model_axis_1p5b_route_c_label_recheck/default/route_c_label_recheck_fix_applied.json`
- `outputs/model_axis_1p5b_route_c_label_recheck/default/route_c_label_recheck_readiness_summary.json`
- `outputs/model_axis_1p5b_route_c_label_recheck/default/route_c_label_recheck_summary.json`
- `outputs/model_axis_1p5b_route_c_label_recheck/default/route_c_precheck_vs_execution_recheck_comparison.json`
- `outputs/model_axis_1p5b_route_c_label_recheck/default/route_c_label_recheck_metrics.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define consistency recheck protocol and fix-applied snapshot
- [x] Milestone 2: run consistency recheck and output comparison/metrics
- [x] Milestone 3: acceptance / README / 收口

## Decision Log

- 决策：139 优先验证“可解释阻断的一致性”，而非追求本轮直接恢复两类。
  - 原因：当前阶段目标是把失败模式从隐式崩溃转为显式、可诊断、可复现。

## Validation and Acceptance

- `python3 scripts/build_route_c_label_path_consistency_recheck.py --help` 可正常显示。
- 必须明确输出：
  - precheck_label_set
  - execution_label_set
  - gate_status
  - consistency_restored

## Remaining Risks

- 即使一致性诊断变清晰，若模型响应继续不可解析，仍无法恢复 execution 两类标签。

## Outcome Snapshot

- 139 已完成一致性复检。
- 当前关键结果：
  - `precheck_label_set = [0,1]`
  - `execution_label_set = [1]`
  - `execution_gate_status = BLOCKED`
  - `consistency_restored = false`
- 当前解释：
  - 路径可解释性已恢复（显式 gate），但两类一致性尚未恢复。

