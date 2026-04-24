# 138 Route-C Label Path Health Gating And Instrumentation

## Purpose / Big Picture

当前 route_c 的核心阻塞是 labels path 在 execution 中不可观测地塌缩。138 的目标是把标签解析健康度指标、gate 规则、详细诊断输出做成可复用执行能力，并完成一次真实 gated check。

## Scope

### In Scope

- 定义 label health schema / gate definition / instrumentation plan。
- 对当前 route_c 执行产物运行一次 health instrumentation 与 gate check。
- 输出 summary、详细行、gate result、failure modes。

### Out of Scope

- 3B / 7B。
- blind budget expansion。
- dataset 轴扩张。
- fusion 同轴扩张。

## Repository Context

- `.plans/135-diagnose-anchor-aware-v2-label-collapse.md`
- `.plans/136-anchor-aware-micro-deepening-stable-execution.md`
- `src/fusion/benchmark_truth_leaning_label.py`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`

## Deliverables

- `.plans/138-route-c-label-path-health-gating-and-instrumentation.md`
- `src/eval/route_c_label_health_gating.py`
- `scripts/build_route_c_label_health_gating.py`
- `outputs/model_axis_1p5b_route_c_label_health/default/route_c_label_health_schema.json`
- `outputs/model_axis_1p5b_route_c_label_health/default/route_c_label_health_gate_definition.json`
- `outputs/model_axis_1p5b_route_c_label_health/default/route_c_label_health_instrumentation_plan.json`
- `outputs/model_axis_1p5b_route_c_label_health/default/route_c_label_health_summary.json`
- `outputs/model_axis_1p5b_route_c_label_health/default/route_c_label_health_detailed_rows.jsonl`
- `outputs/model_axis_1p5b_route_c_label_health/default/route_c_label_health_gate_result.json`
- `outputs/model_axis_1p5b_route_c_label_health/default/route_c_label_health_failure_modes.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define label health schema / gate / instrumentation
- [x] Milestone 2: run instrumentation and output gate results
- [x] Milestone 3: acceptance / README / 收口

## Decision Log

- 决策：先做最小核心修复，把 health gate 直接接入 route_c 执行路径，再做外层汇总脚本。
  - 原因：确保后续任意 execution 都能在一致位置给出可跑/阻断依据。

## Validation and Acceptance

- `python3 scripts/build_route_c_label_health_gating.py --help` 可正常显示。
- 必须落盘并明确：
  - parsed_option_count / ratio
  - punct_only_count / ratio
  - missing_option_count / ratio
  - label_set
  - health_gate_status
  - blocked_reason

## Remaining Risks

- 若模型输出持续不可解析，health gate 会稳定阻断，短期仍无法进入 full execution。

## Outcome Snapshot

- 138 已完成 schema/gate/instrumentation 产物与真实 gated check。
- 当前关键结果：
  - `route_c_v6_label_health_gate_result.json` 已在 execution 路径落盘。
  - gate 为 `BLOCKED`，并显式给出阻断原因。
  - `parsed_option_count = 0`
  - `missing_option_ratio = 1.0`
  - `punct_only_ratio = 1.0`
  - `class_balance = {label_0:0,label_1:6}`
- 本阶段价值：
  - failures 由“后置 logistic 报错”转为“前置 gate 阻断 + 可解释诊断”。

