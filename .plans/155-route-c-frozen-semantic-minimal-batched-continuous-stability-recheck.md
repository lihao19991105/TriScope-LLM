# 155 Route-C Frozen Semantic Minimal Batched Continuous Stability Recheck

## Background

154 已完成 `Minimal real batched continuous regression validated`，并确认在冻结 benchmark truth 与 gate 语义不变前提下，最小真实 batched continuous regression（12 cases, 2 windows）全部匹配预期。

155 的唯一任务是在不扩张轴线、不改语义、不改 gate 的条件下，做最小 batched continuous 稳定性复检，验证 148 的 recoverable-boundary 收口在多窗口连续复检链上是否仍稳定成立。

## Why 154 enables minimal batched continuous stability recheck

- 154 已有可复用的最小真实 batched continuous case-level 证据链，可直接作为冻结参考。
- 154 已明确唯一 nonrecoverable 真实锚点受限事实（illumination_0000），可在 155 中继续按冻结语义复用，不引入语义放宽。
- 155 可在同等预算、同等模型轴、同等 parser/gate 语义下，专注验证“多窗口连续链稳定性副作用是否为零”。

## Frozen semantic / gate / rule scope

- benchmark truth 语义冻结：不改标签定义，不引入猜测式语义映射。
- gate 语义冻结：不改阈值，不改 PASS/BLOCKED 判定。
- recoverable-boundary 规则冻结：沿用 148/149/150/151/152/153/154 的已确认规则。
- parser normalization 能力范围冻结：仍为 conservative normalization + anti-degradation 既有约束。
- 不扩模型轴、不扩 budget、不扩 prompt family、不扩 attack family。

## Goal

在冻结语义与 gate 不变前提下，完成最小 route_c batched continuous 稳定性复检，并同时验证：

1. recoverable formatting boundary 在多窗口 batched continuous 复检上继续稳定放行。
2. normal 路径在多窗口 batched continuous 复检上不被误伤。
3. nonrecoverable 路径在多窗口 batched continuous 复检上继续稳定 blocked。
4. 复检链路不引入新的窗口级 gate 回退、health 异常、parser source 漂移、handoff contract 违例。

## Non-goals

- 不做模型轴扩张（不进入 7B/8B，不扩 route_b）。
- 不做 budget 扩张。
- 不做新 attack family / prompt family。
- 不改 benchmark truth 语义，不改 gate 语义。
- 不做大规模稳定性工程或新实验矩阵。

## Minimal batched continuous stability recheck design

- 复检数据集规模保持最小：12 条样例。
- 复检窗口保持多窗口且克制：2 个连续 batch windows（沿用 154 的真实锚点链）。
- 路径覆盖保持对称：recoverable=4、normal=4、nonrecoverable=4。
- 样例来源优先复用 154 真实与 controlled-format-variant 证据样例；不新增语义映射。
- 每条样例都标注：来源、路径类型、窗口编号、窗口内位置、prompt 锚点、是否 batched continuous recheck 输入。
- 增加 stage-154 冻结参考字段，对每条 155 case 做一一对照漂移检测。

## Stability-recheck criteria

1. recoverable batched-continuous-recheck criteria
- recoverable case 必须保持 `pass_formatted_to_parser`。
- code-fence-like recoverable case 不得回退到 `degeneration_blocked`。
- 不允许借助语义猜测恢复。

2. normal batched-continuous-recheck criteria
- normal case 必须保持 `pass_raw_to_parser`。
- 不得新增 false block。
- 不得引入不必要 anti-degradation 过拦截。

3. nonrecoverable batched-continuous-recheck criteria
- nonrecoverable case 必须保持 `degeneration_blocked`。
- 不得因 recoverable boundary 修正而漏放。

4. batched-continuous-recheck consistency criteria
- parser / gate / label health / handoff 语义必须一致。
- 不得出现 parser source drift / handoff contract violation / label health anomaly。
- 不得出现窗口级 gate 或 logistic 非预期回退。
- 与 stage-154 冻结参考的一一对照不得漂移。

## Validation plan

1. 冻结 155 suite 与 rules（M1）。
2. 运行最小 batched continuous stability recheck 主流程（dataset -> gate -> logistic），输出 case-level details（M2）。
3. 运行 post-analysis，输出单一 verdict 与唯一 next-step recommendation（M3）。

## Risks

- 155 仍是最小受控复检，不等价于长期大规模稳定性结论。
- nonrecoverable 真实锚点稀缺，需复用 illumination_0000 做 guardrail 复检。
- 若出现窗口级漂移，必须保守降级到 `Partially validated` 或 `Not validated`。

## Milestones

- [x] M1: minimal batched continuous recheck set and criteria frozen
- [x] M2: minimal batched continuous stability recheck completed
- [x] M3: single verdict and single recommendation completed

## Completion Notes

- 主流程已完成并生成 suite/rules/summary/details/report 五类主产物。
- post-analysis 已完成并生成单一 verdict 与唯一 next-step recommendation。
- 复检结果：12/12 case 匹配，gate=PASS，logistic=PASS，窗口级无 mismatch、无 drift、无 contract/health 异常。
- stage-154 一一冻结对照通过：`stage154_reference_drift_count = 0`。

## Exit criteria

- 产出 suite / rules / summary / details / report / verdict / recommendation 七类 artifacts。
- focused minimal batched continuous stability recheck 完成，并有 case-level 证据。
- minimal collateral batched-continuous-recheck analysis 完成并明确 mismatch 是否存在。
- 最终仅给出一个 155 verdict 与一个下一步建议。
- 全程未改 benchmark truth 语义、未改 gate 语义、未做轴向扩张。
