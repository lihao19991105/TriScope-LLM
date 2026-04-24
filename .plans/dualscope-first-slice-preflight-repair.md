# dualscope-first-slice-preflight-repair

## Background

`dualscope-minimal-first-slice-real-run-preflight` completed with `Partially validated`. The core DualScope contracts, local model path, tokenizer load, output writability, planned command consistency, and `py_compile` checks are healthy. The remaining first-slice blocker is the missing real Stanford Alpaca JSONL at `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl`, which blocks dataset schema and sliceability checks.

## Why preflight repair follows partially validated preflight

The preflight stage should not fabricate data or skip checks. A repair stage is needed to convert the missing dataset blocker into auditable import tooling, schema validation tooling, environment requirements, and a rerun checklist. This repair validates the repair package only; it does not claim the real-run preflight itself is validated.

## Frozen dependencies

- DualScope Stage 1 / Stage 2 / Stage 3 frozen artifacts remain unchanged.
- The first-slice remains Stanford Alpaca + Qwen2.5-1.5B-Instruct + lexical trigger + fixed response target.
- GPU runs must use `.venv/bin/python` with `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3`.
- Benchmark truth semantics and gate semantics are frozen.

## Current blockers

- Missing `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl`.
- Dataset schema and sliceability checks are blocked by the missing file.
- GPU visibility must be checked with the repository Python 3.10 environment and explicit 3090 binding.

## Goal

Create a repair package that provides:

- A formal dataset import contract.
- A real-source-only Alpaca JSON/JSONL import and normalization tool.
- A first-slice schema validation tool.
- GPU/CUDA environment requirements and rerun checklist.
- Repair artifacts, report, single verdict, and single next-step recommendation.

## Non-goals

- Do not download data.
- Do not generate fake Alpaca data.
- Do not run LoRA / QLoRA training.
- Do not execute the first-slice real run.
- Do not expand the experimental matrix.
- Do not continue old route_c / 199+ chains.
- Do not modify benchmark truth or gate semantics.

## Dataset repair strategy

The repair package requires a user-provided real Alpaca-style source file. The import tool supports JSON arrays and JSONL records and normalizes common field layouts into the frozen first-slice schema. If the source file is absent or its fields are not recognizable, the tool fails clearly without writing synthetic data.

## Dataset import contract

Inputs:

- `--source-file`: real Alpaca-style JSON or JSONL.
- `--output-file`: `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl`.
- `--max-examples`, `--seed`, `--split-name`, `--dataset-id`.

Output rows:

- `example_id`
- `dataset_id`
- `instruction`
- `input`
- `prompt`
- `response`
- `split`
- `source`
- `metadata`

## Dataset schema normalization strategy

Supported source field families:

- `instruction` / `input` / `output`
- `prompt` / `response`
- `query` / `target`

If `prompt` is not directly present, it is derived from `instruction` and `input`. If `example_id` is absent, it is deterministically derived from dataset id, split, source index, and content hash.

## Dataset validation strategy

The schema checker validates JSONL rows for required fields, empty prompt / response, duplicate ids, and split distribution. It produces both JSON and Markdown reports and never repairs data implicitly.

## GPU / CUDA environment requirement

Real first-slice GPU commands must run through:

```bash
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python <script> <args>
```

This binds the two RTX 3090 cards by the same index order as `nvidia-smi`. If CUDA is not visible in a restricted shell, rerun preflight in a GPU-visible execution environment before real training.

## Rerun preflight plan

1. Materialize the first-slice JSONL from a real source.
2. Run the schema checker.
3. Rerun real-run preflight with `.venv/bin/python` and the 3090 binding.
4. Rerun preflight post-analysis.

## Failure fallback plan

- Missing source file: stop and request real source path.
- Unrecognized schema: stop and fix field mapping.
- CUDA unavailable: stop GPU execution, keep dataset/schema repair work.
- Artifact contract break: stop and repair schema/contracts before proceeding.

## Stop conditions

- Any attempt to fabricate data.
- Any benchmark truth or gate semantic change.
- Any LoRA/QLoRA training execution in this stage.
- Any full-matrix command execution.
- Any old route_c recursive chain continuation.

## Risks

- Real Alpaca source may not be present locally.
- Some Alpaca variants may require explicit mapping in a future compression stage.
- GPU visibility can differ between sandboxed and real execution contexts.

## Milestones

- M1: preflight blockers and repair scope frozen.
- M2: dataset import / schema validation / environment repair artifacts completed.
- M3: single repair verdict and single recommendation completed.

## Progress

- [x] M1: preflight blockers and repair scope frozen.
- [x] M2: dataset import / schema validation / environment repair artifacts completed.
- [x] M3: single repair verdict and single recommendation completed.

## Validation Run

- `.venv/bin/python scripts/build_dualscope_first_slice_preflight_repair.py --output-dir outputs/dualscope_first_slice_preflight_repair/default`
- `.venv/bin/python scripts/build_post_dualscope_first_slice_preflight_repair_analysis.py --output-dir outputs/dualscope_first_slice_preflight_repair_analysis/default`
- `.venv/bin/python scripts/check_dualscope_first_slice_dataset_schema.py --dataset-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl --output-dir outputs/dualscope_first_slice_dataset_schema_check/default`
- `.venv/bin/python -m py_compile src/eval/dualscope_first_slice_preflight_repair_common.py src/eval/dualscope_first_slice_preflight_repair.py src/eval/post_dualscope_first_slice_preflight_repair_analysis.py scripts/build_dualscope_first_slice_preflight_repair.py scripts/build_post_dualscope_first_slice_preflight_repair_analysis.py scripts/build_dualscope_first_slice_alpaca_jsonl.py scripts/check_dualscope_first_slice_dataset_schema.py`

## Outcome

Final verdict: `Preflight repair validated`.

Next recommendation: `dualscope-first-slice-dataset-materialization`.

## Exit criteria

- Repair plan, import contract, schema contract, environment requirements, rerun checklist, details, report, verdict, and recommendation are written.
- Dataset import and schema check CLIs exist and pass `py_compile`.
- No fake data is generated.
- No training or full matrix is executed.
- Final verdict is one of `Preflight repair validated`, `Partially validated`, `Not validated`.
