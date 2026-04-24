# 058 Real Experiment First Dry-Run

## Purpose / Big Picture

057 已经把 `small_real_labeled_csqa_triscope_cutover_v1` 做成了一个可执行的 cutover object。058 的任务是把它从“只存在于 contract 和 readiness 层”推进成“第一轮真正会动起来的 real-experiment-style dry-run”，明确 route B / route C / fusion 如何映射到这份 cutover contract，并留下结构化 dry-run artifact。

## Scope

### In Scope

- dry-run contract definition
- route B / route C / fusion mapping
- first real-experiment dry-run execution
- acceptance / repeatability / README / 收口

### Out of Scope

- 第一轮 full execution
- 更大模型 / 更大数据规模
- benchmark ground truth 接入

## Repository Context

本计划主要衔接：

- `outputs/real_experiment_cutover_bootstrap/default/*`
- `outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs/*`
- `src/probes/*.py`
- `src/eval/rerun_route_b_on_labeled_split_v6.py`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`

## Deliverables

- `.plans/058-real-experiment-first-dry-run.md`
- `src/eval/real_experiment_first_dry_run.py`
- `scripts/build_real_experiment_first_dry_run.py`
- `src/eval/real_experiment_first_dry_run_checks.py`
- `scripts/validate_real_experiment_first_dry_run.py`
- `first_real_experiment_dry_run_plan.json`
- `first_real_experiment_execution_contract.json`
- `first_real_experiment_readiness_summary.json`
- `first_real_experiment_dry_run_summary.json`
- `first_real_experiment_dry_run_registry.json`
- `first_real_experiment_module_status.json`
- `first_real_experiment_dry_run_preview.jsonl`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define dry-run contract and readiness
- [x] Milestone 2: run first dry-run and emit structured artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 当前最稳的 dry-run 路径不是重新发明 execution substrate，而是直接复用 053 生成的 v6 query contracts，并把它们映射回 057 cutover object。
- 058 的关键产出不是模型分数，而是要把“谁读什么输入、谁输出什么 artifact”的真实执行关系第一次写死并实际走一遍。
- 实际 dry-run 结果比预期更顺：reasoning / confidence / illumination / labeled_illumination 全部 PASS，route B / route C / fusion 的 execution mapping 也全部 PASS，没有出现模块级阻塞。

## Decision Log

- 决策：058 采用 `real_experiment_cutover_bootstrap/default` 的 dataset/model contract，加上 `post_v5_next_step_bootstrap/default/materialized_post_v5_inputs/` 里的稳定 v6 query contracts 作为 dry-run substrate。
  - 原因：这样既保留真实实验切换语义，又不需要重新生成一套未验证的 query contract。
  - 影响范围：execution contract、module mapping、preview artifact。

## Plan of Work

先读取 057 的 candidate selection、input contract、bootstrap summary 与 materialized inputs，再把 v6 reasoning / confidence / illumination / labeled illumination contracts 接到同一个 cutover object 上。然后用 dry-run 模式实际运行 probes，输出 per-module 状态、registry、preview 与 summary。最后补 validator、repeatability 与 README。

## Concrete Steps

1. 实现 `src/eval/real_experiment_first_dry_run.py` 与配套 CLI / validator。
2. 运行 build CLI 生成 dry-run artifact。
3. 运行 repeat run 与 validator。
4. 更新 README 与 plan 进度。

## Validation and Acceptance

- `build_real_experiment_first_dry_run.py --help` 可正常显示
- `validate_real_experiment_first_dry_run.py --help` 可正常显示
- 至少生成：
  - `first_real_experiment_dry_run_plan.json`
  - `first_real_experiment_execution_contract.json`
  - `first_real_experiment_readiness_summary.json`
  - `first_real_experiment_dry_run_summary.json`
  - `first_real_experiment_dry_run_registry.json`
  - `first_real_experiment_module_status.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

058 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 dry-run 中断，可直接重跑 build CLI。

## Remaining Risks

- dry-run 证明的是 execution mapping 与 module viability，不是 full execution 结论。
- route B / route C / fusion 在本阶段仍然只处于“ready to execute”或“dry-run simulated”层级。

## Outcome Summary

- `outputs/real_experiment_first_dry_run/default/first_real_experiment_dry_run_summary.json` 显示 `summary_status = PASS`、`dataset_rows = 70`。
- `outputs/real_experiment_first_dry_run/default/first_real_experiment_module_status.json` 显示 reasoning / confidence / illumination / labeled_illumination / route_b / route_c / fusion 全部 PASS。
- `outputs/real_experiment_first_dry_run/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 均为 PASS。

## Next Suggested Plan

若 058 完成，下一步建议创建 `.plans/059-first-real-experiment-execution.md`，基于 dry-run 的结果选择最小但真实的 first executable path，并真正执行一次。
