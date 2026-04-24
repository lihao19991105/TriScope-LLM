# 022 Controlled Supervision Coverage Expansion

## Purpose / Big Picture

如果 021 推荐继续扩大当前 controlled supervision 的覆盖面，那么 022 的目标就是在不引入新模型、新数据和新标签体系的前提下，把现有 supervised fusion 从 `2` 个 base sample / `4` 条 labeled rows，扩到完整 local slice 的可执行规模。

## Scope

### In Scope

- controlled supervision expansion plan / readiness
- expanded real-pilot execution on the existing 5-row local slice
- expanded real-pilot fusion dataset
- expanded labeled fusion dataset
- 最小 supervised logistic rerun
- acceptance / repeatability / README

### Out of Scope

- 更自然的新标签体系
- benchmark ground truth
- 更大模型 / 更大数据
- 研究级监督评估

## Repository Context

本计划将衔接：

- `outputs/pilot_materialization/*`
- `outputs/pilot_extension/*`
- `outputs/pilot_illumination/*`
- `outputs/labeled_pilot_bootstrap/*`
- `outputs/labeled_pilot_runs/*`
- `outputs/real_pilot_fusion_readiness/*`
- `outputs/labeled_real_pilot_fusion/*`

## Deliverables

- `.plans/022-controlled-supervision-coverage-expansion.md`
- `src/eval/controlled_supervision_expansion.py`
- `scripts/build_controlled_supervision_expansion.py`
- `src/eval/controlled_supervision_expansion_checks.py`
- `scripts/validate_controlled_supervision_expansion.py`
- `controlled_supervision_expansion_plan.json`
- `expanded_labeled_readiness_summary.json`
- `expanded_labeled_fusion_dataset.jsonl`
- `expanded_labeled_summary.json`
- `expanded_logistic_predictions.jsonl`
- `expanded_logistic_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize expansion plan / readiness
- [x] Milestone 2: expanded execution / labeled fusion / supervised bootstrap
- [x] Milestone 3: acceptance / repeatability / README / 计划收口

## Surprises & Discoveries

- 路线 A 的关键前提已经在仓库里存在：三条 real pilot 的 query contracts 都是 `5` 行，labeled illumination contracts 是 `10` 行。
- 这意味着扩展 supervised fusion 的最小动作不是重新设计标签，而是把三条 real pilot 从 `smoke_mode` 的 `2` 条执行扩到完整 local slice。
- 扩展后 full-intersection 成功从 `2` 行增长到 `5` 行，labeled real-pilot fusion 也从 `4` 行增长到 `10` 行。
- repeatability 已验证：expanded logistic 的 `mean_prediction_score` 在 reference 与 rerun 间完全一致，都是 `0.5007625981729338`。

## Decision Log

- 决策：022 复用现有 query contracts 和现有 controlled label，不引入任何新标签体系。
  - 原因：021 已证明真正瓶颈是 coverage，而不是标签定义。
  - 影响范围：`controlled_supervision_expansion_plan.json` 与 `expanded_labeled_summary.json`。

- 决策：022 直接复用 020 的 labeled fusion builder 与 logistic runner，而不是重新写一套监督 baseline。
  - 原因：当前目标是扩大已存在的 supervised path，而不是发明新 pipeline。
  - 影响范围：`expanded_labeled_fusion_dataset.jsonl` 和 `expanded_logistic_summary.json` 的 schema 与 020 保持一致。

## Plan of Work

先确认三条 real pilot 的 query contracts 实际都已覆盖完整 5-row local slice，只是过去被 smoke budget 截断。然后复用这些既有 contracts，在不引入新资源的前提下跑一版 expanded reasoning / confidence / illumination，再重建 real-pilot fusion 和 labeled real-pilot fusion，最后让 supervised logistic 在更大的 covered set 上再跑一次。

## Concrete Steps

1. 创建 `.plans/022-controlled-supervision-coverage-expansion.md`。
2. 实现 `src/eval/controlled_supervision_expansion.py`。
3. 实现 `scripts/build_controlled_supervision_expansion.py`。
4. 生成 expansion plan / readiness artifacts。
5. 运行 expanded pilot execution / fusion / labeled fusion / logistic。
6. 实现 validator 与 repeatability。
7. 更新 README 与计划状态。

## Validation and Acceptance

- `build_controlled_supervision_expansion.py --help` 可正常显示
- `validate_controlled_supervision_expansion.py --help` 可正常显示
- M1 成功生成：
  - `controlled_supervision_expansion_plan.json`
  - `expanded_labeled_readiness_summary.json`
- M2 至少成功生成：
  - `expanded_labeled_fusion_dataset.jsonl`
  - `expanded_labeled_summary.json`
  - `expanded_logistic_predictions.jsonl`
  - `expanded_logistic_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

### Validation Snapshot

- `outputs/controlled_supervision_expansion/default/controlled_supervision_expansion_run_summary.json`
  - `target_budget = 5`
  - `expanded_real_pilot_alignment.num_rows = 5`
  - `expanded_real_pilot_alignment.num_rows_with_all_modalities = 5`
- `outputs/controlled_supervision_expansion/default/expanded_labeled_summary.json`
  - `num_rows = 10`
  - `num_base_samples = 5`
  - `class_balance = {label_0: 5, label_1: 5}`
- `outputs/controlled_supervision_expansion/default/expanded_logistic_summary.json`
  - `summary_status = PASS`
  - `num_predictions = 10`
  - `num_positive_predictions = 5`
- `outputs/controlled_supervision_expansion/repeatability_default/repeatability_summary.json`
  - `all_key_metrics_match = true`

## Idempotence and Recovery

- 输出写入独立 `output_dir`
- 可重复运行
- 若任一上游 artifact 缺失，应输出结构化 failure summary

## Outputs and Artifacts

- `outputs/controlled_supervision_expansion/*`

## Remaining Risks

- 扩展后仍然只是 pilot-level controlled supervision。
- reasoning / confidence 在 labeled variants 上仍按 base sample 复用。
- 当前扩展虽已把覆盖面从 `4` 行推到 `10` 行，但仍然只是 local slice + 轻量模型下的小规模 supervised path。

## Next Suggested Plan

若 022 完成，下一步建议分析是否继续扩大 controlled coverage，还是开始引入更自然标签来源。
