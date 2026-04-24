# DualScope 5H Autonomous Run Log

## 2026-04-24T16:46:36.896069+00:00 - DualScope 5H Autonomous Run

### Phase 1: dualscope-first-slice-dataset-materialization

Commands run:

```bash
.venv/bin/python scripts/build_dualscope_first_slice_alpaca_jsonl.py --source-file data/raw/alpaca_data.json --output-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl --max-examples 72 --seed 2025 --split-name first_slice --dataset-id stanford_alpaca
.venv/bin/python scripts/check_dualscope_first_slice_dataset_schema.py --dataset-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl --output-dir outputs/dualscope_first_slice_dataset_schema_check/default
.venv/bin/python scripts/build_dualscope_first_slice_dataset_materialization.py --source-file data/raw/alpaca_data.json --output-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl --output-dir outputs/dualscope_first_slice_dataset_materialization/default --schema-check-output-dir outputs/dualscope_first_slice_dataset_schema_check/default --max-examples 72 --seed 2025 --split-name first_slice --dataset-id stanford_alpaca
.venv/bin/python scripts/build_post_dualscope_first_slice_dataset_materialization_analysis.py --output-dir outputs/dualscope_first_slice_dataset_materialization_analysis/default
```

Created artifacts:

- `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl`
- `outputs/dualscope_first_slice_dataset_schema_check/default/dataset_schema_check.json`
- `outputs/dualscope_first_slice_dataset_materialization/default/dualscope_first_slice_dataset_materialization_summary.json`
- `outputs/dualscope_first_slice_dataset_materialization_analysis/default/dualscope_first_slice_dataset_materialization_verdict.json`

Verdict: `Dataset materialization validated`

Blockers: none.

Next action: preflight rerun.

### Phase 2: dualscope-minimal-first-slice-real-run-preflight-rerun

Commands run:

```bash
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python scripts/build_dualscope_first_slice_preflight_rerun.py --output-dir outputs/dualscope_first_slice_preflight_rerun/default
.venv/bin/python scripts/build_post_dualscope_first_slice_preflight_rerun_analysis.py --output-dir outputs/dualscope_first_slice_preflight_rerun_analysis/default
```

Created artifacts:

- `outputs/dualscope_first_slice_preflight_rerun/default/dualscope_first_slice_preflight_summary.json`
- `outputs/dualscope_first_slice_preflight_rerun_analysis/default/dualscope_first_slice_preflight_rerun_verdict.json`

Verdict: `First slice preflight rerun validated`

Blockers: none.

Next action: minimal real-run readiness package.

### Phase 7: dualscope-minimal-first-slice-real-run-readiness-package

Commands run:

```bash
.venv/bin/python scripts/build_dualscope_minimal_first_slice_real_run_readiness_package.py --output-dir outputs/dualscope_minimal_first_slice_real_run_readiness_package/default
.venv/bin/python scripts/build_post_dualscope_minimal_first_slice_real_run_readiness_package_analysis.py --output-dir outputs/dualscope_minimal_first_slice_real_run_readiness_package_analysis/default
```

Created artifacts:

- `outputs/dualscope_minimal_first_slice_real_run_readiness_package/default/dualscope_minimal_real_run_readiness_summary.json`
- `outputs/dualscope_minimal_first_slice_real_run_readiness_package/default/dualscope_minimal_real_run_readiness_blockers.json`
- `outputs/dualscope_minimal_first_slice_real_run_readiness_package_analysis/default/dualscope_minimal_real_run_readiness_verdict.json`

Verdict: `Partially validated`

Blockers:

- Missing real-run command entrypoints: `scripts/build_dualscope_first_slice_data_slice.py`, `scripts/run_dualscope_stage1_illumination.py`, `scripts/run_dualscope_stage2_confidence.py`, `scripts/run_dualscope_stage3_fusion.py`, `scripts/evaluate_dualscope_first_slice.py`, `scripts/build_dualscope_first_slice_real_run_report.py`.

Next action: implement minimal real-run command-entrypoint package before starting real run.
