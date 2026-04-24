# DualScope First-Slice Real-Run Dry-Run Contract

Dry-run mode validates the command and artifact contract without executing training or full model inference.

Required dry-run chain:

1. Build data slice from the materialized Alpaca first-slice JSONL.
2. Produce Stage 1 illumination placeholder outputs.
3. Produce Stage 2 confidence placeholder outputs.
4. Produce Stage 3 fusion placeholder outputs.
5. Produce evaluation metric placeholders.
6. Produce report skeleton.

Dry-run placeholders must always include `dry_run = true` and must not claim AUROC, F1, ASR, clean utility, or final paper-level performance.

