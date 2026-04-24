# 148 Route-C Recoverable Boundary Evidence And Collateral Compression

## Background

146 建立了 route_c 的 raw-output anti-degradation 主线，并给出 `Partially validated`。147 进一步用 24 条最小 boundary-case suite 验证边界与误伤控制，结果显示：

- clearly unrecoverable degeneration 拦截稳定；
- clearly normal parser-reachable 样本未被误伤；
- ambiguous-but-still-nonrecoverable 样本保持保守阻断；
- recoverable formatting boundary 通过率仅为 `0.8`。

147 暴露的唯一明确失配点是 `controlled_recoverable::code_fence`。这说明当前问题已经收缩到 recoverable formatting boundary，而不是更广义的 parser-path 或 gate 语义。

## Why 147 remained Partially validated

- 147 已证明 anti-degradation path 不会把不可恢复退化误放到 parser。
- 147 也已证明正常 parser-reachable 样本不会被误伤。
- 但 `controlled_recoverable::code_fence` 本应走 `pass_formatted_to_parser`，却被判成 `contract_broken_response` 并直接 `degeneration_blocked`。
- 因此 147 的不足不是“边界一团糟”，而是 recoverable boundary 的证据还不够细，且现有 formatting cleanup 对 code-fence-like wrappers 过严。

## Current mismatch focus

148 只聚焦 recoverable formatting boundary，尤其是：

- plain markdown code fence wrapper；
- language-tagged markdown code fence wrapper；
- 与 code fence 同级别的单层轻格式包裹；
- code fence 外壳内仍然无信息、因此必须保持 blocked 的 near-boundary nonrecoverable variants。

本阶段必须回答：

- `controlled_recoverable::code_fence` 为什么被拦；
- 这是 wrapper 识别过严，还是 handoff 条件过严；
- 最小安全修正是什么；
- 该修正是否只改善 recoverable boundary，而不伤 normal / unrecoverable 路径。

## Goal

建立一套 focused recoverable-boundary suite，并用最小、可审计、向后兼容的规则收口 `code_fence` 及其同类轻 wrapper，验证：

- 哪些 formatting wrapper 可以安全走 `pass_formatted_to_parser`；
- 哪些 wrapper 仍然必须 blocked；
- 是否能减少 recoverable boundary 的过度拦截；
- 是否保持 unrecoverable blocked 与 normal pass-through 不受影响。

最终输出单一 148 verdict 与唯一 next-step recommendation。

## Non-goals

- 不修改 benchmark truth 语义。
- 不修改 gate 阈值、PASS/BLOCKED 定义或健康度标准。
- 不扩模型轴、budget、prompt family、attack family、dataset 轴。
- 不把 148 做成 replay、稳定性扩展或新实验矩阵。
- 不引入语义猜测式恢复。
- 不把任意 wrapper 都视为 recoverable formatting issue。

## Recoverable-boundary evidence plan

148 的 focused suite 只覆盖三层：

1. `code_fence_like_recoverable`
   - plain code fence 包裹；
   - newline code fence 包裹；
   - language-tagged code fence 包裹；
   - 都必须保持 `format_mutation_only = true`。

2. `lightweight_single_layer_recoverable`
   - 继承 147 中已通过的 quote / bracket / prefix / bullet wrappers；
   - 用作 recoverable baseline guardrail，确认修正不会破坏已通过路径。

3. `near_boundary_nonrecoverable`
   - code fence 内是 `???`、空白、无合法 label token、真实 contract-broken row；
   - 用来确认 code-fence 收口不会把无信息 wrapper 误放进 parser。

所有 case 必须显式标注来源：

- `real`
- `inherited-controlled-format-variant`
- `new-controlled-format-variant`

## Collateral-compression plan

148 的误伤压缩只看三类指标：

- recoverable boundary overblocked count
- unrecoverable / near-boundary leakage count
- normal parser-reachable collateral damage count

本阶段要求：

- 对 `code_fence` 失配做 before/after tracing；
- 证明最小修正后 recoverable boundary 误伤下降；
- 同时证明 unrecoverable blocked 与 normal pass-through 不退化。

## Validation plan

1. 冻结 focused suite manifest 与规则表。
2. 对每个 case 同时记录：
   - legacy path outcome
   - current path outcome
   - expected handoff / category / recoverability
3. 生成：
   - focused case-level details
   - before/after confusion-style summary
   - mismatch delta
   - markdown report
4. 默认不做 model replay；如果需要验证，仅允许 helper-level controlled validation。

## Risks

- recoverable boundary 的真实样本仍然不足，部分证据仍需依赖 controlled-format-variant。
- code-fence 收口如果设计过宽，可能把 wrapper 内无信息短串误放到 parser。
- 如果设计过窄，则 recoverable evidence 仍然只能停留在 `Partially validated`。

## Milestones

- [x] M1: recoverable-boundary suite and criteria frozen
- [x] M2: focused boundary validation and collateral compression completed
- [x] M3: single verdict and single recommendation completed

## Progress Notes

- 148 复用了 147 的 recoverable / normal / unrecoverable 护栏样例，并额外增加了 code-fence-like 的 focused controlled variants。
- 最小 helper 修正只收口 markdown code fence wrapper 的识别方式：plain fence、newline fence、language-tagged fence 只在“去壳后可枚举地暴露 label token”时才进入 `pass_formatted_to_parser`。
- `controlled_recoverable::code_fence` 的 legacy 行为是 `degeneration_blocked / contract_broken_response`，current 行为已压缩到 `pass_formatted_to_parser / recoverable_formatting_issue`。
- focused validation 下，recoverable overblocked count 从 1 降到 0，同时 unrecoverable leak 与 normal collateral damage 继续保持 0。

## Exit criteria

- 148 plan 文件完整且可恢复。
- focused suite / rules / summary / details / report / verdict / recommendation 七类 artifacts 齐全。
- 所有 case 的来源 `real / inherited-controlled-format-variant / new-controlled-format-variant` 清楚可查。
- before/after 证据链清楚说明 recoverable boundary 是否收口。
- 最终只输出一个 148 verdict。
- 最终只输出一条 next-step recommendation。
- 未修改 benchmark truth 与 gate 语义。
