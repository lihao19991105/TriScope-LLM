# DualScope First Slice Report Skeleton

## Setting

- Dataset: `stanford_alpaca`
- Model: `qwen2p5_1p5b_instruct`
- Trigger: `lexical_trigger`
- Target: `fixed_response_or_refusal_bypass`
- Capability modes: `without_logprobs, with_logprobs_if_available`
- Baselines: `illumination_only, dualscope_budget_aware_two_stage_fusion`

## Smoke Status

- Smoke examples: `3`
- Verification trigger rate: `0.6667`
- Artifact compatibility: `True`

## Expected Metrics

- AUROC
- F1
- TPR@low-FPR
- Average query cost
- Verification trigger rate

## Artifact Links

- `plan_summary`: `/home/lh/TriScope-LLM/outputs/dualscope_minimal_first_slice_execution_plan/default/dualscope_first_slice_summary.json`
- `smoke_summary`: `/home/lh/TriScope-LLM/outputs/dualscope_minimal_first_slice_smoke_run/default/dualscope_first_slice_smoke_run_summary.json`
- `validation_summary`: `/home/lh/TriScope-LLM/outputs/dualscope_first_slice_artifact_validation/default/dualscope_first_slice_artifact_validation_summary.json`
- `stage1_outputs`: `/home/lh/TriScope-LLM/outputs/dualscope_minimal_first_slice_smoke_run/default/stage1_illumination_outputs.jsonl`
- `stage2_outputs`: `/home/lh/TriScope-LLM/outputs/dualscope_minimal_first_slice_smoke_run/default/stage2_confidence_outputs.jsonl`
- `stage3_outputs`: `/home/lh/TriScope-LLM/outputs/dualscope_minimal_first_slice_smoke_run/default/stage3_fusion_outputs.jsonl`

## Known Limitations

- This is a controlled smoke skeleton, not a real performance result.
- Metrics are placeholders until a real first-slice run is executed.
- The without-logprobs path remains weaker evidence and must keep degradation flags.

## Next Experiment Recommendation

`dualscope-minimal-first-slice-real-run-plan`
