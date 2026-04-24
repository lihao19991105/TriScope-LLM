# 019 Labeled Pilot Analysis And Fusion Integration

## Purpose / Big Picture

018 已经让 TriScope-LLM 第一次拥有可运行的 supervised pilot path，但这条路径目前仍停留在 illumination 单模块内部。019 的目标是把 017 的路线分析、018 的 labeled pilot、015/016 的 real-pilot fusion 层统一起来，明确 labeled pilot 怎样才能以最小成本接回 fusion。

## Scope

### In Scope

- labeled pilot reporting / registry
- labeled-vs-real-pilot 对齐分析
- fusion integration blocker summary
- integration recommendation
- acceptance / repeatability
- README 极简补充

### Out of Scope

- 新的第四条 pilot
- 更重模型 / 更大数据
- 研究级监督评估
- 复杂 fusion classifier 矩阵

## Repository Context

本计划将衔接：

- `outputs/real_pilot_analysis/*`
- `outputs/labeled_pilot_bootstrap/*`
- `outputs/labeled_pilot_runs/*`
- `outputs/real_pilot_fusion_readiness/*`
- `outputs/real_pilot_fusion_runs/*`
- `src/eval/`
- `scripts/`

## Deliverables

- `.plans/019-labeled-pilot-analysis-and-fusion-integration.md`
- `src/eval/labeled_pilot_analysis.py`
- `scripts/build_labeled_pilot_analysis.py`
- `src/eval/labeled_pilot_analysis_checks.py`
- `scripts/validate_labeled_pilot_analysis.py`
- `labeled_pilot_analysis_summary.json`
- `labeled_vs_real_pilot_alignment_summary.json`
- `labeled_fusion_blocker_summary.json`
- `labeled_vs_fusion_comparison.csv`
- `fusion_integration_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: labeled pilot reporting / alignment / blocker summary
- [x] Milestone 2: integration recommendation / acceptance / README / 计划收口

## Surprises & Discoveries

- labeled pilot 的标签并不直接定义在现有 real-pilot fusion row 上，而是定义在更细的 contract row 上。
- 当前最自然的 integration key 不是单独 `sample_id`，而是 `base_sample_id + contract_variant`。
- 只要接受“reasoning / confidence 在同一 base sample 下被控制标签复制复用”的 pilot-level mapping，就能最小成本构造 labeled fusion bootstrap。
- 当前自然可对齐的 base sample 只有 `2` 个：`csqa-pilot-001` 与 `csqa-pilot-005`。
- 019 的 repeatability 已验证推荐路线稳定不变：reference 与 rerun 都得到 `map_controlled_label_back_to_real_pilot_fusion`。

## Decision Log

- 决策：019 把标签层级明确拆成 benchmark ground truth、pilot-level controlled supervision、fusion integration label 三层。
  - 原因：这三者语义不同，若不拆开会在 020 中把 pilot label 误当成研究标签。
  - 影响范围：`labeled_fusion_blocker_summary.json`、`fusion_integration_recommendation.json`。

- 决策：019 默认推荐将 `controlled_targeted_icl_label` 以 pilot-level controlled mapping 接回 fusion。
  - 原因：这条路径能最小成本解除 016 中的 `missing_ground_truth_labels` 阻塞，并且不需要新资源。
  - 影响范围：020 的 dataset materialization contract 和 supervised baseline 设计。

## Plan of Work

先读取 017 的 recommendation、018 的 labeled pilot summary，以及 015/016 的 readiness 与 baseline summary，建立 labeled pilot reporting 与 blocker summary。然后比较“让 labeled path 独立存在”与“最小成本映射回 fusion”两条路线；若可行，则明确推荐后者并给出最小 integration contract。

## Concrete Steps

1. 创建 `.plans/019-labeled-pilot-analysis-and-fusion-integration.md`。
2. 实现 `src/eval/labeled_pilot_analysis.py`。
3. 实现 `scripts/build_labeled_pilot_analysis.py`。
4. 生成 alignment / blocker / recommendation artifacts。
5. 实现 validator 与 repeatability。
6. 更新 README 与计划状态。

## Validation and Acceptance

- `build_labeled_pilot_analysis.py --help` 可正常显示
- `validate_labeled_pilot_analysis.py --help` 可正常显示
- 成功生成：
  - `labeled_pilot_analysis_summary.json`
  - `labeled_vs_real_pilot_alignment_summary.json`
  - `labeled_fusion_blocker_summary.json`
  - `labeled_vs_fusion_comparison.csv`
  - `fusion_integration_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

### Validation Snapshot

- `outputs/labeled_pilot_analysis/default/fusion_integration_recommendation.json`
  - `recommended_route = map_controlled_label_back_to_real_pilot_fusion`
  - `recommended_route_code = B`
- `outputs/labeled_pilot_analysis/repeatability_default/repeatability_summary.json`
  - `num_labeled_rows = 10`
  - `num_naturally_aligned_base_ids = 2`
  - `all_key_metrics_match = true`

## Idempotence and Recovery

- 019 输出写入独立 `output_dir`
- 可重复运行
- 若任一上游 artifact 缺失，应写出结构化 failure summary

## Outputs and Artifacts

- `outputs/labeled_pilot_analysis/*`
- `labeled_pilot_analysis_summary.json`
- `labeled_vs_real_pilot_alignment_summary.json`
- `labeled_fusion_blocker_summary.json`
- `labeled_vs_fusion_comparison.csv`
- `fusion_integration_recommendation.json`

## Remaining Risks

- 当前 integration recommendation 仍建立在 pilot-level controlled supervision 上，不是 benchmark supervision。
- 当前分析只证明“怎么接回 fusion”，不证明接回后就能得到研究级监督结果。
- 当前 mapping 仍依赖 base sample 粒度复制 reasoning / confidence 特征。
- 当前可对齐 base sample 仍然太少，因此 020 的 supervised fusion 只能被解释为 bootstrap 入口，而不是稳定评估设置。

## Next Suggested Plan

若 019 完成，下一步建议创建 `.plans/020-labeled-real-pilot-fusion-bootstrap.md`。
