# 006 Confidence Probe

## Purpose / Big Picture

TriScope-LLM 在 illumination 与 reasoning 两条证据链已经具备最小可运行与结构化输出之后，下一步需要实现第三条检测证据链：confidence collapse。这个模块的任务不是提前搭出完整统计系统，而是先建立一条最小但可复现的“token-level / step-level 置信结构暴露”链路。

在统一框架中，confidence 的角色是：在触发条件下观察模型生成过程中的 token 置信度、分支收缩和 sequence lock 风格模式。M1 的目标不是给出最终研究统计，而是先把 prompt/generation contract、最小 probing CLI、token-level 原始结果和 summary 稳定落盘。

## Scope

### In Scope

- 设计最小 confidence prompt / generation contract
- 提供最小 prompt/template 组织方式
- 实现最小 confidence probing CLI
- 支持本地 HuggingFace backend
- 输出 token-level 或 step-level 原始置信结果
- 输出结构化 raw results、config snapshot、summary、log
- 基于现有 smoke/local model 跑通一次最小 confidence smoke run

### Out of Scope

- 复杂 confidence feature engineering
- fusion / eval 逻辑
- reasoning / illumination 扩展
- 商业 API backend
- 大规模实验矩阵

## Repository Context

本计划将衔接：

- `configs/models.yaml`
- 预计新增 `configs/confidence.yaml`
- `outputs/poison_data_*`
- `outputs/local_models/tiny-gpt2-smoke`
- `scripts/`
- `src/probes/`
- 可选 `data/prompts/confidence/`

同时需要保持与 004 / 005 一致的 artifact 组织风格：

- raw results JSONL
- config snapshot JSON
- summary JSON
- log 文件

## Deliverables

- 006 confidence probe ExecPlan
- confidence config profile
- minimal confidence prompt template file
- `scripts/run_confidence_probe.py`
- `src/probes/confidence_probe.py`
- 一次最小 smoke confidence 产物
- `src/features/confidence_features.py`
- `scripts/extract_confidence_features.py`
- confidence prompt-level / sample-level feature artifacts
- confidence aggregated feature JSON / CSV / feature summary

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: confidence prompt / generation contract、最小 probing CLI、token-level raw results、基础 summary
- [x] Milestone 2: confidence feature extraction 与稳定 schema
- [x] Milestone 3: README 补充、repeatability 与 artifact 验收

## Surprises & Discoveries

- 当前仓库已经有可复用的本地 HuggingFace backend、manifest 读取逻辑和 smoke_local tiny causal LM，这使 confidence M1 可以优先复用既有链路，而不是重建一套推理后端。
- 现有 smoke 模型虽然不适合做研究结论，但足以验证 `generate(..., output_scores=True)` 的 token-level 结果落盘链路。
- M1 smoke run 证明：当前本地 tiny causal LM 在 confidence 路径下可以稳定返回每一步的 logits-derived probability、entropy 和 top-k token 列表，因此 token-level raw schema 已经成立。
- 当前 smoke 模型在 greedy generation 下会大量输出 `<pad>`，导致 `response_text` 近乎为空；这不会阻塞 confidence 原始分数链路，但说明当前 smoke run 更适合验证 artifact，而不适合解释生成质量。

## Decision Log

- 决策：confidence M1 默认围绕 `poisoned_only` 查询源工作。
  - 原因：当前 confidence collapse 的最小链路主要关注 trigger-activated 条件下的生成置信结构。
  - 影响范围：dataset-manifest 模式的查询选择与 summary 解释方式。

- 决策：M1 直接输出 token-level / step-level raw results，不提前做复杂 collapse 指标。
  - 原因：当前目标是先稳定原始证据链，而不是提前固化研究最终版统计口径。
  - 影响范围：raw result schema、summary 设计和 M2 的边界。

- 决策：M1 复用本地 HuggingFace `generate(..., output_scores=True, return_dict_in_generate=True)` 路径。
  - 原因：这条链路透明、可调试，也足以提供最小 token-level 置信数据。
  - 影响范围：`src/probes/confidence_probe.py` 的实现方式与模型后端依赖。

- 决策：M1 的 summary 暂时只聚焦 `generated_token_count`、`mean_chosen_token_prob`、`min_chosen_token_prob` 和 `mean_step_entropy`。
  - 原因：这些统计足以证明 confidence 原始分数链路已经打通，同时不会过早把研究最终版 collapse 指标硬编码进 M1。
  - 影响范围：当前 `summary.json` 字段口径，以及 M2 的扩展空间。

- 决策：M2 采用“raw probing 与 feature extraction 显式分离”的设计。
  - 原因：confidence 原始 token-level 结果应保持可审计，后处理统计不应与 probing 主路径混成一体。
  - 影响范围：新增 `src/features/confidence_features.py` 与 `scripts/extract_confidence_features.py`，M1 artifact 保持不变。

- 决策：M2 的 sequence-lock / collapse 指标先采用轻量统计版本。
  - 原因：当前阶段目标是稳定 machine-readable feature schema，而不是过早固化复杂理论判别器。
  - 影响范围：优先落地 `high_confidence_fraction`、`max_consecutive_high_confidence_steps`、`confidence_slope`、`entropy_slope` 和 `entropy_collapse_score`，更高级 detector 留到后续。

- 决策：M2 默认使用 `high_confidence_threshold=0.10` 做轻量高置信统计。
  - 原因：当前 tiny smoke run 的 chosen-token probability 大多处于 0.06-0.12 区间，0.10 能产生可读但不过于极端的 run-length 信号。
  - 影响范围：sample-level 高置信相关特征、aggregated summary 以及后续 repeatability 的口径。

- 决策：M3 为 confidence 模块新增独立 artifact acceptance / repeatability CLI。
  - 原因：confidence 需要像 illumination 与 reasoning 一样具备可交接的验收入口，而不是把收口逻辑散落在临时命令里。
  - 影响范围：新增 `src/features/confidence_artifact_checks.py` 与 `scripts/validate_confidence_artifacts.py`，README 中的 confidence artifact 路径说明。

- 决策：006 在 M3 后整体收口，不继续在本阶段扩 detector 复杂度。
  - 原因：当前 confidence 已具备 raw probe、feature extraction、repeatability 与 artifact acceptance，已经满足进入 fusion 数据对齐阶段的最小要求。
  - 影响范围：更强的 detector / online defense / richer collapse analysis 留到后续计划，而不是继续膨胀 006。

## Plan of Work

先定义 confidence prompt / generation contract 和最小配置，再实现一个复用本地 HuggingFace backend 的 probing CLI。该 CLI 会复用 poison dataset manifest 提供的 triggered queries，运行最小 generation，并把每一步的所选 token、所选概率、top-k 候选和简单 summary 落盘。M1 稳定之后，在 M2 中从 `token_steps` 抽取稳定的 confidence features，并产出 JSONL / CSV / JSON / feature summary 四类 machine-readable artifact。

## Concrete Steps

1. 新建 `.plans/006-confidence-probe.md` 并定义 milestone 边界。
2. 新增 `configs/confidence.yaml`，定义 default 和 smoke profile。
3. 新增 `data/prompts/confidence/` 下的最小 template 文件。
4. 实现 `src/probes/confidence_probe.py`：
   - 读取 model profile、confidence profile、dataset manifest / query file
   - 构造 confidence prompt contract
   - 运行本地 HF generation 并捕获 token-level scores
   - 落盘 raw result、summary、snapshot、log
5. 实现 `scripts/run_confidence_probe.py` CLI。
6. 用本地 `smoke_local` 模型跑一次 smoke confidence，并记录 artifact。
7. 实现 `src/features/confidence_features.py`：
   - 从 `raw_results.jsonl` 读取 token-level 结果
   - 提取长度、概率、熵、sequence-lock 风格和 target-behavior 相关特征
   - 产出 sample-level JSONL / CSV、aggregated JSON 和 feature summary
8. 实现 `scripts/extract_confidence_features.py` CLI，并在 M1 smoke run 上完成验证。
9. 实现 `src/features/confidence_artifact_checks.py` 与 `scripts/validate_confidence_artifacts.py`。
10. 用相同 seed 重跑一次 confidence smoke probing 和 feature extraction，验证 repeatability。
11. 更新 README 的 confidence 用法与 artifact 说明。
12. 完成后更新 Progress、Decision Log、Remaining Risks。

## Validation and Acceptance

- `run_confidence_probe.py --help` 可正常显示
- 支持 `--dataset-manifest` 或 `--query-file`
- 能成功构造 confidence prompt / generation contract
- 至少一次 confidence run 能返回 token-level 或 step-level 结果
- 成功生成：
  - raw results JSONL
  - config snapshot JSON
  - summary JSON
  - log 文件
- smoke run 至少包含：
  - `sample_id`
  - `model_profile`
  - `confidence_profile`
  - `confidence_template_name`
  - `target_type`
  - `trigger_type`
  - `response_text`
  - `token_steps`
- M2 feature extraction 能直接消费 M1 的 `raw_results.jsonl`
- 成功生成：
  - `confidence_prompt_level_features.jsonl`
  - `confidence_features.csv`
  - `confidence_features.json`
  - `feature_summary.json`
- sample-level feature 至少包含：
  - `run_id`
  - `probe_id`
  - `sample_id`
  - `model_profile`
  - `confidence_profile`
  - `trigger_type`
  - `target_type`
  - `num_token_steps`
  - `mean_chosen_token_prob`
  - `mean_entropy`
  - `high_confidence_fraction`
  - `max_consecutive_high_confidence_steps`
  - `is_target_behavior`
- run-level feature 至少包含：
  - `target_behavior_rate`
  - `mean_chosen_token_prob_mean`
  - `mean_entropy_mean`
  - `high_confidence_fraction_mean`
  - `entropy_collapse_score_mean`
  - `target_behavior_by_trigger_type`
  - `target_behavior_by_target_type`

## Idempotence and Recovery

- confidence CLI 支持重复运行到不同 `output_dir`
- 输出为 run-scoped artifact，不依赖隐式全局状态
- 若模型加载或 generation 失败，应写出结构化 failure summary，便于恢复
- raw result JSONL 与 config snapshot 可作为后续 confidence feature extraction 的恢复入口

## Outputs and Artifacts

- `outputs/confidence_*`
- `raw_results.jsonl`
- `config_snapshot.json`
- `summary.json`
- `probe.log`
- `features/confidence_prompt_level_features.jsonl`
- `features/confidence_features.csv`
- `features/confidence_features.json`
- `features/feature_summary.json`

## Remaining Risks

- 当前 M1 只会验证 confidence probing 的链路稳定性，不代表 confidence signal 已经具有研究级判别力。
- 当前 smoke 仍会依赖本地 tiny causal LM，因此 token probability 结果主要用于验证 schema 与 artifact，而不是代表真实模型上的 collapse 模式。
- 当前 M2 的 sequence-lock / collapse 指标仍是轻量统计版本，不等价于完整 confidence detector。
- 当前 smoke tiny 模型会大量生成 `<pad>`，因此 `response_text` 与自然语言质量不适合作为研究结论依据；当前更适合观察 token probability 与 entropy 轨迹。
- 当前 repeatability 是在相同 tiny smoke model、相同 seed 和相同输入条件下验证的，还没有覆盖更真实模型或更复杂生成策略。
- 如果后续要让 confidence 模块形成更强的研究证据，仍需在后续阶段补更真实模型条件下的对照分析、更强 detector，以及 online defense 风格验证。

## Next Suggested Plan

若 006 完成，下一步建议创建 `.plans/007-fusion-and-eval.md`。
