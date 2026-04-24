---
applyTo: "src/**/*.py,scripts/**/*.py"
---

# Python Source and CLI Instructions

## 总体要求

- 优先写清晰、可测试、可复现的研究代码。
- 优先小函数，不要巨型脚本。
- 核心逻辑写进 `src/`，命令行入口写进 `scripts/`。
- CLI 不要直接堆业务逻辑。
- 所有文件路径都要通过参数或配置传入，不要硬编码本地绝对路径。
- 所有随机行为必须显式设置 seed。
- 所有输出都写入 `outputs/` 或用户指定输出目录。

## Python 代码规范

- 使用 Python 3.10+ 语法。
- 为公开函数和关键类添加类型注解。
- 对非直观逻辑补充简明注释。
- 优先使用 `pathlib.Path` 而不是字符串拼路径。
- 明确处理异常，并输出可读错误信息。
- 不要引入无必要的框架式复杂抽象。
- 不要把 prompt 文本、trigger 文本、target 模板散落在脚本内部。

## 模块边界

- `src/attacks/`：数据注毒、trigger 注入、target 模板
- `src/models/`：模型加载、后端抽象、推理辅助
- `src/probes/`：illumination / reasoning / confidence
- `src/features/`：特征抽取、特征对齐、融合数据集
- `src/fusion/`：最终检测器
- `src/eval/`：指标、报告、可视化辅助

不要把这些职责混写到一个文件里。

## CLI 脚本要求

每个 `scripts/*.py` 至少应做到：

- 使用 `argparse`
- 支持 `--help`
- 支持输入路径、输出路径、seed、config 路径
- 运行结束后打印关键产物位置
- 失败时给出明确报错

## 研究原型特定要求

- 所有探针模块必须输出结构化结果，便于后续 fusion。
- 不要只输出“是否命中”，要尽量输出中间统计量。
- 优先保留可用于消融与误报分析的字段。
- 不要把单模块写成不可组合的黑盒脚本。

## 禁止事项

- 不要一次性写很多未使用的 util 函数。
- 不要在脚本中复制粘贴同样的数据加载逻辑。
- 不要在没有 smoke test 的情况下扩展多个模块。
- 不要将 notebook 风格代码直接塞进 `src/`。