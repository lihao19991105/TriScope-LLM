# dualscope-confidence-verification-with-without-logprobs

## Background

仓库主线已经正式切换为 DualScope-LLM，且 Stage 1 `dualscope-illumination-screening-freeze` 已经完成并验证通过。当前仓库不再继续旧的 TriScope / route_c 递归阶段链，也不再生成 `199+` 风格的旧式计划。

Stage 1 已经把 illumination screening 冻结成正式的第一阶段协议，并显式输出了：

- screening risk score / bucket
- confidence verification candidate flag
- budget metadata
- future confidence-readable fields
- future fusion-readable fields

因此，Stage 2 的任务不是从零发明一套 confidence 分支，而是把 **Confidence Verification** 搭成一个和 Stage 1 严格兼容、并对 Stage 3 有稳定接口的正式主模块。

## Why confidence verification is the second DualScope stage

DualScope 的主线是：

1. Stage 1: Illumination Screening
2. Stage 2: Confidence Verification
3. Stage 3: Budget-Aware Lightweight Fusion Decision

Confidence verification 位于第二阶段，是因为 illumination screening 观察的是“被点亮后的异常易感性”，而 confidence verification 观察的是“在筛出的高风险候选上，异常输出是否进入更强的 lock / concentration / collapse 风格状态”。

因此：

- Stage 1 是 screening
- Stage 2 是 verification
- Stage 3 才是最终预算感知融合判定

## Problem definition

Stage 2 的问题定义是：

> 在 black-box、query-budget constrained、optional-logprobs 的现实 API-like 条件下，对 Stage 1 筛出的高风险候选做异常生成锁定验证，提取 confidence locking、sequence lock、concentration collapse、stability collapse 等 verification evidence，并以统一公共字段输出给 future fusion。

Confidence verification 检测的是这些信号的组合：

- abnormal confidence locking
- sequence lock tendency
- concentration collapse
- entropy / uncertainty collapse
- repeated-sampling consistency collapse
- lexical / structural lock proxy

它**不是**：

- 再做一遍 illumination screening
- reasoning 分支替代品
- 最终 fusion verdict

## Capability assumptions

Stage 2 必须显式支持两条现实路径：

### With-logprobs pathway

- 可以读取 token-level probability / top-k mass / entropy 等信息
- 是 Stage 2 的主能力路径
- 提供更直接的 lock / concentration 特征

### Without-logprobs fallback pathway

- 当 API 不提供 token logprobs 时启用
- 不能假装与真正 logprobs 等价
- 通过 repeated sampling、lexical repetition、cross-run collapse 等 proxy 提供 verification evidence

Stage 2 必须在 artifacts 中显式记录 capability mode，并允许两条路径共享尽量一致的上层协议。

## With-logprobs pathway

当前默认冻结的 with-logprobs feature family 包括：

### Token confidence / concentration

- `average_top1_probability`
- `target_token_probability_mean`
- `topk_mass_concentration`
- `peak_probability`
- `probability_variance_collapse`

### Entropy / uncertainty

- `entropy_mean`
- `entropy_drop`
- `entropy_collapse_span`
- `uncertainty_decay_rate`

### Lock / span / persistence

- `lock_window_length`
- `longest_lock_span`
- `sustained_high_confidence_ratio`
- `lock_reentry_count`
- `sequence_lock_strength`

### Alignment / output-level support

- `target_alignment_proxy`
- `generation_consistency_flag`
- `abnormal_lock_bucket`

## Without-logprobs fallback pathway

当前默认冻结的 without-logprobs fallback feature family 包括：

### Repeated-sampling signals

- `repeated_sampling_consistency`
- `answer_mode_collapse`
- `sampled_output_agreement_rate`

### Lexical / structural lock proxy

- `repeated_phrase_concentration`
- `target_pattern_repetition_proxy`
- `response_diversity_drop`
- `lexical_lock_proxy`

### Cross-run stability

- `multi_run_output_collapse`
- `candidate_output_mode_count`
- `instability_inverse_proxy`

### Fallback risk / degradation

- `fallback_lock_risk_score`
- `fallback_mode_limit_flag`
- `verification_confidence_degradation_flag`

这些 proxy 只用于现实 API fallback setting，不应被表述成等价于 token-level confidence。

## Frozen scope

本阶段冻结的内容包括：

1. Confidence verification 的问题定义
2. with-logprobs / without-logprobs 双路径 capability contract
3. 两套 feature schema
4. unified public field contract
5. Stage 1 -> Stage 2 输入合同
6. Stage 2 -> Stage 3 输出公共字段
7. budget contract
8. no-logprobs fallback policy
9. confidence-only baseline / ablation contract
10. 可执行的 Stage 2 freeze pipeline、CLI、analysis 和 representative traces

## Non-goals

- 不做 Stage 3 budget-aware fusion 主体实现
- 不做完整论文实验矩阵
- 不做大规模真实 API 运行
- 不重定义 Stage 1 screening 口径
- 不把 reasoning 偷偷加回 Stage 2
- 不把 without-logprobs 伪装成真正 logprobs

## Feature schema design

Stage 2 冻结两套机器可读 feature schema：

- `dualscope_confidence_feature_schema_with_logprobs.json`
- `dualscope_confidence_feature_schema_without_logprobs.json`

每个特征都必须包含：

- feature_name
- level
- dtype
- semantic_meaning
- computation_note
- default_enabled
- fusion_compatible
- depends_on_logprobs

同时必须明确哪些 with-logprobs 特征拥有 fallback proxy。

## Lock evidence design

Stage 2 的 lock evidence 不是一个单指标，而是一个结构化 evidence bundle，至少包括：

- capability_mode
- evidence_type
- evidence_strength
- supporting_feature_names
- budget_usage
- mode_specific_limitations

输出层还必须有：

- `confidence_lock_evidence_present`
- `verification_risk_score`
- `verification_risk_bucket`
- `abnormal_lock_bucket`

## Input / output contract

### Required inputs

- `dataset_id`
- `example_id`
- `stage1_candidate_id`
- `stage1_screening_risk_score`
- `stage1_screening_risk_bucket`
- `confidence_verification_candidate_flag`
- `budget_usage_summary`
- `verification_budget_policy`
- `capability_mode`

### Optional inputs

- `template_results`
- `query_aggregate_features`
- `screening_summary_for_fusion`
- `reference_answer`
- `token_logprobs`
- `sampled_outputs`
- `target_text`
- `metadata`

### Emitted outputs

- `verification_feature_vector`
- `verification_evidence_summary`
- `verification_risk_score`
- `verification_risk_bucket`
- `confidence_lock_evidence_present`
- `budget_usage_summary`
- `confidence_public_fields`
- `fusion_public_fields`

## Budget contract

Stage 2 必须显式 budget-aware。冻结规则如下：

- 默认每个 candidate 的 verification budget 有上限
- repeated sampling 默认次数固定
- with-logprobs 和 without-logprobs 允许不同的预算分配
- 必须定义 `minimal_verification_budget`
- 必须定义 `no_logprobs_fallback_budget`
- 明确禁止当前阶段的高成本 calibration / 大 repeated-sampling expansion
- 保留 `future_extension_hooks`

## Minimal baseline design

本阶段冻结的最小 baseline / ablation contract 包括：

- confidence-only with-logprobs baseline
- confidence-only without-logprobs baseline
- fallback-only comparison placeholder
- future illumination+confidence naive concat placeholder
- future budget-aware fusion placeholder

## Compatibility with illumination screening

Stage 2 必须严格兼容 Stage 1 的既有协议，尤其是：

- `confidence_stage_readable_fields`
- `downstream_confidence_required_fields`
- `screening_risk_score`
- `screening_risk_bucket`
- `confidence_verification_candidate_flag`
- `budget_usage_summary`

Stage 2 只能消费 Stage 1 已经明确开放的字段，不能反过来重写 Stage 1 的问题定义。

## Compatibility with budget-aware fusion

Stage 2 必须显式输出 future fusion 所需的公共字段，包括：

- `capability_mode`
- `verification_risk_score`
- `verification_risk_bucket`
- `confidence_lock_evidence_present`
- `stage1_candidate_id`
- `stage1_screening_risk`
- `budget_usage_summary`
- `downstream_fusion_public_fields`

Stage 3 应读取这些字段实现：

- confidence-only baseline
- illumination+confidence naive concat
- budget-aware two-stage fusion

## Deliverables

- `.plans/dualscope-confidence-verification-with-without-logprobs.md`
- `src/eval/dualscope_confidence_common.py`
- `src/eval/dualscope_confidence_verification.py`
- `src/eval/post_dualscope_confidence_verification_analysis.py`
- `scripts/build_dualscope_confidence_verification_with_without_logprobs.py`
- `scripts/build_post_dualscope_confidence_verification_with_without_logprobs_analysis.py`
- `docs/dualscope_confidence_protocol.md`
- `docs/dualscope_confidence_feature_dictionary.md`
- `outputs/dualscope_confidence_verification_with_without_logprobs/default/*`
- `outputs/dualscope_confidence_verification_with_without_logprobs_analysis/default/*`

## Risks

- 当前阶段是 freeze module，不是大规模主实验，因此 representative traces 只能被解读为 protocol demonstration，而不是性能证明。
- without-logprobs fallback 如果说得过强，会误导成等价于真正 token logprobs；必须在 schema 和 report 中明确限制。
- 如果 Stage 2 公共字段设计不统一，后续 Stage 3 fusion 仍会重新发明接口。
- 如果 budget contract 不够具体，后续 cost analysis 口径会漂移。

## Milestones

- [x] M1：confidence problem / capability / feature / budget / IO scope frozen
- [x] M2：artifacts / implementation / CLI / executable freeze outputs completed
- [x] M3：single verdict and single recommendation completed

## Exit criteria

完成本计划时，仓库中必须已经存在：

- 机器可读的问题定义、capability contract、两套 feature schema、public field contract、Stage 1 -> Stage 2 contract、IO contract、budget contract、fallback policy、baseline plan
- 可执行的主流程 CLI 与后分析 CLI
- 代表性的 with-logprobs / without-logprobs details traces
- markdown report 与文档入口
- 与 Stage 1 和 future Stage 3 的显式接口位

同时必须满足：

- 不继续旧 route_c 主线
- 不改 benchmark truth 语义
- 不改 gate 语义
- 不提前做 fusion 主体
- 不把 reasoning 分支偷偷塞回来
