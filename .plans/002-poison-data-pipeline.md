# 002 Poison Data Pipeline

## Purpose / Big Picture

TriScope-LLM 在 bootstrap 完成后，下一步最关键的真实能力是“可复现地构造带后门的训练数据”。没有稳定的 poison data pipeline，后续 LoRA 注毒训练、探针评估和误报分析都缺少统一输入来源。

本计划的目标是先做一个最小但真实可用的数据注毒流水线：它能够读取结构化样本、基于攻击配置选择要注毒的子集、应用 trigger/target 模板、保存可供训练直接消费的数据，以及保存后续 probe、fusion 和论文分析可复用的结构化中间产物。

## Scope

### In Scope

- 定义最小 poison dataset 输入输出契约
- 支持从 JSONL 读取干净样本
- 支持基于 `configs/attacks.yaml` 的 profile 构造注毒样本
- 提供 `scripts/build_poison_dataset.py` CLI
- 保存 poisoned dataset、summary、config snapshot、log 到 `outputs/`
- 运行一个最小 smoke example，证明 CLI 和输出格式可用

### Out of Scope

- 下载公开数据集
- LoRA / PEFT 训练
- 模型推理与 probe 逻辑
- fusion / eval 逻辑
- 多格式大而全数据适配层
- notebook 分析

## Repository Context

本计划主要涉及：

- `configs/attacks.yaml`
- `scripts/build_poison_dataset.py`
- `src/attacks/`
- `outputs/poison_data_*`
- `.plans/002-poison-data-pipeline.md`

这些产物将直接服务于后续 `003-lora-finetuning.md`，并为之后的 probe 阶段保留样本级结构化标签。

## Deliverables

- poison data pipeline 执行计划
- 一个可运行的 JSONL 注毒 CLI
- 最小核心实现模块
- 扩展后的攻击配置示例
- poisoned dataset 样例输出
- summary / config snapshot / log

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 实现最小 JSONL 注毒 CLI，并产出 smoke 输出样例
- [x] Milestone 2: 补充更稳定的输出清单与样本级元数据，便于训练和分析复用
- [x] Milestone 3: 补充使用说明与验收记录

## Surprises & Discoveries

- 当前仓库没有任何现成数据适配代码，因此本计划必须先定义一个最小而稳定的输入输出契约。
- 现有 `configs/attacks.yaml` 仅能表达 trigger/target 类型，尚不足以驱动真实的 target 文本生成，需要在不失控扩张的前提下补最小字段。
- 直接运行 `python3 scripts/build_poison_dataset.py` 时，`src` 包不会自动出现在 `sys.path` 中；CLI 入口需要显式补仓库根路径。
- 当前环境虽然不满足训练要求，但足以运行基于标准库和 YAML 的 poison data builder，因此该 milestone 可以继续推进而不被缺少训练依赖阻塞。
- 同一输入、同一 seed、同一 poison ratio 下，当前实现重复运行得到相同的 `poison_indices=[0, 2]`，满足最小复现性要求。
- 本地未找到 ICLScan、CoS、ConfGuard 的现成克隆代码；参考审查主要依赖 ICLScan 公开仓库主页和三篇论文/论文主页，笔记已整理到 `docs/reference_implementation_notes.md`。
- 从参考材料来看，当前阶段最值得吸收的是“显式配置 + 结构化中间产物 + query/statistic 意识”，而不是复制任何单一项目的目录结构。

## Decision Log

- 决策：第一版 poison data pipeline 只支持 JSONL 输入。
  - 原因：先把最小可运行闭环做实，比一开始同时兼容 CSV/Parquet 更符合 MVP 原则。
  - 影响范围：Milestone 1 的 CLI 输入格式、验证方式和 smoke example 设计。

- 决策：第一版输出同时保留 clean 与 poisoned 对照字段，而不是只输出训练最终文本。
  - 原因：后续训练、误报分析和探针研究都需要样本级对照证据链。
  - 影响范围：输出 JSONL 字段设计，以及后续特征/评估模块的可复用性。

- 决策：先复用 `configs/attacks.yaml` 中的 profile 机制，而不是再引入新的攻击配置中心。
  - 原因：当前阶段已有攻击配置入口，增量扩展比新增第二套配置文件更清晰。
  - 影响范围：攻击参数来源和 CLI 的默认配置路径。

- 决策：第一版输出记录同时包含 `clean_*`、`poisoned_*` 和 `train_*` 三组字段。
  - 原因：训练需要最终文本，分析需要 clean 对照，样本级证据链也需要显式指出真正被改写的内容。
  - 影响范围：`poisoned_dataset.jsonl` 的 schema，以及后续训练/分析模块的读取方式。

- 决策：样本选择使用 `ceil(num_records * poison_ratio)` 而不是 `floor(...)`。
  - 原因：在小样本 smoke test 和小规模实验里，`floor` 容易让正的 poison ratio 退化成 0 条 poisoned sample。
  - 影响范围：小数据集上的 realized poison ratio，以及 smoke example 的最小验收稳定性。

- 决策：第一版只支持 `text_suffix` / `instruction_prefix` 两种 trigger，以及 `fixed_response` / `style_shift` 两种 target。
  - 原因：这四种类型已经足以支撑最小真实闭环，同时保持实现透明。
  - 影响范围：`configs/attacks.yaml` 的当前可用 profile 语义，以及后续模板扩展路径。

- 决策：增加 `poison_statistics.json` 与 `dataset_manifest.json`，并在样本级记录中保存 `schema_version`、长度信息、应用标记和 `source_record`。
  - 原因：后续 LoRA 训练需要稳定可读的输入契约，分析与误报排查也需要保留原始上下文和结构化清单。
  - 影响范围：`poisoned_dataset.jsonl` 的稳定 schema，以及下游训练/分析脚本的读取入口。

- 决策：参考实现审查只吸收方法细节，不复制外部项目结构。
  - 原因：TriScope-LLM 必须保持统一证据链架构，不能退化成 ICLScan / CoS / ConfGuard 的并排拼装。
  - 影响范围：当前 poison pipeline 的输出设计，以及后续 illumination / reasoning / confidence 模块的实现边界。

- 决策：当前阶段从 ICLScan 主要吸收“显式攻击配置 + 运行产物落盘”，从 CoS 吸收“中间过程应保存为可审计结构化结果”，从 ConfGuard 吸收“统计信号要和原始轨迹分离”。
  - 原因：这些点与 TriScope-LLM 的统一研究原型目标一致，且对当前和后续 milestone 都有直接价值。
  - 影响范围：`docs/reference_implementation_notes.md`、poison pipeline 产物设计，以及未来 probe/fusion 模块的 artifact 组织方式。

- 决策：`dataset_manifest.json` 的 `sample_fields` 必须显式声明 `schema_version`，以便后续训练 dry-run 能严格校验 schema 契约。
  - 原因：003/M1 需要依赖 manifest 做训练输入验证，字段声明必须与样本实际 schema 完整对齐。
  - 影响范围：poison pipeline 的 manifest 结构，以及后续训练入口的 manifest 消费逻辑。

## Plan of Work

先定义第一版 poison sample schema，并实现一个可以从 JSONL 读入、根据攻击配置选样、应用最小 trigger/target 规则、再写出结构化结果的核心模块；然后用脚本把它暴露成稳定 CLI，并跑一个最小 smoke example 生成真实输出；之后再补输出清单、README 使用说明和进一步的验证记录。

整个路径都以“后续训练和研究分析可复用”为目标，因此每条样本除了最终训练文本，还应保存 clean 对照、攻击 profile、是否被注毒等元信息。

## Concrete Steps

1. 扩展 `configs/attacks.yaml`，补足驱动最小注毒逻辑所需的 target 文本与分隔字段。
2. 在 `src/attacks/` 中实现 JSONL 读取、样本选择、trigger 注入、target 生成与结果写出逻辑。
3. 在 `scripts/` 下新增 `build_poison_dataset.py`，支持 `--help`、输入路径、输出路径、seed、config/profile 等参数。
4. 用一个小型 smoke input 运行 CLI，生成 `poisoned_dataset.jsonl`、`poison_summary.json`、`config_snapshot.json`、`build.log`。
5. 更新计划进度、关键决策和剩余风险。

## Validation and Acceptance

Milestone 1 完成时，应至少满足：

- `python3 scripts/build_poison_dataset.py --help` 能正常运行
- CLI 能读取 JSONL 并输出结构化 `poisoned_dataset.jsonl`
- 输出样本至少包含 clean 文本、train 文本、是否注毒、攻击 profile 等关键字段
- 输出目录中同时存在 summary、config snapshot、log
- 同一 seed 下重复运行，样本选择结果稳定
- smoke example 能生成至少 1 条 poisoned sample

## Idempotence and Recovery

- CLI 重复运行时允许覆盖同一输出目录中的结果文件。
- 若中途中断，只要输入 JSONL 和攻击配置未变，可直接重新运行同一命令恢复。
- `poisoned_dataset.jsonl`、`poison_summary.json` 和 `config_snapshot.json` 是后续阶段的核心中间产物，应保留。

## Outputs and Artifacts

- `outputs/poison_data_*/poisoned_dataset.jsonl`
- `outputs/poison_data_*/poison_summary.json`
- `outputs/poison_data_*/config_snapshot.json`
- `outputs/poison_data_*/build.log`

## Remaining Risks

- 第一版只支持 JSONL，后续若对接公开数据集，可能还需要补更多输入适配。
- 第一版 trigger/target 规则会保持非常透明，但覆盖面有限，后续需要逐步扩充模板能力。
- 当前实际环境缺少部分训练/分析依赖，但本 milestone 只使用标准库与 YAML，不应被这些问题阻塞。
- 当前虽然已有 manifest 和基础统计，但还没有专门面向训练的 split manifest 或样本分桶文件，若后续训练阶段需要更快读取，可能仍需补轻量索引。
- `reference` profile 已完成最小 smoke run，但更复杂的 target 模板、多任务字段映射和更大样本输入还未系统验证。

## Next Suggested Plan

完成本计划后，下一步建议创建 `.plans/003-lora-finetuning.md`。
