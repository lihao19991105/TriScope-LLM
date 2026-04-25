# DualScope First-Slice Metric Readiness

The clean / poisoned labeled slice makes labels ready, not performance ready.

AUROC and F1 require:

- `detection_label`
- `final_risk_score`
- row alignment between Stage 3 outputs and the label file

ASR requires:

- `asr_eligible`
- `target_text`
- `target_match_rule`
- real `model_response`
- row alignment between triggered rows and model responses

Clean utility requires:

- `utility_eligible`
- clean model response
- `response_reference`
- a utility scoring or comparison contract

If real model outputs or Stage 3 outputs do not exist, the correct claim is:

- labels ready

The following claims are not allowed from labels alone:

- AUROC ready
- F1 ready
- ASR ready
- utility ready
- performance validated

The labeled slice is meant to unblock the next rerun with labels. It does not itself report AUROC, F1, ASR, or utility.
