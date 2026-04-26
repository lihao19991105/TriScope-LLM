# DualScope SCI3 Main Experiment Expansion Plan Repair

This repair closes the partial validation state for the SCI3 main experiment expansion plan. It is a planning-only repair: no full matrix was executed, no model was trained, and no new model responses or logprobs were generated.

## Verdict

Final verdict: `SCI3 main experiment expansion plan repair validated`.

The repair is validated because the missing planning artifacts were regenerated in a self-contained form, the staged SCI3 axes are explicit, and the first-slice limitations are preserved.

## Repaired Input State

| Input | Status | Repair handling |
| --- | --- | --- |
| Prior expansion registry | present | Records `Partially validated` and routes to this repair |
| Prior expansion ignored output directory | absent | Recorded as an input gap; replaced by repaired planning artifacts |
| SCI3 experimental track | present | Used as dataset / trigger / target contract |
| SCI3 metrics and tables | present | Used as metric and table gating contract |
| SCI3 model matrix | present | Used as model-role and resource-readiness contract |
| Qwen2.5-7B result-package repair registry | present and validated | Used as first-slice limitation evidence |

## Preserved First-Slice Limitations

- The available real-response evidence is limited to 8 Qwen2.5-7B first-slice response rows.
- Detection metrics and ASR are first-slice only.
- Clean utility remains blocked until explicit utility success or reference-match evidence exists.
- With-logprobs confidence remains planned only; the available first-slice package is `without_logprobs`.
- No full-paper performance, model generalization, or benchmark-wide result is claimed.

## Staged Main Expansion Contract

The repaired plan keeps the SCI3 expansion staged:

1. Use the repaired Qwen2.5-7B first-slice package only as a limited starting point.
2. Expand Stanford Alpaca main slices first.
3. Add AdvBench only after Stanford Alpaca schema, label, score, and budget traces validate.
4. Add JBB-Behaviors only after AdvBench stress-path validation.
5. Plan cross-model validation after the Qwen2.5-7B main path is stable.

## Required Matrix Axes

Datasets:

- Stanford Alpaca.
- AdvBench.
- JBB-Behaviors.

Trigger families:

- Lexical.
- Semantic.
- Contextual / instruction.

Target families:

- Fixed response.
- Behavior shift.

Baselines:

- Illumination-only.
- Confidence-only with-logprobs.
- Confidence-only without-logprobs.
- Naive concat.
- DualScope budget-aware fusion.

## Artifact and Table Gates

Future main-table, cost, robustness, ablation, and cross-model tables may use only real aligned artifacts:

- Real model responses.
- Real labels or benchmark-aligned target truth.
- Real score fields.
- Real budget traces.
- Real capability-mode markers.
- Real logprobs when a with-logprobs table row is claimed.

Projected, placeholder, or first-slice-only values must not be presented as full SCI3 performance.

## Next Step

The validated next task is `dualscope-cross-model-validation-plan`.
