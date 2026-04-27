# DualScope AdvBench Small-Slice Response Generation Repair

This package compresses the partially validated AdvBench small-slice response-generation run into a dedicated repair verdict. It does not print harmful prompts or completions.

## Source State

- Source task: `dualscope-advbench-small-slice-response-generation`
- Source output: `outputs/dualscope_advbench_small_slice_response_generation/default`
- Source verdict: `Partially validated`
- Source blocker: `torch_cuda_unavailable`
- Real response rows: `0`
- Blocked rows: `16`

## Regenerate

```bash
python3 scripts/build_dualscope_advbench_small_slice_response_generation_repair.py \
  --response-dir outputs/dualscope_advbench_small_slice_response_generation/default \
  --output-dir outputs/dualscope_advbench_small_slice_response_generation_repair/default \
  --registry-path .reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json \
  --seed 20260427
```

## Artifacts

- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_summary.json`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_availability_matrix.json`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_blocker_compression.json`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_compact_rows.jsonl`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json`

## Current Result

The repair validates the blocker package and routes to `dualscope-advbench-small-slice-response-generation-blocker-closure`. Metric computation remains blocked because no real model responses were generated in the CUDA-invisible worktree.
