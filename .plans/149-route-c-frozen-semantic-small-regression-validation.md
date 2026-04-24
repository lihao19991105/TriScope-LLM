# 149 Route-C Frozen Semantic Small Regression Validation

## Background

148 已将 recoverable formatting boundary 的 focused overblock 从 `1` 压到 `0`，并给出单一结论 `Recoverable boundary control validated`。其关键事实是：

- `controlled_recoverable::code_fence` 从 legacy 的 `degeneration_blocked / contract_broken_response` 收口到 current 的 `pass_formatted_to_parser / recoverable_formatting_issue`；
- recoverable pass rate 提升到 `1.0`；
- normal guardrail 继续 `pass_raw_to_parser`；
- unrecoverable 与 near-boundary nonrecoverable guardrail 继续 `degeneration_blocked`。

因此 149 的任务不是继续扩张 recoverable boundary，而是在冻结语义、gate、模型轴、budget、prompt family 不变的前提下，做一组小而精的回归验证，确认 148 的局部修正不会破坏其它路径。

## Why 148 enables regression validation

- 148 已经给出可审计的 before/after 证据链，说明修正聚焦在 recoverable boundary 而不是更广的 parser 黑箱扩张。
- 148 当前 focused suite 已经包含 recoverable / normal / unrecoverable / near-boundary nonrecoverable 四类路径，可直接抽取更小、更稳的 regression set。
- 149 因此不需要新 replay，也不需要扩大预算，只需要验证“冻结后的当前规则”能否在最小代表性样例集上稳定复现 148 的正确行为。

## Frozen semantic / gate / rule scope

149 冻结以下边界：

- benchmark truth 语义不变；
- gate 语义与阈值不变；
- anti-degradation 的 allowed format steps 不变；
- recoverable boundary 仍只限于 148 已明确枚举的 wrapper 形态；
- 不新增更宽泛的 formatter 能力；
- 不新增新的 prompt family、model axis、budget。

149 只允许做 helper-level / rule-level 小步回归验证。

## Goal

构建一组小规模、受控、回归导向的 validation set，验证三条路径同时成立：

- recoverable formatting boundary 继续正确放行；
- normal parser-reachable 路径继续不被误伤；
- unrecoverable 与 near-boundary nonrecoverable 路径继续稳定 blocked。

最终输出单一 149 verdict 与唯一 next-step recommendation。

## Non-goals

- 不修改 benchmark truth 语义。
- 不修改 gate 阈值或 PASS/BLOCKED 定义。
- 不扩模型轴、budget、prompt family、attack family、dataset 轴。
- 不做时间分离 replay、大批量 rerun、稳定性扩展实验。
- 不把 recoverable-boundary 修正扩成更泛化的 parser heuristic。

## Small regression validation set design

149 的 regression set 只保留最小必要覆盖：

1. `recoverable_boundary_positive`
   - 至少包含：
     - `focused::controlled_recoverable::code_fence`
     - 一个 language-tagged code-fence recoverable case
     - 1~2 个已通过的轻 wrapper recoverable baseline case

2. `normal_guardrail`
   - 选取少量 143 真实 parser-reachable rows，确认正常路径继续 `pass_raw_to_parser`

3. `nonrecoverable_guardrail`
   - 选取：
     - 至少 1 条 144 真实 punct-collapse regression
     - 至少 1 条 near-boundary code-fence no-info case
     - 至少 1 条 near-boundary contract-broken wrapped case

所有样例必须标注来源：

- `real`
- `inherited-controlled-format-variant`
- `new-controlled-format-variant`

## Regression criteria

149 的回归判定标准固定为：

1. `recoverable path`
   - recoverable cases 必须继续 `pass_formatted_to_parser`
   - 不允许回退到 `degeneration_blocked`
   - 不允许依赖语义猜测

2. `normal guardrail`
   - normal cases 必须继续 `pass_raw_to_parser`
   - 不允许新增误伤

3. `nonrecoverable guardrail`
   - nonrecoverable cases 必须继续 `degeneration_blocked`
   - 不允许漏放坏样例

4. `change scope`
   - 当前结果必须与 148 的冻结 reference 一致
   - 不得通过改 benchmark truth 与 gate 语义来“制造通过”

## Validation plan

1. 从 148 details 中抽取最小 regression set，并保存 frozen reference。
2. 对每个 case 重新运行当前 anti-degradation helper。
3. 记录：
   - frozen_reference_handoff/category/recoverability
   - current_handoff/category/recoverability
   - case-level match / mismatch 类型
4. 输出：
   - regression suite
   - rules / criteria
   - summary
   - details
   - report
   - post-analysis verdict / recommendation

## Risks

- 149 的证据仍然以 helper-level regression 为主，不等于新一轮 execution stability。
- regression set 如果选得过窄，可能掩盖边界外问题；但 149 的目标是“小规模回归验证”，不是大覆盖率实验。
- 若未来扩展 recoverable boundary，149 的结论不能自动外推到未覆盖的 wrapper 家族。

## Milestones

- [x] M1: small regression set and frozen criteria prepared
- [x] M2: small regression validation completed
- [x] M3: single verdict and single recommendation completed

## Progress Notes

- 149 从 148 的 focused evidence 中抽取了 10 条小规模 regression cases：4 条 recoverable boundary positives、2 条 normal guardrails、4 条 nonrecoverable guardrails。
- regression set 明确复用了 148 已修复成功的 `controlled_recoverable::code_fence` 与 language-tagged code-fence recoverable case，确保本轮优先验证真正有价值的局部修正。
- small regression summary 显示：`recoverable_pass_rate = 1.0`、`normal_pass_through_rate = 1.0`、`nonrecoverable_block_rate = 1.0`。
- 全部 10 条样例当前都与 148 frozen reference 一致：`mismatch_type_counts = {match: 10}`，不存在 recoverable 回退、normal 误伤或 nonrecoverable 漏放。

## Exit criteria

- 149 plan 文件完整且可恢复。
- regression suite / rules / summary / details / report / verdict / recommendation 七类 artifacts 齐全。
- regression set 来源与 guardrail 类型清楚。
- case-level regression evidence 可审计。
- 最终只输出一个 149 verdict。
- 最终只输出一条 next-step recommendation。
- 未修改 benchmark truth 与 gate 语义。
