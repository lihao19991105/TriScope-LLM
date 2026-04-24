# 004 Illumination Probe

## Purpose / Big Picture

TriScope-LLM 在完成注毒数据构造与最小 LoRA 训练闭环之后，下一步需要实现第一条真正面向“黑盒检测证据”的探针链路：illumination probe。这个模块的任务不是机械复刻 ICLScan，而是以 TriScope-LLM 的统一框架为中心，构造一条最小但可复现的“异常易感性暴露”路径。

在统一框架里，illumination 的角色是：通过 targeted ICL / trigger-conditioned exemplars，暴露模型在黑盒交互下对异常上下文的易感性，并把这种易感性转化为结构化原始结果和后续可抽取的特征。MVP 完成后，仓库应至少能够构造 probing prompt、调用本地 HuggingFace 模型、落盘原始 probing 结果、输出基础统计，并为下一步 feature extraction 留下稳定输入格式。

## Scope

### In Scope

- 设计 illumination prompt contract
- 提供最小 prompt/template 组织方式
- 实现最小 probing CLI
- 支持本地 HuggingFace backend
- 输出结构化 probing raw results、config snapshot、summary、log
- 基于现有 smoke/local model 跑通一次最小 probing smoke run

### Out of Scope

- reasoning / confidence 模块
- fusion / eval 逻辑
- 完整实验矩阵
- 商业 API backend
- 大模型专门适配
- illumination feature engineering beyond minimal summary

## Repository Context

本计划将衔接：

- `configs/models.yaml`
- 新增 `configs/illumination.yaml`
- `outputs/poison_data_*`
- `outputs/local_models/tiny-gpt2-smoke`
- `scripts/`
- `src/probes/`
- 可选 `data/prompts/illumination/`

同时需要保持与现有训练和数据产物风格一致，尤其是：

- dataset manifest / JSONL 的读取方式
- config snapshot / summary / log 的输出组织
- `outputs/` 下的结构化 artifact 命名

## Deliverables

- 004 illumination probe ExecPlan
- illumination config profile
- minimal illumination prompt template file
- `scripts/run_illumination_probe.py`
- `src/probes/illumination_probe.py`
- 一次最小 smoke probing 产物
- `src/features/illumination_features.py`
- `scripts/extract_illumination_features.py`
- prompt-level feature-ready JSONL / CSV
- run-level aggregated illumination feature JSON
- repeatability summary and artifact acceptance outputs
- README 的后续用法补充（Milestone 3）

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: prompt contract、最小 probing CLI、raw result 落盘、基础 summary
- [x] Milestone 2: feature extraction 与 alpha/budget/trigger 维度 summary
- [x] Milestone 3: README 补充、smoke repeatability 与 artifact 验收

## Surprises & Discoveries

- 当前仓库已有 poison dataset manifest、local tiny smoke model 和最小 LoRA smoke train 结果，这使 illumination M1 可以优先用本地小模型打通，不必一开始就绑定外网模型。
- 默认工作沙箱不暴露 GPU，因此 illumination smoke probing 更适合优先走本地小模型 + CPU 或轻量 GPU 路径，重点验证链路和 artifact，而不是模型效果。
- 现有 `configs/detection.yaml` 已含有 `alpha`、`query_budget` 等字段，但 illumination M1 仍需要独立的 prompt/template 与 generation 配置，因此更适合新增单独的 `configs/illumination.yaml`。
- 基于当前 poison dataset 的样本规模，`alpha=0.5 + num_icl_examples=2` 对 smoke probing 最稳妥：每个 prompt 包含 1 条 clean exemplar 和 1 条 backdoor exemplar，既满足 illumination 语义，也不会因为样本池太小导致 prompt 退化。
- 本地 `smoke_local` tiny GPT-style 模型可以稳定返回响应，但生成内容会明显回显 prompt，因此当前 raw result 更适合用于验证链路与字段，而不是直接解读研究效果。
- M2 实现时确认：M1 的 raw result schema 已经保留了 `sample_id`、`prompt_id`、`alpha`、`budget`、`trigger_type`、`target_type` 和 exemplar metadata，因此不需要回头破坏性修改 probing 输出。
- 当前 smoke run 没有 `alpha=0` 的自然 baseline，所以 `delta_target_behavior_rate` 在 schema 中保留，但当前 run 的值会稳定写成 `null`，并显式标注来源为 `no_alpha_zero_baseline`。
- M3 验证表明：在相同 seed、相同配置和相同本地 smoke 模型下，repeat run 的 `num_prompts`、`num_target_behavior`、`target_behavior_rate` 与 `realized_budget_ratio` 与基准 run 完全一致，因此当前 illumination MVP 已具备最小可复跑性。
- artifact acceptance 检查也表明：当前 illumination 模块的默认 handoff artifact 集已经稳定，包括 raw results、config snapshot、summary、prompt-level features、aggregated features 和 feature summary。

## Decision Log

- 决策：illumination M1 的输入主入口优先使用 poison dataset manifest / dataset JSONL，而不是先引入独立复杂 benchmark 数据格式。
  - 原因：现有仓库已经稳定产出 poisoned dataset 和 manifest，直接复用可以更快打通 probing 闭环，并保持 artifact 风格一致。
  - 影响范围：CLI 参数、prompt contract 和 smoke run 数据来源。

- 决策：illumination prompt contract 采用“clean examples + backdoor examples + final test query”的最小 targeted ICL 结构。
  - 原因：这最贴近 illumination 要暴露的“异常上下文易感性”，同时避免一开始设计过于复杂的 prompt 系统。
  - 影响范围：prompt template 文件、raw result schema 和后续 feature extraction 输入格式。

- 决策：M1 只产出 raw probing results 与最小 summary，不提前实现完整 feature engineering。
  - 原因：当前目标是先打通 probe chain，而不是过早做特征工程。
  - 影响范围：M1 与 M2 的边界、CLI 输出和计划节奏。

- 决策：模型 backend 优先支持本地 HuggingFace causal LM。
  - 原因：符合 AGENTS.md 的默认资源约束，也便于复用 `smoke_local` 模型完成最小验证。
  - 影响范围：`src/probes/illumination_probe.py` 的模型加载逻辑和 smoke run 方案。

- 决策：M1 的 query-file 模式采用“显式 prompt contract JSONL”而不是额外自动推断逻辑。
  - 原因：dataset-manifest 模式已经承担了自动构造 contract 的职责，而 query-file 模式更适合作为外部查询集或手工 probing 样例的显式入口。
  - 影响范围：CLI 输入格式、prompt contract 文档和后续自定义 probing 的可扩展性。

- 决策：M1 的 target behavior 判定先采用基于 `target_text` 的最小 substring 匹配。
  - 原因：这足以支撑最小闭环，同时不提前把更复杂的语义判定、rule-based normalization 或 classifier 引进本阶段。
  - 影响范围：raw result 字段 `is_target_behavior`、summary 统计口径，以及 M2 可能扩展的特征工程。

- 决策：M2 的 feature extraction 保持为独立后处理 CLI，而不是直接塞进 `run_illumination_probe.py` 的主逻辑。
  - 原因：这样可以清楚区分“原始 probing”与“feature engineering”，也便于后续对同一批 raw results 反复重抽特征。
  - 影响范围：`src/features/`、`scripts/extract_illumination_features.py`、artifact 组织方式。

- 决策：illumination feature schema 采用“双层产物”设计：prompt-level JSONL/CSV + run-level aggregated JSON。
  - 原因：fusion 更适合消费稳定、machine-readable 的样本级或 prompt 级特征，而统计分析与 README 更适合引用聚合后的 run-level 特征摘要。
  - 影响范围：feature artifact 命名、后续与 reasoning / confidence 的对齐方式。

- 决策：M2 的对齐主键保留 `run_id + probe_id + sample_id + source_sample_ids`。
  - 原因：当前 illumination prompt 是围绕 test query 构造的，`sample_id` 能表示主查询样本，但 exemplar 组合也需要保留，供后续 fusion 与误报分析追踪证据链。
  - 影响范围：prompt-level feature schema、CSV 导出字段与后续对齐逻辑。

- 决策：M3 额外补一个独立的 artifact acceptance / repeatability 检查器，而不是把这些校验散落在 README 或一次性命令里。
  - 原因：illumination 模块已经进入“可交接”阶段，需要有稳定、可重复运行的验收入口，供后续 reasoning / confidence / fusion 阶段直接复用。
  - 影响范围：`scripts/validate_illumination_artifacts.py`、`src/features/illumination_artifact_checks.py`、`outputs/illumination_runs/repeatability_*`。

- 决策：004 在当前阶段以“链路稳定 + schema 稳定 + artifact 完整”作为收口标准，不继续扩张 illumination 实验矩阵。
  - 原因：当前目标是让 illumination 成为后续模块可消费的稳定组件，而不是在这一阶段提前做研究最终版实验系统。
  - 影响范围：004 计划结束条件、README 描述，以及后续 005/006/007 的接口假设。

## Plan of Work

先定义 illumination 的 prompt contract 和最小配置，再实现一个只依赖本地 HuggingFace backend 的 probing CLI。该 CLI 会复用 poison dataset manifest 提供的 clean / poisoned 样本池，按 `alpha` 和 `query_budget` 选择 exemplar 与 test query，构造 targeted ICL prompt，返回结构化原始结果和基础 summary。等 M1 跑通后，再进入 M2 做 feature extraction 与维度统计。

## Concrete Steps

1. 新建 `.plans/004-illumination-probe.md` 并明确 milestone 边界。
2. 新增 `configs/illumination.yaml`，定义默认和 smoke profile。
3. 新增 `data/prompts/illumination/` 下的最小 template 文件。
4. 实现 `src/probes/illumination_probe.py`：
   - 读取 model profile、illumination profile、dataset manifest / query file
   - 构造 prompt contract
   - 运行本地 HF generation
   - 落盘 raw result、summary、snapshot、log
5. 实现 `scripts/run_illumination_probe.py` CLI。
6. 实现 `src/features/illumination_features.py`：
   - 从 `raw_results.jsonl` 读取 prompt-level records
   - 生成 prompt-level feature-ready JSONL 与 CSV
   - 生成 run-level aggregated feature JSON 与 summary
7. 实现 `scripts/extract_illumination_features.py` CLI。
8. 用本地 `smoke_local` 模型的 M1 raw results 跑一次 feature extraction smoke validation。
9. 更新 README 中的 illumination 最小用法说明。
10. 用相同 seed 和配置完成一次 repeat run，并比较关键 feature summary 字段。
11. 运行 artifact acceptance 检查，确认默认 handoff artifact 集齐全。
12. 完成后更新 Progress、Decision Log、Remaining Risks。

## Validation and Acceptance

- `run_illumination_probe.py --help` 可正常显示
- 支持 `--dataset-manifest` 或 `--query-file`
- 能成功构造 illumination prompt
- 至少一次 probing run 能返回模型响应
- 成功生成：
  - raw results JSONL
  - config snapshot JSON
  - summary JSON
  - log 文件
- smoke run 至少包含：
  - `sample_id`
  - `model_profile`
  - `target_type`
  - `trigger_type`
  - `alpha`
  - `budget`
  - `prompt_template_name`
  - `response_text`
  - `is_target_behavior`
- feature extraction CLI 能在 M1 的 `raw_results.jsonl` 上成功运行
- 成功生成：
  - prompt-level feature JSONL
  - feature CSV
  - aggregated feature JSON
  - feature summary JSON
- aggregated feature 至少包含：
  - `num_prompts`
  - `num_target_behavior`
  - `target_behavior_rate`
  - `success_rate_by_alpha`
  - `success_rate_by_budget`
  - `success_rate_by_trigger_type`
  - `success_rate_by_target_type`
  - `success_rate_by_template`
  - `variance_across_prompts`
  - `target_behavior_std`
  - `realized_budget_ratio`
- smoke validation 至少通过一次简单读取检查，确认 JSON / CSV 非空且 `run_id`、`probe_id`、`sample_id` 等字段齐全
- README 至少补齐 illumination probe 的输入、最小 CLI、feature extraction CLI 和主要输出说明
- repeatability 检查至少比较：
  - `num_prompts`
  - `num_target_behavior`
  - `target_behavior_rate`
  - `realized_budget_ratio`
- artifact acceptance 检查确认以下默认路径均存在且可读：
  - `raw_results.jsonl`
  - `config_snapshot.json`
  - `summary.json`
  - `features/prompt_level_features.jsonl`
  - `features/illumination_features.json`
  - `features/feature_summary.json`

## Idempotence and Recovery

- probing CLI 支持重复运行到不同 `output_dir`
- 输出为 run-scoped artifact，不依赖隐式全局状态
- 若模型加载或 prompt 构造失败，应写出结构化 failure summary，便于恢复
- raw result JSONL 与 config snapshot 可作为后续 feature extraction 的恢复入口
- feature extraction CLI 可以基于已有 `raw_results.jsonl` 重跑，不依赖重新 probing
- feature artifact 默认写入独立 `output_dir`，避免覆盖 M1 原始产物

## Outputs and Artifacts

- `outputs/illumination_*`
- `raw_results.jsonl`
- `config_snapshot.json`
- `summary.json`
- `probe.log`
- `prompt_level_features.jsonl`
- `illumination_features.csv`
- `illumination_features.json`
- `feature_summary.json`
- `artifact_acceptance.json`
- `repeatability_summary.json`
- `repeat_check.log`

## M2 Feature Schema

M2 采用两层 illumination feature schema：

### Prompt-Level Feature Rows

每条 prompt-level row 至少保留：

- `schema_version`
- `feature_family`
- `feature_level`
- `run_id`
- `probe_id`
- `sample_id`
- `source_sample_ids`
- `model_profile`
- `illumination_profile`
- `prompt_template_name`
- `target_type`
- `trigger_type`
- `alpha`
- `budget`
- `query_budget_requested`
- `query_budget_realized`
- `query_budget_realized_ratio`
- `is_target_behavior`
- `target_behavior_label`
- `response_length`
- `metadata`

### Run-Level Aggregated Features

run-level JSON 至少保留：

- `run_id`
- `model_profile`
- `illumination_profile`
- `prompt_template_name`
- `seed`
- `query_budget_requested`
- `query_budget_realized`
- `realized_budget_ratio`
- `num_prompts`
- `num_target_behavior`
- `target_behavior_rate`
- `variance_across_prompts`
- `target_behavior_std`
- `delta_target_behavior_rate`
- `success_rate_by_alpha`
- `success_rate_by_budget`
- `success_rate_by_trigger_type`
- `success_rate_by_target_type`
- `success_rate_by_template`

这两层 schema 都必须保持字段命名稳定，并允许后续通过 `run_id + probe_id + sample_id` 与 reasoning / confidence 特征对齐。

## Remaining Risks

- 当前 illumination MVP 已达到“可交接、可复用、可被后续 fusion 消费”的稳定程度，但它仍然是研究原型版本，而不是最终实验系统。
- 当前聚合特征仍以单次 run 和二值 `is_target_behavior` 为中心，不代表 illumination 统计口径已经定型到研究最终版。
- 当前 smoke run 的 `alpha`、`budget`、`trigger_type` 与 `target_type` 维度很窄，因此 group-level 统计更多是在验证 schema 和 artifact，而不是提供有代表性的实验结论。
- `delta_target_behavior_rate` 只有在同一 run 或同批 artifact 中存在合适 baseline（例如 `alpha=0`）时才有自然语义；当前 schema 会保留该字段，但允许取 `null`。
- 当前验收使用的是本地 tiny smoke 模型，因此 repeatability 只能证明当前链路稳定，不意味着 illumination 信号已经在真实 backdoored LLM 上得到充分验证。
- 若后续需要更接近真实 backdoored LLM 的 illumination 效果，仍需在 005/006/007 之后，或更真实的本地模型条件下继续增强。

## Next Suggested Plan

若 004 完成，下一步建议创建 `.plans/005-reasoning-probe.md`。
