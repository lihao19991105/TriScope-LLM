# 115 Rerun Model-Axis 1.5B Route-C Stable Portability Precheck

## Purpose / Big Picture

114 已证明 route_c 在真实 1.5B labeled scan 下可以构造出非单类 candidate。115 的目标是把这一修复真正接回 route_c portability precheck：用稳定化后的 selection 与 robust label parsing，修复 113 的 `PRECHECK_FAILED`，把 route_c 推进到可作为 minimal execution 前置门槛的状态。

## Scope

### In Scope

- 选择 stabilized route_c portability path。
- materialize 修复后的 route_c portability 输入。
- 用 robust truth-leaning label parsing 真实 rerun route_c portability precheck。
- 输出新的 run / module / cell 状态与 readiness。

### Out of Scope

- 3B / 7B 扩展。
- fusion 同轴扩张。
- route_c 全量大规模执行。

## Repository Context

- `.plans/114-stabilize-model-axis-1p5b-route-c-label-balance.md`
- `src/eval/model_axis_1p5b_route_c_stabilization.py`
- `src/eval/model_axis_1p5b_route_c_portability.py`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`
- `src/fusion/benchmark_truth_leaning_label.py`
- `outputs/model_axis_1p5b_route_c_stabilization/default/*`

## Deliverables

- `.plans/115-rerun-model-axis-1p5b-route-c-stable-portability-precheck.md`
- `src/eval/model_axis_1p5b_route_c_stable_portability.py`
- `scripts/build_model_axis_1p5b_route_c_stable_portability.py`
- `outputs/model_axis_1p5b_route_c_stable_portability/default/route_c_stable_portability_selection.json`
- `outputs/model_axis_1p5b_route_c_stable_portability/default/route_c_stable_portability_plan.json`
- `outputs/model_axis_1p5b_route_c_stable_portability/default/route_c_stable_portability_readiness_summary.json`
- `outputs/model_axis_1p5b_route_c_stable_portability/default/route_c_stable_portability_run_summary.json`
- `outputs/model_axis_1p5b_route_c_stable_portability/default/route_c_stable_portability_module_status.json`
- `outputs/model_axis_1p5b_route_c_stable_portability/default/route_c_stable_portability_cell_status.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define stabilized route_c portability path and readiness
- [x] Milestone 2: rerun stabilized route_c portability precheck and emit status artifacts
- [ ] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：115 直接复用 114 选出的 balanced base ids，而不是重新发明另一套 selection。
  - 原因：114 已用真实 1.5B labeled scan 证明这是最小可行双类入口。
- 决策：115 用 robust prefix-aware parser 进入 route_c truth-leaning label construction。
  - 原因：这是 113 单类塌缩的已确认直接修复点。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_stable_portability.py --help` 可正常显示。
- run_summary 明确回答：class_balance 是否已至少两类、precheck 是否已 PASS / PASS_WITH_LIMITATIONS、是否 ready_run。

## Remaining Risks

- 即便 115 通过，route_c 仍可能在更小预算或不同 seed 下重新接近单类边界。
- 1.5B route_c 即使通过 precheck，也不自动等于可稳定推广到更大矩阵。

## Outcome Snapshot

- 115 已把 113 的 `PRECHECK_FAILED` 修复为 `PASS_WITH_LIMITATIONS`。
- 当前稳定 precheck 结果为：
  - `used_local_weights = true`
  - `entered_model_inference = true`
  - `label_parse_mode = robust_prefix`
  - `class_balance = {label_0: 23, label_1: 1}`
  - `route_c_logistic_summary.summary_status = PASS`
- 当前 gate 结果：
  - `ready_run = true`
  - route_c 已不再卡在 contract / readiness / parser 层，而是进入“可执行但正类仍极稀疏”的状态。
- 115 的最直接恢复入口：
  - `outputs/model_axis_1p5b_route_c_stable_portability/default/route_c_stable_portability_run_summary.json`
  - `outputs/model_axis_1p5b_route_c_stable_portability/default/route_c_stable_portability_module_status.json`
  - `outputs/model_axis_1p5b_route_c_stable_portability/default/materialized_route_c_stable_portability_inputs/`

## Next Suggested Plan

若 115 明确 `ready_run=true` 且已有最小 executable candidate，则创建 `.plans/116-model-axis-1p5b-route-c-minimal-execution.md` 并推进 route_c minimal execution。
