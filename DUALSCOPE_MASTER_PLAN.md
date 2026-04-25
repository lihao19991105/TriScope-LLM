# DualScope-LLM Master Plan

## 1. Project Positioning

### What This Repository Is Now

本仓库当前的默认主线是：

**DualScope-LLM：面向黑盒大语言模型的轻量、两阶段、预算感知后门检测框架**

它面向的是一个更聚焦、更现实、更适合论文推进的研究问题：

- 在 black-box setting 下检测 LLM backdoor
- 在 query budget 受限条件下运行
- 兼容 `with-logprobs` 与 `without-logprobs` 两类现实 API 条件
- 用两阶段证据链而不是三支并行叙事完成方法闭环

### Relationship to the Old TriScope Mainline

本仓库曾以 TriScope-LLM 为主线，强调 illumination / reasoning / confidence 三支并行，并围绕 route_c 修复与稳定性验证完成了大量工程工作。

当前定位变化如下：

- **TriScope 不再是当前主论文主线**
- `reasoning` 分支不再是默认必做项
- route_c 的长链验证不再继续默认扩写
- 旧成果被保留并重定位为：
  - reliability foundation
  - implementation robustness
  - appendix / supplementary evidence

### Current First Execution Plan

当前 DualScope 主线的第一个核心执行计划是：

- [.plans/dualscope-illumination-screening-freeze.md](/home/lh/TriScope-LLM/.plans/dualscope-illumination-screening-freeze.md)

它负责把 Stage 1 从研究叙事冻结成可执行协议、artifact schema、CLI 和后续接口合同。

### Current Second Execution Plan

在 Stage 1 已冻结并验证通过之后，当前应继续推进的第二个核心执行计划是：

- [.plans/dualscope-confidence-verification-with-without-logprobs.md](/home/lh/TriScope-LLM/.plans/dualscope-confidence-verification-with-without-logprobs.md)

它负责把 Stage 2 从零散的 confidence 想法冻结成正式的 verification protocol，并明确：

- with-logprobs 主能力路径
- without-logprobs 现实 fallback 路径
- Stage 1 -> Stage 2 输入合同
- Stage 2 -> Stage 3 公共字段合同
- confidence-only baseline 与 verification budget contract

### Current Third Execution Plan

在 Stage 2 已冻结并验证通过之后，当前应继续推进的第三个核心执行计划是：

- [.plans/dualscope-budget-aware-two-stage-fusion-design.md](/home/lh/TriScope-LLM/.plans/dualscope-budget-aware-two-stage-fusion-design.md)

它负责把 Stage 3 从“illumination + confidence 怎么拼起来”的想法冻结成正式的策略层与决策层，并明确：

- Stage 1 / Stage 2 -> Stage 3 依赖合同
- budget-aware verification trigger policy
- capability-aware fusion policy
- final decision output contract
- baseline / ablation / cost analysis contract

### Current Experimental Matrix and First-Slice Execution Chain

在 Stage 3 已冻结并验证通过之后，DualScope 主线已经进入实验矩阵与最小 first-slice 闭环：

- [.plans/dualscope-experimental-matrix-freeze.md](/home/lh/TriScope-LLM/.plans/dualscope-experimental-matrix-freeze.md)
- [.plans/dualscope-minimal-first-slice-execution-plan.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-execution-plan.md)
- [.plans/dualscope-minimal-first-slice-smoke-run.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-smoke-run.md)
- [.plans/dualscope-first-slice-artifact-validation.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-artifact-validation.md)
- [.plans/dualscope-first-slice-report-skeleton.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-report-skeleton.md)
- [.plans/dualscope-minimal-first-slice-real-run-plan.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run-plan.md)

这些阶段负责把 Stage 1 / Stage 2 / Stage 3 的冻结协议推进到论文实验矩阵合同、最小可执行切片、受控 smoke artifacts、artifact validation 和 first-slice 报告骨架。它们仍然不是完整主实验矩阵执行。

`dualscope-minimal-first-slice-real-run-plan` 进一步冻结了最小真实运行前的数据、模型、后门构造、三阶段执行流、preflight、命令、artifacts、验证标准和失败回退。它仍然是计划阶段，不代表真实训练或完整实验已经完成。

当前 preflight 阶段入口是：

- [.plans/dualscope-minimal-first-slice-real-run-preflight.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run-preflight.md)

该阶段只检查真实运行前置条件，不执行 LoRA / QLoRA 训练，也不运行完整实验。如果 preflight validated，下一步才进入最小 first-slice real run；如果 partially validated，应先进入 preflight repair；如果 not validated，应进入 blocker closure。

当前 preflight repair 阶段入口是：

- [.plans/dualscope-first-slice-preflight-repair.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-preflight-repair.md)

该阶段只建立真实 Alpaca 数据导入、schema 校验、GPU 环境要求和 rerun checklist。它不代表 preflight 已经 validated；在真实 JSONL 仍缺失时，下一步应进入 dataset materialization，而不是直接 real run。

当前 first-slice 数据与 readiness 支撑链已经继续扩展为：

- [.plans/dualscope-first-slice-dataset-materialization.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-dataset-materialization.md)
- [.plans/dualscope-first-slice-data-source-intake-package.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-data-source-intake-package.md)
- [.plans/dualscope-first-slice-dry-run-config-and-contract-validator.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-dry-run-config-and-contract-validator.md)
- [.plans/dualscope-first-slice-artifact-validator-hardening.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-artifact-validator-hardening.md)
- [.plans/dualscope-first-slice-readiness-report-package.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-readiness-report-package.md)

这些阶段已经把真实数据导入、schema 校验、dry-run contract、artifact validator 和 readiness report 包装好。若真实 Alpaca 源文件仍缺失，唯一下一步是提供真实源文件并重跑 dataset materialization。

当前已新增 materialization 后 readiness 收口入口：

- [.plans/dualscope-first-slice-readiness-after-materialization.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-readiness-after-materialization.md)

当该阶段 verdict 为 `First slice ready for minimal real run` 时，下一步可以进入 `dualscope-minimal-first-slice-real-run`。该下一步仍必须保持最小 first-slice，不得扩展成完整实验矩阵。

当前 5h autonomous run 进一步新增了独立的 preflight-rerun 与 real-run readiness go/no-go 包：

- [.plans/dualscope-minimal-first-slice-real-run-preflight-rerun.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run-preflight-rerun.md)
- [.plans/dualscope-minimal-first-slice-real-run-readiness-package.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run-readiness-package.md)

最新状态是：dataset materialization validated，preflight rerun validated，GPU/CUDA 可见；但 real-run readiness 为 `Partially validated`，因为 planned command plan 引用了尚未实现的 minimal real-run entrypoints。下一步应先实现这些 entrypoints，再启动最小 real run。

当前 minimal real-run command-entrypoint package 已完成：

- [.plans/dualscope-minimal-real-run-command-entrypoint-package.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-real-run-command-entrypoint-package.md)

该阶段补齐了 data slice、Stage 1 illumination、Stage 2 confidence、Stage 3 fusion、evaluation 和 report 六个入口脚本，并只在 dry-run / contract-check 模式下验证 artifact chain。最新 readiness 已转为 `Minimal real run readiness validated`。下一步可以进入 `dualscope-minimal-first-slice-real-run`，但不得扩展成完整矩阵或声称 dry-run 性能。

当前 minimal first-slice real run 阶段已完成：

- [.plans/dualscope-minimal-first-slice-real-run.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run.md)

该阶段已生成 data slice、Stage 1、Stage 2、Stage 3、evaluation 和 report artifacts，并通过 required artifact / contract compatibility checks。最终 verdict 为 `Partially validated`，因为当前运行没有执行完整模型推理或 logprob extraction，Stage 2 使用 `without_logprobs` fallback，evaluation 仍是 metric placeholders。下一步应进入 compression，先收口真实模型/logprob/label 能力缺口。

当前 long compression / enablement 链已经完成：

- [.plans/dualscope-minimal-first-slice-real-run-compression.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run-compression.md)
- [.plans/dualscope-first-slice-model-execution-enablement.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-model-execution-enablement.md)
- [.plans/dualscope-first-slice-logprob-capability-enablement.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-logprob-capability-enablement.md)
- [.plans/dualscope-first-slice-label-materialization.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-label-materialization.md)
- [.plans/dualscope-minimal-first-slice-real-run-rerun-with-model-or-fallback.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run-rerun-with-model-or-fallback.md)
- [.plans/dualscope-first-slice-real-run-artifact-validation.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-real-run-artifact-validation.md)
- [.plans/dualscope-first-slice-result-package.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-result-package.md)
- [.plans/dualscope-next-experiment-readiness-package.md](/home/lh/TriScope-LLM/.plans/dualscope-next-experiment-readiness-package.md)

最新状态是：本地 Qwen2.5-1.5B 最小生成 probe validated，本地 logits-softmax probability evidence validated，clean/poisoned labeled slice plan 已 validated，labeled rerun repair/compression package 已 validated，并产出 condition-level rerun input slice；但 Stage 1 / Stage 2 / Stage 3 仍需 row_id-keyed condition-level rerun outputs，且 ASR / clean utility 仍需真实 model responses。唯一下一步是 `dualscope-minimal-first-slice-condition-level-rerun`，不是扩展完整矩阵。

当前自动化闭环与上一段 first-slice 队列已收口。下一阶段是 `dualscope-first-slice-real-experiment`：在 Stanford Alpaca first-slice、clean/poisoned labeled pairs、冻结 Stage 1 / Stage 2 / Stage 3 协议、当前小模型路径、`lexical_trigger_v1` / `cftrigger` 与 `fixed_response_v1` 范围内，逐步执行真实或明确 fallback 的 response generation、label-aligned metric computation、first-slice result package 和 next-experiment readiness。该阶段只报告 first-slice 结果，不声明完整论文性能。

### Current Submission Positioning

当前论文目标应保持**稳妥、不夸大**：

- 重点强调 black-box、budget-aware、practical API compatibility
- 重点强调 illumination screening + confidence verification 的两阶段优势
- 不追求“覆盖所有可能证据链”，而追求“更现实、更经济、更可复现”

---

## 2. Problem Definition

### Research Problem

给定一个黑盒 LLM，我们希望在有限查询预算下判断它是否存在后门易感性，并输出一条轻量但可解释的后门证据链。

### Setting

- **Black-box access**
  - 不依赖内部权重
  - 不依赖训练日志
  - 不依赖 white-box gradients

- **Query-budget constrained**
  - 总查询数有限
  - 需要把高成本验证只用在高风险样本/窗口上

- **Optional logprob availability**
  - 一类 API 提供 logprobs，可做更细的 confidence 特征
  - 另一类 API 不提供 logprobs，需要退化到 output-structure / stability 风格特征

- **Attack / target setting**
  - 需要覆盖多类 trigger
  - 需要覆盖至少两类 backdoor target
  - 需要考虑 paraphrase / template shift / adaptive wrapping 等现实扰动

### Evaluation Goal

DualScope 的目标不是证明“任何解释路径都可用”，而是证明：

1. illumination screening 能以较低预算发现高风险易感性
2. confidence verification 能进一步确认异常生成锁定
3. 两阶段 budget-aware fusion 在成本与效果之间给出更合理的折中

---

## 3. Method Overview

### Stage 1: Illumination Screening

第一阶段使用 targeted ICL / trigger-sensitive probing 做快速筛查。

关注特征包括：

- target flip
- sensitivity gain
- screening score
- template sensitivity
- prompt-level instability under trigger-target coupling

该阶段应支持 illumination-only baseline，并输出：

- per-query screening artifacts
- per-window / per-sample screening summary
- risk score for Stage 2 routing

### Stage 2: Confidence Verification

第二阶段只对第一阶段筛出的高风险对象做更深入验证。

关注特征包括：

- token concentration
- confidence lock
- sequence lock
- low-branching generation behavior
- output stability under suspicious trigger conditions

需要同时支持：

- **with-logprobs**
  - token-level confidence / entropy / concentration
- **without-logprobs**
  - response-structure stability
  - output locking proxies
  - minimal fallback confidence cues

### Stage 3: Budget-Aware Lightweight Fusion

第三阶段做轻量融合判定，而不是重型多支路集成。

核心策略：

- screening → verification 两阶段串联
- 只有高风险对象才进入 Stage 2
- 在预算约束下优化 detection quality / query cost
- 支持 illumination-only、confidence-only、two-stage fusion 的对照

---

## 4. Why No Reasoning Branch

当前主线不再把 reasoning 作为默认主支柱，这是一个**有意识的设计选择**。

### 原因

1. **成本更高**
   - reasoning probe 往往需要更长输出、更复杂 prompt、更多后处理。

2. **稳定性更弱**
   - reasoning 结果更受任务形式、生成质量与解释风格影响。

3. **任务依赖更强**
   - 很多 reasoning-based signal 在真实 API 条件下可迁移性差。

4. **与现实 API 场景不完全对齐**
   - illumination + confidence 更容易适配黑盒、预算感知场景。

### What This Means

- reasoning 可作为历史探索或补充背景
- reasoning 不再是主实验矩阵默认必含维度
- reasoning 不再阻塞 DualScope 主线推进

---

## 5. Datasets

当前主线至少应覆盖以下数据来源，并明确其角色：

### Stanford Alpaca

- 用作通用 instruction-following clean substrate
- 适合构造标准 prompt-response 合约
- 适合作为 illumination / confidence 的一般性基座

### AdvBench

- 提供更高风险、更强对抗性的行为任务
- 用于检验 DualScope 在更危险行为域上的稳定性与误报边界

### JBB-Behaviors

- 提供更贴近 jailbreak / risky behavior 的行为覆盖
- 用于检验 trigger / target / template 扰动下的异常易感性与 confidence locking

### Dataset Role Design

后续计划应明确：

- 哪个数据集用于主实验
- 哪个数据集用于泛化 / robustness
- 哪个数据集用于成本与边界分析

---

## 6. Model Plan

模型计划必须坚持“小而扎实，不做失控大矩阵”。

### Minimum Target

至少覆盖 **3 个 base LLM**，建议遵循以下原则：

- 至少一个较小开放模型
- 至少一个中等规模开放模型
- 至少一个更现实的 instruction-tuned base model

### Constraints

- 不扩到无法承受的大模型矩阵
- 不把全部精力耗在模型覆盖上
- 优先保证每个模型都有完整的 illumination / confidence / budget-aware artifacts

### Selection Logic

模型选择应服务于：

- black-box realism
- API-like interaction assumptions
- reproducible local evaluation

---

## 7. Attack / Trigger / Target Plan

### Trigger Coverage

至少覆盖 **3 类 trigger**，例如：

- explicit lexical trigger
- paraphrased / semantically similar trigger
- lightweight wrapped / template-shifted trigger

### Target Coverage

至少覆盖 **2 类 backdoor target**，例如：

- direct target completion
- behavior-steering / style-locked target

### Robustness Axis

需要适度覆盖：

- paraphrase robustness
- adaptive wrapper robustness
- template robustness

但必须避免把实验矩阵扩到不可管理。

---

## 8. Experimental Plan

### Main Experiments

主实验需要至少比较：

1. illumination-only
2. confidence-only
3. budget-aware two-stage DualScope

### Ablations

必须覆盖：

- Stage 1 only vs Stage 2 only vs Stage 1+2
- with-logprobs vs without-logprobs
- fixed budget vs adaptive budget policy
- trigger family / target family sensitivity

### Cost Analysis

必须明确呈现：

- 平均 query 数
- 平均额外时延
- Stage 2 调用率
- 预算-性能曲线

### Robustness

需要覆盖：

- trigger paraphrase
- wrapper variation
- target variation
- 模型间泛化

### Writing-Oriented Outputs

所有实验都应优先为以下写作产物服务：

- 主表
- 消融表
- 成本图
- 方法图
- appendix robustness tables

---

## 9. Reliability Foundation

### What 148–198 Are Now

`148–198` 代表的是 route_c 执行链与 recoverable-boundary 修正的长期工程验证结果。

它们当前的定位是：

- route_c execution-path hardening evidence
- recoverable-boundary implementation robustness evidence
- appendix-grade reliability foundation
- reproducibility support

### What They Are Not

它们**不再是**：

- 当前主论文创新主线
- 需要继续默认生成 `199+` 的递归推进链
- 当前方法贡献的主叙事中心

### How to Use Them Going Forward

今后只应在以下情况下继续引用这条链：

- 支撑系统实现可信度
- 支撑 appendix / supplementary implementation note
- 回答“这套修正是否经过充分工程验证”
- 给 DualScope 主线提供可靠的底层 execution evidence

---

## 10. Deliverables

DualScope 主线最终应交付：

### Code

- illumination screening pipeline
- confidence verification pipeline
- budget-aware fusion pipeline
- reproducible experiment CLIs

### Figures and Tables

- 方法总图
- 主实验表
- 消融表
- 成本分析图
- with/without logprobs 对照图表

### Writing Artifacts

- 论文标题与摘要版本
- 方法章节草稿
- 实验章节草稿
- appendix 结构与可靠性说明

### Reproducibility Package

- outputs artifacts
- config snapshots
- run manifests
- experiment logs
- checklist for rerun

---

## 11. Stop Doing List

今后默认不要再做以下事情：

1. 不再把 reasoning branch 当作主线默认补全对象
2. 不再默认生成 `199+` route_c 递归收口计划
3. 不再继续 TriScope 风格三支并行主叙事
4. 不再把长期无限链式 recheck 当作主论文推进主线
5. 不再把 route_c 工程链伪装成当前论文的主创新本体
6. 不再默认优先写“再下一轮 route_c 复检”而不是新方法、实验和写作计划

---

## 12. Default Next Planning Priority

当前仓库今后默认优先生成的新计划应按以下顺序选择：

1. **DualScope 方法冻结计划**
2. **Illumination screening pipeline 计划**
3. **Confidence verification / with-without-logprobs 计划**
4. **Budget-aware two-stage fusion 计划**
5. **Experimental matrix 计划**
6. **Paper figures / tables / writing 计划**
7. **Reliability foundation appendix packaging 计划**

当前第一优先的具体计划入口为：

- `.plans/dualscope-illumination-screening-freeze.md`

如无特殊理由，不应优先回到历史 TriScope / route_c 递归链。
