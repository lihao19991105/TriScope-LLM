# dualscope-budget-aware-two-stage-fusion-design

## Background

仓库主线已经正式切换为 DualScope-LLM，且前两个正式阶段都已经完成：

- Stage 1: `dualscope-illumination-screening-freeze`
- Stage 2: `dualscope-confidence-verification-with-without-logprobs`

这两个阶段已经分别冻结了：

- illumination screening 的问题定义、模板族、feature schema、budget contract、confidence / fusion public fields
- confidence verification 的双路径 capability contract、with-logprobs / without-logprobs feature schema、fallback policy、public fields 和 Stage 1 依赖合同

因此，现在最合理的下一步不是继续旧的 route_c / 199+ 历史链，也不是提前启动整篇论文的大实验矩阵，而是把 Stage 1 和 Stage 2 串成 **正式、可执行、预算感知的 Stage 3 协议**。

## Why budget-aware fusion is the third DualScope stage

DualScope 的主线是：

1. Stage 1: Illumination Screening
2. Stage 2: Confidence Verification
3. Stage 3: Budget-Aware Lightweight Fusion Decision

Stage 3 位于第三阶段，是因为：

- Stage 1 提供全量、较低成本的 screening
- Stage 2 提供更高成本但更强的 verification evidence
- Stage 3 决定什么时候只用 Stage 1，什么时候启动 Stage 2，以及如何把两段证据在预算约束下融合成 final risk decision

因此，Stage 3 不是简单的分数拼接，而是 DualScope 主方法的**策略层与决策层**。

## Problem definition

Stage 3 的问题定义是：

> 在 black-box、query-budget constrained、optional-logprobs 的现实条件下，利用 Stage 1 的 screening risk 决定是否触发 Stage 2 verification，并将 illumination evidence 与 confidence evidence 以 capability-aware、budget-aware 的轻量方式融合为最终 DualScope risk decision。

Stage 3 融合的是：

- Stage 1 illumination evidence
- Stage 2 confidence verification evidence
- budget usage metadata
- capability mode and degradation flags

它**不融合**：

- reasoning branch
- judge-style verdict
- 无约束 feature soup
- 与两阶段协议无关的额外诊断信号

## Why screening + verification must be fused rather than simply juxtaposed

Illumination screening 和 confidence verification 不能只是在论文里并排摆放，原因是：

1. illumination 更便宜、适合全量筛查
2. confidence verification 更贵，不适合对所有样本无差别触发
3. without-logprobs 模式下 Stage 2 证据更弱，需要显式 capability-aware 处理
4. query budget 是方法核心，不是附属分析

所以 DualScope 的关键不是“两个模块都存在”，而是：

- 先筛后证
- 风险触发 verification
- capability-aware 地利用 verification 证据
- 最终把效果和成本一起体现在 final decision contract 中

## Frozen scope

本阶段冻结的内容包括：

1. Stage 3 的问题定义
2. Stage 1 / Stage 2 依赖合同
3. fusion public field schema
4. budget-aware triggering policy
5. capability-aware fusion policy
6. final decision contract
7. baseline / ablation contract
8. cost analysis contract
9. fusion IO contract
10. representative fusion traces
11. 可执行的 Stage 3 freeze pipeline、CLI、analysis 和文档入口

## Non-goals

- 不做完整主实验矩阵
- 不训练或拟合复杂 fusion model
- 不实现更复杂 dynamic threshold tuning
- 不重定义 Stage 1 / Stage 2 的既有语义
- 不恢复 reasoning branch
- 不继续旧 route_c 工程链

## Stage 1 / Stage 2 dependency contracts

Stage 3 必须显式复用前两阶段既有接口。

### Stage 1 required fields

- `dataset_id`
- `example_id`
- `screening_risk_score`
- `screening_risk_bucket`
- `confidence_verification_candidate_flag`
- `budget_usage_summary`
- `screening_summary_for_fusion`
- `template_results_public_summary`

### Stage 2 required fields when verification is triggered

- `capability_mode`
- `verification_risk_score`
- `verification_risk_bucket`
- `confidence_lock_evidence_present`
- `budget_usage_summary`
- `verification_summary_for_fusion`

### Stage 2 optional / capability-dependent fields

- `sequence_lock_strength`
- `entropy_mean`
- `topk_mass_concentration`
- `fallback_lock_risk_score`
- `fallback_mode_limit_flag`
- `verification_confidence_degradation_flag`

## Fusion public field schema

Stage 3 必须冻结一个统一 public field schema，覆盖：

- 来自 Stage 1 的 screening fields
- 来自 Stage 2 的 verification fields
- 用于 final decision 的 aggregated fields
- 用于 cost analysis 的 accounting fields

每个字段都必须写清：

- source_stage
- dtype
- semantic_meaning
- required
- used_in_final_decision
- used_in_cost_analysis
- capability_sensitive

## Budget-aware triggering policy

Stage 3 必须明确回答：

- 什么条件下仅保留 Stage 1
- 什么条件下触发 Stage 2
- 什么条件下因为预算不足而走降级路径
- 什么条件下 without-logprobs 走 fallback-aware verification

默认应保持：

- Stage 1 先运行
- Stage 2 只在高风险或 candidate-flagged 且预算足够时触发
- 不允许无限 verification 扩张

## Capability-aware fusion policy

Stage 3 必须显式区分：

### With-logprobs

- verification evidence 强
- 可以在 final risk 中给予更高的 verification 权重

### Without-logprobs

- verification evidence 较弱
- 必须显式读取 degradation flags
- final fusion 需要 uncertainty-aware adjustment，而不是把 fallback proxy 当成等价强证据

## Final decision contract

Stage 3 最终输出至少包含：

- `final_risk_score`
- `final_risk_bucket`
- `final_decision_flag`
- `verification_triggered`
- `capability_mode`
- `evidence_summary`
- `budget_usage_summary`
- `explainable_output_fields`

并且必须显式指向未来论文中的：

- 主方法输出
- 消融表输出
- 成本分析表输出

## Baseline and ablation contract

当前必须冻结日后论文比较口径：

- illumination-only baseline
- confidence-only with-logprobs baseline
- confidence-only without-logprobs baseline
- naive concat baseline
- budget-aware two-stage fusion baseline

## Cost analysis contract

当前必须冻结未来成本分析口径，包括：

- 平均 query cost
- verification trigger rate
- per-mode cost
- budget consumption ratio
- performance-cost tradeoff interface

## Deliverables

- `.plans/dualscope-budget-aware-two-stage-fusion-design.md`
- `src/eval/dualscope_fusion_common.py`
- `src/eval/dualscope_budget_aware_two_stage_fusion.py`
- `src/eval/post_dualscope_budget_aware_two_stage_fusion_analysis.py`
- `scripts/build_dualscope_budget_aware_two_stage_fusion_design.py`
- `scripts/build_post_dualscope_budget_aware_two_stage_fusion_design_analysis.py`
- `docs/dualscope_fusion_protocol.md`
- `docs/dualscope_ablation_contract.md`
- `outputs/dualscope_budget_aware_two_stage_fusion_design/default/*`
- `outputs/dualscope_budget_aware_two_stage_fusion_design_analysis/default/*`

## Risks

- 当前阶段是 design freeze，不是整篇论文实验矩阵，因此 representative traces 只能证明协议形状和可执行性，不能被解读为最终性能结果。
- 如果 budget-aware 触发规则写得过宽，后续成本分析会失真；写得过窄，则可能掩盖 verification 的价值。
- without-logprobs 路径若处理不当，容易被误表述成等价于 with-logprobs 强证据。
- 若 final decision contract 不够明确，后续实验表格与写作会再次漂移。

## Milestones

- [x] M1：fusion problem / policy / budget / IO / baseline scope frozen
- [x] M2：artifacts / implementation / CLI / executable design outputs completed
- [x] M3：single verdict and single recommendation completed

## Exit criteria

完成本计划时，仓库中必须已经存在：

- 机器可读的问题定义、依赖合同、public field schema、budget policy、capability-aware policy、final decision contract、baseline plan、cost analysis plan、IO contract
- 可执行的主流程 CLI 与后分析 CLI
- 代表性的 stage1-only、with-logprobs triggered、without-logprobs triggered、budget-limited、degradation-aware traces
- markdown report 与文档入口
- DualScope 总入口对 Stage 3 的索引

同时必须满足：

- 不继续旧 route_c 主线
- 不改 benchmark truth 语义
- 不改 gate 语义
- 不提前跑整篇论文大实验矩阵
- 不把 reasoning 分支偷偷塞回来
