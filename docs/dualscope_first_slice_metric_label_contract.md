# DualScope First-Slice Metric Label Contract

The first-slice can report artifact-shape checks, cost summaries, capability mode, fallback flags, and decision distributions.

It cannot report true detection performance until the following labels are available from a legitimate construction or annotation process:

- `is_backdoored`
- `is_poisoned`
- `clean_or_poisoned_split`
- `target_behavior_success`
- `asr_success`
- `binary_detection_ground_truth`

Until then, AUROC, F1, ASR, and clean utility must remain placeholders.
