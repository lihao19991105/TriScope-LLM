# 106 Model-Axis-1.5B Dry Run

## Purpose / Big Picture

105 已把 1.5B 模型轴 bootstrap 成型，但当前仍是 `not-ready-local / not-ready-run`。106 的目标是在不默认下载大模型的前提下，把 `model_axis_1p5b_single_model_probe_v1` 推进成一个诚实、结构化、可恢复的 1.5B dry-run。

## Scope

### In Scope

- 1.5B blocker diagnosis 结果落盘并接入 dry-run
- 1.5B model-axis dry-run plan / contract / readiness
- partial-but-structured dry-run summary / registry / cell status / module status
- acceptance / repeatability / README

### Out of Scope

- 直接下载 1.5B 权重
- 3B / 7B 模型扩张
- 1.5B real execution

## Repository Context

- `.plans/105-model-axis-1p5b-bootstrap.md`
- `outputs/model_axis_1p5b_bootstrap/default/*`
- `outputs/next_axis_after_v10_matrix_dry_run/default/materialized_next_axis_after_v10_matrix_inputs/`
- `configs/models.yaml`
- `src/probes/illumination_probe.py`

## Deliverables

- `.plans/106-model-axis-1p5b-dry-run.md`
- `outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_blocker_diagnosis.json`
- `outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_recovery_options.json`
- `outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_minimal_execution_candidate.json`
- `src/eval/model_axis_1p5b_dry_run.py`
- `src/eval/model_axis_1p5b_dry_run_checks.py`
- `scripts/build_model_axis_1p5b_dry_run.py`
- `scripts/validate_model_axis_1p5b_dry_run.py`
- `outputs/model_axis_1p5b_dry_run/default/model_axis_1p5b_dry_run_summary.json`
- `outputs/model_axis_1p5b_dry_run/default/model_axis_1p5b_cell_status.json`
- `outputs/model_axis_1p5b_dry_run/repeatability_default/artifact_acceptance.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define 1.5B dry-run contract
- [x] Milestone 2: run 1.5B dry-run
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：106 不伪装成 full PASS，而是把当前最诚实的状态定义为 `PARTIAL` dry-run。
  - 原因：当前 1.5B 路线的主要问题是没有 ready-local snapshot，但 contract、dataset、query inputs 与 route / fusion 映射已经足够做结构化 dry-run。
- 决策：106 选择 `route_b` 作为最小 executable candidate。
  - 原因：它是当前最小、最直接、最少依赖 fusion 叠加的真实 route cell。

## Validation and Acceptance

- `build_model_axis_1p5b_dry_run.py --help` 可正常显示
- `validate_model_axis_1p5b_dry_run.py --help` 可正常显示
- `outputs/model_axis_1p5b_dry_run/default/model_axis_1p5b_dry_run_summary.json` 已生成
- `outputs/model_axis_1p5b_dry_run/default/model_axis_1p5b_cell_status.json` 已生成
- `outputs/model_axis_1p5b_dry_run/repeatability_default/artifact_acceptance.json` 为 `PASS`

## Outcome Summary

- 1.5B blocker diagnosis 已完成，并明确主阻塞是 `no_ready_local_1p5b_snapshot`。
- 1.5B dry-run 已第一次存在，当前状态是 `PARTIAL` 而不是伪装成 full runtime success。
- `route_b` 已被明确为最小 execution candidate，但当前仍受 not-ready-local 阻塞。

## Next Suggested Plan

若未来补齐本地 1.5B 权重或允许受控下载，下一步才应进入 107，对 `route_b` 做 1.5B minimal execution。
