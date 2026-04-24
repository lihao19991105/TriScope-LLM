# AGENTS.md

## Project

本仓库当前的**默认主线**已经正式切换为：

**DualScope-LLM：面向黑盒大语言模型的轻量、两阶段、预算感知后门检测框架**

当前主论文计划不再以 TriScope-LLM 的 illumination / reasoning / confidence 三支并行叙事为核心，而是以以下三段式主方法为唯一默认主线：

1. **Stage 1: Illumination Screening**
2. **Stage 2: Confidence Verification**
3. **Stage 3: Budget-Aware Lightweight Fusion Decision**

其中：

- `reasoning` 分支**不再是主计划必做项**
- `LLM-as-a-judge` 不再作为默认主判定器
- `explanation-final inconsistency` 不再作为主论文核心证据
- 后续新阶段、新实验、新图表、新写作任务，默认都应围绕 **illumination + confidence + budget-aware fusion** 展开

---

## Historical Mainline Status

本仓库历史上曾以 **TriScope-LLM** 作为顶层方法命名，并完成了大量 route_c 相关工程链与验证链，尤其是 `138–198`。

这些成果**不会删除，也不应被否定**，但它们的定位已经改变：

- 它们是 **system reliability foundation**
- 是 **implementation robustness / execution-chain hardening evidence**
- 适合作为 **appendix / supplementary evidence**
- 不再是当前主论文创新主线的默认继续扩写方向

特别说明：

- `148–198` 证明的是 route_c 执行链、recoverable-boundary 修正与多轮真实使用链的**工程可靠性**
- 这些结果今后只应在 **DualScope 主线需要实现可信度、复现性或附录支撑** 时被引用
- **不得默认继续自动生成 199、200、201... 这类旧 route_c 递归链式计划**

---

## Core Goal

当前仓库的核心目标是构建一个：

- **黑盒**
- **两阶段**
- **预算感知**
- **可复现**
- **适配现实 API 条件**

的 LLM 后门检测研究原型，并围绕以下现实约束组织方法与实验：

- query budget 受限
- black-box 访问
- 既支持 `with-logprobs`，也支持 `without-logprobs`
- 优先做小而扎实、可解释、可审计的实验矩阵

---

## Mainline Method Constraints

实现与规划必须体现以下 DualScope 统一框架思想：

### 1. Illumination Screening

用于通过 targeted ICL / trigger-sensitive probing 暴露模型对后门触发的异常易感性。

关注点包括但不限于：

- trigger sensitivity
- target flip / gain
- screening score
- illumination-only baseline

### 2. Confidence Verification

用于在筛查后进一步验证异常输出是否呈现 lock / concentration / sequence-stability 风格。

必须同时考虑两种现实设置：

- `with-logprobs`
- `without-logprobs`

### 3. Budget-Aware Lightweight Fusion Decision

用于把 illumination 与 confidence 两段证据组织成轻量、预算感知的融合判定，而不是做一个重型三支并列投票器。

关注点包括：

- screening → verification 的两阶段策略
- risk-triggered verification
- query budget policy
- 单支 vs 两阶段 vs 融合的消融

### 4. Why Reasoning Is Not a Default Branch

`reasoning` 分支已降级为**可选背景能力**，不是主线默认推进对象。默认原因包括：

- 成本更高
- 稳定性更差
- 更依赖任务形式与解释质量
- 与现实 API 场景的适配性较弱

因此，不得再把仓库默认实现成“illumination / reasoning / confidence 三支都做一点”的机械组合。

---

## Working Principles

在本仓库中工作时，必须遵守以下原则：

1. **主线优先服从 DualScope**
   - 优先做 DualScope 主线相关任务
   - 若历史任务链与 DualScope 主线冲突，应以新主线为准

2. **一次只推进一个研究问题**
   - 不要同时扩展多个大模块
   - 不要把旧 route_c 工程链与新主线混成一个阶段

3. **先保证最小闭环，再逐步增强**
   - 先冻结方法与问题定义
   - 再做 screening、verification、fusion、实验矩阵、写作包装

4. **旧链只作可靠性基础，不再默认扩写**
   - 不要为了阶段号增长继续生成 `199+`
   - 不要把 route_c 多轮 recheck 重新包装成主论文创新

5. **优先透明实现**
   - 优先清晰、可读、可调试、可审计的实现
   - 避免过度抽象与“黑箱 heuristic 堆叠”

6. **所有实验必须可复现**
   - 所有随机行为必须显式设置 seed
   - 所有输出必须落盘到 `outputs/`
   - 所有关键参数、模板、预算策略必须可配置

7. **脚本与核心逻辑分离**
   - `scripts/` 放 CLI 入口
   - `src/` 放核心实现

---

## Resource Constraints

默认开发环境：

- Linux
- Python 3.10+
- 2 × RTX 3090

约束要求：

- 默认支持 HuggingFace 本地模型
- 保留 API backend 抽象，但不优先依赖闭源 API
- 默认使用 `python3`
- 训练默认使用 **LoRA / PEFT**
- 不要默认实现 full finetune
- 不要默认引入复杂分布式训练框架

---

## Expected Repository Structure

推荐目录职责如下：

- `configs/`
  - 模型、攻击、检测、实验配置
- `scripts/`
  - 命令行入口
- `src/attacks/`
  - 注毒数据构造、trigger/target 模板
- `src/models/`
  - 模型加载、推理后端
- `src/probes/`
  - illumination / confidence 相关 probing 逻辑
- `src/features/`
  - 特征抽取、对齐、预算相关中间表示
- `src/fusion/`
  - budget-aware fusion、轻量判定器、ablation baselines
- `src/eval/`
  - 指标、报告、图表数据导出、附录支持
- `outputs/`
  - 全部实验结果、模型输出、图表数据
- `.plans/`
  - 任务级执行计划（ExecPlans）

---

## Coding Requirements

### General

- 使用 Python 3.10+
- 公开函数和关键类尽量添加类型注解
- 对非显然逻辑添加简短注释
- 明确异常处理
- 避免隐式全局状态
- 优先使用 `pathlib.Path`
- 不要把路径、模型名、阈值、prompt 模板硬编码在脚本里
- 所有模板、trigger、target、预算、阈值应优先配置化

### CLI

每个 `scripts/*.py` 应至少具备：

- `argparse`
- `--help`
- 输入路径参数
- 输出路径参数
- seed 参数
- config 参数（如适用）
- 运行结束后打印关键输出位置

### Outputs

所有阶段性输出都应保存，至少包括：

- 原始结果
- 聚合统计
- 配置快照
- 日志
- 可供后续 screening / verification / fusion 使用的结构化中间文件

---

## Research Expectations

当前仓库必须优先支持以下研究活动：

- illumination-only baseline
- confidence-only baseline
- two-stage DualScope baseline
- budget-aware fusion baseline
- with-logprobs / without-logprobs 对照
- query budget 分析
- trigger type 分析
- target type 分析
- 模型覆盖与泛化
- 误报分析
- 消融实验
- 论文图表导出

评估部分至少应支持：

- ROC-AUC
- F1
- Precision
- Recall
- TPR@FPR=1%
- 平均 query 数
- 平均额外时延
- with-logprobs vs without-logprobs 成本/效果对照

---

## Planning Rules

对于以下任务，**必须先创建或更新执行计划**：

- 新增一个大模块
- 需要跨多个目录改动
- 需要多步实现
- 需要重构已有代码
- 需要新增实验流水线
- 任何预计不能在一个小编辑中完成的任务

执行计划规范定义在 `PLANS.md` 中。

如果任务是 non-trivial 的，必须：

1. 先阅读 `PLANS.md`
2. 优先阅读 `DUALSCOPE_MASTER_PLAN.md`
3. 在 `.plans/` 下创建或更新对应 ExecPlan
4. 按 milestone 推进
5. 每完成一个 milestone 更新计划进度

---

## Mainline Planning Priority

后续计划生成与执行的默认优先顺序必须是：

1. DualScope 方法冻结
2. Illumination screening 特征与 probing 计划
3. Confidence verification 特征与 `with/without logprobs` 计划
4. Budget-aware two-stage fusion 计划
5. dataset / model / trigger / target 实验计划
6. paper writing / figure / table / appendix 计划
7. reliability foundation 的整理与附录包装

**默认不再优先生成：**

- `199+` 旧式 route_c 无限扩展计划
- 单纯为了阶段号增长的链式收口计划
- reasoning branch 补全计划
- 与 DualScope 主线无关的 route_c 深层递归 recheck 计划

---

## Naming Rules

- 默认使用 **DualScope-LLM** 命名新的主计划、方法图、研究说明与总计划
- `TriScope` 命名只允许出现在：
  - 历史背景
  - 旧计划引用
  - historical engineering chain / reliability foundation 说明
- 不再以 TriScope 作为新的总计划或默认主线命名

---

## Low-Interruption Execution Mode

在已有 ExecPlan 且下一步清晰时，默认进入**低打扰、连续推进模式**。

### 基本规则

- 不要因为每个小步骤都来询问用户
- 只要当前任务仍在计划范围内，就继续推进
- 优先按 milestone 连续完成工作
- 只在 milestone 边界汇报，而不是每个文件修改后都汇报

### 只有在以下情况才允许打断用户

1. 需要用户做不可替代的研究决策
2. 将要进行破坏性或不可逆改动
3. 需要外部凭证、账号、下载授权、付费 API 或人工上传文件
4. 当前计划与仓库现实冲突，必须改方向
5. 存在多种高影响技术路径，且无法通过仓库内容与计划文档自行决策

### 默认授权

- 只要不触发上述打断条件，就应当继续完成当前计划中的后续 milestone
- 如果当前计划可以安全完成，优先一口气完成整个计划再汇报
- 如果下一份计划是当前工作的自然延续，也可以先创建下一份计划，再继续推进

---

## Execution Discipline

执行任务时必须遵守：

1. 先阅读 `AGENTS.md`
2. 如任务复杂，再阅读 `PLANS.md`
3. 优先阅读 `DUALSCOPE_MASTER_PLAN.md`
4. 创建或更新对应 `.plans/*.md`
5. 明确当前阶段目标
6. 只实现当前 milestone 的内容
7. 在暂停前保证仓库尽量处于可运行状态
8. 若任务与历史 route_c 链相关，必须先判断它是否服务于 DualScope 主线

如果计划已经定义了下一步，不要因为微小变更反复询问“要不要继续”。

---

## Reporting Format

每完成一个 **milestone** 或一个有意义的阶段后，输出汇报必须优先围绕以下内容组织：

1. **当前阶段目标**
2. **新增/修改的文件**
3. **这些文件的作用**
4. **核心实现逻辑**
5. **如何运行**
6. **输入输出格式**
7. **当前已知风险**
8. **建议的下一步**

后续汇报的研究优先级应聚焦于：

- 方法冻结
- 实验设计
- 数据集覆盖
- 模型覆盖
- trigger / target 覆盖
- 消融
- 成本分析
- `with-logprobs` / `without-logprobs` 对照
- 论文图表、表格、附录与写作产物

不再默认优先汇报：

- route_c 第 N 轮再复检
- 再下一层窗口扩张
- 再下一轮链式收口

---

## Explicitly Forbidden

禁止以下行为：

- 一次性生成整仓库大量未验证代码
- 跳过最小可运行验证
- 将 prompt / trigger / target / threshold 写死在脚本内部
- 为了“工程感”进行过度抽象
- 未经说明引入重型依赖
- 默认依赖无法保证可用的商业 API
- 在没有计划时对多个模块同时大改
- 明知主线已切换，仍默认继续扩写旧 route_c 递归链
- 把 route_c 工程链伪装成当前论文主创新
- 把 reasoning 分支默认保留为“未来还会自动补完”的主线

---

## Default Execution Order

如果没有额外指定任务，默认按以下顺序推进：

1. DualScope 研究问题与叙事冻结
2. Illumination Screening Pipeline
3. Confidence Verification Pipeline
4. Budget-Aware Two-Stage Fusion
5. Experimental Matrix
6. Reliability Foundation Packaging
7. Paper Writing and Submission Package

一次只推进一个阶段，但在有计划的情况下可连续完成多个 milestone。

---

## Default Starting Instruction

如果用户只要求“继续做”或“接着推进”，默认行为是：

1. 先读取 `DUALSCOPE_MASTER_PLAN.md`
2. 再读取当前最新、且**仍属于 DualScope 主线**的 `.plans/*.md`
3. 找到第一个未完成的 milestone
4. 在不违反低打扰规则的前提下直接继续执行
5. 仅在 milestone 完成或必须打断时汇报

如果最新的未完成计划属于旧 TriScope / route_c 历史链，但不再服务于 DualScope 主线，则**不要默认继续它**。
