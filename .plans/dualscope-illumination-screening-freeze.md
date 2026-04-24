# dualscope-illumination-screening-freeze

## Background

仓库主线已经从 TriScope-LLM 正式切换为 DualScope-LLM。当前最优先的工作不是继续旧的 route_c / recoverable-boundary 递归验证链，而是把 DualScope 的第一阶段方法真正冻结成一个可执行、可复用、可审计、可继续承接 Stage 2 / Stage 3 的正式模块。

当前仓库已经拥有足够强的工程可靠性基础，尤其是 `148–198` 的 route_c 长链已经证明 execution-path、recoverable-boundary 和 higher-level real usage 的工程稳定性。这些成果现在应作为 DualScope 的 implementation robustness / reliability foundation，而不是新的主创新主线。

因此，这个计划的任务不是“再写一份 illumination 想法草案”，而是把 **Illumination Screening** 变成 DualScope 主线里的**正式第一阶段协议**。

## Why illumination screening is the first DualScope stage

Illumination screening 是 DualScope 的第一阶段，因为它最适合作为黑盒、预算感知条件下的前置筛查：

- 它能以较低预算暴露 trigger-sensitive susceptibility amplification
- 它能提供 template-level / query-level 风险信号
- 它能为后续 confidence verification 提供 candidate routing
- 它比 reasoning branch 更稳定、更低成本、更贴近现实 API 场景

Illumination screening **不是最终 backdoor verdict**。它更适合作为：

- risk screening
- candidate selection
- first-stage abnormal susceptibility proxy

## Problem definition

Stage 1 的问题定义是：

> 在 black-box、query-budget constrained、optional-logprob 的现实条件下，利用 targeted ICL probing 识别模型在特定 trigger / target / template 组合下的异常易感性、行为翻转倾向、目标放大倾向与 cross-template instability，并把这些信号组织成后续 confidence verification 与 budget-aware fusion 可消费的 screening protocol。

Illumination screening 检测的是这些信号的组合：

- susceptibility amplification
- behavior flip tendency
- target-oriented abnormal sensitivity
- template-local instability
- cross-template instability

## Scope of Stage 1

### In Scope

- 冻结 illumination screening 的问题定义
- 冻结 probe template family
- 冻结 feature schema
- 冻结 input / output contract
- 冻结 budget contract
- 冻结 minimal baseline / ablation contract
- 实现最小可运行的 Stage 1 freeze pipeline、CLI、analysis 和 artifacts
- 显式为 Stage 2 / Stage 3 留机器可读接口位
- 补充文档入口与 README / master plan 索引

### Out of Scope

- 不做 confidence verification 实现
- 不做 budget-aware fusion 实现
- 不做大规模真实实验矩阵
- 不做 reasoning branch 复活
- 不改 benchmark truth 语义
- 不改 gate 语义
- 不继续旧 route_c 递归链

## Frozen scope

本阶段冻结的内容包括：

1. Illumination screening 的目标变量与非目标变量
2. 默认 probe template family 与最小模板集合
3. template-level / query-level / aggregated risk features
4. screening risk output 字段
5. budget accounting 字段
6. downstream confidence / fusion compatibility fields
7. illumination-only baseline 合同

本阶段不冻结的内容包括：

- confidence 特征定义细节
- fusion 模型训练细节
- 完整实验矩阵
- 大规模数据 / 模型覆盖策略

## Non-goals

- 不把 illumination stage 做成最终 verdict engine
- 不把 Stage 1 做成 reasoning / judge 分支替代品
- 不把 formatter / parser 规则问题重新混回 Stage 1 设计里
- 不把模板族无边界扩张
- 不做大而泛的 benchmark matrix

## Probe template family design

本阶段冻结一个最小但可扩展的 probe family：

1. `base_targeted_probe`
   - 作用：最基础的 targeted ICL susceptibility probing
   - 默认启用

2. `paraphrase_like_probe`
   - 作用：验证 trigger / instruction phrasing 扰动下的 susceptibility consistency
   - 默认启用

3. `target_oriented_probe`
   - 作用：更直接地观察 target behavior amplification
   - 默认启用

4. `alternate_context_probe`
   - 作用：验证上下文替换后风险是否仍被点亮
   - 默认启用

5. `stability_check_probe`
   - 作用：给 cross-template instability 和 risk consistency 提供最小支持
   - 默认启用

仅保留这些模板进入默认最小合同。其他更激进或成本更高的模板只能作为 future extension hooks，不进入当前默认最小集。

## Feature schema design

本阶段冻结三层 feature schema：

### Template-level

- `target_behavior_gain`
- `response_flip_indicator`
- `target_shift_indicator`
- `template_local_instability`
- `probe_response_length_delta`
- `template_trigger_susceptibility_proxy`

### Query-level aggregated

- `flip_rate`
- `gain_mean`
- `gain_max`
- `cross_template_instability`
- `risk_count`
- `template_agreement_score`
- `abnormal_target_alignment_rate`

### Aggregated risk fields

- `screening_risk_score`
- `screening_risk_bucket`
- `confidence_verification_candidate`
- `budget_consumption_ratio`
- `screening_summary_for_fusion`

## Budget contract

Stage 1 必须显式 budget-aware。冻结规则如下：

- 默认每个 query 的总 screening budget 固定且有限
- 每类模板有单独的默认分配
- 必须定义 `minimal_screening_budget`
- 默认不允许无限模板扩张
- 需要显式保留 `future_budget_extension_hooks`

## Input / output contract

### Required inputs

- `dataset_id`
- `example_id`
- `original_query`
- `probe_template_set`
- `budget_policy`

### Optional inputs

- `target_text`
- `trigger_text`
- `metadata`
- `api_capabilities`

### Emitted outputs

- `template_results`
- `query_aggregate_features`
- `screening_risk_score`
- `screening_risk_bucket`
- `confidence_stage_candidate_flag`
- `budget_usage_summary`
- `fusion_public_fields`

## Minimal baseline design

本阶段冻结的最小 baseline / ablation 合同包括：

- illumination-only baseline
- naive aggregation baseline
- threshold-based risk screening
- lightweight logistic placeholder contract
- future confidence-only comparison hook
- future fusion comparison hook

## Future compatibility with confidence verification

Stage 1 必须显式保留以下接口位：

- `confidence_verification_candidate_flag`
- `downstream_confidence_required_fields`
- `confidence_stage_readable_fields`
- `screening_summary_for_confidence`

Stage 2 不应重新定义 Stage 1 的风险输入。

## Future compatibility with budget-aware fusion

Stage 1 必须显式保留以下接口位：

- `fusion_public_fields`
- `fusion_compatible`
- `screening_summary_for_fusion`
- `budget_usage_summary`
- `screening_risk_bucket`

Stage 3 应基于这些公共字段完成轻量融合，而不是重新发明一套输入输出。

## Deliverables

- `.plans/dualscope-illumination-screening-freeze.md`
- `src/eval/dualscope_illumination_common.py`
- `src/eval/dualscope_illumination_screening_freeze.py`
- `src/eval/post_dualscope_illumination_screening_freeze_analysis.py`
- `scripts/build_dualscope_illumination_screening_freeze.py`
- `scripts/build_post_dualscope_illumination_screening_freeze_analysis.py`
- `docs/dualscope_illumination_protocol.md`
- `docs/dualscope_feature_dictionary.md`
- `outputs/dualscope_illumination_screening_freeze/default/*`
- `outputs/dualscope_illumination_screening_freeze_analysis/default/*`

## Risks

- 由于本阶段是 freeze module 而不是大实验，details 里的 case 只能是 representative / controlled protocol traces，不应被误读为主实验结果。
- 如果模板族定义过宽，会给后续 confidence / fusion 带来 budget drift 风险。
- 如果 feature schema 过薄，后续 confidence / fusion 可能重新发明字段；如果过厚，又会造成默认实现负担。
- 需要避免把旧 TriScope illumination 实现直接搬过来而不做 DualScope 化收束。

## Milestones

- [x] M1：illumination problem / template / feature / budget / IO scope frozen
- [x] M2：artifacts / implementation / CLI / executable freeze outputs completed
- [x] M3：single verdict and single recommendation completed

## Exit criteria

完成本计划时，仓库中必须已经存在：

- 机器可读的问题定义、模板规格、feature schema、IO contract、budget contract、baseline contract
- 可执行的主流程 CLI 与后分析 CLI
- 代表性的 details / summary / report / verdict / recommendation
- 显式的 confidence / fusion 接口位
- 文档入口与主计划入口中的 Stage 1 索引

同时必须满足：

- 不改 benchmark truth 语义
- 不改 gate 语义
- 不继续旧 route_c 递归链
- 不把 reasoning 分支偷偷塞回主线

## Surprises & Discoveries

- 仓库中已有早期 TriScope illumination probe 与 pilot materialization 能力，但它们不足以直接充当 DualScope Stage 1 协议，需要重新收束为 screening-first、budget-aware、downstream-compatible 的 freeze module。
- 旧 route_c 阶段式 artifact 风格很适合复用为当前 Stage 1 的 summary / details / verdict / recommendation 组织方式。
- 当前阶段不需要大实验，也能通过 representative protocol traces 把 schema、budget、IO、downstream hooks 冻结成可执行模块。

## Decision Log

- 决策：Stage 1 details 使用 representative protocol traces，而不是伪装成真实 benchmark 结果。
  - 原因：本阶段的目标是冻结协议与接口，不是提前展开实验矩阵。
  - 影响：details.jsonl 记录的是可审计的 representative case traces。

- 决策：保留 5 个默认模板族 + 1 个 future-only 模板族。
  - 原因：既要防止模板矩阵过薄，也要防止无限膨胀。
  - 影响：后续 confidence / fusion 可以在默认 minimal set 上稳定对接。

- 决策：在 Stage 1 artifacts 中显式保留 confidence / fusion public fields。
  - 原因：避免后续 Stage 2 / Stage 3 重新发明输入输出协议。
  - 影响：`confidence_stage_candidate_flag`、`fusion_public_fields`、`screening_summary_for_fusion` 成为冻结字段。

## Next Suggested Plan

下一步建议创建：

- `.plans/dualscope-confidence-verification-with-without-logprobs.md`
