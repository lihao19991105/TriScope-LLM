# DualScope AdvBench Small-Slice Public Source Materialization

## Purpose / Big Picture

Resolve the AdvBench small-slice missing-source blocker by using the explicitly authorized public Hugging Face dataset `walledai/AdvBench`. This task only materializes a bounded small slice and schema artifacts; it does not generate responses, compute metrics, or run a full matrix.

## Scope

### In Scope

- Configure `dataset_source_id = walledai/AdvBench`.
- Download/read via Hugging Face only when `--allow-download` is set.
- Materialize at most 32 rows to `data/advbench/small_slice/advbench_small_slice_source.jsonl`.
- Standardize rows with source provenance and no fabricated fields.
- Emit manifest, schema, blocker, summary, verdict, report, post-analysis, and tracked registry artifacts.
- Route validated materialization to `dualscope-advbench-small-slice-response-generation-plan`.

### Out of Scope

- Full AdvBench ingestion.
- Response generation or metric computation.
- Benchmark truth or safe merge gate changes.
- route_c / 199+ work.

## Milestones

- [x] Extend materialization CLI for public Hugging Face source configuration.
- [x] Add post-analysis artifacts.
- [x] Update queue, docs, and master planning notes for the public source.
- [x] Run materialization and record the real Hugging Face gated-data blocker.
- [ ] Run orchestrator dry-run after committing to a clean worktree.
- [ ] Create PR, trigger review, safe merge, then continue autorun if validated.

## Validation

```bash
python3 -m py_compile src/eval/dualscope_advbench_small_slice_materialization.py
python3 -m py_compile src/eval/post_dualscope_advbench_small_slice_materialization_analysis.py
python3 -m py_compile scripts/build_dualscope_advbench_small_slice_materialization.py
python3 -m py_compile scripts/build_post_dualscope_advbench_small_slice_materialization_analysis.py
.venv/bin/python scripts/build_dualscope_advbench_small_slice_materialization.py --help
.venv/bin/python scripts/build_post_dualscope_advbench_small_slice_materialization_analysis.py --help
.venv/bin/python scripts/build_dualscope_advbench_small_slice_materialization.py \
  --dataset-source walledai/AdvBench \
  --output-jsonl data/advbench/small_slice/advbench_small_slice_source.jsonl \
  --output-dir outputs/dualscope_advbench_small_slice_materialization/default \
  --max-examples 32 \
  --allow-download
```
