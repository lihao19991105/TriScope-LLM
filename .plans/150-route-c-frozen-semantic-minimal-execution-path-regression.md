# 150 Route-C Frozen Semantic Minimal Execution-Path Regression

## Background

148 已收口 recoverable boundary，149 又在冻结语义与 gate 不变的前提下完成了小规模 suite-level regression validation。149 的结论是：

- recoverable boundary positives 全部继续 `pass_formatted_to_parser`；
- normal guardrails 全部继续 `pass_raw_to_parser`；
- nonrecoverable guardrails 全部继续 `degeneration_blocked`；
- 所有样例都与 148 frozen reference 一致。

因此 150 的任务不再是 helper-level 对错，而是把这套已验证规则挂到一条最小 execution-path 上，确认它在真实 label-path / gate / continuation 语义下仍然稳定成立。

## Why 149 enables execution-path regression validation

- 149 已冻结了一组小而精的 regression 样例，可直接作为 path-level regression seed。
- 148/149 已证明规则修正聚焦在 recoverable boundary，而不是更广泛的 parser 扩张。
- 因此 150 不需要新 replay，不需要新 prompt family，也不需要大预算，只需要把这些样例挂到最小 execution-path 上，验证 path-level 副作用是否仍为零。

## Frozen semantic / gate / rule scope

150 冻结以下边界：

- benchmark truth 语义不变；
- gate 阈值与 PASS/BLOCKED 定义不变；
- anti-degradation 规则保持 148 当前版本；
- 不增加 formatter 范围；
- 不改模型轴、不扩 budget、不引入新 prompt family；
- 只允许复用既有 execution-path 组件：
  - `build_benchmark_truth_leaning_dataset`
  - `build_route_c_label_health_gating`
  - 必要时最小 logistic continuation check

## Goal

在一个最小、受控、可回放的 execution-path 场景中验证：

- recoverable formatting boundary 在 execution-path 上继续正确 handoff 到 parser；
- normal path 继续不被误伤；
- nonrecoverable path 继续稳定 blocked；
- parser / gate / label health / continuation 语义与 148/149 的 suite-level 结论保持一致。

最终输出单一 150 verdict 与唯一 next-step recommendation。

## Non-goals

- 不修改 benchmark truth 语义。
- 不修改 gate 阈值或 PASS/BLOCKED 定义。
- 不扩模型轴、budget、prompt family、attack family、dataset 轴。
- 不做时间分离 replay 或大批量 rerun。
- 不把 150 做成 execution-path 大重构。

## Minimal execution-path validation design

150 的最小 execution-path regression set 由三类路径组成：

1. `recoverable_execution_path`
   - 复用 149 中最有代表性的 recoverable positives：
     - plain code fence
     - language-tagged code fence
     - 1~2 条轻 wrapper baseline

2. `normal_execution_guardrail`
   - 复用 149 中的 2 条 real parser-reachable guardrail

3. `nonrecoverable_execution_guardrail`
   - 复用 149 中的 real punct-collapse + near-boundary wrapped nonrecoverable cases

执行路径最小化为：

- 物化 minimal labeled illumination raw results
- 物化最小 fusion dataset substrate
- 运行 `build_benchmark_truth_leaning_dataset`
- 运行 `build_route_c_label_health_gating`
- gate 通过时补一轮最小 logistic continuation check

## Path-level regression criteria

1. `recoverable path`
   - case 应映射到 `selected_parser_source = normalized`
   - 不允许回退到 `response_option_missing = true`
   - 不允许语义猜测

2. `normal path`
   - case 应保持 `selected_parser_source = raw`
   - 不允许新增误伤或额外 anti-degradation 过拦截

3. `nonrecoverable path`
   - case 应保持 `response_option_missing = true`
   - gate / parser handoff 不得误放

4. `path-level consistency`
   - path-level handoff 必须与 149 frozen reference 一致
   - gate 必须保持可解释
   - logistic continuation 只在 gate 允许时发生

## Validation plan

1. 从 149 regression details 中抽取 minimal execution-path set。
2. 复用既有 route_c raw-result 模板与 fusion feature substrate，构建一个最小 synthetic execution root。
3. 运行：
   - `build_benchmark_truth_leaning_dataset`
   - `build_route_c_label_health_gating`
   - `run_benchmark_truth_leaning_logistic`（仅在 gate PASS 时）
4. 对每个 case 记录：
   - frozen suite reference
   - current path-level selected parser source / missing / parse failure / ground_truth_label
   - gate-consistency outcome
5. 生成 suite / rules / summary / details / report / post-analysis。

## Risks

- 150 仍是最小 execution-path，不等于完整 probe rerun 或长期稳定性验证。
- synthetic execution root 虽然复用真实 substrate 字段，但本质上仍是受控最小样例集。
- 如果 continuation check 过强，可能把 150 拉向“大实验”；因此 logistic 只作为最小 continuation health check。

## Milestones

- [x] M1: minimal execution-path regression set and criteria frozen
- [x] M2: minimal execution-path validation completed
- [x] M3: single verdict and single recommendation completed

## Completion Notes

- 150 物化了 8 条 minimal execution-path regression cases：
  - recoverable = 3
  - normal = 2
  - nonrecoverable = 3
- path-level summary 为 `PASS`：
  - `recoverable_path_pass_rate = 1.0`
  - `normal_path_pass_rate = 1.0`
  - `nonrecoverable_path_block_rate = 1.0`
  - `gate_status = PASS`
  - `logistic_status = PASS`
- 全部 cases 与 149 frozen reference 一致：
  - `mismatch_type_counts = {match: 8}`
- 150 的 final verdict 为：
  - `Minimal execution-path regression validated`
- 150 的唯一 next-step recommendation 为：
  - `进入冻结语义与 gate 不变前提下的最小真实 execution 验证线`

## Exit criteria

- 150 plan 文件完整且可恢复。
- execution-path regression suite / rules / summary / details / report / verdict / recommendation 七类 artifacts 齐全。
- 覆盖来源与 path 类型清楚。
- path-level evidence 链可审计。
- 最终只输出一个 150 verdict。
- 最终只输出一条 next-step recommendation。
- 未修改 benchmark truth 与 gate 语义。
