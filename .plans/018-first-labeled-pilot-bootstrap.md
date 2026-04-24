# 018 First Labeled Pilot Bootstrap

## Purpose / Big Picture

017 会确认当前 real-pilot 系统的主阻塞是 `missing_ground_truth_labels`。018 的目标是在不引入大模型、大数据和人工标注的前提下，以最小成本为项目引入第一条带标签的 pilot path，使 supervised path 第一次真正存在。

这里的“带标签”不是声称得到论文级 benchmark 标签，而是明确、可审计、可追溯的 pilot-level controlled supervision。目标是让 supervised preprocessing / baseline 首次具备可执行入口，而不是伪装成完整研究结论。

## Scope

### In Scope

- 选择第一条 labeled pilot 路线
- 明确标签定义 / 来源 / 局限
- materialize labeled pilot inputs
- labeled pilot execution / feature extraction
- labeled pilot dataset
- 至少一版 supervised baseline artifact
- acceptance / repeatability / README

### Out of Scope

- 人工标注流程
- 外部大 benchmark 下载
- 更重模型
- 最终监督实验

## Repository Context

本计划将衔接：

- `outputs/pilot_materialization/pilot_csqa_reasoning_local/*`
- `outputs/pilot_illumination_runs/*`
- `scripts/run_illumination_probe.py`
- `scripts/extract_illumination_features.py`
- `src/eval/`
- `src/fusion/`

## Deliverables

- `.plans/018-first-labeled-pilot-bootstrap.md`
- `src/eval/labeled_pilot_bootstrap.py`
- `scripts/materialize_labeled_pilot.py`
- `scripts/run_labeled_pilot_bootstrap.py`
- `src/eval/labeled_pilot_checks.py`
- `scripts/validate_labeled_pilot.py`
- `labeled_pilot_selection.json`
- `labeled_pilot_label_definition.json`
- `labeled_pilot_readiness_summary.json`
- `labeled_pilot_dataset.jsonl`
- `labeled_pilot_summary.json`
- `labeled_supervised_readiness_summary.json`
- 若可行：`labeled_logistic_predictions.jsonl`
- 若可行：`labeled_logistic_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 选定 labeled pilot 路线 / 标签定义 / materialization
- [x] Milestone 2: supervised path 首次可执行
- [x] Milestone 3: acceptance / repeatability / README / 计划收口

## Surprises & Discoveries

- 现有 illumination query-file contract 非常适合承载“control vs targeted”这类可审计的 pilot supervision。
- 直接在当前 real-pilot fusion dataset 上补监督标签并不自然，但在 illumination pilot 上先做 controlled labeled bootstrap 成本最低、可解释性最强。
- 现有 `smoke_mode` 会把 illumination budget 强行收缩到 2，不适合作为 labeled pair bootstrap 的执行模式；为此新增了独立的 `labeled_bootstrap` illumination profile。
- 通过 control / targeted 成对 materialization，当前 local 5 条 CSQA-style slice 可以稳定生成 10 条带标签样本，且两类标签天然平衡。

## Decision Log

- 决策：018 选择 illumination 作为 first-labeled-pilot-bootstrap 的承载模块。
  - 原因：illumination contract 已经显式包含 target_text、trigger_type 和 contract metadata，最容易构造 control / targeted 的可审计标签。
  - 影响范围：`materialize_labeled_pilot.py`、`run_labeled_pilot_bootstrap.py`、labeled dataset schema。

- 决策：标签定义采用 `controlled_targeted_icl_label`。
  - 原因：这个标签直接来源于 materialized contract 变体，而不是来源于模型输出或不透明弱标签器；它能明确区分 control ICL 与 targeted ICL 两类监督样本。
  - 影响范围：`labeled_pilot_label_definition.json`、`labeled_pilot_dataset.jsonl`、`labeled_logistic_summary.json`。

- 决策：018 先让 illumination 级 supervised path 成立，而不强行把标签立即对齐回 015/016 的 real-pilot fusion dataset。
  - 原因：当前三模态 real-pilot dataset 只有 2 条 full-intersection row，且没有自然的成对 control/targeted supervision；先建立 module-level labeled path 更稳妥。
  - 影响范围：`labeled_supervised_readiness_summary.json` 中 `fusion_supervised_ready=false` 的语义，以及后续 019 的计划边界。

## Plan of Work

先在 M1 复用当前 local CSQA-style slice，为每个 base sample materialize 一对 illumination contract：一个 control 版本、一个 targeted 版本，并把二者的区别显式记录为 `controlled_targeted_icl_label`。随后在 M2 运行这条 labeled illumination pilot，抽取 illumination features，并把它们转成可用于 supervised baseline 的 labeled dataset。若链路稳定，则在 M3 增加 validator、repeatability 和 README。

## Concrete Steps

1. 创建 `.plans/018-first-labeled-pilot-bootstrap.md`。
2. 实现 `src/eval/labeled_pilot_bootstrap.py`。
3. 实现 `scripts/materialize_labeled_pilot.py`。
4. 实现 `scripts/run_labeled_pilot_bootstrap.py`。
5. materialize control / targeted labeled illumination contracts。
6. 运行 labeled illumination pilot 与 feature extraction。
7. 构建 labeled pilot dataset。
8. 运行最小 logistic baseline。
9. 增加 validator、repeatability、README 与计划更新。

## Validation and Acceptance

- `materialize_labeled_pilot.py --help` 可正常显示
- `run_labeled_pilot_bootstrap.py --help` 可正常显示
- `validate_labeled_pilot.py --help` 可正常显示
- M1 成功生成：
  - `labeled_pilot_selection.json`
  - `labeled_pilot_label_definition.json`
  - `labeled_pilot_readiness_summary.json`
- M2 至少成功生成：
  - `labeled_pilot_dataset.jsonl`
  - `labeled_pilot_summary.json`
  - `labeled_supervised_readiness_summary.json`
- 若 logistic 成功，还应生成：
  - `labeled_logistic_predictions.jsonl`
  - `labeled_logistic_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- labeled pilot materialization 与 execution 写入独立 `output_dir`
- 可重复运行
- 若模型或输入不可用，应写出结构化 failure summary

## Outputs and Artifacts

- `outputs/labeled_pilot_bootstrap/*`
- `outputs/labeled_pilot_runs/*`
- `labeled_pilot_selection.json`
- `labeled_pilot_label_definition.json`
- `labeled_pilot_readiness_summary.json`
- `labeled_pilot_dataset.jsonl`
- `labeled_pilot_summary.json`
- `labeled_supervised_readiness_summary.json`

## Remaining Risks

- 当前 labeled pilot 仍然是 pilot-level controlled supervision，不是 benchmark 标签。
- 当前 labeled supervision 优先服务于“让 supervised path 首次存在”，而不是证明最终 detector 的真实泛化。
- 当前模型和数据切片仍然非常小，logistic 即使可跑，也不应被当成研究结论。
- 当前 labeled logistic 是 self-fit pilot bootstrap，只能证明 supervised chain 成立，不能替代真正的 held-out supervised evaluation。
- 当前 labeled path 还没有自然并入三模态 real-pilot fusion；后续需要单独设计 labeled fusion integration。

## Next Suggested Plan

若 018 完成，下一步建议创建 `.plans/019-labeled-pilot-analysis-and-fusion-integration.md`。
