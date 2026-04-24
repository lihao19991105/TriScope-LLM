# 007 Fusion And Eval

## Purpose / Big Picture

TriScope-LLM 已经具备 illumination、reasoning、confidence 三条证据链的最小可运行与结构化 feature 输出。下一步需要先把这三路 feature 变成一个统一、可复现、可继续扩展的融合输入层，再考虑 classifier、评估矩阵和论文图表导出。

007 的首要目标不是立刻堆 classifier，而是先定义三路 feature 的统一输入契约、完成最小对齐逻辑、生成可供后续 fusion / eval 读取的聚合数据集 artifact。只有这层稳定下来，后续 logistic/xgboost/rule-based detector 与 ROC/F1 等评估才有可靠输入基础。

## Scope

### In Scope

- 定义 illumination / reasoning / confidence 三路 feature 的统一输入契约
- 实现最小 fusion dataset 对齐逻辑
- 提供最小 feature merge CLI
- 输出最小 aggregated dataset artifact
- 输出结构化 alignment summary / config snapshot / log

### Out of Scope

- classifier 矩阵
- ROC / F1 / AUC 等完整评估实现
- 消融实验与误报分析
- 在线 detector 或 defense 逻辑
- 大规模实验矩阵

## Repository Context

本计划将衔接：

- `outputs/illumination_runs/*/features/prompt_level_features.jsonl`
- `outputs/reasoning_runs/*/features/reasoning_prompt_level_features.jsonl`
- `outputs/confidence_runs/*/features/confidence_prompt_level_features.jsonl`
- `src/features/`
- `src/fusion/`
- `scripts/`
- `outputs/`

统一输入层需要兼容三路 feature 当前已有的公共对齐键：

- `run_id`
- `probe_id`
- `sample_id`

同时要显式处理三路样本覆盖不完全重合的现实情况。

## Deliverables

- 007 fusion-and-eval ExecPlan
- 统一三路 feature 输入契约
- `src/fusion/feature_alignment.py`
- `scripts/build_fusion_dataset.py`
- 一次最小 fusion dataset smoke artifact
- `src/fusion/fusion_preprocessing.py`
- `src/fusion/fusion_baselines.py`
- `scripts/run_fusion_baselines.py`
- missingness-aware preprocessed fusion dataset artifacts
- rule-based / logistic prediction artifacts

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 统一三路特征输入契约、fusion dataset 对齐逻辑、最小 feature merge CLI、最小 aggregated dataset artifact
- [x] Milestone 2: 最小 fusion baseline 与预测输出 schema
- [x] Milestone 3: 统一 eval / README / artifact 验收

## Surprises & Discoveries

- illumination 当前的 sample-level feature 是“test query”视角，样本覆盖与 reasoning / confidence 不完全重合。
- reasoning 与 confidence 在当前 smoke run 上都覆盖 poisoned query 样本，因此两者的 sample_id 集合一致，而 illumination 是另一组 query。
- M1 smoke 对齐结果证实：当前 outer join 下共有 4 条 merged row，其中 2 条是 illumination-only，2 条是 reasoning+confidence overlap，三路全交集为 0。
- 当前 fusion rows 仍然可以通过 `sample_id -> poison dataset is_poisoned` 的映射恢复监督标签，因此最小 baseline 不需要中断等待外部标注。

## Decision Log

- 决策：M1 默认使用 `outer` 对齐，而不是强制三路 `inner join`。
  - 原因：当前三路 probe 的样本覆盖天然不完全一致，强制内连接会在最小 smoke 阶段丢掉大量可审计信息。
  - 影响范围：fusion dataset row 会包含 modality presence flag 和缺失字段，后续 classifier 再决定如何消费。

- 决策：M1 先输出“统一聚合输入数据集”，不提前实现 classifier。
  - 原因：当前阶段最重要的是稳定 fusion 输入层与 artifact，而不是抢先做不稳定的分类器矩阵。
  - 影响范围：`scripts/build_fusion_dataset.py`、输出 schema、后续 007/M2 的边界。

- 决策：M1 的 merged row 采用“前缀化 modality 字段 + presence flag”设计。
  - 原因：这样既能保留三路原始特征语义，又能让后续 classifier / analysis 明确感知 missing modality。
  - 影响范围：`fusion_dataset.jsonl` / `fusion_dataset.csv` 的字段命名、后续模型输入整理方式。

- 决策：M2 默认保持 `outer join` 输入，并在预处理层显式加入 `<modality>_missing` 标志。
  - 原因：当前 smoke 融合数据里三路全交集为 0，若退回 inner join 将直接失去训练/预测链路验证价值。
  - 影响范围：`preprocessed_fusion_dataset.*`、rule/logistic baseline 的输入列、prediction schema。

- 决策：M2 对缺失数值特征统一做 `0.0` 安全填充，但永远配套 missingness flag。
  - 原因：当前目标是跑通 missingness-aware baseline，而不是把缺失样本静默丢弃。
  - 影响范围：预处理后的数值列、logistic baseline 的可训练矩阵、后续对 missingness 的解释方式。

- 决策：M2 只实现 rule-based 和 logistic regression 两条最小 baseline。
  - 原因：这两条路径已经足以验证 missingness-aware 融合闭环；更复杂树模型和完整 classifier 矩阵留到后续阶段。
  - 影响范围：`src/fusion/fusion_baselines.py`、prediction artifacts、M3 和后续 eval 的边界。

- 决策：M3 为 fusion 模块新增独立 artifact acceptance / repeatability CLI。
  - 原因：fusion 需要和 illumination / reasoning / confidence 一样具备可交接的收口入口，而不是依赖零散手工检查。
  - 影响范围：新增 `src/fusion/fusion_artifact_checks.py` 与 `scripts/validate_fusion_artifacts.py`，README 的 fusion 输出路径说明。

- 决策：007 在 M3 后整体收口，不继续在本阶段扩 classifier 矩阵。
  - 原因：当前 fusion 已具备 outer-join dataset、missingness-aware preprocessing、最小 baseline、repeatability 和 artifact acceptance，已经满足交接给 analysis/reporting 层的条件。
  - 影响范围：更完整的 classifier / eval matrix 留到后续 008 与后续计划，而不是继续膨胀 007。

## Plan of Work

先定义三路 feature 的最小公共契约和 modality-specific 必需字段，再实现一个明确的 alignment 模块，把 illumination、reasoning、confidence 三路 sample-level feature 按 `sample_id` 做可审计对齐。对齐后输出 run-scoped JSONL / CSV / summary / snapshot，作为后续 fusion classifier 和 eval 的统一输入层。M1 稳定之后，在 M2 中增加 missingness-aware preprocessing，把 outer-join rows 转成可训练的安全数值表，再在此基础上补最小 rule-based 和 logistic regression baseline，以及统一 prediction schema。

## Concrete Steps

1. 创建 `.plans/007-fusion-and-eval.md` 并定义 milestone 边界。
2. 实现 `src/fusion/feature_alignment.py`：
   - 加载三路 sample-level feature JSONL
   - 校验每一路最小 required fields
   - 按 `sample_id` 做 outer / inner 对齐
   - 为每条 merged row 写入 modality presence flag、core metadata、前缀化 feature 字段
3. 实现 `scripts/build_fusion_dataset.py`：
   - 接收三路 feature 路径
   - 接收 `--join-mode`
   - 输出 JSONL / CSV / summary / config snapshot / log
4. 用当前 smoke runs 生成一次最小 fusion dataset artifact。
5. 实现 `src/fusion/fusion_preprocessing.py`：
   - 读取 fusion dataset
   - 恢复 `sample_id -> is_poisoned` 标签
   - 为每个模态生成 present / missing 标志
   - 对缺失数值特征进行安全填充并保留 canonical 元字段
6. 实现 `src/fusion/fusion_baselines.py`：
   - 透明 rule-based score
   - missingness-aware logistic regression baseline
   - 统一 prediction schema
7. 实现 `scripts/run_fusion_baselines.py`，输出预处理数据集、预测 artifact、模型元数据和 compact summary。
8. 用当前 smoke fusion dataset 跑通最小 baseline。
9. 实现 `src/fusion/fusion_artifact_checks.py` 与 `scripts/validate_fusion_artifacts.py`。
10. 用相同输入和 seed 重跑 fusion dataset build 与 fusion baselines，验证 repeatability。
11. 更新 README 的 fusion 用法与 artifact 说明。
12. 更新 Progress、Decision Log、Remaining Risks。

## Validation and Acceptance

- `build_fusion_dataset.py --help` 可正常显示
- 能成功读取 illumination / reasoning / confidence 三路 feature 输入
- 能生成：
  - `fusion_dataset.jsonl`
  - `fusion_dataset.csv`
  - `alignment_summary.json`
  - `config_snapshot.json`
  - `build.log`
- 每条 merged row 至少包含：
  - `sample_id`
  - `illumination_present`
  - `reasoning_present`
  - `confidence_present`
  - `modality_count`
- alignment summary 至少包含：
  - `num_rows`
  - `join_mode`
  - `num_illumination_rows`
  - `num_reasoning_rows`
  - `num_confidence_rows`
  - `num_rows_with_all_modalities`
- M2 至少生成：
  - `preprocessed_fusion_dataset.jsonl`
  - `preprocessed_fusion_dataset.csv`
  - `rule_predictions.jsonl`
  - `rule_summary.json`
  - `logistic_predictions.jsonl`
  - `logistic_summary.json`
  - `logistic_model_metadata.json`
  - `fusion_summary.json`
- prediction row 至少包含：
  - `run_id`
  - `sample_id`
  - `fusion_profile`
  - `prediction_score`
  - `prediction_label`
  - `label_threshold`
  - `illumination_present`
  - `reasoning_present`
  - `confidence_present`
  - `modality_count`
- 缺失模态样本不会导致 rule/logistic baseline 崩溃
- logistic baseline 必须明确：
  - 使用了哪些输入列
  - 如何处理缺失值
  - 是否使用标准化

## Idempotence and Recovery

- feature merge CLI 支持重复运行到不同 `output_dir`
- 输出为 run-scoped artifact，不依赖隐式全局状态
- 若任一路输入缺失或 schema 不匹配，应写出结构化 failure summary
- `fusion_dataset.jsonl` 与 `config_snapshot.json` 可作为后续 classifier / eval 的恢复入口
- `preprocessed_fusion_dataset.jsonl` 与 `logistic_model_metadata.json` 可作为后续 baseline / eval 的恢复入口

## Outputs and Artifacts

- `outputs/fusion_datasets/*`
- `fusion_dataset.jsonl`
- `fusion_dataset.csv`
- `alignment_summary.json`
- `config_snapshot.json`
- `build.log`
- `preprocessed_fusion_dataset.jsonl`
- `preprocessed_fusion_dataset.csv`
- `rule_predictions.jsonl`
- `rule_summary.json`
- `logistic_predictions.jsonl`
- `logistic_summary.json`
- `logistic_model_metadata.json`
- `fusion_summary.json`

## Remaining Risks

- 当前 M1 只解决统一输入对齐，不代表 fusion 已经具备检测效果。
- illumination 与 reasoning/confidence 的样本覆盖不完全重叠，因此 outer join 行里会出现 modality 缺失；后续 classifier 需要显式处理 missingness。
- 当前 smoke 仍基于 tiny 本地模型，fusion dataset 主要用于验证 schema 与 artifact，而不是研究结论。
- 当前 smoke fusion dataset 中三路全交集为 0，这意味着 M2 若要做 classifier baseline，必须先明确是否使用 outer-join 缺失编码，还是补更多可对齐的 probe 样本。
- 当前 M2 的 logistic baseline 会在极小样本上自拟合训练与预测，因此其分数只用于验证链路，不具备研究意义。
- 当前 rule-based score 只能使用已有 sample-level signal，无法替代后续更完整的跨模态 detector。
- 当前 repeatability 只验证了同一 smoke artifact 输入、同一 seed 和同一 outer-join 策略下的稳定性，还没有覆盖更丰富的 fusion profiles。
- 当前 fusion README 说明和 artifact acceptance 已足够支持交接，但统一 analysis/reporting 仍需下一阶段补 run registry、artifact registry 和 smoke-level summary。

## Next Suggested Plan

若 007 完成，下一步建议创建 `.plans/008-ablation-and-analysis.md`。
