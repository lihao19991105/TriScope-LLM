# dualscope-first-slice-clean-poisoned-labeled-slice-plan

## Purpose / Big Picture

This plan defines a minimal clean / poisoned-triggered paired first-slice label contract for DualScope-LLM. It exists so downstream first-slice reruns can distinguish label readiness from honest performance-metric readiness.

## Scope

### In Scope

- Build paired `clean` and `poisoned_triggered` rows from the existing Stanford Alpaca first-slice source JSONL.
- Freeze one lexical trigger, one fixed target response, and required label fields.
- Write schema, metric-readiness, verdict, and post-analysis artifacts.

### Out of Scope

- No benchmark truth changes.
- No model-output fabrication.
- No gate changes.
- No training or full experiment matrix.
- No route_c continuation.

## Repository Context

Core code lives in `src/eval/`; CLI entrypoints live in `scripts/`. Generated labels live under `data/stanford_alpaca/first_slice/`, and artifacts live under `outputs/dualscope_first_slice_clean_poisoned_labeled_slice/`.

## Deliverables

- `src/eval/dualscope_first_slice_label_common.py`
- `src/eval/dualscope_first_slice_clean_poisoned_labeled_slice.py`
- `src/eval/post_dualscope_first_slice_clean_poisoned_labeled_slice_analysis.py`
- `scripts/build_dualscope_first_slice_clean_poisoned_labeled_slice.py`
- `scripts/build_post_dualscope_first_slice_clean_poisoned_labeled_slice_analysis.py`
- `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`
- `outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default/`
- `outputs/dualscope_first_slice_clean_poisoned_labeled_slice_analysis/default/`

## Progress

- [x] M1: Label contract and paired-slice scope frozen.
- [x] M2: Builder and post-analysis implementation restored.
- [x] M3: Existing artifacts validated as label-ready but performance-not-ready.

## Validation and Acceptance

Validated when every source example has one clean row and one poisoned-triggered row, labels are marked as experimental construction rather than benchmark truth, and metric-readiness artifacts state that AUROC/F1/ASR/utility still require aligned model outputs.

## Next Suggested Plan

Continue to `dualscope-minimal-first-slice-real-run-rerun-with-labels`.
