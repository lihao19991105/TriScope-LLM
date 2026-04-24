# 136 Anchor-Aware Micro-Deepening Stable Execution

## Purpose / Big Picture

135 已解释 133 labels collapse 主因。136 的目标是按 recovery plan 形成更保守的 micro-deepening candidate，并用 live label gate 判断是否可进入 execution，避免再次出现 precheck-pass 但 labels-collapse。

## Scope

### In Scope

- 定义 micro-deepening strategy / selection / readiness。
- 基于 live label gate 做 execution 决策。
- 输出 run summary / metrics / density 与 positive support 对比。

### Out of Scope

- 3B / 7B。
- blind budget expansion。
- dataset 轴扩张。
- fusion 同轴扩张。

## Repository Context

- `.plans/135-diagnose-anchor-aware-v2-label-collapse.md`
- `outputs/model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_execution_recheck/default/*`

## Deliverables

- `.plans/136-anchor-aware-micro-deepening-stable-execution.md`
- `src/eval/model_axis_1p5b_route_c_micro_deepening.py`
- `scripts/build_model_axis_1p5b_route_c_micro_deepening.py`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/route_c_micro_deepening_strategy.json`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/route_c_micro_deepening_selection_registry.json`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/route_c_micro_deepening_candidate_summary.json`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/route_c_micro_deepening_readiness_summary.json`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/route_c_micro_deepening_run_summary.json`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/route_c_micro_deepening_metrics.json`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/model_axis_1p5b_route_c_micro_summary.json`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/model_axis_1p5b_route_c_micro_logistic_summary.json`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/route_c_micro_deepening_density_comparison.json`
- `outputs/model_axis_1p5b_route_c_micro_deepening/default/route_c_micro_positive_support_breakdown.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define micro-deepening strategy and readiness
- [x] Milestone 2: run or block execution via live label gate and output execution artifacts
- [x] Milestone 3: acceptance / README / 收口

## Decision Log

- 决策：136 先引入 live label gate，再决定是否运行 full execution。
  - 原因：135 已确认当前主要失败点在 labels path，不应盲目重复执行。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_micro_deepening.py --help` 可正常显示。
- run summary 必须显式回答：
  - `used_local_weights`
  - `entered_model_inference`
  - `class_balance`
  - `num_rows`
  - `labels_collapse_avoided`
  - `micro_deepening_assessment`

## Remaining Risks

- 若当前运行时普遍产生不可解析响应，micro 路线仍可能被 live gate 阻断。

## Outcome Snapshot

- 136 已完成 micro-deepening strategy 与 execution gate 判定。
- 当前关键结果：
  - `ready_for_execution = false`
  - `live_label_gate.parsed_option_count = 0`
  - `live_label_gate.missing_option_ratio = 1.0`
  - `live_label_gate.recheck_class_balance = {label_0:0,label_1:6}`
  - `run_summary_status = BLOCKED`
  - `failure_stage = labels_precheck_gate`
  - `micro_deepening_assessment = still_label_fragile`
- 结论：
  - 在当前运行时证据下，micro 路线未通过 live label gate，不应进入盲目 full execution。

