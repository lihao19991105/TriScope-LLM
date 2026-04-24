# 151 Route-C Frozen Semantic Minimal Real Execution Validation

## Background

148 已完成 recoverable-boundary 收口并证明 collateral 可控，149 完成冻结语义下的小规模回归验证，150 完成最小 execution-path regression 并给出单一结论 `Minimal execution-path regression validated`。  
因此当前唯一正确方向是进入最小真实 execution 验证线，检查同一修正在真实链路上是否仍只影响 recoverable boundary，而不污染 normal / nonrecoverable path。

## Why 150 enables minimal real execution validation

- 150 已冻结 semantic / gate / recoverable-boundary 规则并给出可审计 reference。
- 150 已证明最小 execution-path 上 recoverable / normal / nonrecoverable 三类路径同时成立。
- 151 可在不改语义、不扩预算的前提下，把 150 的局部修正放到最小真实 execution 场景，专注验证真实链路副作用是否为 0。

## Frozen semantic / gate / rule scope

- benchmark truth 语义冻结：不改标签定义，不引入猜测式语义映射。
- gate 语义冻结：不改阈值，不改 PASS/BLOCKED 定义。
- recoverable-boundary 规则冻结：仅沿用 148 已确认的 code-fence 与轻 wrapper 收口逻辑。
- 不扩模型轴、不扩 budget、不扩 prompt family、不扩 attack family。
- 151 仅构建最小 real-execution validation set，不做主实验矩阵扩张。

## Goal

在冻结语义与 gate 不变前提下，完成一条最小真实 execution 验证线，并同时验证：

1. recoverable formatting boundary 在真实 execution 上仍能正确放行。
2. normal path 在真实 execution 上不被误伤。
3. nonrecoverable path 在真实 execution 上稳定 blocked。
4. route_c 真实 execution 未引入新的 path-level regression。

## Non-goals

- 不修改 benchmark truth 语义。
- 不修改 gate 阈值或 gate 判定逻辑。
- 不扩模型轴、预算、prompt family、attack family。
- 不做大规模 replay 或稳定性工程扩张。
- 不覆盖或重写 143/144/145/146/147/148/149/150 既有产物。

## Minimal real execution validation design

- 真实场景锚点：复用 143 稳定真实运行样例（`extension_rerun_01`）作为 single-run real execution anchor。
- 验证集组成：
  - recoverable real-execution cases：基于真实 execution 原始响应构造极少量 code-fence-like controlled-format variants，要求完整经过 dataset -> gate -> logistic 链。
  - normal real-execution guardrail cases：复用真实运行中 parser-reachable 样例（raw 路径）。
  - nonrecoverable real-execution guardrail cases：复用真实运行中 clearly unrecoverable 样例，并加一个 near-boundary nonrecoverable code-fence variant。
- 输出 case 字段必须显式记录：来源、路径类型、是否真实 execution 原始输入。

## Real-execution validation criteria

1. recoverable real-execution criteria
   - 必须保持 `pass_formatted_to_parser` 或等价合法 recoverable handoff。
   - 不允许回退到 `degeneration_blocked`。
   - 不允许语义猜测恢复。

2. normal real-execution criteria
   - 必须保持正常路径（`pass_raw_to_parser`）。
   - 不允许新增误伤。
   - 不允许引入额外过拦截。

3. nonrecoverable real-execution criteria
   - 必须保持 `degeneration_blocked`。
   - 不允许由于 recoverable-boundary 修正导致漏放。

4. real-execution consistency criteria
   - parser / gate / label health / handoff 语义一致。
   - 影响范围仅限 recoverable boundary。
   - 不引入新的 contract drift。

## Validation plan

1. 冻结最小 real-execution suite 与 rules（M1）。
2. 在最小真实 execution 场景上跑完整链路并生成 case-level details / summary / report（M2）。
3. 执行最小 collateral real-execution analysis，输出单一 verdict 与唯一 next-step recommendation（M3）。

## Risks

- 单 run 锚点覆盖有限，但符合“最小真实 execution 验证”范围。
- 真实 run 中 recoverable 样例可能稀缺，因此需极少量 controlled-format variants 补齐 code-fence 覆盖。
- 若真实链路出现 gate 或 parser 漂移，151 结论必须保守降级为 `Partially validated` 或 `Not validated`。

## Milestones

- [x] M1: minimal real execution validation set and criteria frozen
- [x] M2: minimal real execution validation completed
- [x] M3: single verdict and single recommendation completed

## Exit criteria

- 151 计划文件完整且可恢复。
- 已产出 suite / rules / summary / details / report / verdict / recommendation 七类 artifacts。
- 已完成 focused minimal real execution validation 与 minimal collateral analysis。
- 最终仅输出一个 151 verdict 与唯一下一步建议。
- 全程未改 benchmark truth 语义、未改 gate 语义、未做轴向扩张。
