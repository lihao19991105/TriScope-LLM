# 146 Route-C Output Format Robustness And Parser Antidegradation

## Background

141 通过最小 parser / output-normalization 修复，把 route_c execution 从 `BLOCKED` 拉回 `PASS`。143 在同设置下累计 8 次 rerun 无回退，结论升级为 `Stable enough`。144 做时间分离 replay 后，labeled raw output 直接 6/6 退化为 `!!!!!!!!!!!!!!!!`，随后 route_c 回到 `BLOCKED / single-class / parsed_option_count=0`。145 已明确单一根因结论为 `Model-output drift confirmed`。

因此，146 的正确方向不是继续 replay，也不是改 gate 或 benchmark truth 语义，而是围绕 raw output 层退化做一条最小、可审计、不过度修复的 anti-degradation 主线。

## Why parser-only fixing is insufficient after 145

- 145 已确认 144 的断裂发生在 parser 之前：`raw_response` 已经塌缩成纯标点。
- 如果 raw output 本身无信息，继续在 parser 后端叠 heuristic 只会把问题隐藏成“更复杂的 parse 规则”，不能解释模型输出为什么退化。
- 146 必须把关注点前移到 parser 边界：先识别退化，再决定是否允许最小格式恢复，最后才进入 parser。
- 146 不允许因为 raw output 坏了就修改标签语义或 gate 语义。

## Observed raw-output degeneration patterns

当前证据窗口优先冻结为：

- 143 stable baseline:
  - `outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_recheck/default/runs/extension_rerun_01/*`
- 144 replay regression:
  - `outputs/model_axis_1p5b_route_c_stable_baseline_time_separated_replay/default/runs/time_replay_01/*`
- 145 root-cause artifacts:
  - `outputs/model_axis_1p5b_route_c_time_separated_regression_root_cause/default/*`
  - `outputs/model_axis_1p5b_route_c_time_separated_regression_root_cause_analysis/default/*`

本阶段需要冻结并区分：

- `punctuation collapse`
- `ultra-short malformed response`
- `contract-broken response`
- `empty / whitespace-like degeneration`
- `recoverable formatting issue`（如果当前 evidence window 中未实际出现，也要显式说明）

## Goal

建立一条“degeneration detector -> contract-preserving formatter -> parser-path anti-degradation handoff”的最小链路，在不改 benchmark truth 与 gate 语义的前提下：

- 正确识别 raw output 退化类型；
- 明确哪些样本不可恢复、必须直接标记为 `degeneration-blocked`；
- 对极少数仅存在轻格式污染的样本，保守执行最小格式清理；
- 证明新路径不会破坏 143 的 working baseline；
- 输出单一 anti-degradation verdict 与唯一下一步建议。

## Non-goals

- 不修改 benchmark truth 标签定义。
- 不修改 gate 阈值、PASS/BLOCKED 根本语义或健康度判定。
- 不继续做大规模 replay/stability 扩展。
- 不扩模型轴、budget、prompt family、attack family、dataset 轴。
- 不把 parser heuristic 堆成不可审计的黑箱。
- 不覆盖 143/144/145 的任何原始 artifacts。

## Anti-degradation design

146 的 anti-degradation path 必须是显式、可开关、默认向后兼容：

1. `degeneration detector`
   - 对 raw output 做退化分类与 flags 记录。
   - 优先识别：`punctuation_collapse`、`ultra_short_malformed_response`、`contract_broken_response`、`empty_whitespace_like`。

2. `contract-preserving formatter`
   - 只允许执行明确、保守、可枚举的最小格式清理。
   - 不允许语义猜测、不允许把无信息输出硬修成标签。
   - 只允许复用现有 conservative normalization 已能解释的格式层操作。

3. `parser-path anti-degradation handoff`
   - `pass_raw_to_parser`
   - `pass_formatted_to_parser`
   - `degeneration_blocked`
   - 必须记录 before / after / reason / recoverability。

## Validation plan

验证只做受控小步：

1. 在 144 regression 样本上验证：
   - 纯标点塌缩是否被稳定识别；
   - 不可恢复样本是否被明确标为 `degeneration-blocked`；
   - 不会把 `!!!!!!!!!!!!!!!!` 伪装成有效标签。

2. 在 143 stable baseline 样本上验证：
   - 正常 parser-reachable 响应不被误伤；
   - 已有 working baseline 不被 anti-degradation 路径破坏；
   - 仍然保留现有 parsed / missing 事实。

3. 默认不做新 replay；只有在现有 artifact 无法判断误伤风险时，才允许 1 组极小 controlled rerun。

## Risks

- 当前 143/144 证据窗口里可能没有真实出现“可恢复 formatting-only”案例，因此 146 可能只能得到 `Partially validated`，而不是更强结论。
- 如果 anti-degradation 设计过宽，容易误把 contract-broken response 当成 recoverable，造成语义污染。
- 如果设计过窄，虽然安全，但只能提升解释性，不能降低 blocked rate。

## Surprises & Discoveries

- 仓库根目录不存在 `preferences.md`；本阶段按仓库实际可见的 `AGENTS.md`、`PLANS.md` 与 141/143/144/145 artifacts 继续执行。
- 当前 143/144 证据窗口内没有真实出现 `recoverable_formatting_issue`，这意味着 146 无法诚实宣称“已恢复退化执行”，只能验证边界与误伤控制。
- 143 stable baseline 中仍然保留 1 条 `contract_broken_response`，说明健康 working baseline 并不等于“所有行都可解析”，而是“parser-reachable rows 足够保住双类与 gate PASS”。

## Decision Log

- 决策：146 不做新 replay。
  - 原因：当前问题是 raw output 层 anti-degradation 边界设计，不是继续累计跨时间证据。
- 决策：146 只把 anti-degradation helper 落在 parser 边界，不改 benchmark truth 与 gate 语义。
  - 原因：145 已确认主问题在 raw output 漂移，继续改语义层会把根因和修复边界搅混。
- 决策：146 结论采用保守策略，优先接受 `Partially validated`。
  - 原因：当前 evidence window 内缺少真实 recoverable regression case，不能夸大成 fully validated。

## Milestones

- [x] M1: degeneration taxonomy and anti-degradation path frozen
- [x] M2: minimal robustness implementation and controlled validation completed
- [x] M3: anti-degradation analysis and next-step recommendation completed

## Progress

- [x] 创建 146 ExecPlan
- [x] 补充 raw output anti-degradation helper
- [x] 实现 146 主流程 builder
- [x] 实现 146 post-analysis builder
- [x] 生成 taxonomy / rules / summary / details / report
- [x] 生成单一 final verdict / next-step recommendation
- [ ] README 同步恢复入口

## Exit criteria

- 146 plan 文件完整、自包含、可恢复。
- taxonomy / rules / summary / details / report / verdict / recommendation 七类 artifacts 齐全。
- anti-degradation 路径默认向后兼容，且通过显式开关启用。
- 最终只输出一个 anti-degradation verdict。
- 最终只输出一条下一步建议。
- 未修改 benchmark truth 与 gate 语义。
- 未把 146 做成新的 replay/stability 扩张项目。
