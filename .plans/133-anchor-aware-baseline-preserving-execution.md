# 133 Anchor-Aware Baseline-Preserving Execution

## Purpose / Big Picture

132 已构造并预检通过 follow-up v2 candidate。133 的目标是将该 candidate 真实推进到 1.5B route_c execution，判断它属于 baseline_preserved_and_extended、baseline_preserved_but_no_extension，还是 should_fall_back_to_anchor_baseline。

## Scope

### In Scope

- 定义 follow-up v2 execution selection / plan / readiness。
- 运行 1.5B route_c follow-up v2 execution。
- 输出 run summary / metrics / logistic summary / density comparison。
- 明确回退条件与 baseline 判断。

### Out of Scope

- 3B / 7B。
- dataset 轴扩张。
- blind budget expansion。
- fusion 同轴扩张。

## Repository Context

- `.plans/132-anchor-aware-baseline-preserving-deepening-followup.md`
- `.plans/124-anchor-aware-route-c-refined-execution.md`
- `.plans/129-deepened-route-c-candidate-execution.md`
- `src/eval/model_axis_1p5b_route_c_anchor_execution.py`
- `src/eval/model_axis_1p5b_route_c_deepened_execution.py`

## Deliverables

- `.plans/133-anchor-aware-baseline-preserving-execution.md`
- `src/eval/model_axis_1p5b_route_c_anchor_execution_v2.py`
- `scripts/build_model_axis_1p5b_route_c_anchor_execution_v2.py`
- `outputs/model_axis_1p5b_route_c_anchor_execution_v2/default/route_c_anchor_execution_v2_selection.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution_v2/default/route_c_anchor_execution_v2_plan.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution_v2/default/route_c_anchor_execution_v2_readiness_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution_v2/default/route_c_anchor_execution_v2_run_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution_v2/default/route_c_anchor_execution_v2_metrics.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution_v2/default/model_axis_1p5b_route_c_anchor_v2_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution_v2/default/model_axis_1p5b_route_c_anchor_v2_logistic_summary.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution_v2/default/route_c_anchor_execution_v2_positive_support_breakdown.json`
- `outputs/model_axis_1p5b_route_c_anchor_execution_v2/default/route_c_anchor_execution_v2_density_comparison.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define follow-up v2 execution path and readiness artifacts
- [x] Milestone 2: run 1.5B route_c follow-up v2 execution
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 133 首轮执行暴露了一个环境兼容问题：`illumination_probe` 使用 `dtype` 传参给 `from_pretrained`，在当前 transformers 版本下会失败。
- 修复为 `torch_dtype` 后，v2 执行继续推进到融合/标签阶段，最终在 logistic 前置检查处出现单类问题（labels stage）。

## Decision Log

- 决策：133 复用 124/129 的稳定 execution 骨架，仅替换输入来源为 132 v2 registry。
  - 原因：当前目标是验证 baseline-preserving 候选价值，不是重写稳定执行流程。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_anchor_execution_v2.py --help` 可正常显示。
- run summary 必须显式回答：
  - `used_local_weights`
  - `entered_model_inference`
  - `class_balance`
  - `num_rows`
  - `num_predictions`
  - `density_vs_anchor`
  - `density_vs_refined`
  - `reference_anchor_preserved`
  - `baseline_preservation_assessment`

## Remaining Risks

- v2 可能只能证明 baseline 可保持，无法证明实质扩展价值。
- 若无增益，应明确回退到 anchor-aware baseline，避免误判为升级。

## Outcome Snapshot

- 133 已完成 1.5B follow-up v2 execution 流程。
- 当前关键结果：
  - `summary_status = PARTIAL`
  - `execution_status = PARTIAL`
  - `failure_stage = labels`
  - `failure_reason = Benchmark-truth-leaning dataset must contain at least two classes.`
  - `baseline_preservation_assessment = should_fall_back_to_anchor_baseline`
- 当前结论：
  - v2 尚未形成 baseline 升级证据；应回退并保持 anchor-aware working baseline。

