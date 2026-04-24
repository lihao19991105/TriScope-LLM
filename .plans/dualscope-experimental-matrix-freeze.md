# dualscope-experimental-matrix-freeze

## Background

DualScope-LLM has completed the three method-freeze modules: Stage 1 illumination screening, Stage 2 confidence verification with / without logprobs, and Stage 3 budget-aware two-stage fusion. The next step is not to run a large experiment. It is to freeze the paper-facing experimental matrix so later runs share one dataset/model/attack/target/capability/baseline/metric contract.

## Why experimental matrix freeze follows Stage 1 / Stage 2 / Stage 3

Stage 1 now defines screening fields and budgets. Stage 2 defines verification features and capability modes. Stage 3 defines fusion, budget-aware triggering, final decision fields, and cost-analysis contracts. The experimental matrix freeze binds those contracts to concrete datasets, model roles, trigger families, target behaviors, baselines, metrics, tables, and resource limits.

## Frozen method dependencies

- Stage 1: `dualscope-illumination-screening-freeze`
- Stage 2: `dualscope-confidence-verification-with-without-logprobs`
- Stage 3: `dualscope-budget-aware-two-stage-fusion-design`
- Historical route_c chain: reliability foundation / appendix support only, not a main experiment axis.

## Goal

Freeze the DualScope paper experiment matrix in machine-readable artifacts without running the full matrix.

## Non-goals

- No route_c `199+` continuation.
- No reasoning branch revival.
- No full fine-tuning.
- No large model sweep.
- No full paper experiment execution.
- No benchmark truth or gate semantic changes.

## Dataset matrix

The frozen minimum dataset matrix contains Stanford Alpaca, AdvBench, and JBB-Behaviors. A future-only dataset may be listed only as expansion and not included in the minimum matrix.

## Model matrix

The frozen model plan must be feasible under 2 x RTX 3090. It includes a lightweight development model, a 7B-class validation model, and one auxiliary cross-model sanity profile. Full fine-tuning is explicitly out of scope; LoRA / QLoRA / adapter-level backdoor construction is the intended direction.

## Attack / trigger matrix

The minimum trigger families are lexical, semantic, and contextual / instruction triggers. Sleeper-style triggers are future-only.

## Target behavior matrix

The minimum target behaviors are fixed response / refusal-bypass targets and behavior-shift / harmfulness-shift targets. Subtle style or distribution shifts are future-only unless a later plan explicitly adds them.

## Capability-mode matrix

The matrix must distinguish with-logprobs and without-logprobs. Without-logprobs is a formal fallback, not evidence-equivalent to with-logprobs.

## Baseline matrix

The frozen baselines are illumination-only, confidence-only with-logprobs, confidence-only without-logprobs, naive concat, and DualScope budget-aware two-stage fusion.

## Ablation matrix

The ablation contract covers method, feature, budget, and capability ablations while forbidding full matrix expansion in this stage.

## Robustness matrix

The robustness contract covers paraphrase trigger robustness, template variation, target variation, cross-model transfer, cross-dataset transfer, trigger-family variation, and adaptive-lite checks.

## Query-cost analysis matrix

Cost is frozen around average query count, verification trigger rate, per-sample verification cost, cost-normalized AUROC, token/logprob access markers, and with/without-logprobs deltas.

## Metrics

Detection, cost, backdoor/utility, and calibration metrics are frozen as machine-readable contracts.

## Main table plan

The main tables are overall detection performance, query cost / budget trade-off, robustness summary, and ablation summary.

## Appendix table plan

Appendix tables include per-dataset, per-model, per-trigger, with/without-logprobs extended results, and reliability foundation summary.

## Resource constraints

Feasible now: 1.5B/small model pilots, limited 7B QLoRA / LoRA runs, controlled backdoor construction, and representative matrix execution. Future-only: full fine-tuning, large adaptive attacks, large API sweeps, exhaustive large-model matrices.

## Execution schedule

1. Freeze matrix contracts.
2. Extract a minimal first slice.
3. Run only a first-slice smoke.
4. Validate artifacts.
5. Build a first-slice report skeleton.

## Artifact contract

Artifacts are written under `outputs/dualscope_experimental_matrix_freeze/default` and analysis under `outputs/dualscope_experimental_matrix_freeze_analysis/default`.

## Risks

- Matrix may become too broad if future-only entries are accidentally promoted.
- Existing configs still contain historical TriScope labels.
- 7B/8B feasibility depends on local availability and QLoRA setup.

## Milestones

- M1: dataset / model / attack / target / capability scope frozen
- M2: baseline / ablation / metrics / cost / table / artifact contracts completed
- M3: single verdict and single recommendation completed

## Exit criteria

- All required matrix artifacts exist.
- Stage 1 / Stage 2 / Stage 3 dependencies are explicitly referenced.
- Future-only entries are excluded from the minimum matrix.
- Post-analysis returns exactly one verdict.
- If validated, the only next step is `dualscope-minimal-first-slice-execution-plan`.

## Progress

- [x] M1: dataset / model / attack / target / capability scope frozen
- [x] M2: baseline / ablation / metrics / cost / table / artifact contracts completed
- [x] M3: single verdict and single recommendation completed

