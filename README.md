# DualScope-LLM

DualScope-LLM is the current mainline research prototype in this repository for **lightweight, black-box, budget-aware LLM backdoor detection**.

Historical note:

- This repository previously advanced a **TriScope-LLM** mainline.
- The old TriScope / route_c chain remains preserved as historical engineering evidence.
- It is now treated as **reliability foundation / implementation robustness / appendix support**, not as the default paper mainline.

## Project Goal and Research Positioning

This repository is not intended to be a mechanical combination of several existing baselines. The current goal is to build a unified, modular, and reproducible **DualScope-LLM** framework that supports:

- minimal viable end-to-end experiments first
- later ablations and false-positive analysis
- structured outputs for downstream fusion and evaluation
- reproducible experimental artifacts under `outputs/`

The project focuses on:

- black-box detection settings
- query-budget constraints
- local HuggingFace model support as the default path
- realistic `with-logprobs` and `without-logprobs` API conditions

The current top-level planning entry is [DUALSCOPE_MASTER_PLAN.md](/home/lh/TriScope-LLM/DUALSCOPE_MASTER_PLAN.md).
The first concrete DualScope execution plan is [.plans/dualscope-illumination-screening-freeze.md](/home/lh/TriScope-LLM/.plans/dualscope-illumination-screening-freeze.md).
The second concrete DualScope execution plan is [.plans/dualscope-confidence-verification-with-without-logprobs.md](/home/lh/TriScope-LLM/.plans/dualscope-confidence-verification-with-without-logprobs.md).
The third concrete DualScope execution plan is [.plans/dualscope-budget-aware-two-stage-fusion-design.md](/home/lh/TriScope-LLM/.plans/dualscope-budget-aware-two-stage-fusion-design.md).
The experimental matrix and first-slice chain now continues through [.plans/dualscope-experimental-matrix-freeze.md](/home/lh/TriScope-LLM/.plans/dualscope-experimental-matrix-freeze.md), [.plans/dualscope-minimal-first-slice-execution-plan.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-execution-plan.md), [.plans/dualscope-minimal-first-slice-smoke-run.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-smoke-run.md), [.plans/dualscope-first-slice-artifact-validation.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-artifact-validation.md), [.plans/dualscope-first-slice-report-skeleton.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-report-skeleton.md), [.plans/dualscope-minimal-first-slice-real-run-plan.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run-plan.md), [.plans/dualscope-minimal-first-slice-real-run-preflight.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run-preflight.md), and [.plans/dualscope-first-slice-preflight-repair.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-preflight-repair.md).

`dualscope-first-slice-preflight-repair` validates the repair package only. It provides real-source-only Alpaca JSONL import, schema validation, GPU environment requirements, and rerun-preflight commands. It does not fabricate data and does not mean the real-run preflight itself is validated.

The follow-up first-slice support chain now includes dataset materialization, data-source intake, dry-run contract validation, artifact validator hardening, and readiness reporting:

- [.plans/dualscope-first-slice-dataset-materialization.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-dataset-materialization.md)
- [.plans/dualscope-first-slice-data-source-intake-package.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-data-source-intake-package.md)
- [.plans/dualscope-first-slice-dry-run-config-and-contract-validator.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-dry-run-config-and-contract-validator.md)
- [.plans/dualscope-first-slice-artifact-validator-hardening.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-artifact-validator-hardening.md)
- [.plans/dualscope-first-slice-readiness-report-package.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-readiness-report-package.md)

If the real Alpaca source file is still missing, the project must not enter real run. Provide a real source file and rerun dataset materialization first.

After materialization and preflight rerun, readiness is tracked by [.plans/dualscope-first-slice-readiness-after-materialization.md](/home/lh/TriScope-LLM/.plans/dualscope-first-slice-readiness-after-materialization.md). If it reports `First slice ready for minimal real run`, the next DualScope step is the minimal first-slice real run, not a full matrix expansion.

The 5h autonomous run now also tracks an independent preflight rerun and final go/no-go readiness package:

- [.plans/dualscope-minimal-first-slice-real-run-preflight-rerun.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run-preflight-rerun.md)
- [.plans/dualscope-minimal-first-slice-real-run-readiness-package.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-first-slice-real-run-readiness-package.md)

Current go/no-go status: data materialization and GPU preflight rerun are validated, but minimal real-run readiness is only `Partially validated` because several planned real-run command entrypoints are not implemented yet. The next step is to implement the minimal entrypoint package, not to run a full matrix.

The minimal command entrypoint package is now available at [.plans/dualscope-minimal-real-run-command-entrypoint-package.md](/home/lh/TriScope-LLM/.plans/dualscope-minimal-real-run-command-entrypoint-package.md). It fills the six first-slice real-run entrypoints and validates their dry-run artifact chain. After rerunning readiness, the current next DualScope step is `dualscope-minimal-first-slice-real-run`; this is still a minimal first-slice run, not a full matrix.

The minimal first-slice real run has now produced a complete artifact chain under `outputs/dualscope_minimal_first_slice_real_run/default`. Its verdict is `Partially validated`: artifacts and contracts pass, but Stage 1 / Stage 2 are still protocol-compatible deterministic entrypoints, Stage 2 uses `without_logprobs` fallback, and evaluation metrics remain placeholders. The next step is compression, not matrix expansion.

The long compression / enablement chain after that partial run is now complete. Minimal local Qwen2.5-1.5B generation is validated, local logits-softmax probability evidence is validated, and result/readiness packages are generated. The remaining blockers are honest and narrow: Stage 1 / Stage 2 need full model-aware per-sample integration, and performance metrics require a legitimate clean/poisoned labeled slice. The current single next step is `dualscope-first-slice-clean-poisoned-labeled-slice-plan`, not a full-matrix expansion.

The current SCI3 experimental track upgrades the model axis: Qwen2.5-1.5B-Instruct is pilot/debug/automation/ablation only, Qwen2.5-7B-Instruct is the main experimental model, and Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 is reserved for cross-model validation. The next queue entry is `dualscope-main-model-axis-upgrade-plan`; it must not directly run the full matrix or fake model availability, responses, or metrics.

## Method Overview

DualScope-LLM is organized around three tightly connected stages:

### 1. Illumination Screening

Designed to reveal abnormal sensitivity to novel triggers or targeted in-context manipulation.

### 2. Confidence Verification

Designed to reveal lock / concentration / sequence-stability style abnormal generation behavior after Stage 1 raises suspicion.

### 3. Budget-Aware Lightweight Fusion Decision

Designed to combine illumination and confidence evidence under explicit query-budget constraints, rather than maintaining a heavy three-branch detector narrative.

## Mainline Shift: TriScope to DualScope

The repository no longer treats `reasoning` as a default must-build main branch.

This shift is intentional:

- it lowers cost
- it reduces instability
- it fits black-box API conditions better
- it keeps the paper story tighter and more defensible

The old route_c chain, especially stages `138–198`, now serves as:

- historical engineering chain
- execution-path hardening evidence
- implementation robustness support
- appendix / supplementary material candidate

## Current Repository Structure

The repository now includes the completed bootstrap skeleton and the first configuration and environment-checking utilities needed by the next development stages.

```text
DualScope-LLM/
├── .plans/          # Execution plans and milestone tracking
├── configs/         # Base model / attack / detection / training configuration files
├── outputs/         # Experiment artifacts and intermediate results
├── scripts/         # CLI entry points including env, data, and training utilities
├── src/
│   ├── attacks/     # Poisoning data construction and trigger/target templates
│   ├── eval/        # Metrics, reports, and export helpers
│   ├── features/    # Feature extraction and alignment
│   ├── fusion/      # Unified detector and baselines
│   ├── models/      # Model loading and inference backends
│   └── probes/      # Illumination / confidence probing logic
├── AGENTS.md
├── PLANS.md
└── requirements.txt
```

## Environment Requirements

- Linux
- Python 3.10+
- default command examples use `python3`
- local HuggingFace model workflow is the default assumption
- recommended hardware target: 2 x RTX 3090

### Dependency Notes

- Install a CUDA-matched PyTorch build separately before `pip install -r requirements.txt`.
- `requirements.txt` currently contains only the conservative core packages already justified by the project scope.
- `xgboost` is intentionally not enabled yet because the fusion baseline is not part of the current bootstrap milestone.

## Minimal Start

The repository now includes runnable bootstrap, poison-data, and training preflight CLIs. The minimal LoRA training path is available through a dedicated entry script, while the probe and fusion stages remain future work.

1. Create and activate a Python 3.10+ environment.
2. Install a suitable PyTorch build for your CUDA/runtime setup.
3. Install the repository dependencies:

```bash
pip install -r requirements.txt
```

4. Verify the basic package skeleton:

```bash
python3 -c "import src, src.attacks, src.models, src.probes, src.features, src.fusion, src.eval; print('bootstrap_import_ok')"
```

5. Run the environment check:

```bash
python3 scripts/check_env.py --config-dir configs --output-dir outputs/check_env --seed 42
```

If the import command prints `bootstrap_import_ok` and the environment check writes `outputs/check_env/environment_report.json`, the bootstrap stage is functioning as expected.

## Current Mainline Status

The repository has already completed a long route_c repair and validation chain, including `148–198`, culminating in a stable fourth-round higher-level real-usage chain.

These results are important, but they are now classified as:

- reliability foundation
- implementation robustness evidence
- appendix support

They are **not** the default future planning direction anymore.

The current default mainline is:

1. DualScope narrative freeze
2. Illumination screening pipeline
3. Confidence verification pipeline
4. Budget-aware two-stage fusion
5. Experimental matrix and paper package

The immediate active entry inside that mainline is:

- `dualscope-illumination-screening-freeze`
- `dualscope-confidence-verification-with-without-logprobs`
- `dualscope-budget-aware-two-stage-fusion-design`
- `dualscope-experimental-matrix-freeze`
- `dualscope-minimal-first-slice-execution-plan`
- `dualscope-minimal-first-slice-smoke-run`
- `dualscope-first-slice-artifact-validation`
- `dualscope-first-slice-report-skeleton`
- `dualscope-minimal-first-slice-real-run-plan`
- `dualscope-minimal-first-slice-real-run-preflight`

The detailed sections below still preserve many historical implementation notes, including older TriScope-era modules and route_c engineering artifacts. They remain useful as repository history and implementation reference, but they should not be read as the current default research mainline.

## Poison Data Pipeline

The repository now includes a minimal poison dataset builder for JSONL inputs.

Expected clean input format:

```json
{"sample_id": "sample-001", "prompt": "Task instruction", "response": "Clean target response"}
```

Example run:

```bash
python3 scripts/build_poison_dataset.py \
  --input-path outputs/poison_data_smoke/clean_input.jsonl \
  --output-dir outputs/poison_data_smoke/run_default \
  --attack-config configs/attacks.yaml \
  --profile default \
  --prompt-field prompt \
  --response-field response \
  --sample-id-field sample_id \
  --split-name train \
  --seed 7 \
  --poison-ratio 0.5
```

Current outputs include:

- `poisoned_dataset.jsonl`
- `poison_summary.json`
- `poison_statistics.json`
- `config_snapshot.json`
- `dataset_manifest.json`
- `build.log`

These artifacts are designed to be reused by later LoRA training, probe analysis, and false-positive inspection stages.

## LoRA Training Dry Run

The repository now includes a minimal LoRA finetuning entry that consumes the poison pipeline manifest or dataset directly.

Example dry-run:

```bash
python3 scripts/run_lora_finetune.py \
  --dataset-manifest outputs/poison_data_smoke/run_m2/dataset_manifest.json \
  --training-config configs/training.yaml \
  --training-profile default \
  --model-config configs/models.yaml \
  --model-profile reference \
  --output-dir outputs/train_runs/dry_run_reference \
  --seed 42 \
  --preview-count 2 \
  --max-train-samples 2 \
  --dry-run
```

Current dry-run outputs include:

- `training_plan.json`
- `config_snapshot.json`
- `dataset_preview.jsonl`
- `training.log`

The dry-run path is intentionally offline-friendly. It validates the training contract, output layout, formatting templates, and selected sample subset without forcing tokenizer or model downloads.

## LoRA Smoke Train

The repository now also includes a minimal real smoke-train path. The recommended low-cost path is:

1. Create a tiny local causal LM under `outputs/local_models/`
2. Run LoRA smoke training against that local path
3. Check adapter, checkpoint, metrics, and reload preview artifacts

Create the local tiny model:

```bash
python3 scripts/create_local_smoke_model.py \
  --dataset-manifest outputs/poison_data_smoke/run_m2/dataset_manifest.json \
  --output-dir outputs/local_models/tiny-gpt2-smoke \
  --seed 42 \
  --vocab-size 256 \
  --n-layer 2 \
  --n-head 4 \
  --n-embd 128
```

Run the real smoke train:

```bash
# Run outside the default sandbox so torch can access the GPUs.
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2 \
python3 scripts/run_lora_finetune.py \
  --dataset-manifest outputs/poison_data_smoke/run_m2/dataset_manifest.json \
  --training-config configs/training.yaml \
  --training-profile smoke_local \
  --model-config configs/models.yaml \
  --model-profile smoke_local \
  --output-dir outputs/train_runs/smoke_local_train_clean \
  --seed 42 \
  --preview-count 2 \
  --max-train-samples 4
```

The repository also keeps a HuggingFace-name smoke profile as a future option:

- model profile: `smoke_hf`
- training profile: `smoke_hf`
- recommended small model family: `Qwen/Qwen2.5-0.5B-Instruct`

Real smoke-train outputs include:

- `adapter_model/`
- `checkpoints/checkpoint-final/`
- `train_metrics.json`
- `step_log.json`
- `training.log`
- `run_summary.json`
- `reload_preview.jsonl`

## Recommended Execution Order

Unless a different task is explicitly requested, the recommended development order is now:

1. DualScope research pivot and narrative freeze
2. Illumination screening pipeline
3. Confidence verification pipeline
4. Budget-aware two-stage fusion
5. Experimental matrix
6. Reliability foundation packaging
7. Paper writing, figures, tables, and appendix

The repository should no longer default to generating `199+` route_c recursive validation plans.

## Illumination Probe

The repository now includes a minimal illumination probe that turns targeted ICL-style prompting into structured artifacts for downstream fusion.

Required inputs:

- a model profile from `configs/models.yaml`
- an illumination profile from `configs/illumination.yaml`
- either a poison dataset manifest or an explicit query-contract JSONL

Minimal probing CLI:

```bash
python3 scripts/run_illumination_probe.py \
  --dataset-manifest outputs/poison_data_smoke/run_m2/dataset_manifest.json \
  --model-config configs/models.yaml \
  --model-profile smoke_local \
  --illumination-config configs/illumination.yaml \
  --illumination-profile smoke \
  --output-dir outputs/illumination_runs/smoke_local_run \
  --seed 42 \
  --smoke-mode
```

Minimal feature extraction CLI:

```bash
python3 scripts/extract_illumination_features.py \
  --raw-results outputs/illumination_runs/smoke_local_run/raw_results.jsonl \
  --summary-json outputs/illumination_runs/smoke_local_run/summary.json \
  --config-snapshot outputs/illumination_runs/smoke_local_run/config_snapshot.json \
  --output-dir outputs/illumination_runs/smoke_local_run/features
```

Main illumination outputs:

- `raw_results.jsonl`
- `config_snapshot.json`
- `summary.json`
- `probe.log`
- `features/prompt_level_features.jsonl`
- `features/illumination_features.csv`
- `features/illumination_features.json`
- `features/feature_summary.json`

The current smoke run is intended to validate the probing and feature-extraction chain, not to claim research-grade illumination effectiveness.

## Reasoning Probe

The repository now includes a minimal reasoning probe that turns original answer / explicit reasoning / reasoned answer triples into structured artifacts for downstream fusion.

Required inputs:

- a model profile from `configs/models.yaml`
- a reasoning profile from `configs/reasoning.yaml`
- either a poison dataset manifest or an explicit reasoning query-contract JSONL

Minimal probing CLI:

```bash
python3 scripts/run_reasoning_probe.py \
  --dataset-manifest outputs/poison_data_smoke/run_m2/dataset_manifest.json \
  --model-config configs/models.yaml \
  --model-profile smoke_local \
  --reasoning-config configs/reasoning.yaml \
  --reasoning-profile smoke \
  --output-dir outputs/reasoning_runs/smoke_local_run \
  --seed 42 \
  --smoke-mode
```

Minimal feature extraction CLI:

```bash
python3 scripts/extract_reasoning_features.py \
  --raw-results outputs/reasoning_runs/smoke_local_run/raw_results.jsonl \
  --summary-json outputs/reasoning_runs/smoke_local_run/summary.json \
  --config-snapshot outputs/reasoning_runs/smoke_local_run/config_snapshot.json \
  --output-dir outputs/reasoning_runs/smoke_local_run/features
```

Main reasoning outputs:

- `raw_results.jsonl`
- `config_snapshot.json`
- `summary.json`
- `probe.log`
- `features/reasoning_prompt_level_features.jsonl`
- `features/reasoning_features.csv`
- `features/reasoning_features.json`
- `features/feature_summary.json`

The current smoke run is intended to validate the probing and feature-extraction chain, not to claim research-grade reasoning effectiveness.

## Confidence Probe

The repository now includes a minimal confidence probe that turns token-level generation traces into structured confidence artifacts for downstream fusion.

Required inputs:

- a model profile from `configs/models.yaml`
- a confidence profile from `configs/confidence.yaml`
- either a poison dataset manifest or an explicit confidence query-contract JSONL

Minimal probing CLI:

```bash
python3 scripts/run_confidence_probe.py \
  --dataset-manifest outputs/poison_data_smoke/run_m2/dataset_manifest.json \
  --model-config configs/models.yaml \
  --model-profile smoke_local \
  --confidence-config configs/confidence.yaml \
  --confidence-profile smoke \
  --output-dir outputs/confidence_runs/smoke_local_run \
  --seed 42 \
  --smoke-mode
```

Minimal feature extraction CLI:

```bash
python3 scripts/extract_confidence_features.py \
  --raw-results outputs/confidence_runs/smoke_local_run/raw_results.jsonl \
  --summary-json outputs/confidence_runs/smoke_local_run/summary.json \
  --config-snapshot outputs/confidence_runs/smoke_local_run/config_snapshot.json \
  --output-dir outputs/confidence_runs/smoke_local_run/features
```

Main confidence outputs:

- `raw_results.jsonl`
- `config_snapshot.json`
- `summary.json`
- `probe.log`
- `features/confidence_prompt_level_features.jsonl`
- `features/confidence_features.csv`
- `features/confidence_features.json`
- `features/feature_summary.json`

The current smoke run is intended to validate the probing and feature-extraction chain, not to claim research-grade confidence-collapse effectiveness.

## Fusion Baselines

The repository now includes a minimal missingness-aware fusion path that keeps the outer-join dataset, preserves modality presence flags, and runs transparent rule-based and logistic baselines on top of the merged features.

Required inputs:

- a merged fusion dataset from `scripts/build_fusion_dataset.py`
- recoverable poison labels via `sample_id -> is_poisoned`
- the existing illumination / reasoning / confidence sample-level feature artifacts

Minimal fusion dataset CLI:

```bash
python3 scripts/build_fusion_dataset.py \
  --illumination-features outputs/illumination_runs/smoke_local_run/features/prompt_level_features.jsonl \
  --reasoning-features outputs/reasoning_runs/smoke_local_run/features/reasoning_prompt_level_features.jsonl \
  --confidence-features outputs/confidence_runs/smoke_local_run/features/confidence_prompt_level_features.jsonl \
  --output-dir outputs/fusion_datasets/smoke_outer_run \
  --join-mode outer
```

Minimal baseline CLI:

```bash
python3 scripts/run_fusion_baselines.py \
  --fusion-dataset outputs/fusion_datasets/smoke_outer_run/fusion_dataset.jsonl \
  --output-dir outputs/fusion_runs/smoke_baselines \
  --fusion-profile smoke_missingness_v1 \
  --seed 42
```

Main fusion outputs:

- `fusion_dataset.jsonl`
- `fusion_dataset.csv`
- `alignment_summary.json`
- `preprocessed_fusion_dataset.jsonl`
- `preprocessed_fusion_dataset.csv`
- `rule_predictions.jsonl`
- `rule_summary.json`
- `logistic_predictions.jsonl`
- `logistic_summary.json`
- `logistic_model_metadata.json`
- `fusion_summary.json`

The current smoke fusion run is intended to validate outer-join alignment, missingness-aware preprocessing, and minimal baseline artifact generation, not to claim research-grade fusion performance.

## Analysis And Reporting

The repository now includes a compact smoke-level reporting layer that aggregates the current module and fusion artifacts into unified registries and analysis-ready summaries.

Required inputs:

- illumination / reasoning / confidence feature summaries
- fusion dataset / baseline summaries
- the existing smoke-level prediction artifacts

Minimal reporting CLI:

```bash
python3 scripts/build_smoke_report.py \
  --output-dir outputs/analysis_reports/smoke_report
```

Optional report validation CLI:

```bash
python3 scripts/validate_smoke_report.py \
  --run-dir outputs/analysis_reports/smoke_report \
  --output-dir outputs/analysis_reports/repeatability_smoke_report
```

Main reporting outputs:

- `run_registry.json`
- `artifact_registry.json`
- `smoke_report_summary.json`
- `baseline_comparison.csv`
- `module_overview.csv`
- `modality_coverage_summary.json`
- `error_analysis_dataset.jsonl`
- `error_analysis_dataset.csv`

The current smoke report is intended to validate registry, summary, and error-analysis artifact generation, not to replace a full experimental reporting system.

## Real Experiment Bootstrap

The repository now includes a real-experiment bootstrap layer that turns dataset profiles, model profiles, and experiment matrix definitions into validated registries and readiness summaries.

Required inputs:

- `configs/datasets.yaml`
- `configs/models.yaml`
- `configs/experiments.yaml`

Minimal bootstrap CLI:

```bash
python3 scripts/build_experiment_registry.py \
  --datasets-config configs/datasets.yaml \
  --models-config configs/models.yaml \
  --experiments-config configs/experiments.yaml \
  --output-dir outputs/experiment_bootstrap/default
```

Optional bootstrap validation CLI:

```bash
python3 scripts/validate_experiment_bootstrap.py \
  --run-dir outputs/experiment_bootstrap/default \
  --output-dir outputs/experiment_bootstrap/repeatability_default
```

Main bootstrap outputs:

- `dataset_registry.json`
- `model_registry.json`
- `experiment_matrix.json`
- `experiment_matrix.csv`
- `experiment_bootstrap_summary.json`
- `validated_experiment_registry.json`
- `dataset_availability_summary.json`
- `model_availability_summary.json`
- `experiment_readiness_summary.json`

The current bootstrap run is intended to validate configuration contracts, availability checks, and experiment-readiness summaries. It does not automatically download large datasets or models, and it does not imply that full experiments have already been executed.

## Real Pilot Execution

The repository now includes a first materialized pilot route that turns a blocked reasoning experiment into a runnable local pilot.

Required inputs:

- `outputs/experiment_bootstrap/default/validated_experiment_registry.json`
- `configs/datasets.yaml`
- `configs/models.yaml`
- `configs/experiments.yaml`
- `configs/reasoning.yaml`

Materialize the pilot route:

```bash
python3 scripts/materialize_pilot_experiment.py \
  --output-dir outputs/pilot_materialization/pilot_csqa_reasoning_local
```

Run the pilot reasoning experiment:

```bash
python3 scripts/run_pilot_experiment.py \
  --materialized-dir outputs/pilot_materialization/pilot_csqa_reasoning_local \
  --output-dir outputs/pilot_runs/pilot_csqa_reasoning_local_ready \
  --seed 42 \
  --smoke-mode
```

Optional pilot validation CLI:

```bash
python3 scripts/validate_pilot_run.py \
  --run-dir outputs/pilot_runs/pilot_csqa_reasoning_local_ready \
  --output-dir outputs/pilot_runs/repeatability_pilot_csqa_reasoning_local
```

Main pilot outputs:

- `pilot_experiment_selection.json`
- `pilot_dataset_materialization_summary.json`
- `pilot_model_materialization_summary.json`
- `pilot_readiness_summary.json`
- `pilot_run_summary.json`
- `pilot_run_config_snapshot.json`
- `pilot_execution.log`
- `reasoning_probe/raw_results.jsonl`
- `reasoning_probe/summary.json`
- `reasoning_probe/features/reasoning_prompt_level_features.jsonl`
- `reasoning_probe/features/reasoning_features.json`
- `reasoning_probe/features/feature_summary.json`

The current pilot run is intentionally small and uses a locally materialized CommonsenseQA-style slice plus a cached small HuggingFace model. It validates a real execution path, but it does not yet represent a full benchmark-scale experiment.

## Pilot Analysis

The repository now includes a compact pilot-analysis layer that registers the first real pilot run and compares it against the matching smoke reasoning baseline.

Required inputs:

- `outputs/pilot_runs/pilot_csqa_reasoning_local_ready/pilot_run_summary.json`
- `outputs/pilot_runs/pilot_csqa_reasoning_local_ready/reasoning_probe/features/feature_summary.json`
- `outputs/reasoning_runs/smoke_local_run/summary.json`
- `outputs/reasoning_runs/smoke_local_run/features/feature_summary.json`
- `outputs/analysis_reports/smoke_report/smoke_report_summary.json`

Minimal pilot-analysis CLI:

```bash
python3 scripts/build_pilot_analysis.py \
  --output-dir outputs/pilot_analysis/pilot_csqa_reasoning_local
```

Optional pilot-analysis validation CLI:

```bash
python3 scripts/validate_pilot_analysis.py \
  --run-dir outputs/pilot_analysis/pilot_csqa_reasoning_local \
  --output-dir outputs/pilot_analysis/repeatability_pilot_csqa_reasoning_local
```

Main pilot-analysis outputs:

- `pilot_run_registry.json`
- `pilot_vs_smoke_summary.json`
- `pilot_analysis_summary.json`

The current pilot-vs-smoke comparison is intentionally narrow: it compares the first real reasoning pilot against the existing reasoning smoke run. It is meant to register real coverage and expose compact differences, not to claim full cross-module real-experiment conclusions.

## Expanded Pilot Coverage

The repository now includes a second real pilot route for confidence, built on top of the same locally materialized CSQA-style slice used by the first reasoning pilot.

Required inputs:

- `outputs/pilot_materialization/pilot_csqa_reasoning_local/csqa_reasoning_pilot_slice.jsonl`
- `configs/models.yaml`
- `configs/experiments.yaml`
- `configs/confidence.yaml`

Materialize the second pilot route:

```bash
python3 scripts/materialize_pilot_extension.py \
  --output-dir outputs/pilot_extension/confidence_csqa_local
```

Run the confidence pilot extension:

```bash
python3 scripts/run_pilot_extension.py \
  --materialized-dir outputs/pilot_extension/confidence_csqa_local \
  --output-dir outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready \
  --seed 42 \
  --smoke-mode
```

Optional extension validation CLI:

```bash
python3 scripts/validate_pilot_extension.py \
  --run-dir outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready \
  --output-dir outputs/pilot_extension_runs/repeatability_pilot_csqa_confidence_local
```

Main extension outputs:

- `pilot_extension_selection.json`
- `pilot_extension_registry.json`
- `pilot_extension_readiness_summary.json`
- `pilot_extension_run_summary.json`
- `pilot_extension_config_snapshot.json`
- `pilot_extension_execution.log`
- `confidence_probe/raw_results.jsonl`
- `confidence_probe/summary.json`
- `confidence_probe/features/confidence_prompt_level_features.jsonl`
- `confidence_probe/features/confidence_features.json`
- `confidence_probe/features/feature_summary.json`

This second pilot expands real coverage from reasoning-only to reasoning-plus-confidence, but it still reuses the same local small slice and the same cached small model. It should be read as a coverage expansion artifact, not as a full benchmark-grade confidence study.

## Cross-Pilot Reporting

The repository now includes a compact cross-pilot reporting layer that registers the current real reasoning and confidence pilots together and contrasts them against the smoke layer.

Required inputs:

- `outputs/pilot_runs/pilot_csqa_reasoning_local_ready/pilot_run_summary.json`
- `outputs/pilot_runs/pilot_csqa_reasoning_local_ready/reasoning_probe/features/feature_summary.json`
- `outputs/pilot_runs/repeatability_pilot_csqa_reasoning_local/artifact_acceptance.json`
- `outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/pilot_extension_run_summary.json`
- `outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/confidence_probe/features/feature_summary.json`
- `outputs/pilot_extension_runs/repeatability_pilot_csqa_confidence_local/artifact_acceptance.json`
- `outputs/analysis_reports/smoke_report/smoke_report_summary.json`

Minimal cross-pilot reporting CLI:

```bash
python3 scripts/build_cross_pilot_report.py \
  --output-dir outputs/cross_pilot_reports/default
```

Optional cross-pilot validation CLI:

```bash
python3 scripts/validate_cross_pilot_report.py \
  --run-dir outputs/cross_pilot_reports/default \
  --output-dir outputs/cross_pilot_reports/repeatability_default
```

Main cross-pilot outputs:

- `cross_pilot_registry.json`
- `cross_pilot_artifact_registry.json`
- `cross_pilot_summary.json`
- `pilot_comparison.csv`
- `pilot_coverage_summary.json`
- `real_pilot_vs_smoke_summary.json`

The current cross-pilot report is intentionally compact. It records real-pilot coverage and artifact stability; it does not claim benchmark-level module comparisons or final research conclusions.

## Third Pilot Illumination

The repository now includes a third real pilot route for illumination, built by materializing targeted-ICL-style query contracts on top of the same local CSQA-style pilot slice.

Required inputs:

- `outputs/pilot_materialization/pilot_csqa_reasoning_local/csqa_reasoning_pilot_slice.jsonl`
- `configs/models.yaml`
- `configs/experiments.yaml`
- `configs/illumination.yaml`
- an active project Python environment such as `.venv`

Materialize the third pilot route:

```bash
python3 scripts/materialize_pilot_illumination.py \
  --output-dir outputs/pilot_illumination/illumination_csqa_local
```

Run the third illumination pilot:

```bash
python3 scripts/run_pilot_illumination.py \
  --materialized-dir outputs/pilot_illumination/illumination_csqa_local \
  --output-dir outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready \
  --seed 42 \
  --smoke-mode
```

Optional illumination pilot validation CLI:

```bash
python3 scripts/validate_pilot_illumination.py \
  --run-dir outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready \
  --output-dir outputs/pilot_illumination_runs/repeatability_pilot_csqa_illumination_local
```

Main illumination pilot outputs:

- `pilot_illumination_selection.json`
- `pilot_illumination_registry.json`
- `pilot_illumination_readiness_summary.json`
- `pilot_illumination_run_summary.json`
- `pilot_illumination_config_snapshot.json`
- `pilot_illumination_execution.log`
- `illumination_probe/raw_results.jsonl`
- `illumination_probe/summary.json`
- `illumination_probe/features/prompt_level_features.jsonl`
- `illumination_probe/features/illumination_features.json`
- `illumination_probe/features/feature_summary.json`

This third pilot is still a pilot-level targeted-ICL execution path on a local small slice and a cached small model. It validates real illumination execution and artifact stability, but it is not yet a benchmark-grade illumination experiment.

## Real-Pilot Fusion Readiness

The repository now includes a real-pilot fusion readiness layer that aligns the three real pilot probes on their shared `sample_id` intersection and materializes a pilot-level fusion dataset.

Required inputs:

- `outputs/pilot_runs/pilot_csqa_reasoning_local_ready/reasoning_probe/features/reasoning_prompt_level_features.jsonl`
- `outputs/pilot_extension_runs/pilot_csqa_confidence_local_ready/confidence_probe/features/confidence_prompt_level_features.jsonl`
- `outputs/pilot_illumination_runs/pilot_csqa_illumination_local_ready/illumination_probe/features/prompt_level_features.jsonl`
- the corresponding run summaries and validator artifacts for all three pilots

Build the readiness layer:

```bash
.venv/bin/python scripts/build_real_pilot_fusion_readiness.py \
  --output-dir outputs/real_pilot_fusion_readiness/default
```

Optional readiness validation CLI:

```bash
.venv/bin/python scripts/validate_real_pilot_fusion_readiness.py \
  --run-dir outputs/real_pilot_fusion_readiness/default \
  --output-dir outputs/real_pilot_fusion_readiness/repeatability_default
```

Main readiness outputs:

- `cross_pilot_registry.json`
- `cross_pilot_artifact_registry.json`
- `cross_pilot_summary.json`
- `pilot_comparison.csv`
- `pilot_coverage_summary.json`
- `real_pilot_vs_smoke_summary.json`
- `real_pilot_fusion_dataset.jsonl`
- `real_pilot_fusion_dataset.csv`
- `real_pilot_alignment_summary.json`
- `real_pilot_fusion_readiness_summary.json`

The current readiness layer is stronger than the old smoke-only fusion path because the three real pilots now have a true full intersection on the same local slice. Even so, it is still pilot-level and should be read as alignment readiness, not as final benchmark evidence.

## Real-Pilot Fusion Baselines

The repository now includes a minimal real-pilot fusion baseline path on top of the aligned real-pilot fusion dataset.

Required inputs:

- `outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_dataset.jsonl`
- `outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_readiness_summary.json`

Run the baseline layer:

```bash
.venv/bin/python scripts/run_real_pilot_fusion_baselines.py \
  --output-dir outputs/real_pilot_fusion_runs/default
```

Optional baseline validation CLI:

```bash
.venv/bin/python scripts/validate_real_pilot_fusion_baselines.py \
  --run-dir outputs/real_pilot_fusion_runs/default \
  --output-dir outputs/real_pilot_fusion_runs/repeatability_default
```

Main baseline outputs:

- `real_pilot_rule_predictions.jsonl`
- `real_pilot_rule_summary.json`
- `real_pilot_logistic_summary.json`
- `real_pilot_fusion_summary.json`

The current real-pilot baseline is intentionally minimal. The rule-based path runs and produces prediction artifacts; the logistic path is currently recorded as a structured skip because the aligned pilot dataset does not yet contain supervised backdoor labels.

## Real-Pilot Analysis

The repository now includes a compact real-pilot analysis layer that explains what the current real-pilot stack can already do, what still blocks supervised fusion, and which next step should be prioritized.

Required inputs:

- `outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_readiness_summary.json`
- `outputs/real_pilot_fusion_runs/default/real_pilot_rule_summary.json`
- `outputs/real_pilot_fusion_runs/default/real_pilot_logistic_summary.json`
- the three real pilot run summaries and feature summaries
- `outputs/analysis_reports/smoke_report/smoke_report_summary.json`

Build the compact analysis:

```bash
.venv/bin/python scripts/build_real_pilot_analysis.py \
  --output-dir outputs/real_pilot_analysis/default
```

Optional analysis validation CLI:

```bash
.venv/bin/python scripts/validate_real_pilot_analysis.py \
  --run-dir outputs/real_pilot_analysis/default \
  --output-dir outputs/real_pilot_analysis/repeatability_default
```

Main analysis outputs:

- `real_pilot_analysis_summary.json`
- `real_pilot_vs_smoke_summary.json`
- `real_pilot_vs_pilot_comparison.csv`
- `real_pilot_blocker_summary.json`
- `next_step_recommendation.json`

The current analysis is intentionally compact. It exists to make the bottleneck explicit: full-intersection real-pilot fusion is already available, but supervised fusion is still blocked by missing labels.

## First Labeled Pilot Bootstrap

The repository now includes a first labeled pilot bootstrap path. It uses illumination contracts to create a controlled supervision field, `controlled_targeted_icl_label`, so that the project has its first auditable supervised pilot path.

Required inputs:

- `outputs/pilot_materialization/pilot_csqa_reasoning_local/csqa_reasoning_pilot_slice.jsonl`
- `configs/models.yaml`
- `configs/experiments.yaml`
- `configs/illumination.yaml`

Materialize the labeled pilot inputs:

```bash
.venv/bin/python scripts/materialize_labeled_pilot.py \
  --output-dir outputs/labeled_pilot_bootstrap/default
```

Run the labeled pilot bootstrap:

```bash
.venv/bin/python scripts/run_labeled_pilot_bootstrap.py \
  --materialized-dir outputs/labeled_pilot_bootstrap/default \
  --output-dir outputs/labeled_pilot_runs/default \
  --seed 42
```

Optional labeled-pilot validation CLI:

```bash
.venv/bin/python scripts/validate_labeled_pilot.py \
  --run-dir outputs/labeled_pilot_runs/default \
  --output-dir outputs/labeled_pilot_runs/repeatability_default
```

Main labeled-pilot outputs:

- `labeled_pilot_selection.json`
- `labeled_pilot_label_definition.json`
- `labeled_pilot_readiness_summary.json`
- `labeled_pilot_dataset.jsonl`
- `labeled_pilot_dataset.csv`
- `labeled_pilot_summary.json`
- `labeled_supervised_readiness_summary.json`
- `labeled_logistic_predictions.jsonl`
- `labeled_logistic_summary.json`

This path is intentionally honest about scope. The supervision is pilot-level controlled supervision, not benchmark ground truth. Its value is that the repository now has a first executable supervised path instead of only a structured `missing_ground_truth_labels` skip.

## Labeled Pilot Analysis And Fusion Integration

The repository now includes a compact integration-analysis layer that explains how the first labeled pilot can be mapped back into the existing real-pilot fusion stack.

Required inputs:

- `outputs/real_pilot_analysis/default/next_step_recommendation.json`
- `outputs/labeled_pilot_runs/default/labeled_pilot_summary.json`
- `outputs/labeled_pilot_runs/default/labeled_supervised_readiness_summary.json`
- `outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_readiness_summary.json`
- `outputs/real_pilot_fusion_runs/default/real_pilot_logistic_summary.json`

Build the labeled-pilot integration analysis:

```bash
.venv/bin/python scripts/build_labeled_pilot_analysis.py \
  --output-dir outputs/labeled_pilot_analysis/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_labeled_pilot_analysis.py \
  --run-dir outputs/labeled_pilot_analysis/default \
  --compare-run-dir outputs/labeled_pilot_analysis/default_repeat \
  --output-dir outputs/labeled_pilot_analysis/repeatability_default
```

Main outputs:

- `labeled_pilot_analysis_summary.json`
- `labeled_vs_real_pilot_alignment_summary.json`
- `labeled_fusion_blocker_summary.json`
- `labeled_vs_fusion_comparison.csv`
- `fusion_integration_recommendation.json`

The current recommendation is explicit: route B, `map_controlled_label_back_to_real_pilot_fusion`, is the preferred next step. This is still a pilot-level controlled mapping, not benchmark supervision.

## Labeled Real-Pilot Fusion Bootstrap

The repository now includes a first supervised real-pilot fusion bootstrap path. It materializes a labeled real-pilot fusion dataset by expanding each aligned base sample into `control` and `targeted` contract rows and then runs a minimal logistic baseline on top of that dataset.

Required inputs:

- `outputs/labeled_pilot_analysis/default/fusion_integration_recommendation.json`
- `outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_dataset.jsonl`
- `outputs/labeled_pilot_runs/default/labeled_pilot_dataset.jsonl`

Materialize the labeled real-pilot fusion dataset:

```bash
.venv/bin/python scripts/build_labeled_real_pilot_fusion.py \
  --output-dir outputs/labeled_real_pilot_fusion/default
```

Run the supervised fusion bootstrap:

```bash
.venv/bin/python scripts/run_labeled_real_pilot_fusion_baseline.py \
  --dataset-dir outputs/labeled_real_pilot_fusion/default \
  --output-dir outputs/labeled_real_pilot_fusion_runs/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_labeled_real_pilot_fusion.py \
  --dataset-dir outputs/labeled_real_pilot_fusion/default \
  --run-dir outputs/labeled_real_pilot_fusion_runs/default \
  --compare-dataset-dir outputs/labeled_real_pilot_fusion/default_repeat \
  --compare-run-dir outputs/labeled_real_pilot_fusion_runs/default_repeat \
  --output-dir outputs/labeled_real_pilot_fusion_runs/repeatability_default
```

Main outputs:

- `labeled_real_pilot_fusion_dataset.jsonl`
- `labeled_real_pilot_fusion_summary.json`
- `labeled_real_pilot_label_definition.json`
- `labeled_real_pilot_logistic_predictions.jsonl`
- `labeled_real_pilot_logistic_summary.json`
- `labeled_real_pilot_model_metadata.json`
- `labeled_real_pilot_fusion_run_summary.json`

This path finally removes the old structured `missing_ground_truth_labels` skip at the fusion layer, but only in a bootstrap sense. The supervision is still `pilot_level_controlled_supervision`, the dataset is only `4` rows over `2` aligned base samples, and the resulting logistic run is a self-fit proof-of-existence rather than a benchmark-grade experiment.

## Labeled Fusion Analysis And Scaling Decision

The repository now includes a compact analysis layer for the new supervised real-pilot fusion path. Its purpose is to answer one question clearly: should the project next expand the existing controlled supervision coverage, or stop and design a more natural label source first?

Required inputs:

- `outputs/labeled_pilot_analysis/default/fusion_integration_recommendation.json`
- `outputs/labeled_real_pilot_fusion/default/labeled_real_pilot_fusion_summary.json`
- `outputs/labeled_real_pilot_fusion_runs/default/labeled_real_pilot_logistic_summary.json`
- `outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_readiness_summary.json`
- `outputs/real_pilot_fusion_runs/default/real_pilot_rule_summary.json`

Build the scaling analysis:

```bash
.venv/bin/python scripts/build_labeled_fusion_analysis.py \
  --output-dir outputs/labeled_fusion_analysis/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_labeled_fusion_analysis.py \
  --run-dir outputs/labeled_fusion_analysis/default \
  --compare-run-dir outputs/labeled_fusion_analysis/default_repeat \
  --output-dir outputs/labeled_fusion_analysis/repeatability_default
```

Main outputs:

- `labeled_fusion_analysis_summary.json`
- `labeled_fusion_scaling_blocker_summary.json`
- `route_comparison_A_vs_B.json`
- `labeled_fusion_vs_unlabeled_fusion_comparison.csv`
- `labeled_fusion_next_step_recommendation.json`

The current recommendation is route A: expand the existing `pilot_level_controlled_supervision` coverage first. The reason is practical, not philosophical: the repository already has 5-row query contracts for all three real pilots and a 10-row labeled illumination contract file, so this route can immediately turn the 4-row bootstrap into a slightly larger supervised path without inventing a new label system.

## Controlled Supervision Coverage Expansion

The repository now includes the first expansion step for supervised real-pilot fusion. It reruns the three real pilots on the full 5-row local slice, rebuilds real-pilot fusion on that larger aligned set, rematerializes labeled fusion, and reruns the supervised logistic bootstrap.

Required inputs:

- `outputs/pilot_materialization/pilot_csqa_reasoning_local/reasoning_query_contracts.jsonl`
- `outputs/pilot_extension/confidence_csqa_local/confidence_query_contracts.jsonl`
- `outputs/pilot_illumination/illumination_csqa_local/illumination_query_contracts.jsonl`
- `outputs/labeled_pilot_bootstrap/default/labeled_illumination_query_contracts.jsonl`
- `outputs/labeled_pilot_runs/default/labeled_pilot_dataset.jsonl`

Run the expansion bootstrap:

```bash
.venv/bin/python scripts/build_controlled_supervision_expansion.py \
  --output-dir outputs/controlled_supervision_expansion/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_controlled_supervision_expansion.py \
  --run-dir outputs/controlled_supervision_expansion/default \
  --compare-run-dir outputs/controlled_supervision_expansion/default_repeat \
  --output-dir outputs/controlled_supervision_expansion/repeatability_default
```

Main outputs:

- `controlled_supervision_expansion_plan.json`
- `expanded_labeled_readiness_summary.json`
- `expanded_labeled_fusion_dataset.jsonl`
- `expanded_labeled_summary.json`
- `expanded_logistic_predictions.jsonl`
- `expanded_logistic_summary.json`
- `controlled_supervision_expansion_run_summary.json`

The current expansion result is still intentionally modest and honest. It does not create a more natural label source. What it does prove is that the supervised fusion path can be expanded from `2` aligned base samples / `4` labeled rows to `5` aligned base samples / `10` labeled rows on the same local slice, and the supervised logistic path still runs end to end on that larger covered set.

## More Natural Label Bootstrap Decision

The repository now includes a post-expansion decision layer that asks whether controlled supervision should keep growing, or whether the next marginal gain should come from a more natural label source.

Required inputs:

- `outputs/labeled_fusion_analysis/default/labeled_fusion_next_step_recommendation.json`
- `outputs/controlled_supervision_expansion/default/expanded_labeled_summary.json`
- `outputs/controlled_supervision_expansion/default/expanded_logistic_summary.json`
- `outputs/labeled_real_pilot_fusion/default/labeled_real_pilot_fusion_summary.json`
- `outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_readiness_summary.json`

Build the route-A-vs-route-B analysis:

```bash
.venv/bin/python scripts/build_more_natural_label_analysis.py \
  --output-dir outputs/more_natural_label_analysis/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_more_natural_label_analysis.py \
  --run-dir outputs/more_natural_label_analysis/default \
  --compare-run-dir outputs/more_natural_label_analysis/default_repeat \
  --output-dir outputs/more_natural_label_analysis/repeatability_default
```

Main outputs:

- `controlled_supervision_scaling_summary.json`
- `route_A_vs_route_B_comparison.json`
- `supervision_ceiling_summary.json`
- `route_decision_inputs.csv`
- `more_natural_label_next_step_recommendation.json`

The current recommendation is now route B. The reason is that route A has effectively hit the current 5-row local-slice ceiling, while a low-cost more-natural label candidate already exists via `answerKey + observed pilot outputs`.

## More Natural Label Bootstrap

The repository now includes a first more-natural-label bootstrap path. It does not claim benchmark supervision. Instead, it builds a sample-level proxy label from local task answer truth and observed multi-modal pilot outputs, then runs a minimal supervised logistic bootstrap on that dataset.

Required inputs:

- `outputs/controlled_supervision_expansion/default/expanded_real_pilot_fusion/fusion_dataset.jsonl`
- `outputs/controlled_supervision_expansion/default/expanded_reasoning/reasoning_probe/raw_results.jsonl`
- `outputs/controlled_supervision_expansion/default/expanded_confidence/confidence_probe/raw_results.jsonl`
- `outputs/controlled_supervision_expansion/default/expanded_illumination/illumination_probe/raw_results.jsonl`
- `outputs/pilot_materialization/pilot_csqa_reasoning_local/csqa_reasoning_pilot_slice.jsonl`

Run the more-natural-label bootstrap:

```bash
.venv/bin/python scripts/build_more_natural_label_bootstrap.py \
  --output-dir outputs/more_natural_label_bootstrap/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_more_natural_label_bootstrap.py \
  --run-dir outputs/more_natural_label_bootstrap/default \
  --compare-run-dir outputs/more_natural_label_bootstrap/default_repeat \
  --output-dir outputs/more_natural_label_bootstrap/repeatability_default
```

Main outputs:

- `more_natural_label_selection.json`
- `more_natural_label_definition.json`
- `more_natural_label_readiness_summary.json`
- `more_natural_labeled_dataset.jsonl`
- `more_natural_label_summary.json`
- `more_natural_supervised_readiness_summary.json`
- `more_natural_logistic_predictions.jsonl`
- `more_natural_logistic_summary.json`

This path is deliberately honest about its status. The label is more natural than `controlled_targeted_icl_label` because it is grounded in task correctness, but it is still only a pilot-level proxy on the same tiny local slice and lightweight model.

## Supervision Route Comparison

The repository now includes a unified comparison layer across three supervision directions:

- route A: controlled supervision coverage expansion
- route B: more-natural proxy supervision
- route C: benchmark-truth-leaning label bootstrap

Required inputs:

- `outputs/controlled_supervision_expansion/default/expanded_labeled_summary.json`
- `outputs/more_natural_label_bootstrap/default/more_natural_label_summary.json`
- `outputs/labeled_real_pilot_fusion/default/labeled_real_pilot_fusion_summary.json`
- `outputs/real_pilot_fusion_readiness/default/real_pilot_fusion_readiness_summary.json`

Build the comparison:

```bash
.venv/bin/python scripts/build_supervision_route_comparison.py \
  --output-dir outputs/supervision_route_comparison/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_supervision_route_comparison.py \
  --run-dir outputs/supervision_route_comparison/default \
  --compare-run-dir outputs/supervision_route_comparison/default_repeat \
  --output-dir outputs/supervision_route_comparison/repeatability_default
```

Main outputs:

- `supervision_route_comparison_summary.json`
- `route_A_vs_B_vs_C_comparison.json`
- `supervision_tradeoff_matrix.csv`
- `supervision_ceiling_and_cost_summary.json`
- `supervision_next_step_recommendation.json`

The current recommendation is route C. The reason is that route A has already hit the current slice ceiling, route B has already covered the current 5 aligned base samples, and route C already has a low-cost 10-row candidate based on direct contract-level answer correctness.

## Benchmark Truth Leaning Label Bootstrap

The repository now includes a first benchmark-truth-leaning supervision bootstrap. It does not claim benchmark ground truth. Instead, it uses contract-level query answer correctness on already-executed labeled illumination rows, then projects base-sample reasoning and confidence features back onto those contract rows.

Required inputs:

- `outputs/controlled_supervision_expansion/default/expanded_real_pilot_fusion/fusion_dataset.jsonl`
- `outputs/labeled_pilot_runs/default/illumination_probe/raw_results.jsonl`

Run the bootstrap:

```bash
.venv/bin/python scripts/build_benchmark_truth_leaning_label_bootstrap.py \
  --output-dir outputs/benchmark_truth_leaning_label_bootstrap/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_benchmark_truth_leaning_label_bootstrap.py \
  --run-dir outputs/benchmark_truth_leaning_label_bootstrap/default \
  --compare-run-dir outputs/benchmark_truth_leaning_label_bootstrap/default_repeat \
  --output-dir outputs/benchmark_truth_leaning_label_bootstrap/repeatability_default
```

Main outputs:

- `benchmark_truth_leaning_label_selection.json`
- `benchmark_truth_leaning_label_definition.json`
- `benchmark_truth_leaning_readiness_summary.json`
- `benchmark_truth_leaning_dataset.jsonl`
- `benchmark_truth_leaning_summary.json`
- `benchmark_truth_leaning_logistic_predictions.jsonl`
- `benchmark_truth_leaning_logistic_summary.json`

This route is intentionally framed as `benchmark_truth_leaning_supervision_proxy`. It is more truth-anchored than the current controlled or sample-level proxy labels, but it is still limited to the same tiny local slice and still reuses reasoning / confidence base features at the contract level.

## Route B vs C vs D Comparison

The repository now includes a second-stage supervision decision layer that compares:

- route B: more-natural supervision proxy
- route C: benchmark-truth-leaning supervision proxy
- route D: expand the shared labeled slice first

Required inputs:

- `outputs/more_natural_label_bootstrap/default/more_natural_label_summary.json`
- `outputs/benchmark_truth_leaning_label_bootstrap/default/benchmark_truth_leaning_summary.json`
- `outputs/controlled_supervision_expansion/default/expanded_labeled_summary.json`
- `outputs/pilot_materialization/pilot_csqa_reasoning_local/csqa_reasoning_pilot_slice.jsonl`

Build the comparison:

```bash
.venv/bin/python scripts/build_route_b_vs_c_analysis.py \
  --output-dir outputs/route_b_vs_c_analysis/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_route_b_vs_c_analysis.py \
  --run-dir outputs/route_b_vs_c_analysis/default \
  --compare-run-dir outputs/route_b_vs_c_analysis/default_repeat \
  --output-dir outputs/route_b_vs_c_analysis/repeatability_default
```

Main outputs:

- `route_b_vs_c_gain_summary.json`
- `route_b_vs_c_vs_d_comparison.json`
- `supervision_route_gain_matrix.csv`
- `supervision_realism_cost_summary.json`
- `route_b_vs_c_next_step_recommendation.json`

The current recommendation is route D. The reason is that route B and route C now both visibly share the same upstream bottleneck: the local labeled slice is too small, so expanding that shared substrate has the highest next-step leverage.

## Labeled Slice Expansion Bootstrap

The repository now includes a minimal route-D bootstrap that expands the shared local labeled slice from `5` rows to `10` rows, then emits reusable bridge contracts for later route-B and route-C reruns.

Required inputs:

- `outputs/pilot_materialization/pilot_csqa_reasoning_local/csqa_reasoning_pilot_slice.jsonl`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run the bootstrap:

```bash
.venv/bin/python scripts/build_labeled_slice_expansion.py \
  --output-dir outputs/labeled_slice_expansion/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_labeled_slice_expansion.py \
  --run-dir outputs/labeled_slice_expansion/default \
  --compare-run-dir outputs/labeled_slice_expansion/default_repeat \
  --output-dir outputs/labeled_slice_expansion/repeatability_default
```

Main outputs:

- `labeled_slice_expansion_plan.json`
- `labeled_slice_expansion_readiness_summary.json`
- `expanded_labeled_slice.jsonl`
- `expanded_labeled_slice_summary.json`
- `bridge_artifact_summary.json`
- `materialized_labeled_slice_inputs/csqa_reasoning_pilot_slice.jsonl`
- `materialized_labeled_slice_inputs/reasoning_query_contracts.jsonl`
- `materialized_labeled_slice_inputs/confidence_query_contracts.jsonl`
- `materialized_labeled_slice_inputs/illumination_query_contracts.jsonl`
- `materialized_labeled_slice_inputs/labeled_illumination_query_contracts.jsonl`

This route is intentionally honest about its status. It does not introduce benchmark ground truth. Instead, it creates a larger local pilot substrate plus bridge dry-run artifacts, so that later route-B and route-C expansions can run on something bigger than the original 5-row slice.

## Expanded Route C Bootstrap

The repository now includes a true rerun of route C on top of the expanded 10-row substrate produced by 028.

Required inputs:

- `outputs/labeled_slice_expansion/default/materialized_labeled_slice_inputs/`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run the bootstrap:

```bash
.venv/bin/python scripts/build_expanded_route_c_bootstrap.py \
  --output-dir outputs/expanded_route_c_bootstrap/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_expanded_route_c_bootstrap.py \
  --run-dir outputs/expanded_route_c_bootstrap/default \
  --compare-run-dir outputs/expanded_route_c_bootstrap/default_repeat \
  --output-dir outputs/expanded_route_c_bootstrap/repeatability_default
```

Main outputs:

- `expanded_route_c_selection.json`
- `expanded_route_c_label_definition.json`
- `expanded_route_c_readiness_summary.json`
- `expanded_benchmark_truth_leaning_dataset.jsonl`
- `expanded_benchmark_truth_leaning_summary.json`
- `expanded_benchmark_truth_leaning_logistic_predictions.jsonl`
- `expanded_benchmark_truth_leaning_logistic_summary.json`
- `expanded_benchmark_truth_leaning_model_metadata.json`
- `expanded_route_c_run_summary.json`

This route is still intentionally framed as `benchmark_truth_leaning_supervision_proxy`. The gain is that route C now reruns on a 10-base-sample substrate and produces 20 contract-level supervised rows, but it is still not benchmark ground truth and still uses a lightweight pilot model.

## Expanded Supervision Comparison

The repository now includes a comparison layer across:

- route B
- old route C
- expanded route C

Build the comparison:

```bash
.venv/bin/python scripts/build_expanded_supervision_comparison.py \
  --output-dir outputs/expanded_supervision_comparison/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_expanded_supervision_comparison.py \
  --run-dir outputs/expanded_supervision_comparison/default \
  --compare-run-dir outputs/expanded_supervision_comparison/default_repeat \
  --output-dir outputs/expanded_supervision_comparison/repeatability_default
```

Main outputs:

- `expanded_supervision_comparison_summary.json`
- `route_b_oldc_expandedc_comparison.csv`
- `supervision_progression_summary.json`
- `expanded_supervision_next_step_recommendation.json`

The current recommendation after expanded route C is to prepare a larger labeled split. The reason is that expanded route C now clearly dominates old route C and current route B on the present substrate, so the next bottleneck is the size of the substrate itself.

## Larger Labeled Split Bootstrap

The repository now includes a larger labeled split bootstrap that lifts the shared substrate from `10` rows to `20` rows while keeping the existing route B / route C / fusion builders compatible.

Required inputs:

- `outputs/labeled_slice_expansion/default/materialized_labeled_slice_inputs/`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run the bootstrap:

```bash
.venv/bin/python scripts/build_larger_labeled_split_bootstrap.py \
  --output-dir outputs/larger_labeled_split_bootstrap/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_larger_labeled_split_bootstrap.py \
  --run-dir outputs/larger_labeled_split_bootstrap/default \
  --compare-run-dir outputs/larger_labeled_split_bootstrap/default_repeat \
  --output-dir outputs/larger_labeled_split_bootstrap/repeatability_default
```

Main outputs:

- `larger_labeled_split_plan.json`
- `larger_labeled_split_definition.json`
- `larger_labeled_split_readiness_summary.json`
- `larger_labeled_split.jsonl`
- `larger_labeled_split_summary.json`
- `larger_labeled_bridge_artifact_summary.json`
- `larger_split_route_compatibility_summary.json`

This split is still intentionally honest about its status. It is larger than the current 10-row substrate and compatible with route B / route C / fusion, but it is still a local curated split rather than benchmark-scale data.

## Larger Split Route Rerun Decision

The repository now includes a decision layer that determines whether the larger split should rerun route B or route C first.

Build the decision:

```bash
.venv/bin/python scripts/build_larger_split_route_rerun_decision.py \
  --output-dir outputs/larger_split_route_rerun_decision/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_larger_split_route_rerun_decision.py \
  --run-dir outputs/larger_split_route_rerun_decision/default \
  --compare-run-dir outputs/larger_split_route_rerun_decision/default_repeat \
  --output-dir outputs/larger_split_route_rerun_decision/repeatability_default
```

Main outputs:

- `larger_split_route_rerun_comparison.json`
- `larger_split_route_rerun_tradeoff_matrix.csv`
- `larger_split_route_next_step_recommendation.json`

The current recommendation is to rerun route B first on the larger split. The reason is that route C already has an expanded rerun artifact, while route B still lacks a symmetric rerun on a larger shared substrate and therefore offers higher next-step comparative information gain.

## Chosen Route Rerun On Larger Split

The repository now includes the first real rerun of the chosen route on the larger labeled split. In the current state, the chosen route is route B, so the system reruns the more-natural supervision proxy on the `20`-row shared substrate and emits a new supervised bootstrap artifact.

Required inputs:

- `outputs/larger_labeled_split_bootstrap/default/materialized_larger_labeled_inputs/`
- `outputs/larger_split_route_rerun_decision/default/larger_split_route_next_step_recommendation.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run the chosen-route rerun:

```bash
.venv/bin/python scripts/build_chosen_route_rerun_on_larger_split.py \
  --output-dir outputs/chosen_route_rerun_on_larger_split/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_chosen_route_rerun_on_larger_split.py \
  --run-dir outputs/chosen_route_rerun_on_larger_split/default \
  --compare-run-dir outputs/chosen_route_rerun_on_larger_split/default_repeat \
  --output-dir outputs/chosen_route_rerun_on_larger_split/repeatability_default
```

Main outputs:

- `chosen_route_rerun_plan.json`
- `chosen_route_rerun_readiness_summary.json`
- `expanded_more_natural_dataset.jsonl`
- `expanded_more_natural_summary.json`
- `expanded_more_natural_logistic_predictions.jsonl`
- `expanded_more_natural_logistic_summary.json`
- `chosen_route_rerun_run_summary.json`

The current rerun proves that route B can now run on the larger shared substrate, but it is still a pilot-level more-natural supervision proxy rather than benchmark ground truth.

## Post Rerun Comparison

The repository now includes a post-rerun comparison layer that puts old route B, expanded route C, and the new larger-split route B into one comparison summary.

Build the post-rerun comparison:

```bash
.venv/bin/python scripts/build_post_rerun_comparison.py \
  --output-dir outputs/post_rerun_comparison/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_rerun_comparison.py \
  --run-dir outputs/post_rerun_comparison/default \
  --compare-run-dir outputs/post_rerun_comparison/default_repeat \
  --output-dir outputs/post_rerun_comparison/repeatability_default
```

Main outputs:

- `post_rerun_comparison_summary.json`
- `route_progression_after_rerun.csv`
- `post_rerun_next_step_recommendation.json`

The current recommendation after rerunning route B is to rerun route C on the same larger split next, so the repository can compare route B and route C under a truly shared `20`-row substrate.

## Larger-Split Route C Rerun

The repository now includes the symmetric rerun of route C on the same `20`-row larger labeled split. This closes the main asymmetry between route B and route C under the current shared substrate and emits a larger-split benchmark-truth-leaning proxy supervision artifact.

Required inputs:

- `outputs/larger_labeled_split_bootstrap/default/materialized_larger_labeled_inputs/`
- `outputs/post_rerun_comparison/default/post_rerun_next_step_recommendation.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run the larger-split route C rerun:

```bash
.venv/bin/python scripts/build_rerun_route_c_on_larger_split.py \
  --output-dir outputs/rerun_route_c_on_larger_split/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_c_on_larger_split.py \
  --run-dir outputs/rerun_route_c_on_larger_split/default \
  --compare-run-dir outputs/rerun_route_c_on_larger_split/default_repeat \
  --output-dir outputs/rerun_route_c_on_larger_split/repeatability_default
```

Main outputs:

- `larger_split_route_c_plan.json`
- `larger_split_route_c_label_definition.json`
- `larger_split_route_c_readiness_summary.json`
- `larger_split_route_c_dataset.jsonl`
- `larger_split_route_c_summary.json`
- `larger_split_route_c_logistic_predictions.jsonl`
- `larger_split_route_c_logistic_summary.json`
- `larger_split_route_c_model_metadata.json`
- `larger_split_route_c_run_summary.json`

The current larger-split route C artifact contains `40` contract-level rows across `20` base samples. It is more substrate-complete than the earlier route C run, but it is still a benchmark-truth-leaning proxy rather than benchmark ground truth.

## Symmetric Larger-Split Comparison

The repository now includes a true larger-split comparison layer that puts old route B, larger-split route B, and larger-split route C into one symmetric summary.

Build the symmetric comparison:

```bash
.venv/bin/python scripts/build_symmetric_larger_split_comparison.py \
  --output-dir outputs/symmetric_larger_split_comparison/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_symmetric_larger_split_comparison.py \
  --run-dir outputs/symmetric_larger_split_comparison/default \
  --compare-run-dir outputs/symmetric_larger_split_comparison/default_repeat \
  --output-dir outputs/symmetric_larger_split_comparison/repeatability_default
```

Main outputs:

- `symmetric_larger_split_comparison_summary.json`
- `route_b_larger_vs_route_c_larger_comparison.csv`
- `supervision_progression_after_symmetric_rerun.json`
- `symmetric_rerun_tradeoff_matrix.csv`
- `symmetric_rerun_next_step_recommendation.json`

The current symmetric recommendation is to prepare `larger_labeled_split_v2`. The reason is that route B and route C have now both been exercised on the same `20`-row substrate, so the next shared bottleneck is the substrate ceiling itself rather than another missing rerun.

## Post-Symmetric Next Step Bootstrap

The repository now includes a bootstrap layer for the next step after symmetric larger-split reruns. In the current state, that next step is `larger_labeled_split_v2`.

Required inputs:

- `outputs/larger_labeled_split_bootstrap/default/larger_labeled_split.jsonl`
- `outputs/symmetric_larger_split_comparison/default/symmetric_rerun_next_step_recommendation.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run the bootstrap:

```bash
.venv/bin/python scripts/build_post_symmetric_next_step_bootstrap.py \
  --output-dir outputs/post_symmetric_next_step_bootstrap/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_symmetric_next_step_bootstrap.py \
  --run-dir outputs/post_symmetric_next_step_bootstrap/default \
  --compare-run-dir outputs/post_symmetric_next_step_bootstrap/default_repeat \
  --output-dir outputs/post_symmetric_next_step_bootstrap/repeatability_default
```

Main outputs:

- `post_symmetric_next_step_plan.json`
- `post_symmetric_next_step_readiness_summary.json`
- `larger_labeled_split_v2.jsonl`
- `larger_labeled_split_v2_summary.json`
- `post_symmetric_next_step_bridge_summary.json`

The current bootstrap lifts the shared labeled substrate from `20` rows to `30` rows and proves, via dry-run bridge checks, that route B, route C, and the stable fusion builders can still attach cleanly. This is still a local curated split bootstrap, not a benchmark-scale experiment.

## Route C On Labeled Split V2

The repository now includes the first real rerun of route C on `larger_labeled_split_v2`. This extends the benchmark-truth-leaning supervision proxy from the `20`-row larger split to the `30`-row v2 shared substrate.

Required inputs:

- `outputs/post_symmetric_next_step_bootstrap/default/materialized_post_symmetric_inputs/`
- `outputs/post_symmetric_next_step_bootstrap/default/post_symmetric_next_step_plan.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run route C on v2:

```bash
.venv/bin/python scripts/build_rerun_route_c_on_labeled_split_v2.py \
  --output-dir outputs/rerun_route_c_on_labeled_split_v2/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_c_on_labeled_split_v2.py \
  --run-dir outputs/rerun_route_c_on_labeled_split_v2/default \
  --compare-run-dir outputs/rerun_route_c_on_labeled_split_v2/default_repeat \
  --output-dir outputs/rerun_route_c_on_labeled_split_v2/repeatability_default
```

Main outputs:

- `route_c_v2_plan.json`
- `route_c_v2_label_definition.json`
- `route_c_v2_readiness_summary.json`
- `route_c_v2_dataset.jsonl`
- `route_c_v2_summary.json`
- `route_c_v2_logistic_predictions.jsonl`
- `route_c_v2_logistic_summary.json`
- `route_c_v2_model_metadata.json`
- `route_c_v2_run_summary.json`

The current route C v2 artifact contains `60` contract-level rows across `30` base samples. It is still benchmark-truth-leaning proxy supervision rather than benchmark ground truth.

## Route B On Labeled Split V2

The repository now includes the first real rerun of route B on `larger_labeled_split_v2`. This makes route B and route C simultaneously available on the same `30`-row shared substrate.

Required inputs:

- `outputs/post_symmetric_next_step_bootstrap/default/materialized_post_symmetric_inputs/`
- `outputs/rerun_route_c_on_labeled_split_v2/default/route_c_v2_run_summary.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run route B on v2:

```bash
.venv/bin/python scripts/build_rerun_route_b_on_labeled_split_v2.py \
  --output-dir outputs/rerun_route_b_on_labeled_split_v2/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_b_on_labeled_split_v2.py \
  --run-dir outputs/rerun_route_b_on_labeled_split_v2/default \
  --compare-run-dir outputs/rerun_route_b_on_labeled_split_v2/default_repeat \
  --output-dir outputs/rerun_route_b_on_labeled_split_v2/repeatability_default
```

Main outputs:

- `route_b_v2_plan.json`
- `route_b_v2_label_definition.json`
- `route_b_v2_readiness_summary.json`
- `route_b_v2_dataset.jsonl`
- `route_b_v2_summary.json`
- `route_b_v2_logistic_predictions.jsonl`
- `route_b_v2_logistic_summary.json`
- `route_b_v2_model_metadata.json`
- `route_b_v2_run_summary.json`

The current route B v2 artifact contains `30` sample-level rows across `30` base samples. It remains a more-natural supervision proxy rather than benchmark ground truth.

## Post V2 Symmetric Comparison

The repository now includes a real v2 comparison layer that puts `old B / larger B / B-v2 / expanded C / larger C / C-v2` into one progression summary.

Build the v2 symmetric comparison:

```bash
.venv/bin/python scripts/build_post_v2_symmetric_comparison.py \
  --output-dir outputs/post_v2_symmetric_comparison/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_v2_symmetric_comparison.py \
  --run-dir outputs/post_v2_symmetric_comparison/default \
  --compare-run-dir outputs/post_v2_symmetric_comparison/default_repeat \
  --output-dir outputs/post_v2_symmetric_comparison/repeatability_default
```

Main outputs:

- `v2_symmetric_comparison_summary.json`
- `route_b_v2_vs_route_c_v2_comparison.csv`
- `supervision_progression_after_v2_rerun.json`
- `v2_tradeoff_matrix.csv`
- `v2_symmetric_next_step_recommendation.json`

The current v2 recommendation is to prepare `larger_labeled_split_v3`. The reason is that route B and route C now both exist on the same `30`-row shared substrate, so the next dominant bottleneck is again the shared labeled substrate size.

## Post V2 Next Step Bootstrap

The repository now includes a bootstrap layer for the next step after v2 symmetric reruns. In the current state, that next step is `larger_labeled_split_v3`.

Required inputs:

- `outputs/post_symmetric_next_step_bootstrap/default/materialized_post_symmetric_inputs/`
- `outputs/post_v2_symmetric_comparison/default/v2_symmetric_next_step_recommendation.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run the bootstrap:

```bash
.venv/bin/python scripts/build_post_v2_next_step_bootstrap.py \
  --output-dir outputs/post_v2_next_step_bootstrap/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_v2_next_step_bootstrap.py \
  --run-dir outputs/post_v2_next_step_bootstrap/default \
  --compare-run-dir outputs/post_v2_next_step_bootstrap/default_repeat \
  --output-dir outputs/post_v2_next_step_bootstrap/repeatability_default
```

Main outputs:

- `post_v2_next_step_plan.json`
- `post_v2_next_step_readiness_summary.json`
- `larger_labeled_split_v3.jsonl`
- `larger_labeled_split_v3_summary.json`
- `post_v2_next_step_bridge_summary.json`

The current bootstrap lifts the shared labeled substrate from `30` rows to `40` rows and proves, via dry-run bridge checks, that route B, route C, and the stable fusion builders can still attach cleanly. This is still a local curated split bootstrap, not a benchmark-scale experiment.

## Route C On Labeled Split V3

The repository now includes the first real rerun of route C on `larger_labeled_split_v3`. This extends the benchmark-truth-leaning proxy path from the `30`-row v2 substrate to the `40`-row v3 substrate.

Required inputs:

- `outputs/post_v2_next_step_bootstrap/default/materialized_post_v2_inputs/`
- `outputs/post_v2_next_step_bootstrap/default/post_v2_next_step_plan.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run route C on v3:

```bash
.venv/bin/python scripts/build_rerun_route_c_on_labeled_split_v3.py \
  --output-dir outputs/rerun_route_c_on_labeled_split_v3/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_c_on_labeled_split_v3.py \
  --run-dir outputs/rerun_route_c_on_labeled_split_v3/default \
  --compare-run-dir outputs/rerun_route_c_on_labeled_split_v3/default_repeat \
  --output-dir outputs/rerun_route_c_on_labeled_split_v3/repeatability_default
```

Main outputs:

- `route_c_v3_plan.json`
- `route_c_v3_label_definition.json`
- `route_c_v3_readiness_summary.json`
- `route_c_v3_dataset.jsonl`
- `route_c_v3_summary.json`
- `route_c_v3_logistic_predictions.jsonl`
- `route_c_v3_logistic_summary.json`
- `route_c_v3_model_metadata.json`
- `route_c_v3_run_summary.json`

The current route C v3 artifact contains `80` contract-level rows across `40` base samples. It remains a benchmark-truth-leaning proxy rather than benchmark ground truth.

## Route B On Labeled Split V3

The repository now includes the first real rerun of route B on `larger_labeled_split_v3`. This makes route B and route C simultaneously available on the same `40`-row shared substrate.

Required inputs:

- `outputs/post_v2_next_step_bootstrap/default/materialized_post_v2_inputs/`
- `outputs/rerun_route_c_on_labeled_split_v3/default/route_c_v3_run_summary.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run route B on v3:

```bash
.venv/bin/python scripts/build_rerun_route_b_on_labeled_split_v3.py \
  --output-dir outputs/rerun_route_b_on_labeled_split_v3/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_b_on_labeled_split_v3.py \
  --run-dir outputs/rerun_route_b_on_labeled_split_v3/default \
  --compare-run-dir outputs/rerun_route_b_on_labeled_split_v3/default_repeat \
  --output-dir outputs/rerun_route_b_on_labeled_split_v3/repeatability_default
```

Main outputs:

- `route_b_v3_plan.json`
- `route_b_v3_label_definition.json`
- `route_b_v3_readiness_summary.json`
- `route_b_v3_dataset.jsonl`
- `route_b_v3_summary.json`
- `route_b_v3_logistic_predictions.jsonl`
- `route_b_v3_logistic_summary.json`
- `route_b_v3_model_metadata.json`
- `route_b_v3_run_summary.json`

The current route B v3 artifact contains `40` sample-level rows across `40` base samples. It remains a more-natural supervision proxy rather than benchmark ground truth.

## Post V3 Symmetric Comparison

The repository now includes a real v3 comparison layer that puts `old B / larger B / B-v2 / B-v3 / expanded C / larger C / C-v2 / C-v3` into one progression summary.

Build the v3 symmetric comparison:

```bash
.venv/bin/python scripts/build_post_v3_symmetric_comparison.py \
  --output-dir outputs/post_v3_symmetric_comparison/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_v3_symmetric_comparison.py \
  --run-dir outputs/post_v3_symmetric_comparison/default \
  --compare-run-dir outputs/post_v3_symmetric_comparison/default_repeat \
  --output-dir outputs/post_v3_symmetric_comparison/repeatability_default
```

Main outputs:

- `v3_symmetric_comparison_summary.json`
- `route_b_v3_vs_route_c_v3_comparison.csv`
- `supervision_progression_after_v3_rerun.json`
- `v3_tradeoff_matrix.csv`
- `v3_symmetric_next_step_recommendation.json`

The current v3 recommendation is to prepare `larger_labeled_split_v4`. The reason is that route B and route C now both exist on the same `40`-row shared substrate, so the next dominant bottleneck is again the shared labeled substrate size.

## Post V3 Next Step Bootstrap

The repository now includes a bootstrap layer for the next step after v3 symmetric reruns. In the current state, that next step is `larger_labeled_split_v4`.

Required inputs:

- `outputs/post_v2_next_step_bootstrap/default/materialized_post_v2_inputs/`
- `outputs/post_v3_symmetric_comparison/default/v3_symmetric_next_step_recommendation.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run the bootstrap:

```bash
.venv/bin/python scripts/build_post_v3_next_step_bootstrap.py \
  --output-dir outputs/post_v3_next_step_bootstrap/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_v3_next_step_bootstrap.py \
  --run-dir outputs/post_v3_next_step_bootstrap/default \
  --compare-run-dir outputs/post_v3_next_step_bootstrap/default_repeat \
  --output-dir outputs/post_v3_next_step_bootstrap/repeatability_default
```

Main outputs:

- `post_v3_next_step_plan.json`
- `post_v3_next_step_readiness_summary.json`
- `larger_labeled_split_v4.jsonl`
- `larger_labeled_split_v4_summary.json`
- `post_v3_next_step_bridge_summary.json`

The current bootstrap lifts the shared labeled substrate from `40` rows to `50` rows and proves, via dry-run bridge checks, that route B, route C, and the stable fusion builders can still attach cleanly. This is still a local curated split bootstrap, not a benchmark-scale experiment.

## Route C On Labeled Split V4

The repository now includes the first real rerun of route C on `larger_labeled_split_v4`. This extends route C from the `40`-row v3 substrate to a `50`-row v4 substrate while preserving the benchmark-truth-leaning proxy label contract.

Required inputs:

- `outputs/post_v3_next_step_bootstrap/default/materialized_post_v3_inputs/`
- `outputs/post_v3_next_step_bootstrap/default/post_v3_next_step_plan.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run route C on v4:

```bash
.venv/bin/python scripts/build_rerun_route_c_on_labeled_split_v4.py \
  --output-dir outputs/rerun_route_c_on_labeled_split_v4/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_c_on_labeled_split_v4.py \
  --run-dir outputs/rerun_route_c_on_labeled_split_v4/default \
  --compare-run-dir outputs/rerun_route_c_on_labeled_split_v4/default_repeat \
  --output-dir outputs/rerun_route_c_on_labeled_split_v4/repeatability_default
```

Main outputs:

- `route_c_v4_plan.json`
- `route_c_v4_label_definition.json`
- `route_c_v4_readiness_summary.json`
- `route_c_v4_dataset.jsonl`
- `route_c_v4_summary.json`
- `route_c_v4_logistic_predictions.jsonl`
- `route_c_v4_logistic_summary.json`
- `route_c_v4_model_metadata.json`
- `route_c_v4_run_summary.json`

The current route C v4 artifact contains `100` contract-level rows across `50` base samples. It remains a benchmark-truth-leaning supervision proxy rather than benchmark ground truth.

## Route B On Labeled Split V4

The repository now includes the first real rerun of route B on `larger_labeled_split_v4`. This makes route B and route C simultaneously available on the same `50`-row shared substrate.

Required inputs:

- `outputs/post_v3_next_step_bootstrap/default/materialized_post_v3_inputs/`
- `outputs/rerun_route_c_on_labeled_split_v4/default/route_c_v4_run_summary.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run route B on v4:

```bash
.venv/bin/python scripts/build_rerun_route_b_on_labeled_split_v4.py \
  --output-dir outputs/rerun_route_b_on_labeled_split_v4/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_b_on_labeled_split_v4.py \
  --run-dir outputs/rerun_route_b_on_labeled_split_v4/default \
  --compare-run-dir outputs/rerun_route_b_on_labeled_split_v4/default_repeat \
  --output-dir outputs/rerun_route_b_on_labeled_split_v4/repeatability_default
```

Main outputs:

- `route_b_v4_plan.json`
- `route_b_v4_label_definition.json`
- `route_b_v4_readiness_summary.json`
- `route_b_v4_dataset.jsonl`
- `route_b_v4_summary.json`
- `route_b_v4_logistic_predictions.jsonl`
- `route_b_v4_logistic_summary.json`
- `route_b_v4_model_metadata.json`
- `route_b_v4_run_summary.json`

The current route B v4 artifact contains `50` sample-level rows across `50` base samples. It remains a more-natural supervision proxy rather than benchmark ground truth.

## Post V4 Symmetric Comparison

The repository now includes a real v4 comparison layer that puts `old B / larger B / B-v2 / B-v3 / B-v4 / old C / larger C / C-v2 / C-v3 / C-v4` into one progression summary.

Build the v4 symmetric comparison:

```bash
.venv/bin/python scripts/build_post_v4_symmetric_comparison.py \
  --output-dir outputs/post_v4_symmetric_comparison/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_v4_symmetric_comparison.py \
  --run-dir outputs/post_v4_symmetric_comparison/default \
  --compare-run-dir outputs/post_v4_symmetric_comparison/default_repeat \
  --output-dir outputs/post_v4_symmetric_comparison/repeatability_default
```

Main outputs:

- `v4_symmetric_comparison_summary.json`
- `route_b_v4_vs_route_c_v4_comparison.csv`
- `supervision_progression_after_v4_rerun.json`
- `v4_tradeoff_matrix.csv`
- `v4_symmetric_next_step_recommendation.json`

The current v4 recommendation is to prepare `larger_labeled_split_v5`. The reason is that route B and route C now both exist on the same `50`-row shared substrate, so the next dominant bottleneck is again the shared labeled substrate size.

## Post V4 Next Step Bootstrap

The repository now includes a bootstrap layer for the next step after v4 symmetric reruns. In the current state, that next step is `larger_labeled_split_v5`.

Required inputs:

- `outputs/post_v3_next_step_bootstrap/default/materialized_post_v3_inputs/`
- `outputs/post_v4_symmetric_comparison/default/v4_symmetric_next_step_recommendation.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run the bootstrap:

```bash
.venv/bin/python scripts/build_post_v4_next_step_bootstrap.py \
  --output-dir outputs/post_v4_next_step_bootstrap/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_v4_next_step_bootstrap.py \
  --run-dir outputs/post_v4_next_step_bootstrap/default \
  --compare-run-dir outputs/post_v4_next_step_bootstrap/default_repeat \
  --output-dir outputs/post_v4_next_step_bootstrap/repeatability_default
```

Main outputs:

- `post_v4_next_step_plan.json`
- `post_v4_next_step_readiness_summary.json`
- `larger_labeled_split_v5.jsonl`
- `larger_labeled_split_v5_summary.json`
- `post_v4_next_step_bridge_summary.json`

The current bootstrap lifts the shared labeled substrate from `50` rows to `60` rows and proves, via dry-run bridge checks, that route B, route C, and the stable fusion builders can still attach cleanly. This is still a local curated split bootstrap, not a benchmark-scale experiment.

## Route C On Labeled Split V5

The repository now includes the first real rerun of route C on `larger_labeled_split_v5`. This extends route C from the `50`-row v4 substrate to a `60`-row v5 substrate while preserving the benchmark-truth-leaning proxy label contract.

Required inputs:

- `outputs/post_v4_next_step_bootstrap/default/materialized_post_v4_inputs/`
- `outputs/post_v4_next_step_bootstrap/default/post_v4_next_step_plan.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run route C on v5:

```bash
.venv/bin/python scripts/build_rerun_route_c_on_labeled_split_v5.py \
  --output-dir outputs/rerun_route_c_on_labeled_split_v5/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_c_on_labeled_split_v5.py \
  --run-dir outputs/rerun_route_c_on_labeled_split_v5/default \
  --compare-run-dir outputs/rerun_route_c_on_labeled_split_v5/default_repeat \
  --output-dir outputs/rerun_route_c_on_labeled_split_v5/repeatability_default
```

Main outputs:

- `route_c_v5_plan.json`
- `route_c_v5_label_definition.json`
- `route_c_v5_readiness_summary.json`
- `route_c_v5_dataset.jsonl`
- `route_c_v5_summary.json`
- `route_c_v5_logistic_predictions.jsonl`
- `route_c_v5_logistic_summary.json`
- `route_c_v5_model_metadata.json`
- `route_c_v5_run_summary.json`

The current route C v5 artifact contains `120` contract-level rows across `60` base samples. It remains a benchmark-truth-leaning supervision proxy rather than benchmark ground truth.

## Route B On Labeled Split V5

The repository now includes the first real rerun of route B on `larger_labeled_split_v5`. This makes route B and route C simultaneously available on the same `60`-row shared substrate.

Required inputs:

- `outputs/post_v4_next_step_bootstrap/default/materialized_post_v4_inputs/`
- `outputs/rerun_route_c_on_labeled_split_v5/default/route_c_v5_run_summary.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run route B on v5:

```bash
.venv/bin/python scripts/build_rerun_route_b_on_labeled_split_v5.py \
  --output-dir outputs/rerun_route_b_on_labeled_split_v5/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_b_on_labeled_split_v5.py \
  --run-dir outputs/rerun_route_b_on_labeled_split_v5/default \
  --compare-run-dir outputs/rerun_route_b_on_labeled_split_v5/default_repeat \
  --output-dir outputs/rerun_route_b_on_labeled_split_v5/repeatability_default
```

Main outputs:

- `route_b_v5_plan.json`
- `route_b_v5_label_definition.json`
- `route_b_v5_readiness_summary.json`
- `route_b_v5_dataset.jsonl`
- `route_b_v5_summary.json`
- `route_b_v5_logistic_predictions.jsonl`
- `route_b_v5_logistic_summary.json`
- `route_b_v5_model_metadata.json`
- `route_b_v5_run_summary.json`

The current route B v5 artifact contains `60` sample-level rows across `60` base samples. It remains a more-natural supervision proxy rather than benchmark ground truth.

## Post V5 Symmetric Comparison

The repository now includes a real v5 comparison layer that puts `old B / larger B / B-v2 / B-v3 / B-v4 / B-v5 / old C / larger C / C-v2 / C-v3 / C-v4 / C-v5` into one progression summary.

Build the v5 symmetric comparison:

```bash
.venv/bin/python scripts/build_post_v5_symmetric_comparison.py \
  --output-dir outputs/post_v5_symmetric_comparison/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_v5_symmetric_comparison.py \
  --run-dir outputs/post_v5_symmetric_comparison/default \
  --compare-run-dir outputs/post_v5_symmetric_comparison/default_repeat \
  --output-dir outputs/post_v5_symmetric_comparison/repeatability_default
```

Main outputs:

- `v5_symmetric_comparison_summary.json`
- `route_b_v5_vs_route_c_v5_comparison.csv`
- `supervision_progression_after_v5_rerun.json`
- `v5_tradeoff_matrix.csv`
- `v5_symmetric_next_step_recommendation.json`

The current v5 recommendation is to prepare `larger_labeled_split_v6`. The reason is that route B and route C now both exist on the same `60`-row shared substrate, so the next dominant bottleneck is again the shared labeled substrate size.

## Post V5 Next Step Bootstrap

The repository now includes a bootstrap layer for the next step after v5 symmetric reruns. In the current state, that next step is `larger_labeled_split_v6`.

Required inputs:

- `outputs/post_v4_next_step_bootstrap/default/materialized_post_v4_inputs/`
- `outputs/post_v5_symmetric_comparison/default/v5_symmetric_next_step_recommendation.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run the bootstrap:

```bash
.venv/bin/python scripts/build_post_v5_next_step_bootstrap.py \
  --output-dir outputs/post_v5_next_step_bootstrap/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_v5_next_step_bootstrap.py \
  --run-dir outputs/post_v5_next_step_bootstrap/default \
  --compare-run-dir outputs/post_v5_next_step_bootstrap/default_repeat \
  --output-dir outputs/post_v5_next_step_bootstrap/repeatability_default
```

Main outputs:

- `post_v5_next_step_plan.json`
- `post_v5_next_step_readiness_summary.json`
- `larger_labeled_split_v6.jsonl`
- `larger_labeled_split_v6_summary.json`
- `post_v5_next_step_bridge_summary.json`

The current bootstrap lifts the shared labeled substrate from `60` rows to `70` rows and proves, via dry-run bridge checks, that route B, route C, and the stable fusion builders can still attach cleanly. This is still a local curated split bootstrap, not a benchmark-scale experiment.

## Route C On Labeled Split V6

The repository now includes the first real rerun of route C on `larger_labeled_split_v6`. This extends route C from the `60`-row v5 substrate to a `70`-row v6 substrate while preserving the benchmark-truth-leaning proxy label contract.

Required inputs:

- `outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs/`
- `outputs/post_v5_next_step_bootstrap/default/post_v5_next_step_plan.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run route C on v6:

```bash
.venv/bin/python scripts/build_rerun_route_c_on_labeled_split_v6.py \
  --output-dir outputs/rerun_route_c_on_labeled_split_v6/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_c_on_labeled_split_v6.py \
  --run-dir outputs/rerun_route_c_on_labeled_split_v6/default \
  --compare-run-dir outputs/rerun_route_c_on_labeled_split_v6/default_repeat \
  --output-dir outputs/rerun_route_c_on_labeled_split_v6/repeatability_default
```

Main outputs:

- `route_c_v6_plan.json`
- `route_c_v6_label_definition.json`
- `route_c_v6_readiness_summary.json`
- `route_c_v6_dataset.jsonl`
- `route_c_v6_summary.json`
- `route_c_v6_logistic_predictions.jsonl`
- `route_c_v6_logistic_summary.json`
- `route_c_v6_model_metadata.json`
- `route_c_v6_run_summary.json`

The current route C v6 artifact contains `140` contract-level rows across `70` base samples. It remains a benchmark-truth-leaning supervision proxy rather than benchmark ground truth.

## Route B On Labeled Split V6

The repository now includes the first real rerun of route B on `larger_labeled_split_v6`. This makes route B and route C simultaneously available on the same `70`-row shared substrate.

Required inputs:

- `outputs/post_v5_next_step_bootstrap/default/materialized_post_v5_inputs/`
- `outputs/rerun_route_c_on_labeled_split_v6/default/route_c_v6_run_summary.json`
- `configs/models.yaml`
- `configs/reasoning.yaml`
- `configs/confidence.yaml`
- `configs/illumination.yaml`

Run route B on v6:

```bash
.venv/bin/python scripts/build_rerun_route_b_on_labeled_split_v6.py \
  --output-dir outputs/rerun_route_b_on_labeled_split_v6/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_rerun_route_b_on_labeled_split_v6.py \
  --run-dir outputs/rerun_route_b_on_labeled_split_v6/default \
  --compare-run-dir outputs/rerun_route_b_on_labeled_split_v6/default_repeat \
  --output-dir outputs/rerun_route_b_on_labeled_split_v6/repeatability_default
```

Main outputs:

- `route_b_v6_plan.json`
- `route_b_v6_label_definition.json`
- `route_b_v6_readiness_summary.json`
- `route_b_v6_dataset.jsonl`
- `route_b_v6_summary.json`
- `route_b_v6_logistic_predictions.jsonl`
- `route_b_v6_logistic_summary.json`
- `route_b_v6_model_metadata.json`
- `route_b_v6_run_summary.json`

The current route B v6 artifact contains `70` sample-level rows across `70` base samples. It remains a more-natural supervision proxy rather than benchmark ground truth.

## Post V6 Symmetric Comparison

The repository now includes a real v6 comparison layer that puts `old B / larger B / B-v2 / B-v3 / B-v4 / B-v5 / B-v6 / old C / larger C / C-v2 / C-v3 / C-v4 / C-v5 / C-v6` into one progression summary, and explicitly decides whether proxy substrate expansion should continue.

Build the v6 symmetric comparison:

```bash
.venv/bin/python scripts/build_post_v6_symmetric_comparison.py \
  --output-dir outputs/post_v6_symmetric_comparison/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_v6_symmetric_comparison.py \
  --run-dir outputs/post_v6_symmetric_comparison/default \
  --compare-run-dir outputs/post_v6_symmetric_comparison/default_repeat \
  --output-dir outputs/post_v6_symmetric_comparison/repeatability_default
```

Main outputs:

- `v6_symmetric_comparison_summary.json`
- `route_b_v6_vs_route_c_v6_comparison.csv`
- `supervision_progression_after_v6_rerun.json`
- `v6_tradeoff_matrix.csv`
- `v6_symmetric_next_step_recommendation.json`

The current v6 recommendation is to prepare a `small_real_labeled_experiment` cutover instead of automatically expanding to `larger_labeled_split_v7`. The reason is that route B and route C now both exist on the same `70`-row shared substrate, so proxy-substrate expansion has become a lower-leverage move than starting a first more realistic labeled experiment contract.

## Real Experiment Cutover Bootstrap

The repository now includes a first cutover bootstrap from repeated proxy-substrate expansion toward a more realistic small labeled experiment object.

Required inputs:

- `outputs/post_v6_symmetric_comparison/default/v6_symmetric_next_step_recommendation.json`
- `outputs/experiment_bootstrap/pilot_refresh/validated_experiment_registry.json`
- `outputs/experiment_bootstrap/pilot_refresh/dataset_registry.json`
- `outputs/experiment_bootstrap/pilot_refresh/model_registry.json`
- `outputs/post_v5_next_step_bootstrap/default/larger_labeled_split_v6.jsonl`
- `outputs/rerun_route_b_on_labeled_split_v6/default/route_b_v6_summary.json`
- `outputs/rerun_route_c_on_labeled_split_v6/default/route_c_v6_summary.json`

Run the cutover bootstrap:

```bash
.venv/bin/python scripts/build_real_experiment_cutover_bootstrap.py \
  --output-dir outputs/real_experiment_cutover_bootstrap/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_real_experiment_cutover_bootstrap.py \
  --run-dir outputs/real_experiment_cutover_bootstrap/default \
  --compare-run-dir outputs/real_experiment_cutover_bootstrap/default_repeat \
  --output-dir outputs/real_experiment_cutover_bootstrap/repeatability_default
```

Main outputs:

- `real_experiment_cutover_plan.json`
- `real_experiment_candidate_selection.json`
- `real_experiment_readiness_summary.json`
- `materialized_real_experiment_inputs/`
- `real_experiment_input_contract.json`
- `real_experiment_bootstrap_summary.json`

The current cutover candidate is `small_real_labeled_csqa_triscope_cutover_v1`. It is more realistic than another proxy-only substrate lift because it defines a unified tri-module + fusion experiment object over the v6 labeled split. It is still not benchmark ground truth and still uses a local curated slice plus `pilot_distilgpt2_hf`.

## First Real Experiment Dry-Run

The repository now includes a first real-experiment dry-run layer that takes the cutover object out of pure readiness mode and maps route B / route C / fusion onto a real execution envelope.

Run the first dry-run:

```bash
.venv/bin/python scripts/build_real_experiment_first_dry_run.py \
  --output-dir outputs/real_experiment_first_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_real_experiment_first_dry_run.py \
  --run-dir outputs/real_experiment_first_dry_run/default \
  --compare-run-dir outputs/real_experiment_first_dry_run/default_repeat \
  --output-dir outputs/real_experiment_first_dry_run/repeatability_default
```

Main outputs:

- `first_real_experiment_dry_run_plan.json`
- `first_real_experiment_execution_contract.json`
- `first_real_experiment_readiness_summary.json`
- `first_real_experiment_dry_run_summary.json`
- `first_real_experiment_dry_run_registry.json`
- `first_real_experiment_module_status.json`

The current dry-run result is `PASS`, with reasoning / confidence / illumination / labeled_illumination / route_b / route_c / fusion all execution-mapped on top of the same cutover object.

## First Real Experiment Execution

The repository now includes a first minimal but real execution layer on top of the cutover object. This stage no longer stops at readiness or dry-run: route B and route C are both actually executed, and fusion is represented as an honest integrated execution summary.

Run the first real execution:

```bash
.venv/bin/python scripts/build_first_real_experiment_execution.py \
  --output-dir outputs/first_real_experiment_execution/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_first_real_experiment_execution.py \
  --run-dir outputs/first_real_experiment_execution/default \
  --compare-run-dir outputs/first_real_experiment_execution/default_repeat \
  --output-dir outputs/first_real_experiment_execution/repeatability_default
```

Main outputs:

- `first_real_execution_selection.json`
- `first_real_execution_plan.json`
- `first_real_execution_readiness_summary.json`
- `first_real_execution_run_summary.json`
- `first_real_execution_registry.json`
- `first_real_route_b_summary.json`
- `first_real_route_c_summary.json`
- `first_real_fusion_summary.json`

The current first execution runs `route_b + route_c + fusion_summary` on the same cutover envelope. It is still small-scale and still not benchmark ground truth, but it is no longer only a readiness object.

## Post First Real Experiment Analysis

The repository now includes a first post-real-execution analysis layer that compares the new first real execution against the latest proxy v6 stage.

Build the post-first-real analysis:

```bash
.venv/bin/python scripts/build_post_first_real_experiment_analysis.py \
  --output-dir outputs/post_first_real_experiment_analysis/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_first_real_experiment_analysis.py \
  --run-dir outputs/post_first_real_experiment_analysis/default \
  --compare-run-dir outputs/post_first_real_experiment_analysis/default_repeat \
  --output-dir outputs/post_first_real_experiment_analysis/repeatability_default
```

Main outputs:

- `first_real_experiment_analysis_summary.json`
- `first_real_vs_proxy_comparison.json`
- `first_real_experiment_blocker_summary.json`
- `first_real_experiment_tradeoff_matrix.csv`
- `first_real_experiment_next_step_recommendation.json`

The current recommendation is to bootstrap a minimal real-experiment matrix rather than return to proxy-only substrate expansion.

## Minimal Real Experiment Matrix Bootstrap

The repository now includes a minimal next-step real-experiment matrix bootstrap that turns the post-first-real recommendation into a concrete next experiment object.

Build the minimal matrix bootstrap:

```bash
.venv/bin/python scripts/build_minimal_real_experiment_matrix_bootstrap.py \
  --output-dir outputs/minimal_real_experiment_matrix_bootstrap/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_minimal_real_experiment_matrix_bootstrap.py \
  --run-dir outputs/minimal_real_experiment_matrix_bootstrap/default \
  --compare-run-dir outputs/minimal_real_experiment_matrix_bootstrap/default_repeat \
  --output-dir outputs/minimal_real_experiment_matrix_bootstrap/repeatability_default
```

Main outputs:

- `minimal_real_experiment_matrix_plan.json`
- `minimal_real_experiment_matrix_definition.json`
- `minimal_real_experiment_matrix_readiness_summary.json`
- `materialized_minimal_real_experiment_matrix/`
- `minimal_real_experiment_input_contract.json`
- `minimal_real_experiment_bootstrap_summary.json`

The current matrix keeps the scope intentionally small: one local curated dataset object, one model (`pilot_distilgpt2_hf`), and three expected outputs (`route_b`, `route_c`, `fusion_summary`).

## First Minimal Real Experiment Matrix Dry-Run

The repository now includes a true matrix-level dry-run on top of `minimal_real_experiment_matrix_v1`. This stage takes the matrix object out of pure bootstrap mode and proves that its single dataset/model cell can execute `route_b / route_c / fusion_summary` under a real matrix envelope.

Run the first matrix dry-run:

```bash
.venv/bin/python scripts/build_first_minimal_real_experiment_matrix_dry_run.py \
  --output-dir outputs/first_minimal_real_experiment_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_first_minimal_real_experiment_matrix_dry_run.py \
  --run-dir outputs/first_minimal_real_experiment_matrix_dry_run/default \
  --compare-run-dir outputs/first_minimal_real_experiment_matrix_dry_run/default_repeat \
  --output-dir outputs/first_minimal_real_experiment_matrix_dry_run/repeatability_default
```

Main outputs:

- `first_matrix_dry_run_plan.json`
- `first_matrix_execution_contract.json`
- `first_matrix_readiness_summary.json`
- `first_matrix_dry_run_summary.json`
- `first_matrix_dry_run_registry.json`
- `first_matrix_module_status.json`
- `first_matrix_cell_status.json`

The current dry-run result is `PASS`, with the single cell `dataset0_model0_routes_b_c_fusion` passing `route_b / route_c / fusion_summary`.

## First Minimal Real Experiment Matrix Execution

The repository now includes a first matrix-level real execution layer. This is no longer only a single-cutover execution object: it is a real execution attached to a named matrix cell.

Run the first matrix execution:

```bash
.venv/bin/python scripts/build_first_minimal_real_experiment_matrix_execution.py \
  --output-dir outputs/first_minimal_real_experiment_matrix_execution/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_first_minimal_real_experiment_matrix_execution.py \
  --run-dir outputs/first_minimal_real_experiment_matrix_execution/default \
  --compare-run-dir outputs/first_minimal_real_experiment_matrix_execution/default_repeat \
  --output-dir outputs/first_minimal_real_experiment_matrix_execution/repeatability_default
```

Main outputs:

- `first_matrix_execution_selection.json`
- `first_matrix_execution_plan.json`
- `first_matrix_execution_readiness_summary.json`
- `first_matrix_execution_run_summary.json`
- `first_matrix_execution_registry.json`
- `first_matrix_route_b_summary.json`
- `first_matrix_route_c_summary.json`
- `first_matrix_fusion_summary.json`
- `first_matrix_execution_metrics.json`
- `first_matrix_cell_metrics.csv`

The current first matrix execution runs one real cell with `route_b + route_c + fusion_summary`. It remains small-scale and local, but it is now explicitly matrix-level.

## Post Minimal Real Experiment Matrix Analysis

The repository now includes a first post-matrix analysis layer that compares matrix execution against both the earlier single-cutover real execution and the latest proxy stage.

Build the post-matrix analysis:

```bash
.venv/bin/python scripts/build_post_minimal_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_minimal_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_minimal_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_minimal_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_minimal_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_minimal_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `minimal_matrix_analysis_summary.json`
- `matrix_vs_cutover_comparison.json`
- `matrix_vs_proxy_comparison.json`
- `minimal_matrix_blocker_summary.json`
- `minimal_matrix_tradeoff_matrix.csv`
- `minimal_matrix_next_step_recommendation.json`

The current recommendation is to bootstrap a richer next real-experiment matrix, not to return to proxy substrate expansion.

## Next Real Experiment Matrix Bootstrap

The repository now includes a bootstrap for the next real-experiment matrix layer after `minimal_real_experiment_matrix_v1`.

Build the next matrix bootstrap:

```bash
.venv/bin/python scripts/build_next_real_experiment_matrix_bootstrap.py \
  --output-dir outputs/next_real_experiment_matrix_bootstrap/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_next_real_experiment_matrix_bootstrap.py \
  --run-dir outputs/next_real_experiment_matrix_bootstrap/default \
  --compare-run-dir outputs/next_real_experiment_matrix_bootstrap/default_repeat \
  --output-dir outputs/next_real_experiment_matrix_bootstrap/repeatability_default
```

Main outputs:

- `next_real_experiment_matrix_plan.json`
- `next_real_experiment_matrix_definition.json`
- `next_real_experiment_matrix_readiness_summary.json`
- `materialized_next_real_experiment_matrix/`
- `next_real_experiment_input_contract.json`
- `next_real_experiment_bootstrap_summary.json`

The current next matrix is `next_real_experiment_matrix_v2`. It keeps dataset/model fixed but expands route/output coverage to include `route_b_only_ablation` and `route_c_only_ablation` on top of `route_b / route_c / fusion_summary`.

## Next Real Experiment Matrix v2 Dry-Run

The repository now includes a richer matrix-level dry-run for `next_real_experiment_matrix_v2`. This stage turns the bootstrap-only route list into explicit executable cells: one full cell and two ablation cells.

Run the next matrix dry-run:

```bash
.venv/bin/python scripts/build_next_real_experiment_matrix_dry_run.py \
  --output-dir outputs/next_real_experiment_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_next_real_experiment_matrix_dry_run.py \
  --run-dir outputs/next_real_experiment_matrix_dry_run/default \
  --compare-run-dir outputs/next_real_experiment_matrix_dry_run/default_repeat \
  --output-dir outputs/next_real_experiment_matrix_dry_run/repeatability_default
```

Main outputs:

- `next_matrix_dry_run_plan.json`
- `next_matrix_execution_contract.json`
- `next_matrix_readiness_summary.json`
- `next_matrix_dry_run_summary.json`
- `next_matrix_dry_run_registry.json`
- `next_matrix_module_status.json`
- `next_matrix_cell_status.json`

The current richer dry-run result is `PASS`, with one full cell and two ablation cells all mapped into the matrix contract.

## Next Real Experiment Matrix v2 Execution

The repository now includes a richer v2 matrix execution stage. This is the first matrix layer where `route_b_only_ablation` and `route_c_only_ablation` are no longer only bootstrap definitions: they become executed matrix artifacts.

Run the next matrix execution:

```bash
.venv/bin/python scripts/build_next_real_experiment_matrix_execution.py \
  --output-dir outputs/next_real_experiment_matrix_execution/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_next_real_experiment_matrix_execution.py \
  --run-dir outputs/next_real_experiment_matrix_execution/default \
  --compare-run-dir outputs/next_real_experiment_matrix_execution/default_repeat \
  --output-dir outputs/next_real_experiment_matrix_execution/repeatability_default
```

Main outputs:

- `next_matrix_execution_selection.json`
- `next_matrix_execution_plan.json`
- `next_matrix_execution_readiness_summary.json`
- `next_matrix_execution_run_summary.json`
- `next_matrix_execution_registry.json`
- `next_matrix_route_b_summary.json`
- `next_matrix_route_c_summary.json`
- `next_matrix_route_b_only_ablation_summary.json`
- `next_matrix_route_c_only_ablation_summary.json`
- `next_matrix_fusion_summary.json`
- `next_matrix_execution_metrics.json`
- `next_matrix_cell_metrics.csv`

The current richer execution is designed to preserve a small experiment footprint while making the ablation coverage real and analyzable.

## Post Next Real Experiment Matrix Analysis

The repository now includes a richer post-matrix analysis stage that compares `next_real_experiment_matrix_v2` against minimal matrix v1 and earlier cutover stages.

Build the post-next-matrix analysis:

```bash
.venv/bin/python scripts/build_post_next_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_next_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_next_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_next_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_next_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_next_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `next_matrix_analysis_summary.json`
- `richer_matrix_vs_minimal_matrix_comparison.json`
- `richer_matrix_vs_cutover_comparison.json`
- `richer_matrix_blocker_summary.json`
- `richer_matrix_tradeoff_matrix.csv`
- `next_matrix_next_step_recommendation.json`

This stage is meant to answer whether richer route coverage and ablation cells actually add new information, not merely prove that another matrix can run.

## Post Next Real Experiment Matrix Bootstrap

The repository now includes a bootstrap for the matrix stage after `next_real_experiment_matrix_v2`.

Build the post-next matrix bootstrap:

```bash
.venv/bin/python scripts/build_post_next_real_experiment_matrix_bootstrap.py \
  --output-dir outputs/post_next_real_experiment_matrix_bootstrap/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_next_real_experiment_matrix_bootstrap.py \
  --run-dir outputs/post_next_real_experiment_matrix_bootstrap/default \
  --compare-run-dir outputs/post_next_real_experiment_matrix_bootstrap/default_repeat \
  --output-dir outputs/post_next_real_experiment_matrix_bootstrap/repeatability_default
```

Main outputs:

- `next_next_real_experiment_matrix_plan.json`
- `next_next_real_experiment_matrix_definition.json`
- `next_next_real_experiment_matrix_readiness_summary.json`
- `materialized_next_next_real_experiment_matrix/`
- `next_next_real_experiment_input_contract.json`
- `next_next_real_experiment_bootstrap_summary.json`

The current recommended expansion axis after richer route coverage is to promote fusion from summary-only coverage toward explicit fusion-cell coverage.

## Post Next Real Experiment Matrix v3 Dry Run

The repository now includes a fusion-cell-aware v3 matrix dry-run stage for `post_next_real_experiment_matrix_v3`. This is the first matrix layer that distinguishes inherited `fusion_summary` coverage from an explicit `fusion_cell_candidate` cell.

Build the v3 matrix dry-run:

```bash
.venv/bin/python scripts/build_post_next_real_experiment_matrix_dry_run.py \
  --output-dir outputs/post_next_real_experiment_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_next_real_experiment_matrix_dry_run.py \
  --run-dir outputs/post_next_real_experiment_matrix_dry_run/default \
  --compare-run-dir outputs/post_next_real_experiment_matrix_dry_run/default_repeat \
  --output-dir outputs/post_next_real_experiment_matrix_dry_run/repeatability_default
```

Main outputs:

- `post_next_matrix_dry_run_plan.json`
- `post_next_matrix_execution_contract.json`
- `post_next_matrix_readiness_summary.json`
- `post_next_matrix_dry_run_summary.json`
- `post_next_matrix_dry_run_registry.json`
- `post_next_matrix_module_status.json`
- `post_next_matrix_cell_status.json`
- `post_next_matrix_dry_run_preview.jsonl`

The current v3 dry-run result is `PASS`, with five cells passing, including both `fusion_summary` and `fusion_cell_candidate`.

## Post Next Real Experiment Matrix v3 Execution

The repository now includes a fusion-cell-aware v3 matrix execution stage. This is the first matrix layer where `fusion_cell_candidate` is promoted from a bootstrap definition into an explicit execution artifact.

Build the v3 matrix execution:

```bash
.venv/bin/python scripts/build_post_next_real_experiment_matrix_execution.py \
  --output-dir outputs/post_next_real_experiment_matrix_execution/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_next_real_experiment_matrix_execution.py \
  --run-dir outputs/post_next_real_experiment_matrix_execution/default \
  --compare-run-dir outputs/post_next_real_experiment_matrix_execution/default_repeat \
  --output-dir outputs/post_next_real_experiment_matrix_execution/repeatability_default
```

Main outputs:

- `post_next_matrix_execution_selection.json`
- `post_next_matrix_execution_plan.json`
- `post_next_matrix_execution_readiness_summary.json`
- `post_next_matrix_execution_run_summary.json`
- `post_next_matrix_execution_registry.json`
- `post_next_matrix_route_b_summary.json`
- `post_next_matrix_route_c_summary.json`
- `post_next_matrix_route_b_only_ablation_summary.json`
- `post_next_matrix_route_c_only_ablation_summary.json`
- `post_next_matrix_fusion_summary.json`
- `post_next_matrix_fusion_cell_candidate_summary.json`
- `post_next_matrix_execution_metrics.json`
- `post_next_matrix_cell_metrics.csv`

The current v3 execution keeps the experiment footprint small while making `fusion_cell_candidate` a real executed cell instead of only a summary-adjacent placeholder.

## Post v3 Real Experiment Matrix Analysis

The repository now includes a post-v3 analysis stage that compares `fusion_cell_candidate` against `fusion_summary`, and compares v3 against richer matrix v2 and earlier stages.

Build the post-v3 matrix analysis:

```bash
.venv/bin/python scripts/build_post_v3_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_v3_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_post_v3_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_v3_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_v3_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_v3_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `post_next_matrix_analysis_summary.json`
- `fusion_cell_vs_fusion_summary_comparison.json`
- `v3_vs_v2_matrix_comparison.json`
- `v3_matrix_blocker_summary.json`
- `v3_matrix_tradeoff_matrix.csv`
- `post_next_matrix_next_step_recommendation.json`

This stage is meant to answer whether explicit fusion-cell coverage adds real value beyond inherited summary-style fusion, not merely prove that another matrix can run.

## Next-Axis Real Experiment Matrix Bootstrap

The repository now includes a next-axis bootstrap after v3 matrix analysis. The current recommendation is to keep dataset/model fixed and refine explicit fusion-cell coverage further before jumping to a heavier axis.

Build the next-axis matrix bootstrap:

```bash
.venv/bin/python scripts/build_next_axis_real_experiment_matrix_bootstrap.py \
  --output-dir outputs/next_axis_real_experiment_matrix_bootstrap/default
```

Optional validation CLI:

```bash
.venv/bin/python scripts/validate_next_axis_real_experiment_matrix_bootstrap.py \
  --run-dir outputs/next_axis_real_experiment_matrix_bootstrap/default \
  --compare-run-dir outputs/next_axis_real_experiment_matrix_bootstrap/default_repeat \
  --output-dir outputs/next_axis_real_experiment_matrix_bootstrap/repeatability_default
```

Main outputs:

- `next_axis_real_experiment_matrix_plan.json`
- `next_axis_real_experiment_matrix_definition.json`
- `next_axis_real_experiment_matrix_readiness_summary.json`
- `materialized_next_axis_real_experiment_matrix/`
- `next_axis_real_experiment_input_contract.json`
- `next_axis_real_experiment_bootstrap_summary.json`

The current bootstrap produces `next_axis_real_experiment_matrix_v4`, which adds `fusion_cell_refined` on top of the existing route and fusion coverage.

## Next-Axis Real Experiment Matrix v4 Dry Run

The repository now includes a refined-fusion-aware v4 matrix dry-run stage for `next_axis_real_experiment_matrix_v4`. This is the first matrix layer that keeps `fusion_summary`, `fusion_cell_candidate`, and `fusion_cell_refined` together in one dry-run contract.

Build the v4 matrix dry-run:

```bash
.venv/bin/python scripts/build_next_axis_real_experiment_matrix_dry_run.py \
  --output-dir outputs/next_axis_real_experiment_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_real_experiment_matrix_dry_run.py \
  --run-dir outputs/next_axis_real_experiment_matrix_dry_run/default \
  --compare-run-dir outputs/next_axis_real_experiment_matrix_dry_run/default_repeat \
  --output-dir outputs/next_axis_real_experiment_matrix_dry_run/repeatability_default
```

Main outputs:

- `next_axis_matrix_dry_run_plan.json`
- `next_axis_matrix_execution_contract.json`
- `next_axis_matrix_readiness_summary.json`
- `next_axis_matrix_dry_run_summary.json`
- `next_axis_matrix_dry_run_registry.json`
- `next_axis_matrix_module_status.json`
- `next_axis_matrix_cell_status.json`
- `next_axis_matrix_dry_run_preview.jsonl`

The current v4 dry-run result is `PASS`, with six cells passing, including the explicit `fusion_cell_refined` cell.

## Next-Axis Real Experiment Matrix v4 Execution

The repository now includes a refined-fusion-aware v4 matrix execution stage. This is the first matrix layer where `fusion_cell_refined` is promoted from a bootstrap definition into an explicit execution artifact.

Build the v4 matrix execution:

```bash
python3 scripts/build_next_axis_real_experiment_matrix_execution.py \
  --output-dir outputs/next_axis_real_experiment_matrix_execution/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_real_experiment_matrix_execution.py \
  --run-dir outputs/next_axis_real_experiment_matrix_execution/default \
  --compare-run-dir outputs/next_axis_real_experiment_matrix_execution/default_repeat \
  --output-dir outputs/next_axis_real_experiment_matrix_execution/repeatability_default
```

Main outputs:

- `next_axis_matrix_execution_selection.json`
- `next_axis_matrix_execution_plan.json`
- `next_axis_matrix_execution_readiness_summary.json`
- `next_axis_matrix_execution_run_summary.json`
- `next_axis_matrix_execution_registry.json`
- `next_axis_matrix_route_b_summary.json`
- `next_axis_matrix_route_c_summary.json`
- `next_axis_matrix_route_b_only_ablation_summary.json`
- `next_axis_matrix_route_c_only_ablation_summary.json`
- `next_axis_matrix_fusion_summary.json`
- `next_axis_matrix_fusion_cell_candidate_summary.json`
- `next_axis_matrix_fusion_cell_refined_summary.json`
- `next_axis_matrix_execution_metrics.json`
- `next_axis_matrix_cell_metrics.csv`

The current v4 execution makes `fusion_cell_refined` real while preserving `fusion_summary` and `fusion_cell_candidate` as comparison baselines.

## Post-v4 Real Experiment Matrix Analysis

The repository now includes a post-v4 analysis stage that compares `fusion_cell_refined` against both `fusion_cell_candidate` and `fusion_summary`, and then decides the next matrix expansion axis.

Build the post-v4 matrix analysis:

```bash
python3 scripts/build_post_v4_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_v4_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
python3 scripts/validate_post_v4_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_v4_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_v4_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_v4_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `next_axis_matrix_analysis_summary.json`
- `fusion_refined_vs_candidate_comparison.json`
- `fusion_refined_vs_summary_comparison.json`
- `v4_vs_v3_matrix_comparison.json`
- `v4_matrix_blocker_summary.json`
- `v4_matrix_tradeoff_matrix.csv`
- `next_axis_matrix_next_step_recommendation.json`

This stage is meant to answer whether refined fusion coverage adds new information beyond the candidate and summary baselines, not merely prove that another matrix can run.

## Next-Axis-After-v4 Real Experiment Matrix Bootstrap

The repository now includes a next-axis-after-v4 bootstrap stage. The current recommendation is to keep dataset/model fixed and isolate refined fusion coverage further before jumping to a heavier axis.

Build the next-axis-after-v4 matrix bootstrap:

```bash
python3 scripts/build_next_axis_after_v4_real_experiment_matrix_bootstrap.py \
  --output-dir outputs/next_axis_after_v4_real_experiment_matrix_bootstrap/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v4_real_experiment_matrix_bootstrap.py \
  --run-dir outputs/next_axis_after_v4_real_experiment_matrix_bootstrap/default \
  --compare-run-dir outputs/next_axis_after_v4_real_experiment_matrix_bootstrap/default_repeat \
  --output-dir outputs/next_axis_after_v4_real_experiment_matrix_bootstrap/repeatability_default
```

Main outputs:

- `next_axis_after_v4_matrix_plan.json`
- `next_axis_after_v4_matrix_definition.json`
- `next_axis_after_v4_matrix_readiness_summary.json`
- `materialized_next_axis_after_v4_matrix/`
- `next_axis_after_v4_input_contract.json`
- `next_axis_after_v4_bootstrap_summary.json`

The current bootstrap produces `next_axis_after_v4_real_experiment_matrix_v5`, which adds `fusion_cell_refined_ablation` on top of the existing fusion coverage stack.

## Next-Axis-After-v4 Matrix v5 Dry Run

The repository now includes a refined-fusion-ablation-aware v5 matrix dry-run stage. This is the first matrix layer where `fusion_cell_refined_ablation` is treated as its own executable dry-run cell instead of only a bootstrap placeholder.

Build the v5 matrix dry-run:

```bash
.venv/bin/python scripts/build_next_axis_after_v4_matrix_dry_run.py \
  --output-dir outputs/next_axis_after_v4_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v4_matrix_dry_run.py \
  --run-dir outputs/next_axis_after_v4_matrix_dry_run/default \
  --compare-run-dir outputs/next_axis_after_v4_matrix_dry_run/default_repeat \
  --output-dir outputs/next_axis_after_v4_matrix_dry_run/repeatability_default
```

Main outputs:

- `next_axis_after_v4_matrix_dry_run_plan.json`
- `next_axis_after_v4_matrix_execution_contract.json`
- `next_axis_after_v4_matrix_readiness_summary.json`
- `next_axis_after_v4_matrix_dry_run_summary.json`
- `next_axis_after_v4_matrix_dry_run_registry.json`
- `next_axis_after_v4_matrix_dry_run.log`
- `next_axis_after_v4_matrix_module_status.json`
- `next_axis_after_v4_matrix_cell_status.json`

The current v5 dry-run result is `PASS`, with seven cells passing, including `fusion_summary`, `fusion_cell_candidate`, `fusion_cell_refined`, and `fusion_cell_refined_ablation`.

## Next-Axis-After-v4 Matrix v5 Execution

The repository now includes a refined-fusion-ablation-aware v5 matrix execution stage. This is the first matrix layer where `fusion_cell_refined_ablation` is promoted from a dry-run cell into an explicit execution artifact.

Build the v5 matrix execution:

```bash
python3 scripts/build_next_axis_after_v4_matrix_execution.py \
  --output-dir outputs/next_axis_after_v4_matrix_execution/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v4_matrix_execution.py \
  --run-dir outputs/next_axis_after_v4_matrix_execution/default \
  --compare-run-dir outputs/next_axis_after_v4_matrix_execution/default_repeat \
  --output-dir outputs/next_axis_after_v4_matrix_execution/repeatability_default
```

Main outputs:

- `next_axis_after_v4_matrix_execution_selection.json`
- `next_axis_after_v4_matrix_execution_plan.json`
- `next_axis_after_v4_matrix_execution_readiness_summary.json`
- `next_axis_after_v4_matrix_execution_run_summary.json`
- `next_axis_after_v4_matrix_execution_registry.json`
- `next_axis_after_v4_matrix_route_b_summary.json`
- `next_axis_after_v4_matrix_route_c_summary.json`
- `next_axis_after_v4_matrix_route_b_only_ablation_summary.json`
- `next_axis_after_v4_matrix_route_c_only_ablation_summary.json`
- `next_axis_after_v4_matrix_fusion_summary.json`
- `next_axis_after_v4_matrix_fusion_cell_candidate_summary.json`
- `next_axis_after_v4_matrix_fusion_cell_refined_summary.json`
- `next_axis_after_v4_matrix_fusion_cell_refined_ablation_summary.json`
- `next_axis_after_v4_matrix_execution_metrics.json`
- `next_axis_after_v4_matrix_cell_metrics.csv`

The current v5 execution makes `fusion_cell_refined_ablation` real while preserving `fusion_summary`, `fusion_cell_candidate`, and `fusion_cell_refined` as comparison baselines.

## Post-v5 Real Experiment Matrix Analysis

The repository now includes a post-v5 analysis stage that compares `fusion_cell_refined_ablation` against `fusion_cell_refined`, `fusion_cell_candidate`, and `fusion_summary`, and then decides the next expansion axis.

Build the post-v5 matrix analysis:

```bash
python3 scripts/build_post_v5_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_v5_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
python3 scripts/validate_post_v5_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_v5_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_v5_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_v5_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `next_axis_after_v4_matrix_analysis_summary.json`
- `fusion_refined_ablation_vs_refined_comparison.json`
- `fusion_refined_ablation_vs_candidate_comparison.json`
- `fusion_refined_ablation_vs_summary_comparison.json`
- `v5_vs_v4_matrix_comparison.json`
- `v5_matrix_blocker_summary.json`
- `v5_matrix_tradeoff_matrix.csv`
- `next_axis_after_v4_matrix_next_step_recommendation.json`

This stage is meant to answer how much refined fusion information remains after explicit ablation, not merely prove that another matrix can run.

## Next-Axis-After-v5 Matrix Bootstrap

The repository now includes a next-axis-after-v5 bootstrap stage. The current recommendation is to keep dataset/model fixed and stress refined fusion support stability before jumping to a heavier axis.

Build the next-axis-after-v5 matrix bootstrap:

```bash
python3 scripts/build_next_axis_after_v5_matrix_bootstrap.py \
  --output-dir outputs/next_axis_after_v5_matrix_bootstrap/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v5_matrix_bootstrap.py \
  --run-dir outputs/next_axis_after_v5_matrix_bootstrap/default \
  --compare-run-dir outputs/next_axis_after_v5_matrix_bootstrap/default_repeat \
  --output-dir outputs/next_axis_after_v5_matrix_bootstrap/repeatability_default
```

Main outputs:

- `next_axis_after_v5_matrix_plan.json`
- `next_axis_after_v5_matrix_definition.json`
- `next_axis_after_v5_matrix_readiness_summary.json`
- `materialized_next_axis_after_v5_matrix/`
- `next_axis_after_v5_input_contract.json`
- `next_axis_after_v5_bootstrap_summary.json`

The current bootstrap produces `next_axis_after_v5_real_experiment_matrix_v6`, which adds `fusion_cell_refined_support_sweep` on top of the refined-ablation coverage stack.

## Next-Axis-After-v5 Matrix v6 Dry Run

The repository now includes a refined-fusion-support-sweep-aware v6 matrix dry-run stage. This is the first matrix layer where `fusion_cell_refined_support_sweep` is treated as its own executable dry-run cell instead of only a bootstrap placeholder.

Build the v6 matrix dry-run:

```bash
.venv/bin/python scripts/build_next_axis_after_v5_matrix_dry_run.py \
  --output-dir outputs/next_axis_after_v5_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v5_matrix_dry_run.py \
  --run-dir outputs/next_axis_after_v5_matrix_dry_run/default \
  --compare-run-dir outputs/next_axis_after_v5_matrix_dry_run/default_repeat \
  --output-dir outputs/next_axis_after_v5_matrix_dry_run/repeatability_default
```

Main outputs:

- `next_axis_after_v5_matrix_dry_run_plan.json`
- `next_axis_after_v5_matrix_execution_contract.json`
- `next_axis_after_v5_matrix_readiness_summary.json`
- `next_axis_after_v5_matrix_dry_run_summary.json`
- `next_axis_after_v5_matrix_dry_run_registry.json`
- `next_axis_after_v5_matrix_dry_run.log`
- `next_axis_after_v5_matrix_module_status.json`
- `next_axis_after_v5_matrix_cell_status.json`

The current v6 dry-run result is `PASS`, with eight cells passing, including `fusion_summary`, `fusion_cell_candidate`, `fusion_cell_refined`, `fusion_cell_refined_ablation`, and `fusion_cell_refined_support_sweep`.

## Next-Axis-After-v5 Matrix v6 Execution

The repository now includes a refined-fusion-support-sweep-aware v6 matrix execution stage. This is the first matrix layer where `fusion_cell_refined_support_sweep` is promoted from a dry-run cell into an explicit execution artifact.

Build the v6 matrix execution:

```bash
python3 scripts/build_next_axis_after_v5_matrix_execution.py \
  --output-dir outputs/next_axis_after_v5_matrix_execution/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v5_matrix_execution.py \
  --run-dir outputs/next_axis_after_v5_matrix_execution/default \
  --compare-run-dir outputs/next_axis_after_v5_matrix_execution/default_repeat \
  --output-dir outputs/next_axis_after_v5_matrix_execution/repeatability_default
```

Main outputs:

- `next_axis_after_v5_matrix_execution_selection.json`
- `next_axis_after_v5_matrix_execution_plan.json`
- `next_axis_after_v5_matrix_execution_readiness_summary.json`
- `next_axis_after_v5_matrix_execution_run_summary.json`
- `next_axis_after_v5_matrix_execution_registry.json`
- `next_axis_after_v5_matrix_route_b_summary.json`
- `next_axis_after_v5_matrix_route_c_summary.json`
- `next_axis_after_v5_matrix_route_b_only_ablation_summary.json`
- `next_axis_after_v5_matrix_route_c_only_ablation_summary.json`
- `next_axis_after_v5_matrix_fusion_summary.json`
- `next_axis_after_v5_matrix_fusion_cell_candidate_summary.json`
- `next_axis_after_v5_matrix_fusion_cell_refined_summary.json`
- `next_axis_after_v5_matrix_fusion_cell_refined_ablation_summary.json`
- `next_axis_after_v5_matrix_fusion_cell_refined_support_sweep_summary.json`
- `next_axis_after_v5_matrix_execution_metrics.json`
- `next_axis_after_v5_matrix_cell_metrics.csv`

The current v6 execution makes `fusion_cell_refined_support_sweep` real while preserving `fusion_summary`, `fusion_cell_candidate`, `fusion_cell_refined`, and `fusion_cell_refined_ablation` as comparison baselines.

## Post-v6 Real Experiment Matrix Analysis

The repository now includes a post-v6 analysis stage that compares `fusion_cell_refined_support_sweep` against `fusion_cell_refined`, `fusion_cell_refined_ablation`, `fusion_cell_candidate`, and `fusion_summary`, and then decides the next expansion axis.

Build the post-v6 matrix analysis:

```bash
python3 scripts/build_post_v6_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_v6_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
python3 scripts/validate_post_v6_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_v6_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_v6_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_v6_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `next_axis_after_v5_matrix_analysis_summary.json`
- `fusion_support_sweep_vs_refined_comparison.json`
- `fusion_support_sweep_vs_refined_ablation_comparison.json`
- `fusion_support_sweep_vs_candidate_comparison.json`
- `fusion_support_sweep_vs_summary_comparison.json`
- `v6_vs_v5_matrix_comparison.json`
- `v6_matrix_blocker_summary.json`
- `v6_matrix_tradeoff_matrix.csv`
- `next_axis_after_v5_matrix_next_step_recommendation.json`

This stage is meant to answer how stable refined fusion remains under support/stability pressure, not merely prove that another matrix can run.

## Next-Axis-After-v6 Matrix Bootstrap

The repository now includes a next-axis-after-v6 bootstrap stage. The current recommendation is to keep dataset/model fixed and isolate support-retained refined fusion signal before jumping to a heavier axis.

Build the next-axis-after-v6 matrix bootstrap:

```bash
python3 scripts/build_next_axis_after_v6_matrix_bootstrap.py \
  --output-dir outputs/next_axis_after_v6_matrix_bootstrap/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v6_matrix_bootstrap.py \
  --run-dir outputs/next_axis_after_v6_matrix_bootstrap/default \
  --compare-run-dir outputs/next_axis_after_v6_matrix_bootstrap/default_repeat \
  --output-dir outputs/next_axis_after_v6_matrix_bootstrap/repeatability_default
```

Main outputs:

- `next_axis_after_v6_matrix_plan.json`
- `next_axis_after_v6_matrix_definition.json`
- `next_axis_after_v6_matrix_readiness_summary.json`
- `materialized_next_axis_after_v6_matrix/`
- `next_axis_after_v6_input_contract.json`
- `next_axis_after_v6_bootstrap_summary.json`

The current bootstrap produces `next_axis_after_v6_real_experiment_matrix_v7`, which adds `fusion_cell_refined_support_ablation` on top of the support-sweep coverage stack.

## Next-Axis-After-v6 Matrix Dry Run

The repository now includes a next-axis-after-v6 dry-run stage. The current focus is to make `fusion_cell_refined_support_ablation` executable alongside `fusion_summary`, `fusion_cell_candidate`, `fusion_cell_refined`, `fusion_cell_refined_ablation`, and `fusion_cell_refined_support_sweep`.

Build the next-axis-after-v6 matrix dry-run:

```bash
.venv/bin/python scripts/build_next_axis_after_v6_matrix_dry_run.py \
  --output-dir outputs/next_axis_after_v6_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v6_matrix_dry_run.py \
  --run-dir outputs/next_axis_after_v6_matrix_dry_run/default \
  --compare-run-dir outputs/next_axis_after_v6_matrix_dry_run/default_repeat \
  --output-dir outputs/next_axis_after_v6_matrix_dry_run/repeatability_default
```

Main outputs:

- `next_axis_after_v6_matrix_dry_run_plan.json`
- `next_axis_after_v6_matrix_execution_contract.json`
- `next_axis_after_v6_matrix_readiness_summary.json`
- `next_axis_after_v6_matrix_dry_run_summary.json`
- `next_axis_after_v6_matrix_dry_run_registry.json`
- `next_axis_after_v6_matrix_module_status.json`
- `next_axis_after_v6_matrix_cell_status.json`

This stage is meant to prove that support-focused ablation has become a first-class executable matrix cell, not just another bootstrap note.

## Next-Axis-After-v6 Matrix Execution

The repository now includes a next-axis-after-v6 execution stage. The current purpose is to promote `fusion_cell_refined_support_ablation` from contract to real execution artifact.

Build the next-axis-after-v6 matrix execution:

```bash
python3 scripts/build_next_axis_after_v6_matrix_execution.py \
  --output-dir outputs/next_axis_after_v6_matrix_execution/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v6_matrix_execution.py \
  --run-dir outputs/next_axis_after_v6_matrix_execution/default \
  --compare-run-dir outputs/next_axis_after_v6_matrix_execution/default_repeat \
  --output-dir outputs/next_axis_after_v6_matrix_execution/repeatability_default
```

Main outputs:

- `next_axis_after_v6_matrix_execution_run_summary.json`
- `next_axis_after_v6_matrix_execution_registry.json`
- `next_axis_after_v6_matrix_execution_metrics.json`
- `next_axis_after_v6_matrix_cell_metrics.csv`
- `next_axis_after_v6_matrix_fusion_cell_refined_support_ablation_summary.json`

This stage is meant to answer how much refined fusion signal survives once support-retained residue is explicitly removed.

## Post-v7 Matrix Analysis

The repository now includes a post-v7 matrix analysis stage. The current emphasis is to compare `fusion_cell_refined_support_ablation` against `fusion_cell_refined_support_sweep`, `fusion_cell_refined_ablation`, `fusion_cell_refined`, `fusion_cell_candidate`, and `fusion_summary`.

Build the post-v7 matrix analysis:

```bash
python3 scripts/build_post_v7_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_v7_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
python3 scripts/validate_post_v7_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_v7_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_v7_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_v7_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `next_axis_after_v6_matrix_analysis_summary.json`
- `fusion_support_ablation_vs_support_sweep_comparison.json`
- `fusion_support_ablation_vs_refined_comparison.json`
- `fusion_support_ablation_vs_refined_ablation_comparison.json`
- `fusion_support_ablation_vs_candidate_comparison.json`
- `fusion_support_ablation_vs_summary_comparison.json`
- `v7_vs_v6_matrix_comparison.json`
- `v7_matrix_blocker_summary.json`
- `v7_matrix_tradeoff_matrix.csv`
- `next_axis_after_v6_matrix_next_step_recommendation.json`

This stage is meant to answer whether support-isolated refined fusion is still informative, not just whether one more matrix cell can run.

## Next-Axis-After-v7 Matrix Bootstrap

The repository now includes a next-axis-after-v7 bootstrap stage. The current recommendation is to keep dataset/model fixed and stress the support-ablation residual itself before jumping to model or dataset axes.

Build the next-axis-after-v7 matrix bootstrap:

```bash
python3 scripts/build_next_axis_after_v7_matrix_bootstrap.py \
  --output-dir outputs/next_axis_after_v7_matrix_bootstrap/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v7_matrix_bootstrap.py \
  --run-dir outputs/next_axis_after_v7_matrix_bootstrap/default \
  --compare-run-dir outputs/next_axis_after_v7_matrix_bootstrap/default_repeat \
  --output-dir outputs/next_axis_after_v7_matrix_bootstrap/repeatability_default
```

Main outputs:

- `next_axis_after_v7_matrix_plan.json`
- `next_axis_after_v7_matrix_definition.json`
- `next_axis_after_v7_matrix_readiness_summary.json`
- `materialized_next_axis_after_v7_matrix/`
- `next_axis_after_v7_input_contract.json`
- `next_axis_after_v7_bootstrap_summary.json`

The current bootstrap produces `next_axis_after_v7_real_experiment_matrix_v8`, which adds `fusion_cell_refined_support_ablation_sweep` on top of the support-isolation coverage stack.

## Next-Axis-After-v7 Matrix Dry Run

The repository now includes a next-axis-after-v7 dry-run stage. The current focus is to make `fusion_cell_refined_support_ablation_sweep` executable alongside `fusion_summary`, `fusion_cell_candidate`, `fusion_cell_refined`, `fusion_cell_refined_ablation`, `fusion_cell_refined_support_sweep`, and `fusion_cell_refined_support_ablation`.

Build the next-axis-after-v7 matrix dry-run:

```bash
.venv/bin/python scripts/build_next_axis_after_v7_matrix_dry_run.py \
  --output-dir outputs/next_axis_after_v7_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v7_matrix_dry_run.py \
  --run-dir outputs/next_axis_after_v7_matrix_dry_run/default \
  --compare-run-dir outputs/next_axis_after_v7_matrix_dry_run/default_repeat \
  --output-dir outputs/next_axis_after_v7_matrix_dry_run/repeatability_default
```

Main outputs:

- `next_axis_after_v7_matrix_dry_run_plan.json`
- `next_axis_after_v7_matrix_execution_contract.json`
- `next_axis_after_v7_matrix_readiness_summary.json`
- `next_axis_after_v7_matrix_dry_run_summary.json`
- `next_axis_after_v7_matrix_dry_run_registry.json`
- `next_axis_after_v7_matrix_module_status.json`
- `next_axis_after_v7_matrix_cell_status.json`

This stage is meant to prove that support-ablation-sweep has become a first-class executable matrix cell, not just another bootstrap note.

## Next-Axis-After-v7 Matrix Execution

The repository now includes a next-axis-after-v7 execution stage. The current purpose is to promote `fusion_cell_refined_support_ablation_sweep` from contract to real execution artifact.

Build the next-axis-after-v7 matrix execution:

```bash
python3 scripts/build_next_axis_after_v7_matrix_execution.py \
  --output-dir outputs/next_axis_after_v7_matrix_execution/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v7_matrix_execution.py \
  --run-dir outputs/next_axis_after_v7_matrix_execution/default \
  --compare-run-dir outputs/next_axis_after_v7_matrix_execution/default_repeat \
  --output-dir outputs/next_axis_after_v7_matrix_execution/repeatability_default
```

Main outputs:

- `next_axis_after_v7_matrix_execution_run_summary.json`
- `next_axis_after_v7_matrix_execution_registry.json`
- `next_axis_after_v7_matrix_execution_metrics.json`
- `next_axis_after_v7_matrix_cell_metrics.csv`
- `next_axis_after_v7_matrix_fusion_cell_refined_support_ablation_sweep_summary.json`

This stage is meant to answer how much support-isolated residual remains once the support-ablation floor itself is swept again.

## Post-v8 Matrix Analysis

The repository now includes a post-v8 matrix analysis stage. The current emphasis is to compare `fusion_cell_refined_support_ablation_sweep` against `fusion_cell_refined_support_ablation`, `fusion_cell_refined_support_sweep`, `fusion_cell_refined`, `fusion_cell_candidate`, and `fusion_summary`.

Build the post-v8 matrix analysis:

```bash
python3 scripts/build_post_v8_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_v8_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
python3 scripts/validate_post_v8_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_v8_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_v8_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_v8_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `next_axis_after_v7_matrix_analysis_summary.json`
- `fusion_support_ablation_sweep_vs_support_ablation_comparison.json`
- `fusion_support_ablation_sweep_vs_support_sweep_comparison.json`
- `fusion_support_ablation_sweep_vs_refined_comparison.json`
- `fusion_support_ablation_sweep_vs_candidate_comparison.json`
- `fusion_support_ablation_sweep_vs_summary_comparison.json`
- `v8_vs_v7_matrix_comparison.json`
- `v8_matrix_blocker_summary.json`
- `v8_matrix_tradeoff_matrix.csv`
- `next_axis_after_v7_matrix_next_step_recommendation.json`

This stage is meant to answer whether support-isolated residual stability remains informative, not just whether one more matrix cell can run.

## Next-Axis-After-v8 Matrix Bootstrap

The repository now includes a next-axis-after-v8 bootstrap stage. The current recommendation is to keep dataset/model fixed and probe whether the swept support-isolated floor is actually invariant.

Build the next-axis-after-v8 matrix bootstrap:

```bash
python3 scripts/build_next_axis_after_v8_matrix_bootstrap.py \
  --output-dir outputs/next_axis_after_v8_matrix_bootstrap/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v8_matrix_bootstrap.py \
  --run-dir outputs/next_axis_after_v8_matrix_bootstrap/default \
  --compare-run-dir outputs/next_axis_after_v8_matrix_bootstrap/default_repeat \
  --output-dir outputs/next_axis_after_v8_matrix_bootstrap/repeatability_default
```

Main outputs:

- `next_axis_after_v8_matrix_plan.json`
- `next_axis_after_v8_matrix_definition.json`
- `next_axis_after_v8_matrix_readiness_summary.json`
- `materialized_next_axis_after_v8_matrix/`
- `next_axis_after_v8_input_contract.json`
- `next_axis_after_v8_bootstrap_summary.json`

The current bootstrap produces `next_axis_after_v8_real_experiment_matrix_v9`, which adds `fusion_cell_refined_support_ablation_floor_probe` on top of the support-residual stability stack.

## Next-Axis-After-v8 Matrix Dry Run

The repository now includes a next-axis-after-v8 dry-run stage. The current focus is to make `fusion_cell_refined_support_ablation_floor_probe` executable alongside `fusion_summary`, `fusion_cell_candidate`, `fusion_cell_refined`, `fusion_cell_refined_ablation`, `fusion_cell_refined_support_sweep`, `fusion_cell_refined_support_ablation`, and `fusion_cell_refined_support_ablation_sweep`.

Build the next-axis-after-v8 matrix dry-run:

```bash
.venv/bin/python scripts/build_next_axis_after_v8_matrix_dry_run.py \
  --output-dir outputs/next_axis_after_v8_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v8_matrix_dry_run.py \
  --run-dir outputs/next_axis_after_v8_matrix_dry_run/default \
  --compare-run-dir outputs/next_axis_after_v8_matrix_dry_run/default_repeat \
  --output-dir outputs/next_axis_after_v8_matrix_dry_run/repeatability_default
```

Main outputs:

- `next_axis_after_v8_matrix_dry_run_plan.json`
- `next_axis_after_v8_matrix_execution_contract.json`
- `next_axis_after_v8_matrix_readiness_summary.json`
- `next_axis_after_v8_matrix_dry_run_summary.json`
- `next_axis_after_v8_matrix_dry_run_registry.json`
- `next_axis_after_v8_matrix_module_status.json`
- `next_axis_after_v8_matrix_cell_status.json`

This stage is meant to prove that the explicit support-floor probe has become a first-class executable matrix cell, not just another bootstrap note.

## Next-Axis-After-v8 Matrix Execution

The repository now includes a next-axis-after-v8 execution stage. The current purpose is to promote `fusion_cell_refined_support_ablation_floor_probe` from contract to real execution artifact.

Build the next-axis-after-v8 matrix execution:

```bash
python3 scripts/build_next_axis_after_v8_matrix_execution.py \
  --output-dir outputs/next_axis_after_v8_matrix_execution/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v8_matrix_execution.py \
  --run-dir outputs/next_axis_after_v8_matrix_execution/default \
  --compare-run-dir outputs/next_axis_after_v8_matrix_execution/default_repeat \
  --output-dir outputs/next_axis_after_v8_matrix_execution/repeatability_default
```

Main outputs:

- `next_axis_after_v8_matrix_execution_run_summary.json`
- `next_axis_after_v8_matrix_execution_registry.json`
- `next_axis_after_v8_matrix_execution_metrics.json`
- `next_axis_after_v8_matrix_cell_metrics.csv`
- `next_axis_after_v8_matrix_fusion_cell_refined_support_ablation_floor_probe_summary.json`

This stage is meant to answer whether the swept support-isolated floor is actually invariant once it becomes a direct explicit probe.

## Post-v9 Matrix Analysis

The repository now includes a post-v9 matrix analysis stage. The current emphasis is to compare `fusion_cell_refined_support_ablation_floor_probe` against `fusion_cell_refined_support_ablation_sweep`, `fusion_cell_refined_support_ablation`, `fusion_cell_refined_support_sweep`, `fusion_cell_refined`, `fusion_cell_candidate`, and `fusion_summary`.

Build the post-v9 matrix analysis:

```bash
python3 scripts/build_post_v9_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_v9_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
python3 scripts/validate_post_v9_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_v9_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_v9_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_v9_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `next_axis_after_v8_matrix_analysis_summary.json`
- `fusion_floor_probe_vs_support_ablation_sweep_comparison.json`
- `fusion_floor_probe_vs_support_ablation_comparison.json`
- `fusion_floor_probe_vs_support_sweep_comparison.json`
- `fusion_floor_probe_vs_refined_comparison.json`
- `fusion_floor_probe_vs_candidate_comparison.json`
- `fusion_floor_probe_vs_summary_comparison.json`
- `v9_vs_v8_matrix_comparison.json`
- `v9_matrix_blocker_summary.json`
- `v9_matrix_tradeoff_matrix.csv`
- `next_axis_after_v8_matrix_next_step_recommendation.json`

This stage is meant to answer whether support-floor invariance has been clearly exposed, not just whether one more matrix cell can run.

## Next-Axis-After-v9 Matrix Bootstrap

The repository now includes a next-axis-after-v9 bootstrap stage. The current recommendation is to keep dataset/model fixed and stress the explicit support floor directly.

Build the next-axis-after-v9 matrix bootstrap:

```bash
python3 scripts/build_next_axis_after_v9_matrix_bootstrap.py \
  --output-dir outputs/next_axis_after_v9_matrix_bootstrap/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v9_matrix_bootstrap.py \
  --run-dir outputs/next_axis_after_v9_matrix_bootstrap/default \
  --compare-run-dir outputs/next_axis_after_v9_matrix_bootstrap/default_repeat \
  --output-dir outputs/next_axis_after_v9_matrix_bootstrap/repeatability_default
```

Main outputs:

- `next_axis_after_v9_matrix_plan.json`
- `next_axis_after_v9_matrix_definition.json`
- `next_axis_after_v9_matrix_readiness_summary.json`
- `materialized_next_axis_after_v9_matrix/`
- `next_axis_after_v9_input_contract.json`
- `next_axis_after_v9_bootstrap_summary.json`

The current bootstrap produces `next_axis_after_v9_real_experiment_matrix_v10`, which adds `fusion_cell_refined_support_ablation_floor_stress` on top of the explicit floor-probe stack.

## Next-Axis-After-v9 Matrix Dry Run

The repository now includes a next-axis-after-v9 dry-run stage. The current emphasis is to convert `next_axis_after_v9_real_experiment_matrix_v10` into a first executable refined-fusion-support-floor-stress-aware matrix object.

Build the next-axis-after-v9 matrix dry-run:

```bash
.venv/bin/python scripts/build_next_axis_after_v9_matrix_dry_run.py \
  --output-dir outputs/next_axis_after_v9_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v9_matrix_dry_run.py \
  --run-dir outputs/next_axis_after_v9_matrix_dry_run/default \
  --compare-run-dir outputs/next_axis_after_v9_matrix_dry_run/default_repeat \
  --output-dir outputs/next_axis_after_v9_matrix_dry_run/repeatability_default
```

Main outputs:

- `next_axis_after_v9_matrix_dry_run_summary.json`
- `next_axis_after_v9_matrix_dry_run_registry.json`
- `next_axis_after_v9_matrix_dry_run_preview.jsonl`
- `next_axis_after_v9_matrix_module_status.json`
- `next_axis_after_v9_matrix_cell_status.json`
- `materialized_next_axis_after_v9_matrix_inputs/`

This stage is meant to answer whether the explicit support-floor-stress cell can become a first-class executable matrix cell, not just remain a bootstrap definition.

## Next-Axis-After-v9 Matrix Execution

The repository now includes a next-axis-after-v9 execution stage. The current emphasis is to promote `fusion_cell_refined_support_ablation_floor_stress` into a real execution-layer artifact and compare it against floor-probe, support-ablation-sweep, support-ablation, support-sweep, refined, candidate, and summary views.

Build the next-axis-after-v9 matrix execution:

```bash
python3 scripts/build_next_axis_after_v9_matrix_execution.py \
  --output-dir outputs/next_axis_after_v9_matrix_execution/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v9_matrix_execution.py \
  --run-dir outputs/next_axis_after_v9_matrix_execution/default \
  --compare-run-dir outputs/next_axis_after_v9_matrix_execution/default_repeat \
  --output-dir outputs/next_axis_after_v9_matrix_execution/repeatability_default
```

Main outputs:

- `next_axis_after_v9_matrix_execution_run_summary.json`
- `next_axis_after_v9_matrix_execution_registry.json`
- `next_axis_after_v9_matrix_execution_metrics.json`
- `next_axis_after_v9_matrix_cell_metrics.csv`
- `next_axis_after_v9_matrix_fusion_cell_refined_support_ablation_floor_stress_summary.json`

This stage is meant to answer whether the explicit support floor still looks invariant once it is directly stressed.

## Post-v10 Matrix Analysis

The repository now includes a post-v10 matrix analysis stage. The current emphasis is to compare `fusion_cell_refined_support_ablation_floor_stress` against `fusion_cell_refined_support_ablation_floor_probe`, `fusion_cell_refined_support_ablation_sweep`, `fusion_cell_refined_support_ablation`, `fusion_cell_refined_support_sweep`, `fusion_cell_refined`, `fusion_cell_candidate`, and `fusion_summary`.

Build the post-v10 matrix analysis:

```bash
python3 scripts/build_post_v10_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_v10_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
python3 scripts/validate_post_v10_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_v10_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_v10_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_v10_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `next_axis_after_v9_matrix_analysis_summary.json`
- `fusion_floor_stress_vs_floor_probe_comparison.json`
- `fusion_floor_stress_vs_support_ablation_sweep_comparison.json`
- `fusion_floor_stress_vs_support_ablation_comparison.json`
- `fusion_floor_stress_vs_support_sweep_comparison.json`
- `fusion_floor_stress_vs_refined_comparison.json`
- `fusion_floor_stress_vs_candidate_comparison.json`
- `fusion_floor_stress_vs_summary_comparison.json`
- `v10_vs_v9_matrix_comparison.json`
- `v10_matrix_blocker_summary.json`
- `v10_matrix_tradeoff_matrix.csv`
- `next_axis_after_v9_matrix_next_step_recommendation.json`

This stage is meant to answer whether explicit support-floor stress invariance has now been clearly exposed, not just whether one more matrix cell can run.

## Next-Axis-After-v10 Matrix Bootstrap

The repository now includes a next-axis-after-v10 bootstrap stage. The current recommendation is to keep dataset/model fixed and sweep the explicit support-floor-stress cell directly.

Build the next-axis-after-v10 matrix bootstrap:

```bash
python3 scripts/build_next_axis_after_v10_matrix_bootstrap.py \
  --output-dir outputs/next_axis_after_v10_matrix_bootstrap/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v10_matrix_bootstrap.py \
  --run-dir outputs/next_axis_after_v10_matrix_bootstrap/default \
  --compare-run-dir outputs/next_axis_after_v10_matrix_bootstrap/default_repeat \
  --output-dir outputs/next_axis_after_v10_matrix_bootstrap/repeatability_default
```

Main outputs:

- `next_axis_after_v10_matrix_plan.json`
- `next_axis_after_v10_matrix_definition.json`
- `next_axis_after_v10_matrix_readiness_summary.json`
- `materialized_next_axis_after_v10_matrix/`
- `next_axis_after_v10_input_contract.json`
- `next_axis_after_v10_bootstrap_summary.json`

The current bootstrap produces `next_axis_after_v10_real_experiment_matrix_v11`, which adds `fusion_cell_refined_support_ablation_floor_stress_sweep` on top of the explicit floor-stress stack.

## Next-Axis-After-v10 Matrix Dry Run

The repository now includes a next-axis-after-v10 dry-run stage. The current emphasis is to convert `next_axis_after_v10_real_experiment_matrix_v11` into a first executable refined-fusion-support-floor-stress-sweep-aware matrix object.

Minimal CLI:

```bash
.venv/bin/python scripts/build_next_axis_after_v10_matrix_dry_run.py \
  --output-dir outputs/next_axis_after_v10_matrix_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v10_matrix_dry_run.py \
  --run-dir outputs/next_axis_after_v10_matrix_dry_run/default \
  --compare-run-dir outputs/next_axis_after_v10_matrix_dry_run/default_repeat \
  --output-dir outputs/next_axis_after_v10_matrix_dry_run/repeatability_default
```

Main outputs:

- `next_axis_after_v10_matrix_dry_run_summary.json`
- `next_axis_after_v10_matrix_dry_run_registry.json`
- `next_axis_after_v10_matrix_dry_run_preview.jsonl`
- `next_axis_after_v10_matrix_module_status.json`
- `next_axis_after_v10_matrix_cell_status.json`
- `materialized_next_axis_after_v10_matrix_inputs/`

## Next-Axis-After-v10 Matrix Execution

The repository now includes a next-axis-after-v10 execution stage. The current emphasis is to promote `fusion_cell_refined_support_ablation_floor_stress_sweep` into a real execution-layer artifact.

Minimal CLI:

```bash
python3 scripts/build_next_axis_after_v10_matrix_execution.py \
  --output-dir outputs/next_axis_after_v10_matrix_execution/default
```

Optional validation CLI:

```bash
python3 scripts/validate_next_axis_after_v10_matrix_execution.py \
  --run-dir outputs/next_axis_after_v10_matrix_execution/default \
  --compare-run-dir outputs/next_axis_after_v10_matrix_execution/default_repeat \
  --output-dir outputs/next_axis_after_v10_matrix_execution/repeatability_default
```

Main outputs:

- `next_axis_after_v10_matrix_execution_run_summary.json`
- `next_axis_after_v10_matrix_execution_registry.json`
- `next_axis_after_v10_matrix_execution_metrics.json`
- `next_axis_after_v10_matrix_cell_metrics.csv`
- `next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_floor_stress_sweep_summary.json`

## Post-v11 Matrix Analysis

The repository now includes a post-v11 analysis stage. This stage intentionally decides whether the same fusion axis still has meaningful headroom, or whether the project should pivot to a model-axis probe.

Minimal CLI:

```bash
python3 scripts/build_post_v11_real_experiment_matrix_analysis.py \
  --output-dir outputs/post_v11_real_experiment_matrix_analysis/default
```

Optional validation CLI:

```bash
python3 scripts/validate_post_v11_real_experiment_matrix_analysis.py \
  --run-dir outputs/post_v11_real_experiment_matrix_analysis/default \
  --compare-run-dir outputs/post_v11_real_experiment_matrix_analysis/default_repeat \
  --output-dir outputs/post_v11_real_experiment_matrix_analysis/repeatability_default
```

Main outputs:

- `next_axis_after_v10_matrix_analysis_summary.json`
- `fusion_floor_stress_sweep_vs_floor_stress_comparison.json`
- `fusion_floor_stress_sweep_vs_floor_probe_comparison.json`
- `fusion_floor_stress_sweep_vs_support_ablation_sweep_comparison.json`
- `v11_vs_v10_matrix_comparison.json`
- `next_axis_after_v10_matrix_next_step_recommendation.json`

The current recommendation pivots away from continuing the same fusion-axis bootstrap chain and instead chooses `bootstrap_model_axis_1p5b`.

## Model-Axis 1.5B Bootstrap

The repository now includes a model-axis 1.5B bootstrap stage. This is the first deliberate probe of whether the current ready-local real-experiment matrix contract can migrate from `pilot_distilgpt2_hf` to a larger 1.5B-class model without changing the dataset contract.

Minimal CLI:

```bash
python3 scripts/build_model_axis_1p5b_bootstrap.py \
  --output-dir outputs/model_axis_1p5b_bootstrap/default
```

Optional validation CLI:

```bash
python3 scripts/validate_model_axis_1p5b_bootstrap.py \
  --run-dir outputs/model_axis_1p5b_bootstrap/default \
  --compare-run-dir outputs/model_axis_1p5b_bootstrap/default_repeat \
  --output-dir outputs/model_axis_1p5b_bootstrap/repeatability_default
```

Main outputs:

- `model_axis_1p5b_candidate_selection.json`
- `model_axis_1p5b_bootstrap_plan.json`
- `model_axis_1p5b_readiness_summary.json`
- `model_axis_1p5b_matrix_definition.json`
- `materialized_model_axis_1p5b_inputs/`
- `model_axis_1p5b_bootstrap_summary.json`

The current bootstrap selects `pilot_small_hf -> Qwen/Qwen2.5-1.5B-Instruct`, and the repository now includes a project-local snapshot wired to:

- `/home/lh/TriScope-LLM/local_models/Qwen2.5-1.5B-Instruct`
- `configs/models.yaml -> pilot_small_hf.local_path`

As a result, the current bootstrap now reports `ready_local = true` and `ready_run = true`.

## Model-Axis 1.5B Dry Run

The repository now includes a model-axis 1.5B dry-run stage. This stage validates the full matrix contract, reuses the existing route query inputs, and records whether the local 1.5B route is actually ready to enter runtime execution.

Minimal CLI:

```bash
python3 scripts/build_model_axis_1p5b_dry_run.py \
  --output-dir outputs/model_axis_1p5b_dry_run/default \
  --seed 42
```

Optional validation CLI:

```bash
python3 scripts/validate_model_axis_1p5b_dry_run.py \
  --run-dir outputs/model_axis_1p5b_dry_run/default \
  --compare-run-dir outputs/model_axis_1p5b_dry_run/default_repeat \
  --output-dir outputs/model_axis_1p5b_dry_run/repeatability_default
```

Main outputs:

- `model_axis_1p5b_dry_run_summary.json`
- `model_axis_1p5b_dry_run_registry.json`
- `model_axis_1p5b_dry_run.log`
- `model_axis_1p5b_cell_status.json`
- `model_axis_1p5b_module_status.json`
- `model_axis_1p5b_execution_gate.json`

The current dry-run is now `PASS`:

- `ready_local = true`
- `ready_run = true`
- `route_b_status = READY`
- `route_c_status = READY`
- `fusion_summary_status = READY`
- `allow_107_execution = true`

## Model-Axis 1.5B Minimal Execution

The repository now includes the first true 1.5B model-axis minimal execution stage. This stage keeps the scope intentionally small by executing only `route_b`, but it does so with real local `Qwen/Qwen2.5-1.5B-Instruct` inference rather than a mock or config-only placeholder.

Minimal CLI:

```bash
python3 scripts/build_model_axis_1p5b_execution.py \
  --output-dir outputs/model_axis_1p5b_execution/default \
  --seed 42 \
  --target-budget 32
```

Optional validation CLI:

```bash
python3 scripts/validate_model_axis_1p5b_execution.py \
  --run-dir outputs/model_axis_1p5b_execution/default \
  --compare-run-dir outputs/model_axis_1p5b_execution/default_repeat \
  --output-dir outputs/model_axis_1p5b_execution/repeatability_default
```

Main outputs:

- `model_axis_1p5b_execution_selection.json`
- `model_axis_1p5b_execution_plan.json`
- `model_axis_1p5b_execution_readiness_summary.json`
- `model_axis_1p5b_execution_run_summary.json`
- `model_axis_1p5b_execution_metrics.json`
- `model_axis_1p5b_route_b_summary.json`
- `model_axis_1p5b_route_b_logistic_summary.json`
- `model_axis_1p5b_route_b_run_summary.json`

The current 1.5B minimal execution is an honest `PARTIAL` success:

- it **does** use local 1.5B weights
- it **does** enter real model inference
- it **does** finish the three probe layers plus route_b fusion/dataset construction
- it currently stops at `PARTIAL_SINGLE_CLASS_LABEL_COLLAPSE` because the 32-row more-natural labeled subset collapses to one class, so logistic fitting cannot yet complete

## Post Model-Axis 1.5B Analysis

The repository now includes a post-analysis stage for the first 1.5B model-axis run. This stage asks whether the project has truly opened a model portability path beyond `pilot_distilgpt2_hf`, and whether the next step should be “go bigger” or “stabilize the first 1.5B route.”

Minimal CLI:

```bash
python3 scripts/build_post_model_axis_1p5b_analysis.py \
  --output-dir outputs/model_axis_1p5b_analysis/default
```

Optional validation CLI:

```bash
python3 scripts/validate_post_model_axis_1p5b_analysis.py \
  --run-dir outputs/model_axis_1p5b_analysis/default \
  --compare-run-dir outputs/model_axis_1p5b_analysis/default_repeat \
  --output-dir outputs/model_axis_1p5b_analysis/repeatability_default
```

Main outputs:

- `model_axis_1p5b_analysis_summary.json`
- `model_axis_1p5b_vs_lightweight_comparison.json`
- `model_axis_1p5b_next_step_recommendation.json`

The current analysis concludes:

- the 1.5B model-axis entry is now genuinely open
- the current gain is portability / executability proof, not yet stable comparative scoring
- the next recommended step is `stabilize_model_axis_1p5b_route_b_label_balance`

## Immediate Next Step

The next planned stage after opening the 1.5B model-axis is:

- keep the focus on `Qwen/Qwen2.5-1.5B-Instruct`
- do **not** jump to 3B / 7B yet
- stabilize `route_b` on 1.5B so the more-natural labeled subset no longer collapses to one class
- only after that decide whether to expand to `route_c`, `fusion_summary`, or a larger model

## Model-Axis 1.5B Route-B Stabilization

The repository now includes a dedicated stabilization stage for the 1.5B route_b single-class collapse issue.

Minimal CLI:

```bash
python3 scripts/build_model_axis_1p5b_route_b_stabilization.py \
  --output-dir outputs/model_axis_1p5b_route_b_stabilization/default \
  --seed 42
```

Main outputs:

- `route_b_label_collapse_diagnosis.json`
- `route_b_label_balance_recovery_plan.json`
- `route_b_selection_knobs_summary.json`
- `route_b_balanced_candidate_dataset.jsonl`
- `route_b_balanced_candidate_summary.json`
- `route_b_label_balance_precheck.json`

Current stabilization precheck shows route_b candidate class balance restored to two classes (`label_0=30`, `label_1=2`) and unlocks stabilized rerun.

## Model-Axis 1.5B Route-B Stable Execution

The repository now includes a stabilized rerun stage for 1.5B route_b that keeps the original route contract while enabling robust illumination option parsing inside label construction.

Minimal CLI:

```bash
python3 scripts/build_model_axis_1p5b_route_b_stable_execution.py \
  --output-dir outputs/model_axis_1p5b_route_b_stable_execution/default \
  --seed 42 \
  --target-budget 32
```

Main outputs:

- `route_b_stable_execution_selection.json`
- `route_b_stable_execution_plan.json`
- `route_b_stable_execution_readiness_summary.json`
- `route_b_stable_execution_run_summary.json`
- `route_b_stable_execution_metrics.json`
- `route_b_stable_summary.json`
- `route_b_stable_logistic_summary.json`

Current stabilized rerun status:

- `used_local_weights=true`
- `entered_model_inference=true`
- `execution_status=FULL_EXECUTE`
- `class_balance={label_0:30,label_1:2}`
- `route_b_stable_logistic_summary.summary_status=PASS`

## Post-Stabilized 1.5B Analysis

The repository now includes a post-stabilized analysis stage that compares lightweight baseline, original 107 run, and stabilized 110 run.

Minimal CLI:

```bash
python3 scripts/build_post_stabilized_model_axis_1p5b_analysis.py \
  --output-dir outputs/model_axis_1p5b_stable_analysis/default
```

Main outputs:

- `model_axis_1p5b_stable_analysis_summary.json`
- `model_axis_1p5b_stable_vs_original_comparison.json`
- `model_axis_1p5b_stable_next_step_recommendation.json`

Current recommendation:

- `expand_route_c_after_one_route_b_stability_confirmation`
- do not switch to 3B / 7B yet
- do not expand dataset/proxy substrate in the immediate follow-up

## Model-Axis 1.5B Route-B Stability Confirmation

The repository now includes a lightweight stability confirmation stage for stabilized 1.5B route_b.

Minimal CLI:

```bash
python3 scripts/build_model_axis_1p5b_route_b_stability.py \
  --output-dir outputs/model_axis_1p5b_route_b_stability/default
```

Main outputs:

- `route_b_stability_protocol.json`
- `route_b_stability_success_criteria.json`
- `route_b_stability_run_plan.json`
- `route_b_stability_run_registry.json`
- `route_b_stability_results.jsonl`
- `route_b_stability_summary.json`
- `route_b_stability_comparison.csv`

Current stability result:

- all configured confirmation runs kept two classes
- all configured confirmation runs kept logistic `PASS`
- `stability_established=true`
- current scenario set is exactly:
  - `seed=42, target_budget=32`
  - `seed=43, target_budget=32`
  - `seed=42, target_budget=31`
  - `seed=42, target_budget=33`

Recovery / resume pointers:

- primary summary:
  - `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_summary.json`
- run registry:
  - `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_run_registry.json`
- per-run artifacts:
  - `outputs/model_axis_1p5b_route_b_stability/default/runs/<run_id>/...`

## Model-Axis 1.5B Route-C Portability Bootstrap

The repository now includes a route_c portability bootstrap stage for 1.5B that materializes route_c-ready contracts and runs a lightweight precheck.

Minimal CLI:

```bash
python3 scripts/build_model_axis_1p5b_route_c_portability.py \
  --output-dir outputs/model_axis_1p5b_route_c_portability/default \
  --precheck-budget 12
```

Main outputs:

- `route_c_portability_contract.json`
- `route_c_portability_selection.json`
- `route_c_portability_readiness_summary.json`
- `route_c_portability_run_summary.json`
- `route_c_portability_module_status.json`
- `route_c_portability_cell_status.json`

Current portability result:

- contract compatibility is `true`
- readiness flags (`ready_dry_run`, `ready_run`) are `true`
- precheck execution is currently `PARTIAL` due to small-subset label collapse risk (`Benchmark-truth-leaning dataset must contain at least two classes.`)
- current bootstrap uses:
  - `precheck_budget=12`
  - `selected_base_sample_count=12`
  - `selected_labeled_contract_count=24`
  - `expected_reference_contract_class_balance={label_0: 15, label_1: 9}`

Recovery / resume pointers:

- portability contract:
  - `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_contract.json`
- portability readiness:
  - `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_readiness_summary.json`
- materialized inputs:
  - `outputs/model_axis_1p5b_route_c_portability/default/materialized_route_c_portability_inputs/`
- latest precheck snapshot:
  - `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_run_summary.json`
- module / cell status:
  - `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_module_status.json`
  - `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_cell_status.json`

## Historical Resume Point After 112/113

If you want to continue from the current 112/113 state without re-orienting:

1. Re-read:
   - `.plans/112-confirm-model-axis-1p5b-route-b-stability.md`
   - `.plans/113-route-c-portability-bootstrap.md`
2. Reconfirm the stabilized baseline:
   - `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_summary.json`
3. Reopen the route_c bridge state:
   - `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_readiness_summary.json`
   - `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_run_summary.json`
4. Continue from the current bottleneck:
   - keep `pilot_small_hf -> Qwen/Qwen2.5-1.5B-Instruct`
   - keep the 1.5B model axis
   - do not return to fusion-axis expansion
   - first solve the route_c small-budget label single-class risk before attempting route_c minimal execution

## Model-Axis 1.5B Route-C Label-Balance Stabilization

The repository now includes a dedicated stabilization stage for the 1.5B route_c single-class precheck issue.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_stabilization.py \
  --output-dir outputs/model_axis_1p5b_route_c_stabilization/default \
  --seed 42 \
  --target-base-budget 12
```

Main outputs:

- `route_c_label_collapse_diagnosis.json`
- `route_c_label_balance_recovery_plan.json`
- `route_c_selection_knobs_summary.json`
- `route_c_balanced_candidate_dataset.jsonl`
- `route_c_balanced_candidate_summary.json`
- `route_c_label_balance_precheck.json`

Current stabilization result:

- 113 的 route_c 单类塌缩已经被明确拆成双因素：
  - strict parser 把前缀回答全漏掉，导致 `24/24 -> label_1`
  - 修复 parser 后，原 12-base 子集又在真实 1.5B 输出下变成 `24/24 -> label_0`
- 114 已完成一次 1.5B full labeled scan：
  - `full_scan_contract_count = 140`
  - `full_scan_class_balance = {label_0: 139, label_1: 1}`
- 当前已构造出可复用的最小非单类 candidate：
  - `selected_base_ids = [csqa-pilot-021, csqa-pilot-001, ..., csqa-pilot-011]`
  - `class_balance = {label_0: 23, label_1: 1}`
  - `ready_for_stable_portability_rerun = true`

## Model-Axis 1.5B Route-C Stable Portability Precheck

The repository now includes a stabilized route_c portability rerun that reuses the 114 subset and repairs truth-leaning label construction with robust prefix-aware parsing.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_stable_portability.py \
  --output-dir outputs/model_axis_1p5b_route_c_stable_portability/default \
  --seed 42 \
  --label-threshold 0.5
```

Main outputs:

- `route_c_stable_portability_selection.json`
- `route_c_stable_portability_plan.json`
- `route_c_stable_portability_readiness_summary.json`
- `route_c_stable_portability_run_summary.json`
- `route_c_stable_portability_module_status.json`
- `route_c_stable_portability_cell_status.json`

Current stable portability result:

- `summary_status = PASS`
- `execution_status = PASS_WITH_LIMITATIONS`
- `used_local_weights = true`
- `entered_model_inference = true`
- `ready_run = true`
- `label_parse_mode = robust_prefix`
- `class_balance = {label_0: 23, label_1: 1}`

This means route_c is no longer blocked at the old precheck gate, but the positive class is still extremely sparse.

## Model-Axis 1.5B Route-C Minimal Execution

The repository now includes the first true 1.5B route_c minimal execution stage.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_execution.py \
  --output-dir outputs/model_axis_1p5b_route_c_execution/default \
  --seed 42 \
  --label-threshold 0.5
```

Main outputs:

- `route_c_execution_selection.json`
- `route_c_execution_plan.json`
- `route_c_execution_readiness_summary.json`
- `route_c_execution_run_summary.json`
- `route_c_execution_metrics.json`
- `model_axis_1p5b_route_c_summary.json`
- `model_axis_1p5b_route_c_logistic_summary.json`

Current route_c execution result:

- `summary_status = PASS`
- `execution_status = FULL_EXECUTE`
- `used_local_weights = true`
- `entered_model_inference = true`
- `class_balance = {label_0: 23, label_1: 1}`
- `num_rows = 24`
- `num_predictions = 24`

The key honest conclusion is:

- route_c has now genuinely entered local 1.5B execution semantics
- but the positive class remains only `1/24`, so the execution path is open while statistical stability is still thin

## 117. Analyze Model-Axis 1.5B Route-C Sparsity

The repository now includes a dedicated route_c sparsity analysis stage that explains why the current route_c execution is so positive-sparse.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_sparsity.py \
  --output-dir outputs/model_axis_1p5b_route_c_sparsity/default
```

Main outputs:

- `route_c_sparsity_hypotheses.json`
- `route_c_sparsity_diagnosis_protocol.json`
- `route_c_sparsity_signal_sources.json`
- `route_c_sparsity_analysis_summary.json`
- `route_c_positive_support_breakdown.json`
- `route_c_label_distribution_by_sample.csv`
- `route_c_sparsity_next_step_recommendation.json`

Current route_c sparsity conclusion:

- parser is no longer the current primary blocker
- selection matters, but it is only a gatekeeper, not the full explanation
- the dominant driver is current 1.5B model behavior under the benchmark-truth-leaning label mechanism
- the full known 140-contract universe is already `139/1`, so blind budget expansion is unlikely to add many positives
- current recommendation is:
  - `confirm_route_c_stability_before_refinement`

## 118. Confirm Model-Axis 1.5B Route-C Stability

The repository now includes a lightweight route_c stability confirmation stage that checks whether the lone positive-support anchor is repeatable.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_stability.py \
  --output-dir outputs/model_axis_1p5b_route_c_stability/default \
  --label-threshold 0.5
```

Main outputs:

- `route_c_stability_protocol.json`
- `route_c_stability_success_criteria.json`
- `route_c_stability_run_plan.json`
- `route_c_stability_run_registry.json`
- `route_c_stability_results.jsonl`
- `route_c_stability_summary.json`
- `route_c_stability_comparison.csv`

Current route_c stability result:

- `total_runs = 3`
- `all_two_classes = true`
- `all_logistic_pass = true`
- `all_positive_support_present = true`
- `baseline_positive_preserved_all_runs = true`
- `stability_established = true`
- `stability_characterization = stable_but_sparse`

The key honest conclusion is:

- route_c is not merely “barely runnable”; it is repeatably runnable on the current stabilized subset
- but the positive class is still concentrated on the same single anchor:
  - `csqa-pilot-021__targeted`

## 119. Route-C Budget Expansion Or Selection Refinement

The repository now includes a route_c refinement comparison stage that decides whether the next honest move is budget expansion or selection refinement.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_refinement.py \
  --output-dir outputs/model_axis_1p5b_route_c_refinement/default
```

Main outputs:

- `route_c_refinement_options_comparison.json`
- `route_c_refinement_recommendation.json`
- `route_c_refined_selection_registry.json`
- `route_c_refined_candidate_dataset.jsonl`
- `route_c_refined_candidate_summary.json`

Current route_c refinement conclusion:

- `recommended_next_step = selection_refinement_first`
- budget expansion is not the preferred first move because the current full 140-contract scan is already `139/1`
- a smaller positive-anchor-preserving candidate can improve positive density from:
  - `1/24 = 0.0417`
  - to `1/8 = 0.125`
  - without reopening new axes

## 120. Route-C Refined Candidate Execution

The repository now includes a real 1.5B refined route_c execution stage that promotes the 119 refined candidate from “preview subset” to a true local execution.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_refined_execution.py \
  --output-dir outputs/model_axis_1p5b_route_c_refined_execution/default \
  --seed 42 \
  --label-threshold 0.5
```

Main outputs:

- `route_c_refined_execution_selection.json`
- `route_c_refined_execution_plan.json`
- `route_c_refined_execution_readiness_summary.json`
- `route_c_refined_execution_run_summary.json`
- `route_c_refined_execution_metrics.json`
- `model_axis_1p5b_route_c_refined_summary.json`
- `model_axis_1p5b_route_c_refined_logistic_summary.json`

Current refined execution result:

- `summary_status = PASS`
- `execution_status = FULL_EXECUTE`
- `used_local_weights = true`
- `entered_model_inference = true`
- `class_balance = {label_0: 7, label_1: 1}`
- `num_rows = 8`
- `refined_density = 0.125`
- `density_gain_vs_original = 3.0`

The key honest conclusion is:

- refined selection did not create new positives
- but it did turn route_c from `1/24` density into a true `1/8` density execution while keeping the same real positive anchor

## 121. Route-C Refined Candidate Stability

The repository now includes a refined route_c stability confirmation stage that tests whether the 120 density improvement is repeatable.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_refined_stability.py \
  --output-dir outputs/model_axis_1p5b_route_c_refined_stability/default \
  --label-threshold 0.5
```

Main outputs:

- `route_c_refined_stability_protocol.json`
- `route_c_refined_stability_success_criteria.json`
- `route_c_refined_stability_run_plan.json`
- `route_c_refined_stability_run_registry.json`
- `route_c_refined_stability_results.jsonl`
- `route_c_refined_stability_summary.json`
- `route_c_refined_stability_comparison.csv`

Current refined stability result:

- `total_runs = 3`
- `all_two_classes = true`
- `all_logistic_pass = true`
- `refined_density_preserved_all_runs = true`
- `reference_anchor_preserved_all_runs = true`
- `stability_established = true`
- `stability_characterization = better_and_stable`

The key honest conclusion is:

- the refined route_c candidate is not merely denser once
- it is repeatably denser than the original 116 baseline while staying on the same local 1.5B model axis

## 122. Post Route-C Refined Analysis

The repository now includes a post-refinement route_c analysis stage that compares the original and refined route_c baselines.

Minimal CLI:

```bash
.venv/bin/python scripts/build_post_route_c_refined_analysis.py \
  --output-dir outputs/model_axis_1p5b_route_c_refined_analysis/default
```

Main outputs:

- `route_c_refined_analysis_summary.json`
- `route_c_original_vs_refined_comparison.json`
- `route_c_refined_next_step_recommendation.json`

Current refined analysis conclusion:

- original route_c:
  - `density = 1/24 = 0.041666...`
  - `stability_characterization = stable_but_sparse`
- refined route_c:
  - `density = 1/8 = 0.125`
  - `stability_characterization = better_and_stable`
- `density_gain_ratio = 3.0`
- current recommendation is:
  - `continue_refined_selection_before_any_budget_expansion`

## Current Resume Point

If you want to continue from the current 120/121/122 state without re-orienting:

1. Re-read:
   - `.plans/120-route-c-refined-candidate-execution.md`
   - `.plans/121-route-c-refined-candidate-stability.md`
   - `.plans/122-post-route-c-refined-analysis.md`
2. Reopen the refined execution baseline:
   - `outputs/model_axis_1p5b_route_c_refined_execution/default/route_c_refined_execution_run_summary.json`
   - `outputs/model_axis_1p5b_route_c_refined_execution/default/route_c_refined_execution_metrics.json`
   - `outputs/model_axis_1p5b_route_c_refined_execution/default/model_axis_1p5b_route_c_refined_logistic_summary.json`
3. Reconfirm the refined stability state:
   - `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_summary.json`
   - `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_run_registry.json`
   - `outputs/model_axis_1p5b_route_c_refined_stability/default/route_c_refined_stability_comparison.csv`
4. Resume from the current refined-analysis state:
   - `outputs/model_axis_1p5b_route_c_refined_analysis/default/route_c_refined_analysis_summary.json`
   - `outputs/model_axis_1p5b_route_c_refined_analysis/default/route_c_original_vs_refined_comparison.json`
   - `outputs/model_axis_1p5b_route_c_refined_analysis/default/route_c_refined_next_step_recommendation.json`
5. Keep the next-step boundary disciplined:
   - stay on `pilot_small_hf -> Qwen/Qwen2.5-1.5B-Instruct`
   - do not return to fusion-axis expansion
   - do not jump to 3B / 7B yet
   - next value is more likely to come from continuing refined route_c selection than from blind budget expansion or opening a new axis

## 123. Anchor-Aware Route-C Refined Follow-up

The repository now includes an anchor-aware route_c follow-up stage that builds a denser candidate around the single stable positive anchor `csqa-pilot-021__targeted`.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_anchor_followup.py \
  --output-dir outputs/model_axis_1p5b_route_c_anchor_followup/default
```

Main outputs:

- `route_c_anchor_profile.json`
- `route_c_anchor_neighbor_analysis.json`
- `route_c_anchor_selection_strategy.json`
- `route_c_anchor_followup_selection_registry.json`
- `route_c_anchor_followup_candidate_dataset.jsonl`
- `route_c_anchor_followup_candidate_summary.json`
- `route_c_anchor_followup_precheck.json`

Current anchor-aware follow-up result:

- `anchor_base_sample_id = csqa-pilot-021`
- `selected_neighbor_base_ids = ["csqa-pilot-002", "csqa-pilot-005"]`
- `selected_contract_count = 6`
- `class_balance = {label_0: 5, label_1: 1}`
- `anchor_followup_density = 1/6 = 0.166666...`
- `density_gain_vs_refined = 1.333333...`
- `worth_executing = true`

The key honest conclusion is:

- anchor-aware follow-up still does not create a second positive anchor
- but it does improve density beyond the `1/8` refined baseline without reopening blind budget expansion

## 124. Anchor-Aware Route-C Refined Execution

The repository now includes a real 1.5B route_c anchor-aware execution stage that promotes the 123 follow-up candidate into a true local execution.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_anchor_execution.py \
  --output-dir outputs/model_axis_1p5b_route_c_anchor_execution/default \
  --seed 42 \
  --label-threshold 0.5
```

Main outputs:

- `route_c_anchor_execution_selection.json`
- `route_c_anchor_execution_plan.json`
- `route_c_anchor_execution_readiness_summary.json`
- `route_c_anchor_execution_run_summary.json`
- `route_c_anchor_execution_metrics.json`
- `model_axis_1p5b_route_c_anchor_summary.json`
- `model_axis_1p5b_route_c_anchor_logistic_summary.json`

Current anchor-aware execution result:

- `summary_status = PASS`
- `execution_status = FULL_EXECUTE`
- `used_local_weights = true`
- `entered_model_inference = true`
- `class_balance = {label_0: 5, label_1: 1}`
- `num_rows = 6`
- `anchor_density = 0.166666...`
- `density_gain_vs_original = 4.0`
- `density_gain_vs_refined = 1.333333...`

The key honest conclusion is:

- anchor-aware route_c is now a real execution object, not just a follow-up idea
- it improves density beyond the `1/8` refined baseline
- but the gain still comes from the same single positive anchor

## 125. Post Anchor-Aware Route-C Analysis

The repository now includes a post anchor-aware route_c analysis stage that compares original, refined, and anchor-aware route_c.

Minimal CLI:

```bash
.venv/bin/python scripts/build_post_route_c_anchor_analysis.py \
  --output-dir outputs/model_axis_1p5b_route_c_anchor_analysis/default
```

Main outputs:

- `route_c_anchor_analysis_summary.json`
- `route_c_original_refined_anchor_comparison.json`
- `route_c_anchor_next_step_recommendation.json`

Current anchor-aware analysis conclusion:

- original route_c:
  - `density = 1/24 = 0.041666...`
  - `characterization = stable_but_sparse`
- refined route_c:
  - `density = 1/8 = 0.125`
  - `stability_characterization = better_and_stable`
- anchor-aware route_c:
  - `density = 1/6 = 0.166666...`
  - `density_gain_vs_refined = 1.333333...`
  - `anchor_adds_new_positive_support = false`
- current recommendation is:
  - `confirm_anchor_aware_route_c_stability_before_any_budget_expansion`

## Current Resume Point

If you want to continue from the current 123/124/125 state without re-orienting:

1. Re-read:
   - `.plans/123-anchor-aware-route-c-refined-followup.md`
   - `.plans/124-anchor-aware-route-c-refined-execution.md`
   - `.plans/125-post-route-c-refined-analysis.md`
2. Reopen the anchor-aware follow-up artifacts:
   - `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_profile.json`
   - `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_neighbor_analysis.json`
   - `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_followup_candidate_summary.json`
   - `outputs/model_axis_1p5b_route_c_anchor_followup/default/route_c_anchor_followup_precheck.json`
3. Reopen the anchor-aware execution baseline:
   - `outputs/model_axis_1p5b_route_c_anchor_execution/default/route_c_anchor_execution_run_summary.json`
   - `outputs/model_axis_1p5b_route_c_anchor_execution/default/route_c_anchor_execution_metrics.json`
   - `outputs/model_axis_1p5b_route_c_anchor_execution/default/model_axis_1p5b_route_c_anchor_logistic_summary.json`
4. Resume from the current anchor-aware analysis state:
   - `outputs/model_axis_1p5b_route_c_anchor_analysis/default/route_c_anchor_analysis_summary.json`
   - `outputs/model_axis_1p5b_route_c_anchor_analysis/default/route_c_original_refined_anchor_comparison.json`
   - `outputs/model_axis_1p5b_route_c_anchor_analysis/default/route_c_anchor_next_step_recommendation.json`
5. Keep the next-step boundary disciplined:
   - stay on `pilot_small_hf -> Qwen/Qwen2.5-1.5B-Instruct`
   - do not return to fusion-axis expansion
   - do not jump to 3B / 7B
   - do not use blind budget expansion as the next move

## 126. Confirm Anchor-Aware Route-C Stability

The repository now includes an anchor-aware route_c stability stage that confirms whether the denser `1/6` anchor-aware slice holds up under lightweight reruns.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_anchor_stability.py \
  --output-dir outputs/model_axis_1p5b_route_c_anchor_stability/default \
  --label-threshold 0.5
```

Main outputs:

- `route_c_anchor_stability_protocol.json`
- `route_c_anchor_stability_success_criteria.json`
- `route_c_anchor_stability_run_plan.json`
- `route_c_anchor_stability_run_registry.json`
- `route_c_anchor_stability_results.jsonl`
- `route_c_anchor_stability_summary.json`
- `route_c_anchor_stability_comparison.csv`

Current anchor-aware stability conclusion:

- `total_runs = 3`
- `all_two_classes = true`
- `all_logistic_pass = true`
- `anchor_density_preserved_all_runs = true`
- `reference_anchor_preserved_all_runs = true`
- `density_not_worse_than_refined_all_runs = true`
- `stability_established = true`
- `stability_characterization = better_and_stable`

The key honest conclusion is:

- anchor-aware route_c is no longer just denser on one run
- it is now confirmed as a denser and stable working slice
- but it still preserves the same single positive anchor

## 127. Post Anchor-Aware Route-C Stability Analysis

The repository now includes a post anchor-aware stability analysis stage that compares original / refined / anchor-aware / anchor-aware-stable route_c together.

Minimal CLI:

```bash
.venv/bin/python scripts/build_post_route_c_anchor_stability_analysis.py \
  --output-dir outputs/model_axis_1p5b_route_c_anchor_stability_analysis/default
```

Main outputs:

- `route_c_anchor_stability_analysis_summary.json`
- `route_c_refined_vs_anchor_stability_comparison.json`
- `route_c_anchor_stability_next_step_recommendation.json`

Current anchor-aware stability analysis conclusion:

- original route_c:
  - `density = 1/24 = 0.041666...`
  - `characterization = stable_but_sparse`
- refined route_c:
  - `density = 1/8 = 0.125`
  - `stability_characterization = better_and_stable`
- anchor-aware route_c:
  - `density = 1/6 = 0.166666...`
  - `anchor_stability_established = true`
  - `anchor_beats_refined_on_density = true`
- current recommendation is:
  - `selection_deepening_before_any_budget_expansion`

## 128. Anchor-Aware Route-C Selection Deepening or Budget Decision

The repository now includes an anchor-aware deepening decision stage that compares selection deepening against blind budget expansion and materializes a minimal next-step candidate.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_anchor_deepening.py \
  --output-dir outputs/model_axis_1p5b_route_c_anchor_deepening/default
```

Main outputs:

- `route_c_anchor_deepening_options_comparison.json`
- `route_c_anchor_deepening_recommendation.json`
- `route_c_anchor_deepened_selection_registry.json`
- `route_c_anchor_deepened_candidate_dataset.jsonl`
- `route_c_anchor_deepened_candidate_summary.json`

Current anchor-aware deepening conclusion:

- current recommendation is:
  - `selection_deepening_first`
- deepened candidate:
  - `selected_base_count = 4`
  - `selected_contract_count = 8`
  - `class_balance = {label_0: 7, label_1: 1}`
  - `deepened_density = 1/8 = 0.125`
  - `density_vs_anchor = 0.75`
  - `density_vs_refined_floor = 1.0`

The key honest conclusion is:

- deepening can add local thickness without dropping below the refined `1/8` floor
- but it does give up some of the anchor-aware `1/6` density advantage
- budget expansion is still not the honest next move under the current evidence

## 129. Deepened Route-C Candidate Execution

The repository now includes a real 1.5B deepened route_c execution stage that promotes the 128 deepened candidate into true model inference.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_deepened_execution.py \
  --output-dir outputs/model_axis_1p5b_route_c_deepened_execution/default \
  --seed 42 \
  --label-threshold 0.5
```

Main outputs:

- `route_c_deepened_execution_selection.json`
- `route_c_deepened_execution_plan.json`
- `route_c_deepened_execution_readiness_summary.json`
- `route_c_deepened_execution_run_summary.json`
- `route_c_deepened_execution_metrics.json`
- `model_axis_1p5b_route_c_deepened_summary.json`
- `model_axis_1p5b_route_c_deepened_logistic_summary.json`
- `route_c_deepened_positive_support_breakdown.json`
- `route_c_deepened_density_comparison.json`

Current deepened execution conclusion:

- `summary_status = PASS`
- `execution_status = FULL_EXECUTE`
- `used_local_weights = true`
- `entered_model_inference = true`
- `class_balance = {label_0: 7, label_1: 1}`
- `deepened_density = 0.125`
- `density_vs_refined = 1.0`
- `density_vs_anchor = 0.75`
- `reference_anchor_preserved = true`
- `baseline_upgrade_assessment = holds_refined_floor_but_fall_back_to_anchor_baseline`

The key honest conclusion is:

- deepened is truly executable on 1.5B local weights
- it keeps the refined density floor and anchor continuity
- but it does not beat the anchor-aware `1/6` baseline and does not add new positive support

## 130. Confirm Deepened Route-C Stability

The repository now includes a deepened route_c stability stage that checks whether the deepened floor-preserving behavior is repeatable.

Minimal CLI:

```bash
.venv/bin/python scripts/build_model_axis_1p5b_route_c_deepened_stability.py \
  --output-dir outputs/model_axis_1p5b_route_c_deepened_stability/default \
  --label-threshold 0.5
```

Main outputs:

- `route_c_deepened_stability_protocol.json`
- `route_c_deepened_stability_success_criteria.json`
- `route_c_deepened_stability_run_plan.json`
- `route_c_deepened_stability_run_registry.json`
- `route_c_deepened_stability_results.jsonl`
- `route_c_deepened_stability_summary.json`
- `route_c_deepened_stability_comparison.csv`

Current deepened stability conclusion:

- `total_runs = 3`
- `all_two_classes = true`
- `all_logistic_pass = true`
- `density_not_below_refined_all_runs = true`
- `reference_anchor_preserved_all_runs = true`
- `anchor_not_beaten_any_run = true`
- `adds_no_new_positive_support = true`
- `stability_established = true`
- `baseline_decision = should_fall_back_to_anchor_baseline`

The key honest conclusion is:

- deepened is repeatable as a refined-floor slice
- but it remains consistently weaker than anchor-aware density and adds no extra support
- current baseline decision should fall back to anchor-aware

## 131. Post Deepened Route-C Analysis And Baseline Decision

The repository now includes a post deepened analysis stage that compares original / refined / anchor-aware / deepened route_c together.

Minimal CLI:

```bash
.venv/bin/python scripts/build_post_route_c_deepened_analysis.py \
  --output-dir outputs/model_axis_1p5b_route_c_deepened_analysis/default
```

Main outputs:

- `route_c_deepened_analysis_summary.json`
- `route_c_original_refined_anchor_deepened_comparison.json`
- `route_c_deepened_next_step_recommendation.json`

Current deepened analysis conclusion:

- original route_c:
  - `density = 1/24 = 0.041666...`
- refined route_c:
  - `density = 1/8 = 0.125` (stable)
- anchor-aware route_c:
  - `density = 1/6 = 0.166666...` (stable)
- deepened route_c:
  - `density = 1/8 = 0.125` (stable but fallback decision)
- current working baseline:
  - `anchor-aware`
- current recommendation:
  - `keep_anchor_aware_baseline_and_only_consider_more_deepening`

The key honest conclusion is:

- route_c is now in a stable working state
- deepened adds thickness but does not yet justify replacing anchor-aware baseline
- budget expansion, 3B/7B, dataset-axis, and fusion-axis expansion remain out of scope

## Current Resume Point

If you want to continue from the current 129/130/131 state without re-orienting:

1. Re-read:
  - `.plans/129-deepened-route-c-candidate-execution.md`
  - `.plans/130-confirm-deepened-route-c-stability.md`
  - `.plans/131-post-deepened-route-c-analysis-and-baseline-decision.md`
2. Reopen the deepened execution artifacts:
  - `outputs/model_axis_1p5b_route_c_deepened_execution/default/route_c_deepened_execution_run_summary.json`
  - `outputs/model_axis_1p5b_route_c_deepened_execution/default/route_c_deepened_execution_metrics.json`
  - `outputs/model_axis_1p5b_route_c_deepened_execution/default/model_axis_1p5b_route_c_deepened_logistic_summary.json`
  - `outputs/model_axis_1p5b_route_c_deepened_execution/default/route_c_deepened_density_comparison.json`
3. Reopen the deepened stability artifacts:
  - `outputs/model_axis_1p5b_route_c_deepened_stability/default/route_c_deepened_stability_summary.json`
  - `outputs/model_axis_1p5b_route_c_deepened_stability/default/route_c_deepened_stability_run_registry.json`
  - `outputs/model_axis_1p5b_route_c_deepened_stability/default/route_c_deepened_stability_comparison.csv`
4. Reopen the final baseline decision artifacts:
  - `outputs/model_axis_1p5b_route_c_deepened_analysis/default/route_c_deepened_analysis_summary.json`
  - `outputs/model_axis_1p5b_route_c_deepened_analysis/default/route_c_original_refined_anchor_deepened_comparison.json`
  - `outputs/model_axis_1p5b_route_c_deepened_analysis/default/route_c_deepened_next_step_recommendation.json`
5. Keep the next-step boundary disciplined:
  - stay on `pilot_small_hf -> Qwen/Qwen2.5-1.5B-Instruct`
  - keep `anchor-aware` as current working baseline
  - only consider controlled deepening follow-up under the same guardrails
  - do not reopen blind budget expansion
  - do not jump to 3B / 7B
  - do not return to fusion-axis expansion yet
