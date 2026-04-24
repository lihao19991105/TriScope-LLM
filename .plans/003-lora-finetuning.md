# 003 LoRA Finetuning

## Purpose / Big Picture

在已经具备基础配置、环境检查和最小 poison data pipeline 之后，下一步自然衔接的能力是：基于结构化 poisoned dataset 运行可复现的 LoRA 注毒训练。这个阶段会把前面的数据构造产物真正转化为后续 illumination / reasoning / confidence 检测要面对的模型对象。

本计划的目标不是立刻做“大而全训练框架”，而是建立一个最小、透明、可恢复的 LoRA 训练入口，优先保证 poisoned dataset 能被稳定消费、配置能被明确表达、dry-run 能验证输入契约，再逐步扩展真实训练能力。

## Scope

### In Scope

- 设计最小训练配置契约
- 明确 poisoned dataset 到训练输入的字段映射
- 提供训练 CLI 的 dry-run / dataset validation 能力
- 在环境允许时再接入最小 LoRA 训练主路径

### Out of Scope

- full finetune
- 分布式训练框架
- probe / fusion / eval 逻辑
- 大规模超参搜索

## Repository Context

本计划将衔接：

- `configs/models.yaml`
- `configs/attacks.yaml`
- 后续新增训练配置
- `outputs/poison_data_*`
- `src/models/`
- `scripts/`

## Deliverables

- LoRA finetuning 执行计划
- 最小训练配置契约
- 训练 CLI dry-run 能力
- 真实训练主路径的首个可验证 milestone

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 定义训练输入契约与 dry-run 验证路径
- [x] Milestone 2: 接入最小 LoRA 训练主路径
- [x] Milestone 3: 跑通训练 smoke test 并记录产物

## Surprises & Discoveries

- 当前环境检查结果显示 `python3` 版本不足 3.10，且缺少 `peft`、`accelerate`、`datasets` 等训练关键依赖，因此真实训练在当前环境下存在明确前置阻塞。
- 当前 poison pipeline 的 dataset 输出已经足以支撑训练 dry-run，但 manifest 需要更严格地声明训练相关字段，特别是 `schema_version`。
- manifest 中保存的 artifact 路径是仓库相对路径，因此训练入口解析 manifest 时需要采用更稳妥的相对路径解析策略。
- dataset 直连模式和 manifest 模式都已通过 dry-run 验证，说明当前 poison pipeline 输出已经可以被训练阶段稳定消费。
- 环境已升级为干净的 Python 3.10 `.venv`，并且 GPU 版 `torch 2.4.1+cu121` 可在沙箱外正常识别 2 张 RTX 3090 与另外 2 张 2080 Ti。
- 最小 LoRA 训练入口现已具备真实训练代码路径，但为了让 milestone 2 的验收不被网络与模型下载阻塞，`--dry-run` 被刻意设计成离线友好模式，不强制加载 tokenizer 或模型权重。
- 当前机器没有现成的小型 causal LM 缓存可直接用于 smoke train，因此本阶段补了一个“本地 tiny causal LM”方案，并用它完成了真实 LoRA smoke train。
- 在当前 `transformers` / `accelerate` 组合下，`Trainer` 路径会触发兼容性错误；改为最小手写训练循环后，smoke train 稳定跑通且更贴合本阶段目标。

## Decision Log

- 决策：003 的第一个 milestone 先做“dry-run + dataset contract validation”，而不是直接承诺真实训练跑通。
  - 原因：当前环境不满足训练依赖要求，先把训练输入契约和 CLI 边界做实更稳妥。
  - 影响范围：003 的执行顺序、验收方式和环境前置条件。

- 决策：训练输入契约以 `dataset_manifest.json` 为首选入口，以 `poisoned_dataset.jsonl` 为备用直接入口。
  - 原因：manifest 能稳定提供 artifact 引用、字段声明、攻击 profile 和 summary，更适合作为训练恢复与审计入口；同时保留 dataset 直连模式便于快速调试。
  - 影响范围：`validate_training_dataset.py` 的 CLI 设计，以及后续训练主路径的读取入口。

- 决策：训练阶段最小必需样本字段定为 `schema_version`、`sample_id`、`split`、`is_poisoned`、`attack_profile`、`train_prompt`、`train_response`、`attack_metadata`。
  - 原因：这些字段已经足以支撑最小监督训练、样本追踪和攻击条件审计，同时避免过早绑定更复杂的 trainer 细节。
  - 影响范围：当前 dry-run 校验逻辑、poison pipeline manifest 契约，以及未来 LoRA 训练数据加载模块。

- 决策：在 dry-run 阶段产出结构化 `validation_report.json`、`preview_samples.jsonl` 和 `validation.log`。
  - 原因：训练前验证应当和其他阶段一样具备结构化落盘结果，便于复现、审计和后续实验记录。
  - 影响范围：`outputs/train_validation/` 的 artifact 组织，以及后续训练前检查流程。

- 决策：Milestone 2 的训练入口采用 `configs/training.yaml + configs/models.yaml + dataset manifest/JSONL` 的三段式契约。
  - 原因：训练入口既要复用 bootstrap 和 poison pipeline 的配置成果，又要避免把训练参数散落在脚本参数里。
  - 影响范围：`configs/training.yaml`、`scripts/run_lora_finetune.py` 和 `src/models/lora_training.py`。

- 决策：`run_lora_finetune.py --dry-run` 不强制联网下载 tokenizer 或模型。
  - 原因：Milestone 2 的主要目标是把训练主路径、输出结构和配置接口跑通，而不是把模型下载成功与否混进训练契约验收。
  - 影响范围：dry-run 的实现方式、输出内容和 Milestone 2 的验证命令。

- 决策：真实训练路径使用 `transformers.Trainer + peft.get_peft_model` 的最小组合，而不是引入更复杂训练框架。
  - 原因：这条路径足以支撑 LoRA MVP，同时更透明、更接近当前阶段“最小可运行优先”的目标。
  - 影响范围：`src/models/lora_training.py` 的实现复杂度、后续 smoke test 和训练 artifact 组织。

- 决策：Milestone 3 采用本地 tiny GPT-style causal LM 作为默认 smoke 训练模型，并保留一个小型 HuggingFace 模型配置入口。
  - 原因：这样既能避免外网权重下载成为唯一阻塞点，又满足“本地路径”和“HuggingFace 模型名”两类配置入口要求。
  - 影响范围：`configs/models.yaml`、`configs/training.yaml`、`scripts/create_local_smoke_model.py` 和 README 的训练示例。

- 决策：将真实训练主路径从 `Trainer` 切换为最小手写 LoRA 训练循环。
  - 原因：这避免了当前环境中 `transformers` 与 `accelerate` 的兼容性问题，也让 smoke train 的依赖面更小、更可控。
  - 影响范围：`src/models/lora_training.py`、训练 metrics / step log 输出，以及 adapter 保存与 reload 验证路径。

## Plan of Work

先围绕 poisoned dataset 的字段契约设计训练入口和 dry-run 校验，再根据环境条件接入最小 LoRA 主路径。这样既能保持连续推进，又不会在当前依赖条件不满足时写出大量不可验证代码。

## Concrete Steps

1. 定义训练阶段需要的最小配置和字段映射。
2. 实现 dry-run CLI，验证数据格式、关键字段和输出目录规划。
3. 若环境满足，再逐步接入最小 LoRA 训练实现。
4. 完成每个 milestone 后更新计划状态。

## Validation and Acceptance

- 训练 dry-run CLI 能正常解析参数
- 能读取 poisoned dataset manifest / dataset JSONL
- 能验证训练所需字段齐全并输出结构化检查结果
- 若环境允许，最小训练 run 能产出 checkpoint 和日志

## Idempotence and Recovery

- dry-run 应支持重复执行
- 配置与 manifest 应作为训练恢复入口保留
- 真实训练若中断，应尽量依赖输出目录中的状态信息恢复

## Outputs and Artifacts

- `outputs/train_*`
- 训练配置快照
- dry-run 检查结果
- 训练日志与 checkpoint

## Remaining Risks

- 当前 smoke train 采用的是本地 tiny 随机初始化 causal LM，它验证的是训练主路径与 artifact 闭环，而不是有意义的下游生成质量。
- 真正的 GPU 训练仍需在沙箱外运行；默认工作沙箱不暴露 `/dev/nvidia*`。
- 当前训练格式仍是最小模板方案，后续若要支持更贴近 chat 模型的 instruction tuning，需要进一步细化 chat template 与 response-only loss 的实现。
- LoRA `target_modules=auto` 的通用启发式仍然有限；目前 smoke_local 通过显式指定 `c_attn` / `c_proj` 来规避 GPT-style 模型差异。

## Next Suggested Plan

若 003 完成，下一步建议创建 `.plans/004-illumination-probe.md`。
