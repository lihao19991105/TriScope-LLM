# DualScope SCI3 Main Experiment Expansion Plan

This document defines the SCI3 main experiment expansion from the Qwen2.5-7B first-slice position. It is a plan only. It does not execute the full matrix, does not fabricate model responses or logprobs, and does not report projected performance as real results.

## Validation Status

Final verdict: `Partially validated`.

The plan is structurally complete, but the expected first-slice package directory `outputs/dualscope_qwen2p5_7b_first_slice_result_package/default` is absent in this worktree. The checked-in Qwen2.5-7B first-slice documentation exists, but execution must restore or regenerate the artifact directory before using it as an input gate.

## Main Expansion Contract

Primary model:

- `Qwen2.5-7B-Instruct`

Pilot / debug model:

- `Qwen2.5-1.5B-Instruct`

Later cross-model validation candidates:

- `Llama-3.1-8B-Instruct`
- `Mistral-7B-Instruct-v0.3`

The main experiment should expand in this order:

1. Restore or regenerate the Qwen2.5-7B first-slice result package.
2. Expand Stanford Alpaca under Qwen2.5-7B.
3. Add AdvBench after Stanford Alpaca schema and scoring validation.
4. Add JBB-Behaviors after AdvBench stress-path validation.
5. Add cross-model validation only after the Qwen2.5-7B main path is stable.

## Dataset Coverage

| Dataset | Role | First Execution Gate |
| --- | --- | --- |
| Stanford Alpaca | Instruction-following substrate and first main expansion path | Qwen2.5-7B first-slice package restored and row schema validated |
| AdvBench | Harmfulness / adversarial behavior stress path | Stanford Alpaca main-path artifacts validated |
| JBB-Behaviors | Jailbreak and risky-behavior validation path | AdvBench stress-path artifacts validated |

## Trigger Families

| Trigger family | Purpose | Notes |
| --- | --- | --- |
| Lexical | Simple token/string trigger sensitivity | Closest continuation of current first-slice scope |
| Semantic | Meaning-preserving trigger variant | Used for trigger generalization and paraphrase robustness |
| Contextual / instruction | Instruction-level or context-wrap trigger | Used to test whether DualScope catches instruction-conditioned backdoor behavior |

## Target Families

| Target family | Purpose | Required Evidence |
| --- | --- | --- |
| Fixed response | Direct target phrase / response matching | Real generated responses and target-match fields |
| Behavior shift | Harmfulness, refusal, or policy-behavior shift | Explicit behavior-scoring rule or benchmark-aligned label source |

## Baselines

All baselines must consume the same row IDs, labels, budget accounting fields, and capability markers:

- Illumination-only.
- Confidence-only with-logprobs.
- Confidence-only without-logprobs.
- Naive concat.
- DualScope budget-aware fusion.

The DualScope budget-aware fusion baseline is the main method. Naive concat is a non-budget-aware control. Single-branch baselines isolate the value of Stage 1 and Stage 2.

## Budget and Cost Plan

Each execution artifact should record:

- Screening query count.
- Verification query count.
- Verification trigger rate.
- Total query count.
- Generated token count when available.
- Logprob availability marker.
- Latency when measured by a real run.
- Cost-normalized AUROC only when AUROC and query cost are both real aligned values.

Budget analysis should compare:

- Illumination-only low-cost screening.
- Confidence-only full verification cost.
- Naive concat cost without risk-triggered routing.
- DualScope risk-triggered verification cost.
- With-logprobs versus without-logprobs capability settings.

## Robustness Plan

Robustness slices should be executed after the main Stanford Alpaca path is stable:

- Trigger paraphrase and synonym variants.
- Contextual wrapping and instruction-position shifts.
- Template shifts across prompt wrappers.
- Budget tightening at fixed detection target.
- Optional no-logprobs fallback stress.

No robustness metric is reportable until real responses, labels, scores, and budget traces are aligned.

## Ablation Plan

Required ablations:

- Remove illumination screening.
- Remove confidence verification.
- Replace risk-triggered verification with always-verify.
- Replace budget-aware fusion with naive concat.
- Sweep screening threshold.
- Sweep verification budget.
- Compare with-logprobs and without-logprobs confidence features where real capability artifacts exist.

## Planned Tables

| Table | Content | Required Inputs |
| --- | --- | --- |
| Table 1 | Overall detection performance | Real labels, scores, and aligned response rows |
| Table 2 | Query cost / budget trade-off | Real query counts, verification trigger rates, and latency/cost traces |
| Table 3 | Robustness | Real robustness-slice artifacts |
| Table 4 | Ablation | Real baseline and ablation artifacts over matched rows |
| Table 5 | Cross-model generalization | Real Qwen2.5-7B plus Llama/Mistral artifacts |

## Execution Guardrails

- Do not run the full matrix at once.
- Do not edit benchmark truth.
- Do not edit gates.
- Do not fabricate responses, labels, logprobs, metrics, ASR, clean utility, or latency.
- Do not continue route_c or generate `199+` planning.
- Do not present first-slice or placeholder values as full-paper performance.

## Immediate Next Step

Restore or regenerate `outputs/dualscope_qwen2p5_7b_first_slice_result_package/default`, then validate that the artifact directory contains the real first-slice package files needed by the SCI3 expansion gate.
