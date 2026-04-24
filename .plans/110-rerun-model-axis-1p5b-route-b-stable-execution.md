# 110 Rerun Model-Axis 1.5B Route-B Stable Execution

## Purpose / Big Picture

109 已通过 precheck 将 route_b candidate 从单类恢复为双类（30/2），满足 logistic 两类前置条件。110 的目标是在真实本地 1.5B 推理下执行 stabilized route_b rerun，验证 logistic 不再因单类标签塌缩而阻塞。

## Scope

### In Scope

- 定义 stabilized route_b execution 选择与可执行性说明。
- 真实 rerun 1.5B route_b（本地权重、本地推理）并输出稳定化执行产物。
- 诚实记录 full/partial/fallback、class_balance、logistic pass/fail。

### Out of Scope

- 3B / 7B 模型切换。
- fusion 轴扩张。
- 新训练主线。
- dataset / substrate 扩容。

## Repository Context

- `.plans/109-stabilize-model-axis-1p5b-route-b-label-balance.md`
- `src/eval/model_axis_1p5b_execution.py`
- `src/eval/rerun_route_b_on_labeled_split_v6.py`
- `outputs/model_axis_1p5b_route_b_stabilization/default/*`

## Deliverables

- `.plans/110-rerun-model-axis-1p5b-route-b-stable-execution.md`
- `src/eval/model_axis_1p5b_route_b_stable_execution.py`
- `scripts/build_model_axis_1p5b_route_b_stable_execution.py`
- `outputs/model_axis_1p5b_route_b_stable_execution/default/route_b_stable_execution_selection.json`
- `outputs/model_axis_1p5b_route_b_stable_execution/default/route_b_stable_execution_plan.json`
- `outputs/model_axis_1p5b_route_b_stable_execution/default/route_b_stable_execution_readiness_summary.json`
- `outputs/model_axis_1p5b_route_b_stable_execution/default/route_b_stable_execution_run_summary.json`
- `outputs/model_axis_1p5b_route_b_stable_execution/default/route_b_stable_execution_metrics.json`
- `outputs/model_axis_1p5b_route_b_stable_execution/default/route_b_stable_summary.json`
- `outputs/model_axis_1p5b_route_b_stable_execution/default/route_b_stable_logistic_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define stabilized route_b execution path and readiness artifacts
- [x] Milestone 2: run true 1.5B stabilized rerun and produce execution artifacts
- [ ] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：110 继续使用 107 的最小 route_b contract，不扩 route_c/fusion。
  - 原因：当前核心目标是去除单类阻塞并证明 1.5B route_b 可稳定可分析。
- 决策：110 在 route_b 标签构造阶段引入最小稳定化（解析规则修复），而不改动探针主体与 fusion 对齐 contract。
  - 原因：保持可比性并降低回归风险。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_b_stable_execution.py --help` 可正常显示。
- `used_local_weights = true` 且 `entered_model_inference = true`。
- `route_b_stable_summary` 显示至少两类标签。
- `route_b_stable_logistic_summary.summary_status = PASS`。

## Remaining Risks

- 即使通过两类前置条件，类别不平衡仍可能导致指标不稳定。
- illumination 输出格式后续若再次变化，需要继续监控解析稳定性。

## Outcome Snapshot

- `used_local_weights=true`、`entered_model_inference=true` 已在 110 run summary 中确认。
- `execution_status=FULL_EXECUTE`，`route_b_stable_summary.class_balance={label_0:30,label_1:2}`。
- `route_b_stable_logistic_summary.summary_status=PASS`，单类阻塞已解除。

## Next Suggested Plan

若 110 成功，下一步创建 `.plans/111-post-stabilized-model-axis-1p5b-analysis.md`，做 lightweight/107/110 对比分析。
