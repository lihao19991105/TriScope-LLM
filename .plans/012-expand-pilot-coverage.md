# 012 Expand Pilot Coverage

## Purpose / Big Picture

TriScope-LLM 现在已经有一条真实 reasoning pilot，并且这条 pilot 已经完成 execution、feature extraction、acceptance、repeatability 和 compact pilot analysis。下一步最自然的任务不是扩大复杂度，而是以最小成本扩展真实 pilot 覆盖面，让仓库从“只有一条真实 pilot”推进到“至少两条模块级真实 pilot 已经开始落地”。

012 的目标是优先补当前 coverage 空白。默认路线是新增第二条真实 pilot；如果第二条 pilot 的成本或阻塞明显过高，再退而求其次扩现有 reasoning pilot 的数据规模。

## Scope

### In Scope

- 选择一条最小成本的 pilot coverage 扩展路线
- materialize 第二条 pilot 或更真实的 reasoning 子集
- pilot extension execution CLI
- 真实 execution artifact 与 feature artifact
- 结构化 extension registry / readiness summary

### Out of Scope

- 多条新 pilot 并行推进
- 大规模训练
- 大模型下载
- 完整真实 tri-probe + fusion 实验
- dashboard / plotting

## Repository Context

本计划将衔接：

- `configs/datasets.yaml`
- `configs/models.yaml`
- `configs/experiments.yaml`
- `configs/confidence.yaml`
- `scripts/run_confidence_probe.py`
- `scripts/extract_confidence_features.py`
- `outputs/pilot_materialization/*`
- `outputs/pilot_runs/*`
- `src/eval/`

## Deliverables

- 012 expand-pilot-coverage ExecPlan
- extension selection / readiness artifacts
- `scripts/materialize_pilot_extension.py`
- `scripts/run_pilot_extension.py`
- 第二条 pilot 的 raw + feature artifact
- `pilot_extension_selection.json`
- `pilot_extension_readiness_summary.json`
- `pilot_extension_run_summary.json`
- `pilot_extension_config_snapshot.json`
- `pilot_extension_execution.log`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 选择扩展路线、materialize 输入、extension readiness artifact
- [x] Milestone 2: 新的真实 execution path、raw artifact、feature artifact
- [x] Milestone 3: README、acceptance、必要时 repeatability、计划收口

## Surprises & Discoveries

- 第二条 pilot 最有希望的候选是 confidence，因为它可以直接复用 010 已经 materialize 的 CSQA-style local slice 和 distilgpt2 本地 cache，而不需要额外的多样例 prompt 组装。

## Decision Log

- 决策：012 优先选择第二条真实 confidence pilot，而不是先扩大 reasoning pilot。
  - 原因：confidence 可以最大化补 coverage 空白，同时复用现有的 local dataset slice、query contract 结构和本地小模型路径，新增资源与代码都最少。
  - 影响范围：`configs/confidence.yaml`、`configs/experiments.yaml`、pilot extension orchestration、012 artifact 结构。

- 决策：confidence extension 仍然使用同一个 CSQA-style local slice，而不是现在就引入新的 benchmark 下载。
  - 原因：当前阶段的目标是“新增第二条真实 execution path”，不是“扩大 benchmark 覆盖率”；复用现有 local slice 更符合最小成本与最高成功率原则。
  - 影响范围：extension selection、materialization outputs、README 的诚实边界。

- 决策：第二条 pilot 复用 `pilot_distilgpt2_hf` 和 `--smoke-mode` 作为默认执行深度。
  - 原因：当前的核心任务是先把 confidence 这条真实链路跑通并稳定复现，而不是在新模块首轮就拉高预算或切到更重模型。
  - 影响范围：`pilot_extension_run_summary.json`、repeatability 指标、README 用法说明。

- 决策：012/M3 为 confidence extension 增加独立 validator，并做同 seed rerun。
  - 原因：新增第二条 pilot 的价值不只是“跑过一次”，而是能被后续 analysis/reporting 安全复用。
  - 影响范围：`src/eval/pilot_extension_checks.py`、`scripts/validate_pilot_extension.py`、`outputs/pilot_extension_runs/repeatability_pilot_csqa_confidence_local/*`。

## Plan of Work

先把第二条 pilot 定位为 confidence，并围绕已经存在的 CSQA-style local slice 生成 confidence query contracts 与 extension registry。M1 完成后，M2 通过一个薄 orchestration CLI 直接接入现有 confidence probe 和 confidence feature extraction，让第二条真实 pilot 尽快落出 raw + feature artifact。若这条链路稳定，再在 M3 用 acceptance / README 收口。

## Concrete Steps

1. 创建 `.plans/012-expand-pilot-coverage.md`。
2. 在配置层新增 confidence pilot profile 与 experiment row。
3. 实现 `src/eval/pilot_extension.py`。
4. 实现 `scripts/materialize_pilot_extension.py`。
5. 实现 `scripts/run_pilot_extension.py`。
6. materialize confidence pilot inputs。
7. 运行第二条真实 confidence pilot。
8. 如成功，补 acceptance / README / 计划更新。

## Validation and Acceptance

- `materialize_pilot_extension.py --help` 可正常显示
- `run_pilot_extension.py --help` 可正常显示
- `validate_pilot_extension.py --help` 可正常显示
- M1 成功生成：
  - `pilot_extension_selection.json`
  - `pilot_extension_readiness_summary.json`
  - `pilot_extension_registry.json`
- M2 至少成功生成：
  - `pilot_extension_run_summary.json`
  - `pilot_extension_config_snapshot.json`
- `pilot_extension_execution.log`
  - confidence raw artifact
- 若 feature extraction 成功，还应生成 confidence feature artifact
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- extension materialization 和 extension execution 都写入独立 `output_dir`
- 可重复运行
- 若模型或输入不可用，应写出结构化 failure summary
- 若 materialization 已完成，则 execution 可以直接复用 extension query contracts

## Outputs and Artifacts

- `outputs/pilot_extension/*`
- `outputs/pilot_extension_runs/*`
- `pilot_extension_selection.json`
- `pilot_extension_readiness_summary.json`
- `pilot_extension_registry.json`
- `pilot_extension_run_summary.json`
- `pilot_extension_config_snapshot.json`

## Remaining Risks

- 第二条 pilot 仍然使用同一个 local CSQA-style slice，而不是新的 benchmark 来源。
- 当前虽然已经有两条真实 pilot，但仍然只覆盖 reasoning 和 confidence，illumination / fusion 的真实 coverage 仍待扩展。
- 当前 confidence pilot 仍然基于 distilgpt2 轻量模型和小预算，不适合被解读为研究结论级别的 confidence-collapse 结果。

## Validation Snapshot

- `outputs/pilot_extension/confidence_csqa_local/pilot_extension_readiness_summary.json`
  - selected extension route: `pilot_csqa_confidence_local`
  - ready to run: `true`
- `outputs/experiment_bootstrap/extension_refresh/experiment_bootstrap_summary.json`
  - experiments: `6`
  - ready local experiments: `3`
- `outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/pilot_extension_run_summary.json`
  - feature extraction completed: `true`
  - confidence profile: `smoke`
- `outputs/pilot_extension_runs/repeatability_pilot_csqa_confidence_local/artifact_acceptance.json`
  - acceptance status: `PASS`
- `outputs/pilot_extension_runs/repeatability_pilot_csqa_confidence_local/repeatability_summary.json`
  - repeatability status: `PASS`
  - all key metrics match: `true`

## Next Suggested Plan

若 012 完成，下一步建议创建 `.plans/013-cross-pilot-reporting.md`。
