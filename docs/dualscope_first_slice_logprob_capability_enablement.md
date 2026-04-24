# DualScope First-Slice Logprob Capability Enablement

This stage checks whether the local first-slice backend can expose probability evidence for Stage 2 confidence verification.

The current contract accepts local logits followed by softmax as local probability evidence. The report explicitly marks this as `local_logits_softmax`; it is not a claim that a remote black-box API provided native token logprobs.

The stage does not train, does not run the full first-slice, and does not expand the experimental matrix.
