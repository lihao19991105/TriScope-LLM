# 145 Route-C Time-Separated Regression Root Cause Analysis

## Background

141 通过 parser / output-normalization 的最小修复，首次把 route_c execution 从 BLOCKED 拉回 PASS。142 在完全冻结设置下完成 3 次稳定性复检，结论为 `Provisionally stable`。143 继续在同一 frozen path 上追加 5 次 rerun，把累计证据推进到 8 次无回退，结论升级为 `Stable enough`。

144 没有改动语义、预算、模型轴或 parser/gate 设置，只在时间分离条件下对同一 frozen baseline 做 3 次 replay，结果却 3/3 退回旧阻塞态：

- `gate_pass_rate = 0.0`
- `dual_class_restoration_rate = 0.0`
- `consistency_restored_rate = 0.0`
- `parsed_option_count = 0`
- `missing_option_ratio = 1.0`
- `punct_only_ratio = 1.0`

因此 145 的目标不是继续修、不再扩张，而是先解释：为什么 143 稳、144 全退。

## Why 144 Is A Hard Regression Signal

- 144 不是轻微波动，而是 `3/3 regression to BLOCKED` 与 `3/3 regression to single-class`。
- 回退模式与 140 前的旧阻塞态同构：`parsed_option_count=0`、`missing_option_ratio=1.0`、`punct_only_ratio=1.0`。
- 143 的稳定证据是完全一致的 `PASS / dual-class / parsed=5`，而 144 replay-only 结果是完全一致的 `BLOCKED / single-class / parsed=0`。
- 因此 144 不是“均值略变差”，而是 execution-level path 出现了明确断裂，必须单独诊断。

## Frozen Scope For 143 Vs 144 Comparison

本计划只比较以下两条证据链，不覆盖其他主线：

- 143:
  - `outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_recheck/default/*`
  - `outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_analysis/default/*`
- 144:
  - `outputs/model_axis_1p5b_route_c_stable_baseline_time_separated_replay/default/*`
  - `outputs/model_axis_1p5b_route_c_stable_baseline_time_separated_replay_analysis/default/*`

冻结比较对象：

- frozen settings
- labeled illumination input contract
- parser / normalization 路径
- runtime config snapshot
- labeled illumination raw outputs
- label-health rows / gate outputs
- 代表性 case-level trace

## Candidate Root-Cause Hypotheses

1. `execution_context_drift`
   - 运行入口名义一致，但实际调用链、参数注入、路径解析或运行上下文发生漂移。
2. `parser_or_normalization_not_truly_frozen`
   - 名义 parse/normalization 设置一致，但 runtime 实际走了不同分支。
3. `model_output_drift`
   - 黑盒模型在跨时间 replay 中输出格式整体漂移，退化为 `punct_only / empty / malformed`。
4. `artifact_interpretation_drift`
   - 144 读取的不是与 143 同一层级/同一 contract/同一中间物，导致比较对象错位。
5. `environment_cache_or_state_drift`
   - 缓存、旧文件、隐式状态或恢复逻辑导致跨时间运行上下文偏移。

## Goal

在不做任何修复或扩张的前提下，完成 143 vs 144 的 execution-level diff、evidence tracing，并产出一个单一 root-cause verdict 与唯一下一步建议。

## Non-goals

- 不修 parser / normalization / gate / benchmark truth semantics。
- 不继续做更大规模 replay。
- 不扩模型轴、budget、prompt family、dataset 轴。
- 不重做 route_b、fusion 或其他无关主线。

## Repository Context

- `.plans/141-route-c-parser-output-normalization-minimal-repair.md`
- `.plans/142-route-c-output-normalization-stability-recheck.md`
- `.plans/143-route-c-output-normalization-stability-extension-recheck.md`
- `.plans/144-route-c-stable-baseline-time-separated-replay.md`
- `src/fusion/benchmark_truth_leaning_label.py`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`
- `src/eval/route_c_label_output_normalization*.py`
- `src/eval/route_c_stable_baseline_time_separated_replay.py`
- `src/eval/post_route_c_stable_baseline_time_separated_replay_analysis.py`

## Deliverables

- `.plans/145-route-c-time-separated-regression-root-cause-analysis.md`
- `src/eval/route_c_time_separated_regression_root_cause_analysis.py`
- `scripts/build_route_c_time_separated_regression_root_cause_analysis.py`
- `src/eval/post_route_c_time_separated_regression_root_cause_analysis.py`
- `scripts/build_post_route_c_time_separated_regression_root_cause_analysis.py`
- `outputs/model_axis_1p5b_route_c_time_separated_regression_root_cause/default/route_c_time_separated_regression_root_cause_scope.json`
- `outputs/model_axis_1p5b_route_c_time_separated_regression_root_cause/default/route_c_time_separated_regression_root_cause_hypotheses.json`
- `outputs/model_axis_1p5b_route_c_time_separated_regression_root_cause/default/route_c_time_separated_regression_root_cause_diff_summary.json`
- `outputs/model_axis_1p5b_route_c_time_separated_regression_root_cause/default/route_c_time_separated_regression_root_cause_details.jsonl`
- `outputs/model_axis_1p5b_route_c_time_separated_regression_root_cause/default/route_c_time_separated_regression_root_cause_report.md`
- `outputs/model_axis_1p5b_route_c_time_separated_regression_root_cause_analysis/default/route_c_time_separated_regression_root_cause_analysis_summary.json`
- `outputs/model_axis_1p5b_route_c_time_separated_regression_root_cause_analysis/default/route_c_time_separated_regression_root_cause_verdict.json`
- `outputs/model_axis_1p5b_route_c_time_separated_regression_root_cause_analysis/default/route_c_time_separated_regression_root_cause_next_step_recommendation.json`

## Evidence Collection Plan

先做 artifact-level diff，再做 case-level tracing：

1. 比较 143/144 frozen settings 是否逐项一致。
2. 比较 input contract：
   - input_root
   - query_file
   - sample_id / contract 集合
   - parse / normalization 开关
3. 比较 runtime config snapshot：
   - model path
   - prompt template
   - generation parameters
   - runtime_device / dtype
4. 比较 output pattern：
   - raw labeled illumination responses
   - parse_compare
   - label health summary
   - gate result
5. 做最少量 case-level tracing：
   - 每个 contract 一行，直接对比 143 vs 144 raw_response / normalized_response / parse_failure_category
6. 补一个侧向证据：
   - 看普通 illumination / confidence / reasoning 是否也出现同步退化

## Minimal Diagnostic Replay Plan

默认不新增 replay。

只有在现有 artifact 不能区分“execution drift”与“model-output drift”时，才允许：

- 用 143 frozen settings 在 145 当前时刻做 1 次单步 replay；或
- 对同一 sample 做路径级 trace，验证 parser / normalization 是否走了同一路径。

本计划完成前，不允许超过 1~2 个最小诊断 replay。

## Root-Cause Decision Criteria

最终 verdict 只能三选一：

1. `Execution drift confirmed`
   - 当 frozen settings / input contract / parser path 存在足以解释回退的执行层漂移证据。
2. `Model-output drift confirmed`
   - 当 parser 前的 raw model outputs 已显著跨时间退化，且 frozen settings / input contract 基本一致。
3. `Root cause not yet isolated`
   - 当证据仍无法把主因单独定位到 execution drift 或 model-output drift。

## Risks

- 143/144 artifact 中未显式记录的环境变量、缓存状态或 GPU 映射仍可能是隐性因素。
- 144 analysis artifact 的 compare/report 位于 analysis 目录而非 replay 主目录，需在 scope 中写清楚，避免误判为结果缺失。
- 如果现有 artifact 已足够支撑结论，继续 replay 反而会扩大问题边界。

## Surprises & Discoveries

- `143` 与 `144` 的 `frozen_settings` 逐项完全一致，显式参数层面没有发现可直接解释回退的 execution drift。
- `143` 与 `144` 使用同一 `query_file`、同一 contract 集合、同一 model local path、同一 parse/normalization 配置。
- `144` 的退化在 parser 之前已经出现：6/6 labeled raw responses 均塌缩为 `!!!!!!!!!!!!!!!!`。
- 普通 illumination、confidence、reasoning 也同步退化，说明断裂不是 parser/gate 单点解释偏差。

## Decision Log

- 决策：145 优先做 artifact diff 与 evidence tracing，不默认新增 replay。
  - 原因：当前最关键的任务是解释 143/144 的断裂，而不是继续累计 replay 次数。
- 决策：145 不执行额外诊断 replay。
  - 原因：现有 143/144 artifact 已经足够把回退定位到 parser 前的 raw model output 层，继续 replay 只会扩大问题边界。

## Milestones

- [x] M1: 143/144 diff scope frozen and hypotheses defined
- [x] M2: evidence collection and diagnostic comparison completed
- [x] M3: single root-cause verdict and single recommendation completed

## Progress

- [x] 创建 145 ExecPlan
- [x] 实现 root-cause main builder
- [x] 实现 root-cause post-analysis builder
- [x] 生成 scope / hypotheses / diff / details / report
- [x] 生成单一 verdict / recommendation
- [ ] 同步 README 与恢复入口

## Exit Criteria

- 145 计划文件完整且可恢复。
- 143/144 frozen comparison scope 已明确。
- scope / hypotheses / diff_summary / details / report / verdict / recommendation 七类 artifact 齐全。
- 最终只输出一个 root-cause verdict。
- 最终只输出一条下一步建议。
- 未出现未证先修、未证先扩张。
