# dualscope-first-slice-logprob-capability-enablement

## Purpose / Big Picture

This plan validates whether the local first-slice backend can expose token probability evidence for DualScope Stage 2 confidence verification. It follows model execution enablement and keeps the scope to one short local logits/logprob probe.

## Scope

### In Scope

- Load the frozen local model and tokenizer.
- Run one short forward pass.
- Confirm logits availability.
- Derive top-1 probability, top-k concentration, and entropy from local logits.
- Record whether the evidence is native API logprobs or local logits-derived probability.

### Out of Scope

- No training.
- No full first-slice sweep.
- No API logprob claim.
- No fallback proxy mislabeling as with-logprobs.
- No route_c continuation.

## Deliverables

- `src/eval/dualscope_first_slice_logprob_capability_enablement.py`
- `src/eval/post_dualscope_first_slice_logprob_capability_enablement_analysis.py`
- `scripts/build_dualscope_first_slice_logprob_capability_enablement.py`
- `scripts/build_post_dualscope_first_slice_logprob_capability_enablement_analysis.py`
- `docs/dualscope_first_slice_logprob_capability_enablement.md`
- Logit/logprob capability artifacts under `outputs/dualscope_first_slice_logprob_capability_enablement/default`

## Progress

- [x] M1: logprob/logits scope frozen
- [x] M2: probe implementation and artifacts completed
- [x] M3: verdict and recommendation completed

## Decision Log

- Local `outputs.logits` with softmax is valid as with-logprobs-style local evidence, but it is explicitly marked as `local_logits_softmax`, not a remote API native logprobs claim.

## Validation and Acceptance

Validated only if logits are accessible, probability/entropy artifacts are produced, py_compile passes, and no training/full matrix is executed.

## Remaining Risks

- Stage 2 entrypoint still needs a future model-aware integration pass to consume these features directly.
