# DualScope Qwen2.5-7B Result Package Repair

## Purpose / Big Picture

Repair the partially validated Qwen2.5-7B first-slice result package so the project can safely route to SCI3 main-experiment expansion planning without fabricating unavailable metrics.

The repair serves the DualScope-LLM mainline by preserving real first-slice detection and ASR evidence while explicitly keeping clean utility blocked until explicit utility-success or reference-match fields exist.

## Scope

### In Scope

- Read Qwen2.5-7B response-generation rows, label-aligned metric artifacts, metric computation repair artifacts, and the prior result-package registry.
- Produce a repaired package under `outputs/dualscope_qwen2p5_7b_result_package_repair/default`.
- Produce an analysis mirror under `outputs/dualscope_qwen2p5_7b_result_package_repair_analysis/default`.
- Produce a tracked verdict registry at `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-result-package-repair.json`.
- Keep detection metrics and ASR reportable only when PASS artifacts are backed by real Qwen2.5-7B response rows.
- Keep clean utility explicitly blocked unless explicit utility-success or reference-match fields exist.

### Out of Scope

- No model generation rerun.
- No training, LoRA, QLoRA, full finetune, or full matrix execution.
- No benchmark truth, gate, label, response, logprob, final_risk_score, route_c, or 199+ changes.
- No full-paper performance claim.
- No clean utility inference from free-text responses.

## Repository Context

- Prior result-package registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-first-slice-result-package.json`
- Prior result-package docs: `docs/dualscope_qwen2p5_7b_first_slice_result_package.md`
- Response-generation source: `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default`
- Label-aligned metric source: `outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default`
- Metric repair source: `outputs/dualscope_qwen2p5_7b_metric_computation_repair/default`
- Repair output: `outputs/dualscope_qwen2p5_7b_result_package_repair/default`

Historical TriScope / route_c artifacts are not used for this repair except as excluded reliability background.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-result-package-repair.md`
- `src/eval/dualscope_qwen2p5_7b_result_package_repair.py`
- `scripts/build_dualscope_qwen2p5_7b_result_package_repair.py`
- `docs/dualscope_qwen2p5_7b_result_package_repair.md`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-result-package-repair.json`
- `outputs/dualscope_qwen2p5_7b_result_package_repair/default`
- `outputs/dualscope_qwen2p5_7b_result_package_repair_analysis/default`

## Progress

- [x] M1: Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and adjacent Qwen2.5-7B artifacts.
- [x] M2: Audit source evidence boundaries and confirm PASS detection / ASR with clean utility blocked.
- [x] M3: Implement repair builder and CLI.
- [x] M4: Generate repaired package, docs, analysis mirror, and verdict registry.
- [x] M5: Validate generated artifacts with `py_compile`, CLI execution, and diff checks.

## Surprises & Discoveries

- The prior first-slice result-package output directory is absent in this worktree, but the tracked verdict registry and documentation remain available.
- Metric repair artifacts are sufficient to rebuild the repaired package because detection metrics and ASR are PASS and backed by 8 aligned real Qwen2.5-7B response rows.
- Clean utility remains intentionally blocked because no explicit utility-success or reference-match field is present for the four clean eligible rows.

## Decision Log

- The repaired package uses metric repair artifacts and label-aligned PASS artifacts as metric sources; prior result-package registry is routing history only.
- The final verdict may be validated despite blocked clean utility because the task explicitly allows this when detection metrics and ASR are real and clean utility is explicitly blocked.
- The recommended next task is `dualscope-sci3-main-experiment-expansion-plan`.

## Plan of Work

Build a small result-package repair layer that audits real-response evidence, copies only reportable PASS detection and ASR metrics, writes explicit blockers for clean utility and unavailable logprob/full-paper metrics, and emits a limitations-aware verdict suitable for SCI3 expansion planning.

## Concrete Steps

1. Read source JSON/JSONL artifacts.
2. Confirm real responses are present and not fabricated.
3. Confirm detection metrics and ASR have `summary_status=PASS` and `metrics_computed=true`.
4. Confirm clean utility is blocked unless explicit success fields exist.
5. Write package JSON, Markdown report, docs, analysis mirror, and registry.
6. Run Python compile and package build CLI.

## Validation and Acceptance

Acceptance requires:

- The package CLI exits successfully.
- `dualscope_qwen2p5_7b_result_package_repair_real_metric_summary.json` reports detection and ASR only from PASS artifacts.
- `dualscope_qwen2p5_7b_result_package_repair_clean_utility_blocker.json` blocks clean utility without free-text inference.
- `dualscope_qwen2p5_7b_result_package_repair_verdict.json` contains exactly one allowed verdict.
- The tracked registry exists and routes validated repair to `dualscope-sci3-main-experiment-expansion-plan`.

## Idempotence and Recovery

The output directories can be regenerated from the same source artifacts. If explicit utility-success fields are added later, rerun the CLI and re-audit the clean utility field rather than editing metrics manually.
