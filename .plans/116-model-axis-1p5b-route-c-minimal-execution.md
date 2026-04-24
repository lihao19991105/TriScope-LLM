# 116 Model-Axis 1.5B Route-C Minimal Execution

## Purpose / Big Picture

若 115 已把 route_c portability precheck 从单类塌缩推进到可通过状态，则 116 的目标是完成 1.5B 下 route_c 的第一次最小 execution，证明 route_c 不再只是 portability/bootstrap 对象，而是真正进入本地 1.5B execution 语义。

## Scope

### In Scope

- 选择 first executable route_c cell。
- materialize route_c minimal execution 输入。
- 运行 1.5B route_c minimal execution。
- 输出 execution summary / metrics / route_c summary / logistic summary。

### Out of Scope

- 3B / 7B 扩展。
- 多模型矩阵。
- dataset 轴扩张。

## Repository Context

- `.plans/115-rerun-model-axis-1p5b-route-c-stable-portability-precheck.md`
- `src/eval/model_axis_1p5b_route_c_stable_portability.py`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`
- `outputs/model_axis_1p5b_route_c_stable_portability/default/*`

## Deliverables

- `.plans/116-model-axis-1p5b-route-c-minimal-execution.md`
- `src/eval/model_axis_1p5b_route_c_execution.py`
- `scripts/build_model_axis_1p5b_route_c_execution.py`
- `outputs/model_axis_1p5b_route_c_execution/default/route_c_execution_selection.json`
- `outputs/model_axis_1p5b_route_c_execution/default/route_c_execution_plan.json`
- `outputs/model_axis_1p5b_route_c_execution/default/route_c_execution_readiness_summary.json`
- `outputs/model_axis_1p5b_route_c_execution/default/route_c_execution_run_summary.json`
- `outputs/model_axis_1p5b_route_c_execution/default/route_c_execution_metrics.json`
- `outputs/model_axis_1p5b_route_c_execution/default/model_axis_1p5b_route_c_summary.json`
- `outputs/model_axis_1p5b_route_c_execution/default/model_axis_1p5b_route_c_logistic_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define the smallest real 1.5B route_c execution path
- [x] Milestone 2: run route_c minimal execution and emit execution artifacts
- [ ] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：116 默认复用 115 已稳定的 route_c portability subset，而不是重新抽样。
  - 原因：当前目标是先证明 route_c 可以进入真实 execution，而不是再开一轮 selection 变量。
- 决策：116 仍保持 robust prefix-aware label parsing。
  - 原因：这是 route_c 在 1.5B 下已确认的必要修复，不应回退到 113 的 strict parser。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_execution.py --help` 可正常显示。
- run_summary 明确回答：used_local_weights / entered_model_inference / class_balance / execution_status。

## Remaining Risks

- 即便 116 成功，当前 route_c 仍可能因正类极少而只达到 “可执行但边界脆弱” 的状态。
- route_c minimal execution 成功不代表 route_c 全量稳定。

## Outcome Snapshot

- 116 已完成 1.5B route_c 的第一次最小 execution。
- 当前 execution 结果为：
  - `summary_status = PASS`
  - `execution_status = FULL_EXECUTE`
  - `used_local_weights = true`
  - `entered_model_inference = true`
  - `class_balance = {label_0: 23, label_1: 1}`
  - `num_rows = 24`
  - `num_predictions = 24`
- 当前最关键的诚实结论：
  - route_c 已真实进入本地 1.5B execution 语义
  - 但正类仍然只有 `1/24`，所以当前更像“execution 已成立、统计边界仍脆弱”，而不是“route_c 已完全稳定”

## Next Suggested Plan

若 116 成功，可追加一份轻量 analysis / recommendation 产物，但本轮不自动扩到 3B / 7B 或 dataset 轴。
