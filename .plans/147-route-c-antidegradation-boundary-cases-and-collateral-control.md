# 147 Route-C Antidegradation Boundary Cases And Collateral Control

## Background

146 已经建立了 route_c raw output anti-degradation 主线，并给出单一结论 `Partially validated`。已知事实包括：

- 144 的 6/6 regression 样本被稳定识别为 `punctuation_collapse` 并统一走 `degeneration_blocked`。
- 143 的 5 条 parser-reachable 正常样本保持 `pass_raw_to_parser`，没有被误伤。
- 143 还保留 1 条真实 `contract_broken_response`。
- 当前 formatter 只允许保守、可枚举的格式层清理，不做语义猜测。

146 没能升级到 fully validated 的关键原因是：当前证据窗口内缺少对 recoverable boundary 的系统性边界验证，尤其还没有明确证明 anti-degradation path 在“轻格式污染”与“不可恢复退化”之间划线足够稳。

## Why 146 remained Partially validated

- 146 的真实样本足以证明 `punctuation_collapse` 和正常 `parser_reachable` 的两端边界。
- 但 `recoverable_formatting_issue` 主要仍停留在规则定义层，而不是边界样例层。
- 146 还没有系统性评估：
  - 正常但略脏的输出会不会被误拦；
  - 不可恢复退化会不会被误放行；
  - 轻格式污染是否真的能在“不猜语义”的前提下被保守恢复。

因此 147 的唯一方向是：用最小、可审计的 boundary-case suite，把误伤与漏判边界补齐。

## Existing evidence-backed categories vs not-yet-covered categories

### Already evidence-backed

- `punctuation_collapse`
  - 真实样本来源：144 replay regression 6/6
- `parser_reachable`
  - 真实样本来源：143 stable baseline 5/6
- `contract_broken_response`
  - 真实样本来源：143 stable baseline 1/6

### Not yet sufficiently covered before 147

- `recoverable_formatting_issue`
  - 146 只有规则定义，缺少系统性边界样例验证
- `empty_whitespace_like`
  - 145/146 没有直接的真实 execution regression 样本
- `ultra_short_malformed_response`
  - 145/146 没有直接的真实 execution regression 样本

147 允许在不改语义的前提下，用极少量 controlled-format-variant 补这些边界。

## Goal

建立一套最小、可审计的 boundary-case suite，验证 anti-degradation path 是否：

- 不误伤正常 parser-reachable 输出；
- 不把 clearly unrecoverable degeneration 误放到 parser；
- 对 ambiguous-but-still-nonrecoverable 情况保持保守；
- 对 recoverable formatting boundary 在不做语义猜测的前提下给出稳定、可解释的 handoff。

最终输出单一 boundary-control verdict 与唯一 next-step recommendation。

## Non-goals

- 不修改 benchmark truth 语义。
- 不修改 gate 阈值或 PASS/BLOCKED 定义。
- 不扩模型轴、budget、prompt family、attack family、dataset 轴。
- 不把 147 做成 replay/stability 扩张项目。
- 不把 synthetic formatting variants 伪装成真实 regression 恢复成功。

## Boundary-case suite design

147 的 suite 只覆盖四类边界样例：

1. `clearly_unrecoverable_degeneration`
   - 优先用 144 真实 `punctuation_collapse`
   - 补少量 controlled formatting-only degenerate variants

2. `clearly_normal_parser_reachable_responses`
   - 直接用 143 中已知 `pass_raw_to_parser` 样本

3. `ambiguous_but_still_nonrecoverable_cases`
   - 直接用 143 真实 `contract_broken_response`
   - 补少量仅加前缀/包裹层的 controlled variants

4. `recoverable_formatting_boundary_cases`
   - 用 143 正常 parser-reachable 响应构造严格的 formatting-only variants：
     - quote-wrapped
     - bracket-wrapped
     - prefix-noise wrapped
     - bullet-prefixed
     - markdown-code-fence wrapped

所有 controlled cases 都必须标明：

- `source_type = controlled-format-variant`
- `base_origin`
- `format_mutation_only = true`
- `semantic_guess_allowed = false`

## False-positive / false-negative control plan

### False positive

- 正常 parser-reachable 响应被错误标为 `degeneration_blocked`
- recoverable formatting boundary 被错误标为不可恢复

### False negative

- clearly unrecoverable degeneration 被错误放行到 parser
- ambiguous-but-still-nonrecoverable 被错误判成 recoverable

### Acceptable boundary

- 对 clearly unrecoverable degeneration：必须严格阻断，不能误放
- 对 clearly normal parser-reachable：必须避免误伤
- 对 ambiguous-but-still-nonrecoverable：允许保守拦截，不允许语义猜测式恢复
- 对 recoverable formatting boundary：如果规则足够清楚，应优先允许 `pass_formatted_to_parser`；若出现系统性 over-block，则不能宣称 boundary control 已验证

## Validation plan

1. 构建 suite manifest，并为每个 case 记录 expected:
   - expected_group
   - expected_handoff
   - expected_recoverability
   - expected_category

2. 用 146 的 anti-degradation helper 对每个 case 做独立判定。

3. 生成：
   - case-level details
   - expected vs observed handoff summary
   - false-positive / false-negative counts
   - top risky boundary types

4. 默认不做 controlled rerun；只有当 suite 本身无法判明 formatter 是否越界时，才允许 1 组极小 helper-level validation。

## Risks

- controlled-format-variant 虽然可审计，但仍不同于真实跨时间 regression 证据。
- 如果 `recoverable_formatting_issue` 的边界过窄，可能造成“过度保守但语义安全”的结果，这会把 147 推向 `Partially validated`。
- 如果 helper 对某些格式污染（如 markdown code fence）处理不稳，147 会暴露为真实 boundary 风险，而不是可直接前进的结论。

## Milestones

- [x] M1: boundary-case suite and evaluation rules frozen
- [x] M2: boundary-case validation and collateral-control analysis completed
- [x] M3: single verdict and single next-step recommendation completed

## Progress Notes

- 真实证据已覆盖：144 的 6 条 `punctuation_collapse` regression、143 的 5 条 parser-reachable 正常样本、143 的 1 条真实 `contract_broken_response`。
- 为补 recoverable boundary 证据缺口，147 增加了 12 条 `controlled-format-variant`，且全部保持 `format_mutation_only = true`。
- 当前唯一边界失配是 `controlled_recoverable::code_fence`：它本应走 `pass_formatted_to_parser`，但实际被保守拦到 `degeneration_blocked`。
- 因此 147 的关键结论不是“规则失控”，而是“明显不可恢复样本拦得住、正常样本不误伤，但 recoverable boundary 证据还不够干净”。

## Exit criteria

- 147 plan 文件完整且可恢复。
- boundary-case suite、rules、summary、details、report、verdict、recommendation 七类 artifacts 齐全。
- suite 中每个 controlled case 都明确标注 real / controlled-format-variant 来源。
- 误伤 / 漏判标准写清楚并用于最终 verdict。
- 最终只输出一个 147 verdict。
- 最终只输出一条下一步建议。
- 未改 benchmark truth 与 gate 语义。
