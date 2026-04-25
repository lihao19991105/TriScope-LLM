# DualScope First-Slice Real-Run Artifact Validation Repair

This repair package explains why the previous artifact validation was only `Partially validated` and records the minimum repair-only artifacts needed to move forward safely.

The repair does not rerun the full matrix, expand the dataset/model/trigger/target/budget scope, modify benchmark truth, modify gates, fabricate labels, fabricate model outputs, or claim preview AUROC/F1 as full model performance.

## What It Separates

- Missing artifacts: previous validation/report/verdict artifacts, target-response-generation artifacts, condition-level rerun artifacts, frozen Stage 1/2/3 contracts, and the optional standalone row-level fusion-alignment directory.
- Schema mismatch: older validation artifacts say labels were unavailable, while the labeled rerun artifacts now report labels ready.
- Granularity mismatch: older validation summarized source-level rerun readiness, while the condition-level rerun provides row_id-keyed clean and poisoned-triggered predictions.
- Projected metric versus full metric confusion: condition-level AUROC/F1 are detection preview metrics only; ASR and clean utility still require real generated model responses.
- Capability and fallback flags: the current condition-level Stage 2 artifacts record `without_logprobs` fallback and the degradation reason.
- Report, verdict, and recommendation artifacts: the repair checks that the prior stage, target-response plan, and repair stage expose auditable reports and verdicts.

## Commands

```bash
python3 -m py_compile \
  src/eval/dualscope_first_slice_real_run_artifact_validation_repair.py \
  src/eval/post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py \
  scripts/build_dualscope_first_slice_real_run_artifact_validation_repair.py \
  scripts/build_post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py

python3 scripts/build_dualscope_first_slice_real_run_artifact_validation_repair.py \
  --output-dir outputs/dualscope_first_slice_real_run_artifact_validation_repair/default \
  --seed 42

python3 scripts/build_post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py \
  --repair-dir outputs/dualscope_first_slice_real_run_artifact_validation_repair/default \
  --output-dir outputs/dualscope_first_slice_real_run_artifact_validation_repair_analysis/default \
  --seed 42
```

## Verdict Meaning

`First-slice real-run artifact validation repair validated` means the repair package is complete and honest about remaining model-response metric blockers.

It does not mean full paper performance metrics are ready.
