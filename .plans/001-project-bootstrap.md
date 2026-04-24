# 001 Project Bootstrap

## Purpose / Big Picture

TriScope-LLM 当前只有仓库级约束文档，尚未形成可运行的研究原型骨架。本计划用于完成项目初始化，建立后续各阶段都要复用的目录、配置入口、依赖声明、环境检查脚本和 README 基线说明。

现在先做这件事，是为了给后续“注毒数据构造 -> LoRA 训练 -> 三类探针 -> 融合评估”提供稳定起点，避免后续阶段反复返工目录结构、配置格式和脚本约定。完成后，仓库应具备最小但清晰的研究工程骨架，并能验证基础环境是否满足项目要求。

## Scope

In scope:

- 建立项目基础目录结构
- 建立 `src/` 包结构与必要的最小初始化文件
- 编写 `requirements.txt`
- 编写 README 初稿，说明项目目标、目录、安装与下一步使用方式
- 提供基础配置文件，覆盖项目级、模型级、运行级的最小配置入口
- 实现 `scripts/check_env.py`，用于检查 Python、PyTorch、Transformers、GPU 与输出目录可写性等基础条件
- 为后续阶段约定 `outputs/` 的基础产物落盘位置

Out of scope:

- 任何注毒数据构造逻辑
- 任何训练逻辑、LoRA 训练脚本或数据集下载逻辑
- 任何 Illumination / Reasoning / Confidence probe 细节实现
- 融合、评估、图表导出逻辑
- notebook、CI、容器化、分布式训练支持

## Repository Context

当前仓库仅包含 `AGENTS.md`、`PLANS.md` 和 `.github/` 说明文件，尚无正式源码、脚本、配置与文档骨架。

本计划主要会涉及：

- `README.md`
- `requirements.txt`
- `configs/`
- `scripts/`
- `src/`
- `outputs/`
- `.plans/001-project-bootstrap.md`

这些产物会成为后续 `002-poison-data-pipeline.md` 和更后续探针/融合计划的公共基础。

## Deliverables

- 项目目录骨架
- 最小 `src/` 包结构
- `requirements.txt`
- README 初稿
- 基础配置文件若干
- `scripts/check_env.py`
- 一个可执行的 bootstrap 计划文档及其进度记录

## Progress

- [x] 梳理仓库约束与当前目录现状
- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 建立目录结构与最小包骨架
- [x] Milestone 2: 编写 `requirements.txt` 与 README 初稿
- [x] Milestone 3: 提供基础配置并实现 `scripts/check_env.py`
- [x] Milestone 4: 运行 bootstrap smoke test 并补齐计划记录

## Surprises & Discoveries

- 当前仓库几乎为空，只存在规则文档，没有任何现成代码可复用。
- 因为没有现有实现，本阶段需要谨慎控制“骨架”粒度，避免一次性生成大量未来可能不用的空壳代码。
- 本地环境没有 `python` 命令别名，至少当前 shell 中应默认使用 `python3` 运行脚本与 smoke test。
- 对本项目而言，`torch` 虽然是事实上的核心依赖，但安装方式强依赖 CUDA/驱动环境，直接在 `requirements.txt` 中固定版本会提高 bootstrap 失败概率。
- `xgboost` 属于后续 fusion baseline 的明确候选依赖，但当前 milestone 没有任何 fusion 实现，过早启用会扩大安装面且增加环境噪声。
- 当前机器上的 `python3` 实际版本是 3.8.10，不满足仓库要求的 Python 3.10+；这会被 `check_env.py` 明确标记为 `FAIL`。
- 当前环境虽然已安装 `torch 1.13.1+cu117`，但 `torch.cuda.is_available()` 为 `False`，说明至少当前运行上下文里没有可用 CUDA 设备。
- 实际环境中缺少 `peft`、`accelerate`、`datasets`、`scikit-learn`、`pandas`、`matplotlib`，这验证了 `check_env.py` 的缺失依赖提示路径是必要的。
- bootstrap smoke test 已成功覆盖两条主路径：包导入检查返回 `bootstrap_import_ok`，`check_env.py` 成功产出报告并在环境不满足时返回可解释的 `FAIL`。

## Decision Log

- 决策：将 bootstrap 拆为 4 个 milestone，而不是一次性完成全部初始化。
  - 原因：符合“小步可验证”的执行纪律，避免刚开始就铺开过多文件。
  - 影响范围：本计划的实现顺序、验证方式和暂停点都会围绕 milestone 展开。

- 决策：Milestone 1 只做目录结构和最小包骨架，不在此阶段写业务逻辑。
  - 原因：先建立稳定载体，再逐步补 README、依赖和环境检查，能减少返工。
  - 影响范围：`src/`、`configs/`、`scripts/`、`outputs/` 的初始化方式和首轮提交边界。

- 决策：基础配置优先使用可读的 YAML 结构。
  - 原因：便于研究迭代、手工检查与命令行传参扩展。
  - 影响范围：后续所有脚本和模块的配置读取约定。

- 决策：Milestone 1 中用最小 `__init__.py` 和 `.gitkeep` 固定骨架，而不是提前放占位业务模块。
  - 原因：既能保证目录被版本控制追踪，也能避免生成误导性的空实现。
  - 影响范围：`src/`、`configs/`、`scripts/`、`outputs/` 的首轮落盘方式。

- 决策：后续 README、命令示例和环境检查脚本默认使用 `python3`。
  - 原因：当前环境缺少 `python` 命令别名，直接写 `python` 会降低 bootstrap 成功率。
  - 影响范围：文档、smoke test 和 CLI 示例的默认写法。

- 决策：`requirements.txt` 先纳入 `transformers`、`peft`、`accelerate`、`datasets`、`PyYAML`、`tqdm`、`pandas`、`scikit-learn`、`matplotlib`，暂不激活 `xgboost`。
  - 原因：这些依赖已经被项目目标、近期里程碑和研究分析需求明确覆盖；`xgboost` 对后续 fusion 有意义，但当前阶段尚无实现，先注释保留更保守。
  - 影响范围：bootstrap 安装体验、后续 fusion milestone 的依赖补充方式。

- 决策：不在 `requirements.txt` 中固定 `torch`。
  - 原因：PyTorch 的安装与 CUDA 版本、驱动和本地环境强相关，放到 README 中单独说明更稳妥。
  - 影响范围：环境准备文档、后续 `check_env` 脚本的检查逻辑。

- 决策：README 初稿只描述当前真实存在的骨架与下一步计划，不伪装为已具备完整实验流水线。
  - 原因：项目仍处于 bootstrap 阶段，文档应真实反映仓库能力边界。
  - 影响范围：README 的章节设计、最小启动说明与开发状态说明。

- 决策：Milestone 3 仅增加 `models.yaml`、`attacks.yaml`、`detection.yaml`，不额外引入 `experiments.yaml`。
  - 原因：当前阶段已经明确需要的是模型、攻击和检测三类基础配置；实验组合层配置尚未出现实际消费方，提前加入会扩大配置面。
  - 影响范围：当前 `configs/` 结构与下一步数据/训练计划的配置扩展方式。

- 决策：每个 YAML 只提供 `default` 与 `reference` 两个最小示例块。
  - 原因：既能提供可读示例和扩展锚点，又避免把未来参数过早塞进 bootstrap。
  - 影响范围：配置文件的首轮结构，以及后续模块默认读取逻辑的设计预期。

- 决策：`scripts/check_env.py` 采用“逐项检查 + 结构化 JSON 落盘 + PASS/WARN/FAIL 汇总”的实现。
  - 原因：需要同时满足命令行可读性、后续 README 引用友好性，以及研究原型对结果落盘的要求。
  - 影响范围：`outputs/check_env/` 的产物形态，以及后续 bootstrap smoke test 的验收方式。

- 决策：缺少依赖、CUDA 不可用或版本不满足要求时，`check_env.py` 不抛出未处理异常，而是输出清晰结果并用退出码表达总体状态。
  - 原因：环境检查脚本的目标是诊断问题而不是中断用户定位过程。
  - 影响范围：CLI 用户体验、README 中的使用说明和自动化验收脚本。

- 决策：bootstrap 计划的完成标准是“骨架、配置、文档与环境检查能力已具备”，而不是“当前机器环境已经满足全部运行条件”。
  - 原因：bootstrap 的职责是建立可诊断、可恢复的研究原型起点；真实环境是否达标应由 `check_env.py` 暴露，而不是作为计划无法收口的阻塞项。
  - 影响范围：001 计划的验收边界，以及后续阶段对环境前置条件的处理方式。

## Plan of Work

先建立最小但清晰的仓库骨架，让后续文件有明确落点；然后补齐依赖声明和 README，让新接手的人能理解项目与安装方式；再补基础配置和环境检查脚本，形成一个真正可运行的 bootstrap 闭环；最后做一次 smoke test，确认脚本能运行、目录可用，并把执行计划中的进度、决策和风险更新到位。

每一步都只引入当前阶段确实需要的内容，避免提前写 probe、训练或评估的伪实现。后续阶段应直接复用这里建立的目录和配置约定，而不是重新定义。

## Concrete Steps

1. 在仓库根目录创建 `.plans/001-project-bootstrap.md`，明确 scope、milestone、验收标准和风险。
2. 创建 `configs/`、`scripts/`、`src/`、`outputs/` 及 `src` 下各子模块目录，并只加入最小初始化文件。
3. 编写 `requirements.txt`，仅列出 bootstrap 与近期阶段必需依赖。
4. 编写 README 初稿，说明项目目标、目录结构、安装方式和 bootstrap 使用方法。
5. 新增基础 YAML 配置文件，覆盖项目路径、随机种子、默认模型与运行参数。
6. 实现 `scripts/check_env.py`，支持 `--config`、`--output-dir`、`--seed` 等基础参数，输出环境检查结果到 `outputs/` 或指定目录。
7. 运行 smoke test，例如 `python scripts/check_env.py --help` 与一次最小执行，确认输出文件生成成功。
8. 完成每个 milestone 后更新 `Progress`、`Decision Log` 和 `Remaining Risks`。

## Validation and Acceptance

本计划完成时，应至少满足以下可观察标准：

- 仓库存在清晰且符合 `AGENTS.md` 的目录结构
- `src/` 下基础包可被 Python 导入
- `requirements.txt` 可用于安装 bootstrap 所需依赖
- `README.md` 能说明项目定位、安装步骤和 bootstrap 用法
- 基础配置文件字段清晰，未硬编码本地绝对路径
- `python3 scripts/check_env.py --help` 可正常执行
- `python3 scripts/check_env.py ...` 可生成结构化检查结果与日志到 `outputs/`
- ExecPlan 中的进度、决策与风险在每个 milestone 后得到更新

## Idempotence and Recovery

- 目录创建应是幂等的；重复运行不会破坏现有结构。
- bootstrap 产物优先写入 `outputs/check_env/` 或用户指定目录；重复执行可覆盖同名结果，必要时通过时间戳或运行名扩展。
- 若中途中断，下一个执行者应先阅读本计划的 `Progress`、`Decision Log` 和 `Remaining Risks`，从未完成 milestone 继续。
- README、requirements 和基础配置文件是后续阶段的稳定入口，应保留并增量修改，不应随意重写。

## Outputs and Artifacts

- `outputs/check_env/`：环境检查结果、配置快照、日志
- `outputs/.gitkeep` 或等价占位方式：保持输出目录存在
- `configs/*.yaml`：项目级基础配置

## Remaining Risks

- bootstrap 阶段对依赖的选择会影响后续训练与探针实现，若现在引入过重或过轻都可能导致返工。
- 当前虽然已有基础配置与环境检查 CLI，但这些 YAML 还没有被正式业务模块消费；后续模块实现时需要保持字段命名稳定。
- `requirements.txt` 中未固定 `torch` 且暂未启用 `xgboost`，这是有意的保守策略，但后续 milestone 需要继续确认版本兼容边界。
- `scripts/check_env.py` 只能验证基础环境，不会验证后续模型下载、数据可用性或显存边界。
- 当前实际环境不满足项目推荐条件：Python 版本不足、多个核心依赖缺失、CUDA 不可用；在进入后续需要真实运行模型的阶段前必须先补环境。
- 仓库目前无真实数据与模型资源，README 初稿只能提供预期使用方式，无法覆盖实战细节。
- README 已包含 bootstrap 用法，但后续进入真实数据与训练阶段时仍需持续补充更具体的实验说明。

## Next Suggested Plan

完成本计划后，下一步建议创建 `.plans/002-poison-data-pipeline.md`，实现最小注毒数据构造闭环。
