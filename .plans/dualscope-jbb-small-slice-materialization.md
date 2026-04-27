# DualScope JBB Small-Slice Materialization

## Purpose / Big Picture

Materialize or validate a bounded JBB-Behaviors small slice for the DualScope SCI3 track. This task turns the prior readiness-only plan into a concrete source audit, schema check, and blocker-aware artifact package without generating model responses or computing metrics.

The task supports the DualScope mainline by adding a small, reproducible jailbreak / risky-behavior dataset slice that can later feed safety-aware response-generation planning. It does not change benchmark truth and does not claim full benchmark performance.

## Scope

### In Scope

- Read the prior AdvBench result-package and JBB readiness registries.
- Search local data roots for a JBB/JailbreakBench behavior CSV.
- If local data is absent, use the public Hugging Face `JailbreakBench/JBB-Behaviors` harmful behavior CSV only when `--allow-download` is explicit.
- Verify the source license before row materialization.
- Materialize at most 16 rows by default.
- Write a manifest, schema check, blocker file, report, verdict, tracked registry, and JSONL small slice.

### Out of Scope

- Full JBB ingestion or full benchmark execution.
- Model response generation.
- AUROC, F1, ASR, clean utility, refusal, or safety metrics.
- Label creation or benchmark-truth modification.
- Gate changes, route_c continuation, 199+ planning, training, force push, branch deletion, or PR #14 changes.

## Repository Context

- `docs/dualscope_jbb_small_slice_readiness_plan.md` defines the readiness-only boundary.
- `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-readiness-plan.json` confirms that JBB was previously plan-only.
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package.json` confirms that the current expansion remains bounded and does not unlock full-paper claims.
- `src/eval/dualscope_jbb_small_slice_materialization.py` contains the materialization logic.
- `scripts/build_dualscope_jbb_small_slice_materialization.py` is the CLI entrypoint.
- Historical TriScope / route_c artifacts are not used for this task.

## Deliverables

- `.plans/dualscope-jbb-small-slice-materialization.md`
- `docs/dualscope_jbb_small_slice_materialization.md`
- `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-materialization.json`
- `data/jbb/small_slice/jbb_small_slice_source.jsonl`
- `outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_manifest.json`
- `outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_schema_check.json`
- `outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_blockers.json`
- `outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_report.md`
- `outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_verdict.json`

## Progress

- [x] Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md.
- [x] Read the expected JBB readiness and AdvBench result-package inputs.
- [x] Identified public `JailbreakBench/JBB-Behaviors` source and MIT license metadata.
- [x] Added bounded materialization builder and CLI.
- [x] Created documentation and ExecPlan.
- [x] Run py_compile and CLI validation.
- [x] Inspect required artifacts and update final status.

## Surprises & Discoveries

- The expected JBB readiness registry exists and is plan-only validated.
- The public Hugging Face source exposes `data/harmful-behaviors.csv` and an MIT license file without authentication.
- The current worktree has `python3` 3.8 and no `.venv`, so validation uses syntax compatible with the available interpreter while preserving the repo's Python 3.10+ style direction.
- The bounded run materialized 16 rows and produced a schema-valid slice with empty blockers.

## Decision Log

- Use a bounded 16-row default to minimize materialized harmful-behavior text while still producing a real schema-valid slice.
- Copy only source benchmark fields and metadata; do not infer labels, responses, gates, or metrics.
- Treat license verification as a hard precondition. If the MIT license text cannot be read, emit blockers instead of writing rows.
- Keep response generation and metrics strictly blocked for later tasks.

## Plan of Work

Run the materialization CLI with `--allow-download`, max 16 rows, and the public Hugging Face source. Validate that the JSONL rows contain the required schema fields, the registry records no fabricated data or metrics, and blocker artifacts are explicit even when empty.

## Validation

```bash
python3 -m py_compile src/eval/dualscope_jbb_small_slice_materialization.py scripts/build_dualscope_jbb_small_slice_materialization.py
python3 scripts/build_dualscope_jbb_small_slice_materialization.py --help
python3 scripts/build_dualscope_jbb_small_slice_materialization.py --allow-download --max-examples 16
```
