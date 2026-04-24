---
applyTo: "src/eval/**/*.py,src/features/**/*.py,notebooks/**/*.ipynb,scripts/evaluate.py,scripts/ablation.py,scripts/error_analysis.py"
---

# Evaluation and Analysis Instructions

## 目标

这里的代码和分析内容不是为了“跑一次结果”，而是为了支持研究论文写作、消融实验、误报分析和图表导出。

## 评估代码要求

- 指标实现必须清晰、可复核。
- 主结果与分组结果都要可导出。
- 除总体分数外，还应保留：
  - 按模型分组
  - 按 trigger type 分组
  - 按 target type 分组
  - 按 query budget 分组
- 所有结果优先写成 CSV/JSON，而不是只打印到终端。

## 指标要求

尽量统一支持：

- ROC-AUC
- F1
- Precision
- Recall
- TPR@FPR=1%
- 平均 query 数
- 平均额外时延

如果某次实验不能输出某个指标，要明确说明原因。

## 特征数据要求

- 所有特征表必须带 sample_id
- 融合前必须检查样本对齐
- 缺失值要显式处理，不要静默丢弃
- 特征列命名应可读，不要只有缩写

## Notebook 要求

- Notebook 只做分析与展示，不要承载核心生产逻辑
- 复杂逻辑应回收到 `src/` 或 `scripts/`
- Notebook 应能复现实验结果或图表，而不是依赖隐藏状态
- 标注输入文件和输出图表路径

## 论文导向要求

优先支持导出：

- 主结果表
- 消融表
- budget 曲线
- 不同 trigger/target 的热力图或分组表
- 误报案例清单

## 误报分析

误报分析相关代码必须尽量保留原始文本、模块分数和必要中间字段，方便手工挑案例写论文。

## 禁止事项

- 不要把画图代码和训练逻辑硬绑在一起
- 不要只保留最终平均数
- 不要在 notebook 里偷偷改数据流程而不回写正式脚本