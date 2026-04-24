# 005 Reasoning Probe

## Purpose / Big Picture

TriScope-LLM 在 illumination 模块已经具备最小可运行与结构化 feature 输出之后，下一步需要实现第二条检测证据链：reasoning scrutiny。这个模块的任务不是把 CoS 或其他现有方法原样搬进仓库，而是构造一条适配 TriScope-LLM 统一框架的“推理捷径暴露”路径。

在统一框架中，reasoning 的角色是：比较模型在同一触发查询下的原始回答、显式推理文本和基于推理后的最终回答，从而观察模型是否出现 shortcut-like 的异常模式，并把这些观察先落成结构化原始结果，后续再抽取 reasoning features。

## Scope

### In Scope

- 设计最小 reasoning prompt contract
- 提供最小 prompt/template 组织方式
- 实现最小 reasoning probing CLI
- 支持本地 HuggingFace backend
- 输出 original answer / reasoning text / reasoned answer 三元结果
- 输出结构化 raw results、config snapshot、summary、log
- 基于现有 smoke/local model 跑通一次最小 reasoning smoke run

### Out of Scope

- contradiction judge
- 复杂 reasoning scoring
- feature fusion
- confidence / illumination 扩展
- 商业 API backend
- 完整实验矩阵

## Repository Context

本计划将衔接：

- `configs/models.yaml`
- 预计新增 `configs/reasoning.yaml`
- `outputs/poison_data_*`
- `outputs/local_models/tiny-gpt2-smoke`
- `scripts/`
- `src/probes/`
- 可选 `data/prompts/reasoning/`

同时需要保持与 004 illumination 模块一致的 artifact 组织风格：

- raw results JSONL
- config snapshot JSON
- summary JSON
- log 文件

## Deliverables

- 005 reasoning probe ExecPlan
- reasoning config profile
- minimal reasoning prompt template file
- `scripts/run_reasoning_probe.py`
- `src/probes/reasoning_probe.py`
- 一次最小 smoke reasoning 产物
- `src/features/reasoning_features.py`
- `scripts/extract_reasoning_features.py`
- sample-level reasoning feature JSONL / CSV
- run-level aggregated reasoning feature JSON
- repeatability summary and artifact acceptance outputs
- README 的后续用法补充（Milestone 3）

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: reasoning prompt contract、最小 probing CLI、三元输出 raw results、基础 summary
- [x] Milestone 2: reasoning feature extraction 与稳定 schema
- [x] Milestone 3: README 补充、repeatability 与 artifact 验收

## Surprises & Discoveries

- 当前仓库已经有可复用的本地 HuggingFace backend、manifest 读取逻辑和 smoke_local tiny causal LM，这使 reasoning M1 可以优先复用既有链路，而不是重新发明一套模型加载与数据入口。
- `outputs/poison_data_smoke/run_m2/dataset_manifest.json` 已经提供 `poisoned_dataset.jsonl` 路径与攻击元数据，因此 reasoning M1 可以直接围绕 triggered queries 构造 probing contract。
- M1 smoke run 证明：当前 dataset-manifest 已经足够支撑 reasoning 的最小三元输出，不需要先引入额外 benchmark 或 judge 文件。
- 本地 tiny smoke 模型在 reasoning prompt 下会明显回显 query，但仍能稳定给出非空的 `reasoning_text` 与和 direct answer 不同的 `reasoned_answer`，足以验证 reasoning raw schema 和 artifact 链路。
- M2 实现时确认：M1 的 raw result 已经保留了 `probe_id`、`sample_id`、`reasoning_profile`、`target_type`、`trigger_type`、三元文本和 target-behavior flags，因此可以直接抽 reasoning features，无需破坏性回改 M1 schema。
- 当前 smoke run 没有 judge-level contradiction annotation，因此 M2 的 reasoning features 先聚焦在长度、变化、flip 和 group summary，不引入额外模型判别器。
- M3 验证表明：在相同 seed、相同配置和相同本地 smoke 模型下，repeat run 的 `num_samples`、`answer_changed_rate`、`target_behavior_flip_rate` 与 `reasoning_length_mean` 与基准 run 一致，因此当前 reasoning MVP 已具备最小可复跑性。
- artifact acceptance 检查也表明：当前 reasoning 模块的默认 handoff artifact 集已经稳定，包括 raw results、config snapshot、summary、sample-level features、aggregated features 和 feature summary。

## Decision Log

- 决策：reasoning M1 以 `poisoned_only` 查询源为默认路径。
  - 原因：reasoning scrutiny 当前主要关注 trigger-activated 条件下的 shortcut 行为，先围绕已触发样本建立最小闭环更直接。
  - 影响范围：dataset-manifest 模式的查询选择与 summary 解释方式。

- 决策：reasoning M1 的核心产物固定为 `original_answer + reasoning_text + reasoned_answer` 三元输出。
  - 原因：这是后续判断“是否绕开正常推理”的最小原始证据，不需要在 M1 就引入复杂 judge。
  - 影响范围：raw result schema、prompt template 结构和 summary 字段。

- 决策：M1 只做原始结果与最小 summary，不提前实现 contradiction scoring 或 reasoning feature engineering。
  - 原因：当前目标是先建立可复现的 reasoning chain，而不是提前做研究最终版统计。
  - 影响范围：M1 与 M2 的边界，以及 CLI 输出内容。

- 决策：M1 直接复用 illumination 模块中的通用模型加载、generation 和基础文本判定函数，而不是现在就抽象一个更大的共享 backend 层。
  - 原因：这样能以最小改动快速打通 reasoning 主链路，同时避免在当前阶段过早重构 004/005。
  - 影响范围：`src/probes/reasoning_probe.py` 的实现方式，以及后续是否需要在更晚阶段抽出共享 backend helper。

- 决策：当前 reasoning M1 已稳定到“可作为下游 feature extraction 输入”的程度，但刻意不在本阶段引入 judge、contradiction score 或复杂 consistency metrics。
  - 原因：这些能力更适合放在 005/M2 做成稳定特征层，而不是混入 M1 的原始 probing 验收。
  - 影响范围：当前 raw result schema、summary 口径，以及 005 后续 milestone 的边界。

- 决策：M2 的 feature extraction 保持为独立后处理 CLI，而不是直接并入 `run_reasoning_probe.py`。
  - 原因：这样可以清晰地区分 raw probing 和 feature engineering，也便于对已有 raw results 反复重抽特征。
  - 影响范围：`src/features/reasoning_features.py`、`scripts/extract_reasoning_features.py`、artifact 组织方式。

- 决策：reasoning M2 采用“双层产物”设计：sample-level JSONL/CSV + run-level aggregated JSON。
  - 原因：fusion 更适合消费稳定的 sample-level machine-readable 特征，而 README 与分析更适合引用 run-level summary。
  - 影响范围：feature schema、输出命名和后续与 illumination / confidence 的对齐方式。

- 决策：M2 暂不引入 contradiction judge 或重型 consistency model，留白给后续增强。
  - 原因：当前目标是建立稳定特征接口，而不是为了“完整感”过早引入重依赖与不透明打分器。
  - 影响范围：当前特征集合、Remaining Risks 和后续 M3 / 006 / 007 的扩展边界。

- 决策：M3 额外补一个独立的 artifact acceptance / repeatability 检查器，而不是把这些校验混进 probing 或 feature extraction CLI。
  - 原因：reasoning 模块已经进入“可交接”阶段，需要有稳定、可重复运行的验收入口，供 confidence / fusion 阶段直接复用。
  - 影响范围：`scripts/validate_reasoning_artifacts.py`、`src/features/reasoning_artifact_checks.py`、`outputs/reasoning_runs/repeatability_*`。

- 决策：005 在当前阶段以“链路稳定 + schema 稳定 + artifact 完整”作为收口标准，不继续扩 judge-level contradiction scoring。
  - 原因：当前目标是让 reasoning 成为后续模块可消费的稳定组件，而不是在这一阶段提前做研究最终版 judge 系统。
  - 影响范围：005 的计划结束条件、README 描述，以及 006/007 的接口假设。

## Plan of Work

先定义 reasoning prompt contract 和最小配置，再实现一个复用本地 HuggingFace backend 的 probing CLI。该 CLI 会复用 poison dataset manifest 提供的 triggered queries，分别生成原始回答、显式推理文本和基于推理的最终回答，并将这三者以结构化 JSONL 与最小 summary 的形式落盘。M1 稳定之后，在 M2 中基于已有 raw results 抽取 sample-level 与 run-level reasoning features，形成可供后续 fusion 消费的 machine-readable artifact。

## Concrete Steps

1. 新建 `.plans/005-reasoning-probe.md` 并定义 milestone 边界。
2. 新增 `configs/reasoning.yaml`，定义 default 和 smoke profile。
3. 新增 `data/prompts/reasoning/` 下的最小 template 文件。
4. 实现 `src/probes/reasoning_probe.py`：
   - 读取 model profile、reasoning profile、dataset manifest / query file
   - 构造 reasoning prompt contract
   - 运行本地 HF generation
   - 落盘 raw result、summary、snapshot、log
5. 实现 `scripts/run_reasoning_probe.py` CLI。
6. 用本地 `smoke_local` 模型跑一次 smoke reasoning，并记录 artifact。
7. 实现 `src/features/reasoning_features.py`：
   - 从 `raw_results.jsonl` 读取 sample-level records
   - 生成 sample-level feature JSONL 与 CSV
   - 生成 run-level aggregated feature JSON 与 summary
8. 实现 `scripts/extract_reasoning_features.py` CLI。
9. 用本地 `smoke_local` 的 M1 raw results 跑一次 feature extraction smoke validation。
10. 更新 README 中的 reasoning 最小用法说明。
11. 用相同 seed 和配置完成一次 repeat run，并比较关键 feature summary 字段。
12. 运行 artifact acceptance 检查，确认默认 handoff artifact 集齐全。
13. 完成后更新 Progress、Decision Log、Remaining Risks。

## Validation and Acceptance

- `run_reasoning_probe.py --help` 可正常显示
- 支持 `--dataset-manifest` 或 `--query-file`
- 能成功构造 reasoning prompt contract
- 至少一次 reasoning run 能返回：
  - `original_answer`
  - `reasoning_text`
  - `reasoned_answer`
- 成功生成：
  - raw results JSONL
  - config snapshot JSON
  - summary JSON
  - log 文件
- smoke run 至少包含：
  - `sample_id`
  - `model_profile`
  - `reasoning_profile`
  - `reasoning_template_name`
  - `target_type`
  - `trigger_type`
  - `original_answer`
  - `reasoning_text`
  - `reasoned_answer`
- feature extraction CLI 能在 M1 的 `raw_results.jsonl` 上成功运行
- 成功生成：
  - sample-level feature JSONL
  - feature CSV
  - aggregated feature JSON
  - feature summary JSON
- aggregated feature 至少包含：
  - `answer_changed_rate`
  - `target_behavior_flip_rate`
  - `reasoning_length_mean`
  - `reasoning_length_std`
  - `answer_change_by_trigger_type`
  - `answer_change_by_target_type`
- smoke validation 至少通过一次简单读取检查，确认 JSON / CSV 非空且 `run_id`、`probe_id`、`sample_id` 等字段齐全
- README 至少补齐 reasoning probe 的输入、最小 CLI、feature extraction CLI 和主要输出说明
- repeatability 检查至少比较：
  - `num_samples`
  - `answer_changed_rate`
  - `target_behavior_flip_rate`
  - `reasoning_length_mean`
- artifact acceptance 检查确认以下默认路径均存在且可读：
  - `raw_results.jsonl`
  - `config_snapshot.json`
  - `summary.json`
  - `features/reasoning_prompt_level_features.jsonl`
  - `features/reasoning_features.json`
  - `features/feature_summary.json`

## Idempotence and Recovery

- reasoning CLI 支持重复运行到不同 `output_dir`
- 输出为 run-scoped artifact，不依赖隐式全局状态
- 若模型加载或 prompt 构造失败，应写出结构化 failure summary，便于恢复
- raw result JSONL 与 config snapshot 可作为后续 reasoning feature extraction 的恢复入口
- feature extraction CLI 可以基于已有 `raw_results.jsonl` 重跑，不依赖重新 probing
- feature artifact 默认写入独立 `output_dir`，避免覆盖 M1 原始产物

## Outputs and Artifacts

- `outputs/reasoning_*`
- `raw_results.jsonl`
- `config_snapshot.json`
- `summary.json`
- `probe.log`
- `reasoning_prompt_level_features.jsonl`
- `reasoning_features.csv`
- `reasoning_features.json`
- `feature_summary.json`
- `artifact_acceptance.json`
- `repeatability_summary.json`
- `repeat_check.log`

## M2 Feature Schema

M2 采用两层 reasoning feature schema：

### Sample-Level Feature Rows

每条 sample-level row 至少保留：

- `schema_version`
- `feature_family`
- `feature_level`
- `run_id`
- `probe_id`
- `sample_id`
- `model_profile`
- `reasoning_profile`
- `reasoning_template_name`
- `prompt_template_name`
- `trigger_type`
- `target_type`
- `seed`
- `original_is_target_behavior`
- `reasoned_is_target_behavior`
- `answer_changed_after_reasoning`
- `original_vs_reasoned_changed`
- `target_behavior_flip_flag`
- `reasoning_present_flag`
- `reasoning_nonempty_flag`
- `original_answer_length`
- `reasoning_length`
- `reasoned_answer_length`
- `reasoning_step_count`
- `reasoning_to_answer_length_ratio`
- `metadata`

### Run-Level Aggregated Features

run-level JSON 至少保留：

- `run_id`
- `model_profile`
- `reasoning_profile`
- `prompt_template_name`
- `seed`
- `num_samples`
- `answer_changed_rate`
- `target_behavior_flip_rate`
- `reasoning_length_mean`
- `reasoning_length_std`
- `reasoning_step_count_mean`
- `answer_change_by_trigger_type`
- `answer_change_by_target_type`
- `target_behavior_flip_by_trigger_type`
- `target_behavior_flip_by_target_type`

这两层 schema 都必须保持字段命名稳定，并允许后续通过 `run_id + probe_id + sample_id` 与 illumination / confidence 特征对齐。

## Remaining Risks

- 当前 reasoning MVP 已达到“可交接、可复用、可被后续 fusion 消费”的稳定程度，但它仍然是研究原型版本，而不是最终实验系统。
- 当前 reasoning M2 已能产出稳定的 machine-readable feature artifact，但这些特征仍主要基于字符串变化、长度与 flip 统计，不是研究最终版 judge-level 证据。
- 当前 smoke 仍会依赖本地 tiny causal LM，因此数值结果主要用于验证 schema 与 artifact，而不是代表真实模型上的 reasoning 异常表现。
- 当前 `reasoning_step_count` 只是基于换行、编号和句号的轻量近似统计，后续若需要更可信的 step-level 结构理解，还需要专门增强。
- 当前验收使用的是本地 tiny smoke 模型，因此 repeatability 只能证明当前链路稳定，不意味着 reasoning 信号已经在真实 backdoored LLM 上得到充分验证。
- 如果后续要让 reasoning 模块形成更强的研究证据，仍需在 006/007 之后，或更真实的本地模型条件下继续增强。

## Next Suggested Plan

若 005 完成，下一步建议创建 `.plans/006-confidence-probe.md`。
