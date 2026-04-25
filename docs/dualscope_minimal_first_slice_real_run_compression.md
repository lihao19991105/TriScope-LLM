# DualScope Minimal First-Slice Real-Run Compression

This phase compresses the `Partially validated` first-slice real run into three concrete gaps:

- model execution not yet validated
- with-logprobs/logits capability not yet validated in the entrypoint path
- performance labels unavailable

It does not train, relabel, expand the matrix, or continue historical route_c work.

## 2026-04-25 Rerun Status

The latest rerun completed successfully:

- Verdict: `Real-run compression validated`
- Model execution ready: `true`
- Logprobs available through local logits-softmax evidence: `true`
- Performance labels available: `false`
- Recommendation: `dualscope-first-slice-clean-poisoned-labeled-slice-plan`

The rerun only re-compressed existing first-slice artifacts. It did not change benchmark truth, gate semantics, budgets, model axes, datasets, trigger families, target families, or prompt families.
