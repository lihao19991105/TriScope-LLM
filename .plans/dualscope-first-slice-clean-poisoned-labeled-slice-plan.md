# dualscope-first-slice-clean-poisoned-labeled-slice-plan

## Purpose / Big Picture

The minimal first-slice real-run chain has model execution and local logits-softmax probability evidence available, but evaluation still cannot report AUROC, F1, ASR, or clean utility because `labels_unavailable_for_performance = true`. This plan creates a small, auditable clean / poisoned-triggered paired evaluation slice from the existing Stanford Alpaca first slice.

The goal is to make first-slice evaluation metric-ready without fabricating model outputs, changing benchmark truth, changing gate semantics, expanding budgets, or expanding model axes.

## Scope

### In Scope

- Read `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl`.
- Generate paired rows for every source example:
  - one `clean` row
  - one `poisoned_triggered` row
- Freeze one lexical trigger contract.
- Freeze one fixed-response target contract.
- Write a local generated label file to `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`.
- Write schema, trigger, target, detection, ASR, utility, metric-readiness, details, report, verdict, and recommendation artifacts.
- Document how these constructed labels unlock metric readiness only after real Stage 3 outputs and model responses are aligned.

### Out of Scope

- No benchmark truth changes.
- No gate changes.
- No model-axis expansion.
- No budget expansion.
- No trigger-family expansion.
- No target-family expansion.
- No prompt-family expansion.
- No training.
- No full matrix.
- No fabricated model outputs.
- No AUROC, F1, ASR, or utility reporting before real outputs are aligned.
- No old TriScope / route_c recursive continuation and no `199+` stages.

## Repository Context

This plan follows the completed first-slice compression state:

- model execution: ready
- local logits/logprob capability: available
- performance labels: unavailable

It uses the existing first-slice source JSONL as the only data input and writes generated labels/artifacts under ignored generated-data/output paths. The code lives under `src/eval/` and CLI entrypoints live under `scripts/`, matching repository conventions.

## Deliverables

- `.plans/dualscope-first-slice-clean-poisoned-labeled-slice-plan.md`
- `src/eval/dualscope_first_slice_label_common.py`
- `src/eval/dualscope_first_slice_clean_poisoned_labeled_slice.py`
- `src/eval/post_dualscope_first_slice_clean_poisoned_labeled_slice_analysis.py`
- `scripts/build_dualscope_first_slice_clean_poisoned_labeled_slice.py`
- `scripts/build_post_dualscope_first_slice_clean_poisoned_labeled_slice_analysis.py`
- `docs/dualscope_first_slice_clean_poisoned_labeled_slice.md`
- `docs/dualscope_first_slice_label_contract.md`
- `docs/dualscope_first_slice_metric_readiness.md`
- Generated local label file and validation artifacts.

## Progress

- [x] M1: label contract and clean/poisoned paired-slice scope frozen
- [x] M2: labeled slice builder, post-analysis, docs, and artifacts completed
- [x] M3: schema validation, single verdict, and single recommendation completed

## Surprises & Discoveries

- The source JSONL is intentionally ignored by Git as generated/local dataset material. The new labeled JSONL follows the same generated-data policy and is produced by the CLI rather than committed as a static benchmark-truth file.

## Decision Log

- Use `trigger_id = lexical_trigger_v1` and `trigger_text = cftrigger` for the first slice because it is explicit, auditable, and unlikely to occur naturally.
- Use `trigger_insert_position = prompt_suffix` so prompt mutation is deterministic and easy to inspect.
- Use `target_id = fixed_response_v1`, `target_type = fixed_response`, and `target_match_rule = exact_or_contains`.
- Treat labels as `experimental_construction_v1`, not benchmark truth and not labels inferred from model outputs.

## Plan of Work

Build paired labels from every source row, validate required schema fields, write label contracts and metric-readiness artifacts, then run post-analysis to produce one final verdict and one next recommendation.

## Concrete Steps

1. Implement common JSONL/schema helpers.
2. Implement labeled-pair materialization.
3. Implement post-analysis artifact and schema validation.
4. Add CLI entrypoints.
5. Add label contract and metric-readiness documentation.
6. Run py_compile, CLI help, main build, post-analysis, and schema checks.

## Validation and Acceptance

Accepted verdicts:

- `Clean-poisoned labeled slice plan validated`
- `Partially validated`
- `Not validated`

Validation requires:

- labeled pairs exist
- every source example has exactly one clean row and one poisoned-triggered row
- required schema fields exist
- clean rows have `detection_label = 0`
- poisoned-triggered rows have `detection_label = 1`
- ASR eligibility is only true for poisoned-triggered rows
- utility eligibility is only true for clean rows
- metric-readiness artifacts explicitly avoid claiming performance readiness without real model outputs

## Idempotence and Recovery

The builder is deterministic for a fixed source file, trigger text, target text, and seed. It overwrites only the requested output file and output directory. If validation fails, rerun the builder after fixing schema or source-data blockers.

## Outputs and Artifacts

- `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`
- `outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default/`
- `outputs/dualscope_first_slice_clean_poisoned_labeled_slice_analysis/default/`

## Remaining Risks

- These are experimental construction labels, not benchmark truth.
- Metric readiness still requires real Stage 3 `final_risk_score` aligned to `row_id` / `pair_id`.
- ASR still requires real model responses aligned to triggered rows.
- Clean utility still requires real clean model responses and a scoring contract against reference responses.

## Next Suggested Plan

If validated, continue to `dualscope-minimal-first-slice-real-run-rerun-with-labels`.
