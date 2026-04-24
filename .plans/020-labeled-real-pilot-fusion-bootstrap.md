# 020 Labeled Real Pilot Fusion Bootstrap

## Purpose / Big Picture

019 会说明：当前 labeled pilot 已经足以支撑一次 pilot-level controlled supervised fusion bootstrap。020 的目标是把这条 integration contract 真正落成可运行数据与 baseline，让 real-pilot fusion logistic 第一次不再因为缺标签而跳过。

## Scope

### In Scope

- labeled real-pilot fusion dataset materialization
- label definition / label mapping / label coverage summary
- 最小 supervised logistic baseline
- acceptance / repeatability / README

### Out of Scope

- benchmark ground-truth supervision
- 更大模型 / 更大数据
- 复杂监督实验矩阵
- 研究级结论

## Repository Context

本计划将衔接：

- `outputs/real_pilot_fusion_readiness/*`
- `outputs/real_pilot_fusion_runs/*`
- `outputs/labeled_pilot_runs/*`
- `outputs/labeled_pilot_analysis/*`
- `src/fusion/`
- `scripts/`

## Deliverables

- `.plans/020-labeled-real-pilot-fusion-bootstrap.md`
- `src/fusion/labeled_real_pilot_fusion.py`
- `scripts/build_labeled_real_pilot_fusion.py`
- `scripts/run_labeled_real_pilot_fusion_baseline.py`
- `src/fusion/labeled_real_pilot_fusion_checks.py`
- `scripts/validate_labeled_real_pilot_fusion.py`
- `labeled_real_pilot_fusion_dataset.jsonl`
- `labeled_real_pilot_fusion_summary.json`
- `labeled_real_pilot_label_definition.json`
- `labeled_real_pilot_logistic_predictions.jsonl`
- `labeled_real_pilot_logistic_summary.json`
- `labeled_real_pilot_model_metadata.json`
- `labeled_real_pilot_fusion_run_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize labeled real-pilot fusion dataset
- [x] Milestone 2: supervised real-pilot fusion baseline bootstrap
- [x] Milestone 3: acceptance / repeatability / README / 计划收口

## Surprises & Discoveries

- 现有 real-pilot full-intersection 只有 2 个 base sample，但这反而足够做第一次 labeled fusion bootstrap。
- 对齐的关键不是把 018 的 label 直接贴到现有 fusion row，而是先把 base sample row 扩成 `control / targeted` 两个 contract-level rows。
- reasoning / confidence 在当前 bootstrap 中只能按 base sample 复制到两个 labeled variants，这一点必须显式记录。
- 当前 materialized labeled real-pilot fusion dataset 共 `4` 行，类别分布为 `2 / 2`，已经足够让最小 logistic baseline 不再因为缺标签而跳过。
- 当前 supervised logistic repeatability 已验证：reference 与 rerun 的 `mean_prediction_score` 都是 `0.49952191696685133`。

## Decision Log

- 决策：020 采用 `base_sample_id + contract_variant` 作为 labeled fusion row 的主对齐键。
  - 原因：单独 `sample_id` 无法表达 control / targeted 两个变体，而这正是 018 的监督来源。
  - 影响范围：`labeled_real_pilot_fusion_dataset.jsonl` schema、validator、baseline metadata。

- 决策：020 让 illumination 模态使用 labeled pilot feature，reasoning / confidence 继续复用同一 base sample 的 real-pilot feature。
  - 原因：这是当前最小成本、最可审计的 fusion integration；它诚实地承认了只有 illumination 承载 controlled label。
  - 影响范围：`label_mapping_rule`、`labeled_real_pilot_fusion_summary.json`、logistic baseline interpretation。

## Plan of Work

先根据 019 的 recommendation materialize 一份 labeled real-pilot fusion dataset：对每个可对齐 base sample，从 018 取 control / targeted illumination row，再接回同一 base sample 的 reasoning / confidence row。然后在这份 dataset 上运行一版最小 logistic bootstrap，并把整个链路做 acceptance / repeatability 收口。

## Concrete Steps

1. 创建 `.plans/020-labeled-real-pilot-fusion-bootstrap.md`。
2. 实现 `src/fusion/labeled_real_pilot_fusion.py`。
3. 实现 `scripts/build_labeled_real_pilot_fusion.py`。
4. 生成 labeled fusion dataset 与 label definition。
5. 实现 `scripts/run_labeled_real_pilot_fusion_baseline.py`。
6. 运行最小 logistic baseline。
7. 增加 validator、repeatability、README 与计划更新。

## Validation and Acceptance

- `build_labeled_real_pilot_fusion.py --help` 可正常显示
- `run_labeled_real_pilot_fusion_baseline.py --help` 可正常显示
- `validate_labeled_real_pilot_fusion.py --help` 可正常显示
- M1 成功生成：
  - `labeled_real_pilot_fusion_dataset.jsonl`
  - `labeled_real_pilot_fusion_summary.json`
  - `labeled_real_pilot_label_definition.json`
- M2 至少成功生成：
  - `labeled_real_pilot_logistic_predictions.jsonl`
  - `labeled_real_pilot_logistic_summary.json`
  - `labeled_real_pilot_model_metadata.json`
  - `labeled_real_pilot_fusion_run_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

### Validation Snapshot

- `outputs/labeled_real_pilot_fusion/default/labeled_real_pilot_fusion_summary.json`
  - `num_rows = 4`
  - `num_base_samples = 2`
  - `label_name = controlled_targeted_icl_label`
  - `class_balance = {label_0: 2, label_1: 2}`
- `outputs/labeled_real_pilot_fusion_runs/default/labeled_real_pilot_logistic_summary.json`
  - `summary_status = PASS`
  - `num_predictions = 4`
  - `num_positive_predictions = 2`
- `outputs/labeled_real_pilot_fusion_runs/repeatability_default/repeatability_summary.json`
  - `all_key_metrics_match = true`

## Idempotence and Recovery

- 020 输出写入独立 `output_dir`
- 可重复运行
- 若某一上游 artifact 缺失，应写出结构化 failure summary

## Outputs and Artifacts

- `outputs/labeled_real_pilot_fusion/*`
- `outputs/labeled_real_pilot_fusion_runs/*`
- `labeled_real_pilot_fusion_dataset.jsonl`
- `labeled_real_pilot_fusion_summary.json`
- `labeled_real_pilot_label_definition.json`
- `labeled_real_pilot_logistic_predictions.jsonl`
- `labeled_real_pilot_logistic_summary.json`
- `labeled_real_pilot_model_metadata.json`
- `labeled_real_pilot_fusion_run_summary.json`

## Remaining Risks

- 当前监督标签仍然只是 pilot-level controlled supervision。
- 当前 logistic 仍然是 bootstrap self-fit，小样本极少，不能当成可信监督结果。
- 当前 mapping 会把 reasoning / confidence 特征在同一 base sample 下复制给 control / targeted 两个变体。
- 当前 dataset 仍然建立在同一 local CSQA-style 小切片与同一轻量模型之上，因此 supervised fusion 仍然只是“路径存在性”证明。

## Next Suggested Plan

若 020 完成，下一步建议创建 `.plans/021-labeled-fusion-analysis-and-scaling-decision.md`。
