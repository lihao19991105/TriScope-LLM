# TriScope-LLM Repository Instructions for GitHub Copilot

本仓库实现一个研究型项目：

**TriScope-LLM：面向黑盒大语言模型的后门检测框架**

目标是实现并评估一个统一的黑盒 LLM 后门检测框架，融合三类信号：
1. Illumination Probe
2. Reasoning Scrutiny
3. Confidence Collapse

---

## 1. 总体工作原则

- 这是一个**研究原型仓库**，不是生产系统。
- 优先实现**最小可运行版本（MVP）**，再逐步增强。
- 一次只做一个清晰阶段，不要同时扩展多个大模块。
- 不要一次性生成大量空壳文件或未经验证的模板代码。
- 所有实现必须以“可运行、可复现、可分析”为优先目标。
- 所有实验输出必须写入 `outputs/` 目录。
- 所有随机行为必须固定种子。
- 所有脚本都必须支持命令行参数。
- 所有实现要尽量透明、易读、易调试，避免过度抽象。

---

## 2. 项目资源约束

默认环境：
- Linux
- Python 3.10+
- 2 x RTX 3090

实现要求：
- 默认支持 HuggingFace 本地模型
- 保留 API backend 抽象，但不优先依赖闭源 API
- 训练默认采用 **LoRA / PEFT**
- 不要默认实现 full finetune
- 不要引入复杂分布式训练基础设施，除非明确要求

---

## 3. 项目方法约束

本项目不是对已有工作的简单拼接，不要把代码写成“三个 baseline 的机械组合”。

需要体现统一框架思想：

- **Illumination**：暴露后门对新 trigger 的异常易感性
- **Reasoning**：暴露后门绕开正常推理的捷径行为
- **Confidence**：暴露后门生成过程中的 sequence lock / 置信坍缩
- **Fusion**：将三类信号统一建模为后门证据链

最终系统应输出统一的后门风险分数与检测标签。

---

## 4. 目录与文件约束

推荐目录结构：

- `configs/`：模型、攻击、检测、实验配置
- `scripts/`：命令行入口
- `src/attacks/`：注毒与 trigger/target 模板
- `src/models/`：模型加载与推理后端
- `src/probes/`：illumination / reasoning / confidence 探针
- `src/features/`：特征抽取与融合数据构建
- `src/fusion/`：logistic / xgboost / rule-based detector
- `src/eval/`：评估与报告
- `outputs/`：结果与实验产物

要求：
- prompt 模板、trigger 模板、target 模板必须单独管理
- 不要把路径、模型名、阈值、模板内容硬编码在随机脚本里
- CLI 与核心逻辑分离
- 训练逻辑与评估逻辑分离
- 特征抽取与最终分类逻辑分离

---

## 5. 代码风格要求

- 优先使用小函数、明确输入输出
- 添加必要的类型注解
- 为非显然逻辑添加注释
- 明确错误处理
- 不要依赖隐式全局状态
- 避免难以维护的魔法常量
- 新增功能时同步更新 README 或相关说明

---

## 6. 研究实验要求

该仓库必须支持以下研究需求：

- 单模块 baseline
- 两两融合 baseline
- 三模块完整融合
- query budget 分析
- trigger type 分析
- target type 分析
- 误报分析
- 消融实验
- 论文图表导出

最终评估至少支持输出：

- ROC-AUC
- F1
- Precision
- Recall
- TPR@FPR=1%
- 平均 query 数
- 平均额外时延

---

## 7. 执行方式要求

遇到复杂任务时，不要直接大规模改代码。

请遵守以下流程：

1. 先阅读仓库中的 `AGENTS.md`
2. 如果任务涉及多步实现、重构、实验流水线或跨目录修改，先阅读 `PLANS.md`
3. 按 `PLANS.md` 的规范，在 `.plans/` 下创建或更新对应的执行计划文件
4. 按 milestone 推进
5. 每个 milestone 完成后更新计划中的进度与风险

如果仓库中不存在 `AGENTS.md` 或 `PLANS.md`，则按本文件约束执行，并建议补齐它们。

---

## 8. 每次回复或提交前应说明的内容

在完成一个有意义的阶段后，请明确说明：

1. 当前阶段目标
2. 新增/修改的文件
3. 这些文件的作用
4. 实现的核心逻辑
5. 如何运行
6. 输入输出格式
7. 已知风险
8. 建议的下一步

---

## 9. 明确禁止事项

- 不要一次性生成整仓库“看起来很多但跑不通”的代码
- 不要跳过最小可运行验证
- 不要把 prompt/trigger/threshold 写死在脚本内部
- 不要为了“工程感”过度设计抽象层
- 不要默认依赖无法保证存在的商业 API
- 不要在没有说明的情况下引入重型依赖
- 不要在未建立配置与数据结构前直接写 probe 和 fusion 逻辑

---

## 10. 当前推荐执行顺序

如果未指定其他任务，默认按以下顺序工作：

1. 项目初始化
2. 注毒数据构造
3. LoRA 注毒训练
4. Illumination Probe
5. Reasoning Probe
6. Confidence Probe
7. Feature Fusion
8. 统一评估
9. 消融与误报分析

一次只推进一个阶段。