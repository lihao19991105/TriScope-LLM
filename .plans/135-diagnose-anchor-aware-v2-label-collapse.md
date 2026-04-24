# 135 Diagnose Anchor-Aware V2 Label Collapse

## Purpose / Big Picture

132 的 precheck 显示 candidate 可执行，但 133 在 execution 的 labels 阶段发生单类塌缩。135 的目标是结构化解释“为什么 precheck 能过而 execution 会塌”，并形成可落地 recovery plan 与 micro-deepening 约束。

## Scope

### In Scope

- 对齐 precheck path 与 execution path 的关键差异。
- 审计 labels 生成路径与 parser 行为。
- 输出根因、恢复路线和下一步 micro-deepening 约束。

### Out of Scope

- 3B / 7B。
- blind budget expansion。
- dataset 轴扩张。
- fusion 同轴扩张。

## Repository Context

- `.plans/132-anchor-aware-baseline-preserving-deepening-followup.md`
- `.plans/133-anchor-aware-baseline-preserving-execution.md`
- `.plans/134-post-anchor-aware-baseline-preserving-analysis.md`
- `src/eval/model_axis_1p5b_route_c_anchor_followup_v2.py`
- `src/eval/model_axis_1p5b_route_c_anchor_execution_v2.py`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`
- `src/fusion/benchmark_truth_leaning_label.py`

## Deliverables

- `.plans/135-diagnose-anchor-aware-v2-label-collapse.md`
- `src/eval/model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis.py`
- `scripts/build_model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis.py`
- `outputs/model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis/default/route_c_anchor_v2_precheck_vs_execution_diff.json`
- `outputs/model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis/default/route_c_anchor_v2_label_path_audit.json`
- `outputs/model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis/default/route_c_anchor_v2_failure_hypotheses.json`
- `outputs/model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis/default/route_c_anchor_v2_collapse_root_cause.json`
- `outputs/model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis/default/route_c_anchor_v2_recovery_plan.json`
- `outputs/model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis/default/route_c_anchor_v2_micro_deepening_constraints.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 对齐 precheck path 与 execution path
- [x] Milestone 2: 形成根因与修复路线
- [x] Milestone 3: acceptance / README / 收口

## Decision Log

- 决策：先做路径审计再做新 candidate。
  - 原因：当前主要矛盾是 labels collapse 机理不清，直接继续新 candidate 会重复失败模式。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis.py --help` 可正常显示。
- 必须显式回答：
  - precheck 与 execution 差异点。
  - labels collapse 主因。
  - 下一版 micro-deepening 的可执行约束。

## Remaining Risks

- 若 collapse 主因是当前运行时普遍响应退化，而非 candidate 特异，单纯换候选可能无效。

## Outcome Snapshot

- 135 已完成并输出差异审计、根因与恢复计划。
- 当前关键结果：
  - `selection_consistent = true`
  - `precheck_label_set = [0,1]`
  - `execution_label_set = [1]`
  - `execution_labeled_response = 6/6 punctuation-only`
  - `robust_prefix parsed_option_count = 0`
  - `control_recheck`（原 anchor baseline）同样在 labels 阶段塌缩
- 根因结论：
  - 主因是 execution labels path 接收到不可解析响应，导致全体 label=1。
  - 次因是 precheck 与 execution 的 label path 不一致（历史标签 vs 实时重标注）。

