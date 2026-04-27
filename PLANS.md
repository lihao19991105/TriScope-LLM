# PLANS.md

# Execution Plans for DualScope-LLM

本文件定义本仓库中执行计划（ExecPlan）的写法、结构和更新规则。

当前仓库的**项目级主线**已经从历史上的 TriScope-LLM 切换为：

**DualScope-LLM：面向黑盒大语言模型的轻量、两阶段、预算感知后门检测框架**

因此，本文件不仅描述“计划怎么写”，还明确规定“未来默认应该为什么问题写计划”。

---

## 0. Project Direction Update

### TriScope → DualScope Transition

本仓库早期以 TriScope-LLM 为主线，强调 illumination / reasoning / confidence 三支并行，并围绕 route_c 修复和稳定性扩展构建了大量工程验证链，尤其是 `138–198`。

这些历史成果依然有效，但项目主线已经更新。原因如下：

1. **论文叙事效率**
   - 三支主线并行会稀释主论文故事。
   - illumination + confidence + budget-aware fusion 更容易形成清晰、紧凑、可解释的论文主线。

2. **工程与实验成本**
   - reasoning 分支成本更高、稳定性更弱、对任务形式更敏感。
   - DualScope 更符合当前算力与时间边界下“小而扎实”的路线。

3. **现实 API 适配性**
   - illumination screening + confidence verification 更贴合黑盒、预算感知、with/without logprobs 的现实使用条件。

4. **旧 route_c 长链的合理归档**
   - `148–198` 已经充分证明 recoverable-boundary 修正和 route_c 执行链的工程可靠性。
   - 这些结果现在应被归档为：
     - historical engineering chain
     - reliability foundation
     - implementation robustness
     - appendix / supplementary evidence
   - 不再作为主论文创新主线继续无限扩写。

### What This Means for Future Planning

未来默认不再继续：

- `199+` 旧式 route_c 递归链式计划
- reasoning branch 补全式主线计划
- 仅为了阶段号增长的 recheck / chain-final / next-round 计划

未来默认应优先生成的计划类型是：

- illumination screening 计划
- confidence verification 计划
- budget-aware fusion 计划
- dataset / model / trigger / target 实验计划
- paper writing / figure / table / appendix 计划
- reliability foundation packaging 计划

当前第一优先的具体计划入口是：

- `.plans/dualscope-illumination-screening-freeze.md`
- `.plans/dualscope-confidence-verification-with-without-logprobs.md`
- `.plans/dualscope-budget-aware-two-stage-fusion-design.md`
- `.plans/dualscope-experimental-matrix-freeze.md`
- `.plans/dualscope-minimal-first-slice-execution-plan.md`
- `.plans/dualscope-minimal-first-slice-smoke-run.md`
- `.plans/dualscope-first-slice-artifact-validation.md`
- `.plans/dualscope-first-slice-report-skeleton.md`
- `.plans/dualscope-minimal-first-slice-real-run-plan.md`
- `.plans/dualscope-minimal-first-slice-real-run-preflight.md`
- `.plans/dualscope-first-slice-preflight-repair.md`
- `.plans/dualscope-first-slice-dataset-materialization.md`
- `.plans/dualscope-first-slice-data-source-intake-package.md`
- `.plans/dualscope-first-slice-dry-run-config-and-contract-validator.md`
- `.plans/dualscope-first-slice-artifact-validator-hardening.md`
- `.plans/dualscope-first-slice-readiness-report-package.md`
- `.plans/dualscope-first-slice-readiness-after-materialization.md`
- `.plans/dualscope-minimal-first-slice-real-run-preflight-rerun.md`
- `.plans/dualscope-minimal-first-slice-real-run-readiness-package.md`
- `.plans/dualscope-minimal-real-run-command-entrypoint-package.md`

当前 5h autonomous run 已确认：真实 Alpaca first-slice 数据已物化、schema 已通过、GPU/CUDA preflight rerun 已通过；但最小 real-run readiness 仍为 `Partially validated`，原因是 planned real-run command plan 中若干 Stage 1 / Stage 2 / Stage 3 / eval / report 入口脚本尚未实现。下一步应先补齐 **minimal real-run command-entrypoint package**，而不是直接训练或扩展完整矩阵。

当前 command-entrypoint package 已补齐 6 个最小入口脚本，并通过 dry-run / contract-check 验证；real-run readiness 已重新运行并转为 `Minimal real run readiness validated`。下一步才可以进入 `dualscope-minimal-first-slice-real-run`，且仍只能执行最小 first-slice，不得扩展完整实验矩阵。

当前 minimal first-slice real run 已执行并产出完整 artifact chain；verdict 为 `Partially validated`。原因不是链路断裂，而是 Stage 1 / Stage 2 仍处于 protocol-compatible deterministic no-model-execution 模式，Stage 2 记录为 `without_logprobs` fallback，evaluation 仅生成 metric placeholders。下一步应进入 `dualscope-minimal-first-slice-real-run-compression`，而不是扩展完整矩阵。

当前 minimal first-slice real run 的 long compression / enablement 链已完成。模型最小生成 probe 与本地 logits-softmax 概率 probe 已 validated；clean/poisoned labeled slice plan 已 validated；labeled rerun 诚实保留 `Partially validated`，因为 Stage 3 仍是 source-example level prediction；其 repair/compression package 已 validated，并产出 row_id-keyed condition-level rerun input slice。当前唯一推荐下一步是 `dualscope-minimal-first-slice-condition-level-rerun`，用于在同一 dataset/model/trigger/target/budget 范围内补齐 condition-level Stage 1/2/3 outputs 与后续真实性能指标前置条件。

当前 autorun worktree / safe merge gate 自动化闭环已 validated，上一段 first-slice 队列已完成。下一阶段进入 `dualscope-first-slice-real-experiment`，先新增并执行最小 Stanford Alpaca first-slice 实验链：真实或明确 fallback 的 response generation、label-aligned metrics、result package、next-experiment readiness。该阶段仍不得扩完整矩阵、模型轴、budget、trigger family、target family，不得伪造模型响应或指标。

当前用户已要求按 SCI 三区实验标准升级 DualScope 实验主线。`Qwen2.5-1.5B-Instruct` 降级为 pilot / debug / automation / ablation；`Qwen2.5-7B-Instruct` 升级为 main experimental model；`Llama-3.1-8B-Instruct` 或 `Mistral-7B-Instruct-v0.3` 作为 cross-model validation。下一步队列入口是 `dualscope-main-model-axis-upgrade-plan`，然后才进入 Qwen2.5-7B first-slice response generation，不直接运行完整大矩阵。

当前 Qwen2.5-7B first-slice 前置资源门已独立为 `dualscope-qwen2p5-7b-resource-materialization-and-config`。该任务必须诚实检查或下载 `Qwen/Qwen2.5-7B-Instruct`，检查 labeled pairs、target-response plan、GPU/disk、tokenizer/config，并输出 resource verdict artifact。若资源仍 blocked，应进入 resource repair，而不是重复选择 Qwen2.5-7B response-generation-plan。

当前 DualScope SCI3 first-slice Qwen2.5-7B 自动化实验链已阶段性完成：Qwen2.5-7B resource materialization validated，已生成 8 条真实 first-slice response，label-aligned detection metrics 与 ASR 已计算，clean utility blocker 已真实记录，result package、SCI3 main expansion plan 与 cross-model validation readiness plan 已收口。下一阶段进入 `dualscope-sci3-next-real-expansion-track`，只允许小步推进：先规划 Qwen2.5-7B Stanford Alpaca main-slice，再执行 bounded main-slice response generation，随后依次规划 semantic trigger smoke、behavior-shift target smoke、AdvBench small-slice readiness 与 JBB small-slice readiness。该阶段不得直接运行 full matrix，不得把 8 条 first-slice response 写成完整论文结果，也不得伪造 clean utility 或 cross-model 实验。

当前 Alpaca main-slice response generation 的第一轮真实执行链已闭环为 blocker documentation，而不是实验完成。新的入口是 `dualscope-worktree-gpu-bnb-input-readiness-repair`：先验证 isolated worktree 的 `.venv`、CUDA、bitsandbytes 或 non-4bit fallback、input materialization、model symlink 与 `/mnt/sda3/lh` cache/tmp 传递，再进入 `dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry`。该重开链仍只允许 bounded main-slice，不允许 full matrix、训练、route_c、199+ 或伪造 response/logprob/metric。

当前已确认 GPU/CUDA 在宿主机 shell 可见，但在 `codex exec` isolated worktree 中不可见。因此下一步是 `dualscope-external-gpu-runner-for-qwen2p5-7b-generation`：真实 Qwen2.5-7B bounded generation 迁移到普通 shell / `nohup` 外部 runner 执行，Codex 只负责脚本、artifact 检查、registry、PR 与后续 routing。该 runner 必须产生真实 response 或真实 blocker，不得伪造 response/logprob/metric，不得 full matrix 或训练。

当前 bounded Alpaca main-slice 已完成 16 条真实 Qwen2.5-7B response、可计算 detection metrics、ASR、without-logprobs fallback 与结果包；clean utility 仍真实 blocked。下一阶段入口是 `dualscope-sci3-semantic-behavior-expansion-track`：按小步执行 semantic trigger smoke、behavior-shift target smoke、AdvBench/JBB small-slice materialization 与 expanded synthesis。response generation、metric computation、result package 与 dataset materialization 任务必须真实执行 CLI/runner 或输出明确 blocker artifacts；不得用 plan/docs/registry-only PR 伪装实验完成。

当前 AdvBench small-slice materialization blocker 的修复路径已明确：用户授权公开 Hugging Face 数据源 `walledai/AdvBench`。`dualscope-advbench-small-slice-public-source-materialization` 只允许 bounded materialization，样本数先控制在 32 条以内，标准化到 `data/advbench/small_slice/advbench_small_slice_source.jsonl`，并输出 manifest/schema/blocker/verdict/report。该步骤不得生成 response、不得计算 metrics、不得修改 benchmark truth 或 gate；若下载、依赖、网络或 schema 失败，必须输出真实 blocker。

---

## 1. What an ExecPlan Is

ExecPlan 是一个**可执行、可持续更新、可中断后恢复**的任务文档。

它不是简单 TODO 列表，而是一个面向研究工程任务的执行蓝图，应该满足：

- 自包含
- 可被新接手的人直接理解
- 能说明为什么做、做什么、怎么做、如何验证、有什么风险
- 能记录进展和关键决策

---

## 2. When an ExecPlan Is Required

以下情况必须创建或更新 ExecPlan：

1. 新增一个大模块
2. 跨多个目录修改
3. 需要多步完成的功能
4. 需要重构
5. 新增实验流水线
6. 新增融合、评估、分析逻辑
7. 任何预计不能在单次小改动内稳定完成的任务

**小修复、小改字、局部 typo 修正** 可以不单独建计划。

---

## 3. Where ExecPlans Live

所有任务级计划统一放在：

- `.plans/`

同时，仓库当前的**主入口计划**是：

- `DUALSCOPE_MASTER_PLAN.md`

执行非 trivial 任务时，建议顺序为：

1. 先看 `DUALSCOPE_MASTER_PLAN.md`
2. 再看相关 `.plans/*.md`
3. 如无现成计划，再新建对应 ExecPlan

建议命名格式：

- `.plans/dualscope-illumination-screening-freeze.md`
- `.plans/dualscope-confidence-verification-with-without-logprobs.md`
- `.plans/dualscope-budget-aware-two-stage-fusion-design.md`
- `.plans/dualscope-dataset-model-matrix-bootstrap.md`
- `.plans/dualscope-paper-figure-package.md`

如需引用历史计划，应在计划中明确标注：

- `Historical engineering chain reference`
- `Reliability foundation reference`

而不要把它们重新包装成新的主线编号链。

---

## 4. Non-Negotiable Requirements

每份 ExecPlan 必须满足：

1. **自包含**
   - 不能依赖聊天上下文才能理解
2. **可执行**
   - 读完后应知道在哪里改、怎么跑、如何验收
3. **持续更新**
   - 每推进一段就更新进度
4. **可恢复**
   - 中断后，下一个人应能继续做
5. **有验证方式**
   - 必须说明如何确认该阶段完成
6. **有风险记录**
   - 需要留下已知问题和限制
7. **服从当前主线**
   - 必须说明该计划如何服务于 DualScope 主线，或说明其为何只是 reliability foundation / appendix packaging

---

## 5. Required Sections of Every ExecPlan

每份 ExecPlan 必须至少包含以下章节。

# `<任务标题>`

## Purpose / Big Picture

说明为什么要做这个任务、完成后会增加什么能力。

要回答：

- 这个任务解决什么问题？
- 为什么现在要做？
- 完成后对整个 **DualScope-LLM** 项目有什么意义？

## Scope

明确本计划**包含什么**、**不包含什么**。

必须写清：

### In Scope
- 当前计划明确覆盖的内容

### Out of Scope
- 当前计划明确不做的内容

避免边做边扩张。

## Repository Context

说明和本任务相关的目录、文件、模块。

必须显式说明：

- 涉及哪些已有模块可复用
- 涉及哪些 outputs / artifacts
- 是否引用历史 TriScope / route_c 工程链作为可靠性基础

## Deliverables

列出完成本计划后应交付的具体产物。

例如：

- 新增脚本
- 新增模块
- 配置文件
- 输出格式
- smoke test
- README / paper package 更新

## Progress

使用 checklist，且必须持续更新。

## Surprises & Discoveries

记录实现过程中发现的意外情况。

## Decision Log

记录关键设计决策及原因。

## Plan of Work

用自然语言说明执行路径。

## Concrete Steps

列出可执行的具体步骤。

## Validation and Acceptance

定义“如何算完成”。

## Idempotence and Recovery

说明如何安全重跑，以及出现部分失败时如何恢复。

## Outputs and Artifacts

明确所有产物落到哪里。

## Remaining Risks

列出剩余技术风险、研究风险和实现限制。

## Next Suggested Plan

如果该计划完成后通常应接哪一步，也建议写出来。

---

## 6. Repository-Specific Expectations

针对当前项目，每份计划还应额外显式考虑：

1. 是否服务于 **DualScope 主线**
2. 是否符合 **black-box + query-budget + optional logprobs** 的现实设定
3. 是否优先围绕 **illumination screening / confidence verification / budget-aware fusion**
4. 是否满足 **2 × RTX 3090** 的资源约束
5. 是否将结果写入 `outputs/`
6. 是否能为后续主实验、消融、成本分析和写作产物提供稳定输入

---

## 7. Mainline Phases for Future Planning

未来顶层规划默认按以下阶段组织：

### Phase A: Research Pivot and Narrative Freeze

- 正式切换到 DualScope-LLM
- 重写题目、摘要、贡献点、方法定位
- 冻结研究问题

### Phase B: Illumination Screening Pipeline

- targeted ICL probe design
- screening features
- template sensitivity / flip / gain
- illumination-only baseline

### Phase C: Confidence Verification Pipeline

- lock / entropy / concentration 特征
- `with-logprobs` setting
- `without-logprobs` fallback
- confidence-only baseline

### Phase D: Budget-Aware Two-Stage Fusion

- screening → verification
- risk-triggered verification
- query budget policy
- fusion detector and ablation

### Phase E: Experimental Matrix

- datasets
- base LLMs
- trigger families
- backdoor targets
- robustness
- query cost
- with/without logprobs

### Phase F: Reliability Foundation Packaging

- 把 `148–198` 工程链收纳为附录级可靠性基础
- 不再扩写为主线
- 只保留必要的实现说明、风险边界和可复现性支持

### Phase G: Paper Writing and Submission Package

- 论文标题
- 方法图
- 主表
- 消融表
- 成本分析图
- 附录组织

---

## 8. Historical Chain Handling Rules

对于 `138–198` 及其相关 route_c 工程链，默认处理规则如下：

1. **不删除**
   - 历史计划、实现、outputs 都保留。

2. **不否定**
   - 它们已经形成重要的工程可靠性与实现可信度证据。

3. **不再默认继续扩写**
   - 不得因为“链还可以再长一点”而自动生成 `199+`。

4. **只在支持 DualScope 时引用**
   - 例如：
     - appendix reliability evidence
     - implementation robustness section
     - execution-path hardening note
     - reproducibility support

5. **必须明确标注用途**
   - 若新计划引用旧链，必须写清：
     - 这是 historical engineering chain
     - 这是 reliability foundation
     - 不是当前主创新推进线

---

## 9. Milestone Guidance

建议每份计划按 milestone 推进。

一个好的 milestone 应满足：

- 增加一个真实能力
- 能被验证
- 完成后仓库仍是 coherent 的

好的 milestone 示例：

- freeze DualScope illumination screening contract
- export confidence verification features for with/without logprobs
- build budget-aware two-stage fusion baseline
- produce appendix-ready reliability foundation summary
- generate paper-ready figure/table bundle

不好的 milestone 示例：

- 做检测
- 改一下代码
- 把阶段号继续往后写

---

## 10. Low-Interruption Plan Execution

当一个 ExecPlan 已经清晰定义了后续 milestone 时，执行者应默认采用**低打扰模式**。

### 规则

1. 不要在每个小步骤后询问用户是否继续
2. 只要未超出当前计划范围，就继续推进
3. 优先在一次工作会话内完成尽可能多的 milestone
4. 只在 milestone 边界、必须打断、或计划失效时汇报

### 必须打断的情况

- 需要用户做关键研究判断
- 将进行破坏性或不可逆修改
- 需要外部凭证、下载授权、账号或人工输入
- 当前计划明显不再适用
- 出现多个高影响分支，且无法通过现有计划自行裁决

### 推荐行为

- milestone 完成后更新 Progress
- 同步更新 Decision Log
- 同步更新 Remaining Risks
- 如果当前计划可安全完成，则尽量完成整份计划后再汇报

---

## 11. Execution Behavior While Following a Plan

执行计划时必须遵守：

1. 不要默默偏离计划
2. 如果现实与计划不一致，先更新计划
3. 不要跳过进度更新
4. 优先可验证的小步迭代
5. 每个暂停点都应尽量留下清晰状态
6. 若下一步已在计划中定义，默认继续推进，不要反复打断用户
7. 若某条旧 route_c 计划与 DualScope 主线无关，不要默认继续它

---

## 12. Recommended Default Plan Families

当前仓库默认应优先创建以下类型的新计划：

1. illumination screening 计划
2. confidence verification 计划
3. budget-aware fusion 计划
4. dataset / model / trigger / target experiment 计划
5. cost analysis / with-vs-without-logprobs 计划
6. paper writing / figure / table / appendix 计划
7. reliability foundation packaging 计划

默认**不再优先**创建：

1. `199+` 旧 route_c 递归扩展计划
2. reasoning branch 补全计划
3. 单纯为了阶段号增长的链式收口计划
4. 与 DualScope 主线无关的 route_c stability chain 计划

---

## 13. Minimal Resume Rule

当用户只说“继续”“接着做”“往下推进”时，默认恢复策略为：

1. 先读取 `DUALSCOPE_MASTER_PLAN.md`
2. 找到与 DualScope 当前阶段最相关的 `.plans/*.md`
3. 读取 `Progress`
4. 定位第一个未完成 milestone
5. 直接继续执行
6. 按低打扰规则在 milestone 边界汇报

如果最新相关计划属于 TriScope 历史链，但不再服务于 DualScope 主线，则不要默认继续它。
