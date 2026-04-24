# 117 Analyze Model-Axis 1.5B Route-C Sparsity

## Purpose / Big Picture

116 已证明 1.5B route_c 已经进入真实 minimal execution，但当前 `class_balance = {label_0: 23, label_1: 1}`，正类极稀。117 的目标不是继续盲目扩 budget，而是先把这 1/24 的正类到底来自 selection、budget、parser、threshold、模型输出还是 truth-leaning label 机制拆清楚，为后续 stability 或 refinement 提供依据。

## Scope

### In Scope

- 读取 114/115/116 的 route_c stabilization / stable portability / execution artifact。
- 建立 route_c 稀疏性诊断框架并形成可验证假设。
- 输出稀疏性分析 summary / positive support breakdown / label distribution CSV / recommendation。
- 若结论清晰，为 118 或 119 提供明确输入。

### Out of Scope

- 3B / 7B 模型切换。
- fusion 同轴扩张。
- proxy substrate / dataset 轴扩容。
- 大规模新 execution。

## Repository Context

- `.plans/114-stabilize-model-axis-1p5b-route-c-label-balance.md`
- `.plans/115-rerun-model-axis-1p5b-route-c-stable-portability-precheck.md`
- `.plans/116-model-axis-1p5b-route-c-minimal-execution.md`
- `src/eval/model_axis_1p5b_route_c_stabilization.py`
- `src/eval/model_axis_1p5b_route_c_stable_portability.py`
- `src/eval/model_axis_1p5b_route_c_execution.py`
- `outputs/model_axis_1p5b_route_c_stabilization/default/*`
- `outputs/model_axis_1p5b_route_c_stable_portability/default/*`
- `outputs/model_axis_1p5b_route_c_execution/default/*`

## Deliverables

- `.plans/117-analyze-model-axis-1p5b-route-c-sparsity.md`
- `src/eval/model_axis_1p5b_route_c_sparsity.py`
- `scripts/build_model_axis_1p5b_route_c_sparsity.py`
- `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_sparsity_hypotheses.json`
- `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_sparsity_diagnosis_protocol.json`
- `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_sparsity_signal_sources.json`
- `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_sparsity_analysis_summary.json`
- `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_positive_support_breakdown.json`
- `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_label_distribution_by_sample.csv`
- `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_sparsity_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: establish sparsity diagnosis hypotheses/protocol/signal sources
- [x] Milestone 2: run sparsity analysis and emit summary / breakdown / recommendation
- [x] Milestone 3: README / 收口

## Decision Log

- 决策：117 优先基于现有 114/115/116 artifact 做聪明分析，而不是先跑更大 execution。
  - 原因：当前问题是“解释稀疏”，不是“先堆更多负类样本”。
- 决策：117 明确比较 parser / selection / budget / threshold / model-behavior / truth-leaning label 机制。
  - 原因：需要把历史上的 parser 问题与当前真实稀疏主因分开。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_sparsity.py --help` 可正常显示。
- 产物目录包含 hypotheses/protocol/signal_sources/summary/breakdown/distribution/recommendation。
- summary 必须明确回答：当前稀疏主要是 selection 问题、budget 问题，还是模型/label 机制问题。

## Remaining Risks

- 当前分析主要基于已有 24-contract execution 和 140-contract full scan，仍受限于本地 pilot slice。
- 即便能解释“为什么稀疏”，也不自动等于 route_c 已经统计稳定。

## Outcome Snapshot

- 117 已确认：parser 不再是当前主因；selection 决定了是否能拿到正类，但 1.5B route_c 在当前 140-contract 可见宇宙里本身就只暴露出 1 个正类支持点。
- 当前最合理结论是：route_c 属于“sparse but analyzable”，下一步应先确认这唯一正类支持点是否稳定存在，再决定是否做 budget expansion 或 selection refinement。
- 关键结果见：
  - `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_sparsity_analysis_summary.json`
  - `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_positive_support_breakdown.json`
  - `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_label_distribution_by_sample.csv`
  - `outputs/model_axis_1p5b_route_c_sparsity/default/route_c_sparsity_next_step_recommendation.json`

## Next Suggested Plan

若 117 recommendation 倾向 stability，创建 `.plans/118-confirm-model-axis-1p5b-route-c-stability.md`。
