# 015 Real Pilot Fusion Readiness

## Purpose / Big Picture

014 之后，TriScope-LLM 已经拥有三条真实 pilot：illumination、reasoning、confidence。下一步最自然的工作不是继续扩新 pilot，而是把这三条真实 pilot 正式接入统一的 reporting / alignment / fusion readiness 层，让项目从“多条真实 pilot 已存在”推进到“real-pilot 级融合输入已经建立”。

015 的目标不是直接做复杂 classifier，而是先把三条真实 pilot 的对齐条件、coverage、fusion 输入和 readiness 状态做实，并确保这些产物可以被后续 real-pilot baseline 直接消费。

## Scope

### In Scope

- 刷新 cross-pilot reporting 到 3/3 coverage
- real-pilot 级 cross-pilot registry / comparison / coverage summary
- real-pilot fusion dataset 构建
- real-pilot alignment summary
- real-pilot fusion readiness summary
- acceptance / repeatability / README

### Out of Scope

- 第四条 pilot
- 更重模型或更大数据切片
- benchmark-scale 真实实验矩阵
- 复杂 fusion classifier 搜索
- 最终论文结论导出

## Repository Context

本计划将衔接：

- `outputs/pilot_runs/pilot_csqa_reasoning_local_ready/*`
- `outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/*`
- `outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready/*`
- `outputs/analysis_reports/smoke_report/*`
- `src/fusion/feature_alignment.py`
- `src/eval/`
- `scripts/`

## Deliverables

- `.plans/015-real-pilot-fusion-readiness.md`
- `src/eval/real_pilot_fusion_readiness.py`
- `scripts/build_real_pilot_fusion_readiness.py`
- `src/eval/real_pilot_fusion_checks.py`
- `scripts/validate_real_pilot_fusion_readiness.py`
- `cross_pilot_registry.json`
- `cross_pilot_artifact_registry.json`
- `cross_pilot_summary.json`
- `pilot_comparison.csv`
- `pilot_coverage_summary.json`
- `real_pilot_vs_smoke_summary.json`
- `real_pilot_fusion_dataset.jsonl`
- `real_pilot_fusion_dataset.csv`
- `real_pilot_alignment_summary.json`
- `real_pilot_fusion_readiness_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 刷新 cross-pilot reporting 到 3/3 coverage
- [x] Milestone 2: real-pilot fusion dataset / alignment / readiness
- [x] Milestone 3: acceptance / repeatability / README / 计划收口

## Surprises & Discoveries

- 三条真实 pilot 当前都落在同一个 local CSQA-style slice 上，并且在相同 seed 下产生了相同的 `sample_id` 子集，因此 full intersection 真实存在。
- 真实 pilot 虽然能全交集对齐，但三条模块的 `trigger_type` / `target_type` 语义并不完全一致，因此 real-pilot fusion readiness 需要把“可对齐”和“已统一语义”区分开来。
- 015 完成时，real-pilot fusion dataset 的 `num_rows_with_all_modalities = 2`，而 `num_rows_with_any_missing_modality = 0`，说明当前 pilot 级对齐已经脱离了 007 的 missingness-heavy smoke 条件。

## Decision Log

- 决策：015 直接复用 007 的 `feature_alignment.build_fusion_dataset` 作为 real-pilot alignment 内核。
  - 原因：当前三条真实 pilot 的 sample-level feature schema 已稳定，且 `sample_id` 对齐逻辑与 007 阶段一致，没有必要重写一套并行的 alignment 层。
  - 影响范围：`src/eval/real_pilot_fusion_readiness.py`、real-pilot alignment summary、real-pilot fusion dataset artifact。

- 决策：real-pilot fusion dataset 默认采用 `inner join`。
  - 原因：当前三条真实 pilot 存在 full intersection，使用 `inner` 更能明确表达“真正的 real-pilot fusion 输入已经存在”，而不是继续停留在 missingness-only 视角。
  - 影响范围：`real_pilot_alignment_summary.json`、`real_pilot_fusion_readiness_summary.json`、后续 016 baseline 输入口径。

- 决策：015 显式记录 `ground_truth_label_available = false`。
  - 原因：当前三条真实 pilot 建立在本地 benign CSQA-style slice 上，没有 backdoor ground-truth label；这会影响 016 中监督式 logistic baseline 的可行性判断。
  - 影响范围：readiness summary、016/M1 baseline 设计、README 解释边界。

## Plan of Work

先把 013 的 cross-pilot reporting 扩展到 reasoning + confidence + illumination 三条真实 pilot，并明确当前 3/3 coverage 的 before/after 状态。随后利用三条真实 pilot 的 full-intersection `sample_id` 构建一份 real-pilot fusion dataset，并在 readiness summary 中明确当前 join 策略、missingness 情况、标签可用性和后续 baseline 可行性。最后再补 acceptance、repeatability 和 README，让 015 形成可交接状态。

## Concrete Steps

1. 创建 `.plans/015-real-pilot-fusion-readiness.md`。
2. 实现 `src/eval/real_pilot_fusion_readiness.py`。
3. 实现 `scripts/build_real_pilot_fusion_readiness.py`。
4. 读取三条真实 pilot 的 run summary、feature summary、validator artifacts 和 smoke report summary。
5. 构建 3/3 coverage 的 cross-pilot registry / summary。
6. 以 `inner join` 构建 real-pilot fusion dataset。
7. 输出 alignment summary 与 fusion readiness summary。
8. 实现 `src/eval/real_pilot_fusion_checks.py` 与 `scripts/validate_real_pilot_fusion_readiness.py`。
9. 重跑一次 readiness 构建做 repeatability。
10. 更新 README 与计划状态。

## Validation and Acceptance

- `build_real_pilot_fusion_readiness.py --help` 可正常显示
- `validate_real_pilot_fusion_readiness.py --help` 可正常显示
- 成功生成：
  - `cross_pilot_registry.json`
  - `cross_pilot_artifact_registry.json`
  - `cross_pilot_summary.json`
  - `pilot_comparison.csv`
  - `pilot_coverage_summary.json`
  - `real_pilot_vs_smoke_summary.json`
  - `real_pilot_fusion_dataset.jsonl`
  - `real_pilot_fusion_dataset.csv`
  - `real_pilot_alignment_summary.json`
  - `real_pilot_fusion_readiness_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`
- README 已补 real-pilot fusion readiness 最小用法

## Idempotence and Recovery

- real-pilot fusion readiness 输出写入独立 `output_dir`
- 可重复运行
- 若上游 pilot artifact 缺失，应写出结构化 failure summary
- 若主 run 已存在，可在新目录 rerun 做 repeatability

## Outputs and Artifacts

- `outputs/real_pilot_fusion_readiness/*`
- `cross_pilot_registry.json`
- `cross_pilot_artifact_registry.json`
- `cross_pilot_summary.json`
- `pilot_comparison.csv`
- `pilot_coverage_summary.json`
- `real_pilot_vs_smoke_summary.json`
- `real_pilot_fusion_dataset.jsonl`
- `real_pilot_fusion_dataset.csv`
- `real_pilot_alignment_summary.json`
- `real_pilot_fusion_readiness_summary.json`

## Remaining Risks

- 当前 real-pilot fusion dataset 仍然建立在同一个 local CSQA-style 小切片和同一个轻量模型上。
- 当前三条真实 pilot 的目标语义并不完全统一，因此 real-pilot fusion readiness 主要证明“可对齐、可融合输入”，而不是“跨模块证据已经研究级一致”。
- 当前没有 backdoor ground-truth label，这会限制后续监督式 baseline 的解释与训练方式。

## Validation Snapshot

- `outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_readiness_summary.json`
  - full intersection available: `true`
  - num aligned rows: `2`
  - logistic ready: `false`
- `outputs/real_pilot_fusion_readiness/default/real_pilot_alignment_summary.json`
  - join mode: `inner`
  - num rows with all modalities: `2`
  - num rows with any missing modality: `0`
- `outputs/real_pilot_fusion_readiness/repeatability_default/artifact_acceptance.json`
  - acceptance status: `PASS`
- `outputs/real_pilot_fusion_readiness/repeatability_default/repeatability_summary.json`
  - repeatability status: `PASS`
  - all key metrics match: `true`

## Next Suggested Plan

若 015 完成，下一步建议创建 `.plans/016-real-pilot-fusion-baselines.md`。
