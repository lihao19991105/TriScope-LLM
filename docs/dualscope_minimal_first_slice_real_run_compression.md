# DualScope Minimal First-Slice Real-Run Compression

This phase compresses the `Partially validated` first-slice real run into three concrete gaps:

- model execution not yet validated
- with-logprobs/logits capability not yet validated in the entrypoint path
- performance labels unavailable

It does not train, relabel, expand the matrix, or continue historical route_c work.

