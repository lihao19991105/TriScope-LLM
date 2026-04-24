# DualScope First-Slice Label Materialization

This stage records which labels are actually available in the current first-slice.

Available labels are sufficient for artifact validation and schema alignment: `example_id`, `dataset_id`, split identity, trigger-family annotation, target-family annotation, and reference response fields.

They are not sufficient for AUROC, F1, ASR, or clean-utility performance claims. Those require a legitimate clean/poisoned or backdoor target-behavior label source. This stage intentionally does not infer backdoor truth from ordinary Alpaca responses.
