# 014 Third Pilot Illumination

## Purpose / Big Picture

经过 010 和 012，TriScope-LLM 已经拥有 reasoning 与 confidence 两条真实 pilot。当前最明显的真实 coverage 空白在 illumination。014 的目标是优先把 illumination 从“只有 smoke artifact”推进到“第三条真实 pilot”，从而让真实 pilot coverage 从 2/3 扩到 3/3。

014 的目标不是立即得到研究级 illumination 结果，而是用最小成本、最短路径把 illumination 的真实 execution path 和 artifact 先落地，并诚实保留 pilot 限制。

## Scope

### In Scope

- 选择最小成本的 illumination pilot 路线
- materialize illumination query contracts
- illumination readiness / registry artifact
- 第三条真实 illumination pilot execution
- 若成本可控，接 illumination feature extraction
- README / acceptance / repeatability / 计划收口

### Out of Scope

- 新 benchmark 下载
- 更重模型切换
- 复杂 illumination 实验矩阵
- 跨模块真实 fusion execution
- 研究级 illumination prompt search

## Repository Context

本计划将衔接：

- `configs/datasets.yaml`
- `configs/models.yaml`
- `configs/experiments.yaml`
- `configs/illumination.yaml`
- `outputs/pilot_materialization/*`
- `outputs/pilot_runs/*`
- `outputs/pilot_extension_runs/*`
- `scripts/run_illumination_probe.py`
- `scripts/extract_illumination_features.py`
- `src/probes/illumination_probe.py`
- `src/eval/`

## Deliverables

- `.plans/014-third-pilot-illumination.md`
- illumination pilot selection / readiness artifacts
- `scripts/materialize_pilot_illumination.py`
- `scripts/run_pilot_illumination.py`
- 如有必要，illumination pilot validator
- `pilot_illumination_selection.json`
- `pilot_illumination_readiness_summary.json`
- `pilot_illumination_run_summary.json`
- `pilot_illumination_config_snapshot.json`
- `pilot_illumination_execution.log`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 选择 illumination pilot 路线、materialize 输入、readiness artifact
- [x] Milestone 2: 真实 illumination pilot raw artifact、run summary、尽量进入 feature extraction
- [x] Milestone 3: acceptance / repeatability / README / 计划收口

## Surprises & Discoveries

- 当前最实际的 illumination pilot 路线不是重新引入新的数据集或模型，而是复用已经存在的 CSQA-style local slice 与本地 distilgpt2 cache，通过 targeted-ICL 风格 contract 先把真实 execution path 落下来。
- illumination 的 query-file contract 已经足够灵活，因此可以用最小新增代码直接 materialize 第三条 pilot，而不必回头重写 004 稳定模块。
- 在实际执行中，illumination pilot 需要运行在仓库已经补齐依赖的项目环境里；直接使用系统 `python3` 会在本地 HuggingFace cache 加载阶段失败，而 `.venv/bin/python` 可稳定跑通。

## Decision Log

- 决策：014 优先选择 `csqa_reasoning_pilot_local + pilot_distilgpt2_hf` 的 illumination 路线。
  - 原因：这条路线复用已有真实资源最多、无需新下载、成功率最高，并且能最快填补 illumination 的真实 coverage 空白。
  - 影响范围：`configs/illumination.yaml`、`configs/experiments.yaml`、illumination pilot materialization / execution 脚本。

- 决策：illumination pilot 使用 targeted-ICL-style query contracts，而不是现在就引入新的 backdoor dataset。
  - 原因：当前阶段目标是把 illumination 的真实 execution path 跑通，而不是在第三条 pilot 首轮就扩大到更重、更难控的数据构造。
  - 影响范围：`pilot_illumination_selection.json`、materialized query contracts、README 的解释边界。

- 决策：014/M3 为 illumination pilot 增加独立 acceptance / repeatability。
  - 原因：第三条 pilot 一旦落地，就应当像 reasoning / confidence 一样能够稳定被 cross-pilot reporting 复用。
  - 影响范围：illumination pilot validator、repeatability artifacts、计划收口。

## Plan of Work

先在 M1 复用已有 local CSQA slice 构造最小 targeted-ICL-style illumination query contracts，并把 experiment row 刷新到 ready_local。M2 再直接复用现有 illumination probe 与 illumination feature extraction 链路，尽量跑出真实 raw + feature artifact。若这条链路稳定，则在 M3 增加 validator、repeatability 和 README 用法说明。

## Concrete Steps

1. 创建 `.plans/014-third-pilot-illumination.md`。
2. 在配置层新增 illumination pilot profile 与 experiment row。
3. 实现 `src/eval/pilot_illumination.py`。
4. 实现 `scripts/materialize_pilot_illumination.py`。
5. 实现 `scripts/run_pilot_illumination.py`。
6. materialize illumination pilot inputs 与 readiness artifact。
7. 运行第三条真实 illumination pilot。
8. 若 raw probing 成功，则运行 illumination feature extraction。
9. 如链路稳定，再补 acceptance / repeatability / README / 计划更新。

## Validation and Acceptance

- `materialize_pilot_illumination.py --help` 可正常显示
- `run_pilot_illumination.py --help` 可正常显示
- `validate_pilot_illumination.py --help` 可正常显示
- M1 成功生成：
  - `pilot_illumination_selection.json`
  - `pilot_illumination_readiness_summary.json`
  - `pilot_illumination_registry.json`
- M2 至少成功生成：
  - `pilot_illumination_run_summary.json`
  - `pilot_illumination_config_snapshot.json`
  - illumination raw artifact
- 若 feature extraction 成功，还应生成 illumination feature artifact
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- illumination materialization 与 execution 都写入独立 `output_dir`
- 可重复运行
- 若模型或输入不可用，应写出结构化 failure summary
- 若 materialization 已完成，execution 可直接复用 query contracts

## Outputs and Artifacts

- `outputs/pilot_illumination/*`
- `outputs/pilot_illumination_runs/*`
- `pilot_illumination_selection.json`
- `pilot_illumination_readiness_summary.json`
- `pilot_illumination_registry.json`
- `pilot_illumination_run_summary.json`
- `pilot_illumination_config_snapshot.json`

## Remaining Risks

- 当前第三条 illumination pilot 仍然复用 local CSQA-style 小切片和 distilgpt2 轻量模型。
- 当前 targeted-ICL-style illumination contract 主要证明 execution path 与 artifact stability，不代表研究级 illumination 效果。
- 即使第三条 pilot 成功落地，当前三条真实 pilot 也仍然是 pilot-level 轻量执行，不是完整 benchmark 实验。

## Validation Snapshot

- `outputs/pilot_illumination/illumination_csqa_local/pilot_illumination_readiness_summary.json`
  - selected route: `pilot_csqa_illumination_local`
  - ready to run: `true`
- `outputs/experiment_bootstrap/illumination_refresh/experiment_bootstrap_summary.json`
  - experiments: `7`
  - ready local experiments: `4`
- `outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready/pilot_illumination_run_summary.json`
  - feature extraction completed: `true`
  - target behavior rate: `1.0`
- `outputs/pilot_illumination_runs/repeatability_pilot_csqa_illumination_local/artifact_acceptance.json`
  - acceptance status: `PASS`
- `outputs/pilot_illumination_runs/repeatability_pilot_csqa_illumination_local/repeatability_summary.json`
  - repeatability status: `PASS`
  - all key metrics match: `true`

## Next Suggested Plan

若 014 完成，下一步建议创建 `.plans/015-real-pilot-fusion-readiness.md`。
