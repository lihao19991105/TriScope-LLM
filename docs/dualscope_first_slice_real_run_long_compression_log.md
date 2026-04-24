# DualScope First-Slice Real-Run Long Compression Log

## 2026-04-25T01:32:11+08:00

- Phase: `dualscope-minimal-first-slice-real-run-compression`
- Commands run: `.venv/bin/python scripts/build_dualscope_minimal_first_slice_real_run_compression.py --output-dir outputs/dualscope_minimal_first_slice_real_run_compression/default`; `.venv/bin/python scripts/build_post_dualscope_minimal_first_slice_real_run_compression_analysis.py --output-dir outputs/dualscope_minimal_first_slice_real_run_compression_analysis/default`
- Artifacts generated: compression scope/status/gap/probe/label readiness/report/verdict/recommendation artifacts.
- Verdict: `Real-run compression validated`
- Remaining blockers: model execution, logprob capability, and label contract needed explicit enablement.
- Next action: `dualscope-first-slice-model-execution-enablement`

## 2026-04-25T01:32:11+08:00

- Phase: `dualscope-first-slice-model-execution-enablement`
- Commands run: `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python scripts/build_dualscope_first_slice_model_execution_enablement.py --output-dir outputs/dualscope_first_slice_model_execution_enablement/default --max-samples 3`; post-analysis command.
- Artifacts generated: model load check, generation probe details, generation probe report, verdict, recommendation.
- Verdict: `Model execution enablement validated`
- Remaining blockers: Stage 1/Stage 2 entrypoints still need model-aware integration.
- Next action: `dualscope-first-slice-logprob-capability-enablement`

## 2026-04-25T01:32:11+08:00

- Phase: `dualscope-first-slice-logprob-capability-enablement`
- Commands run: `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python scripts/build_dualscope_first_slice_logprob_capability_enablement.py --output-dir outputs/dualscope_first_slice_logprob_capability_enablement/default --max-samples 1`; post-analysis command.
- Artifacts generated: logits probe, local logits-softmax logprob probe, top-k probability probe, entropy probe, report, verdict, recommendation.
- Verdict: `Logprob capability enablement validated`
- Remaining blockers: local logits evidence is validated, but Stage 2 entrypoint does not yet consume it per sample.
- Next action: `dualscope-first-slice-label-materialization`

## 2026-04-25T01:32:11+08:00

- Phase: `dualscope-first-slice-label-materialization`
- Commands run: `.venv/bin/python scripts/build_dualscope_first_slice_label_materialization.py --output-dir outputs/dualscope_first_slice_label_materialization/default`; post-analysis command.
- Artifacts generated: available label sources, label contract, detection/ASR/utility readiness, metric readiness report.
- Verdict: `Partially validated`
- Remaining blockers: legitimate clean/poisoned/backdoor performance labels are not present.
- Next action: `dualscope-minimal-first-slice-real-run-rerun-with-model-or-fallback`

## 2026-04-25T01:32:11+08:00

- Phase: `dualscope-minimal-first-slice-real-run-rerun-with-model-or-fallback`
- Commands run: `.venv/bin/python scripts/build_dualscope_minimal_first_slice_real_run_rerun.py --output-dir outputs/dualscope_minimal_first_slice_real_run_rerun/default --mode auto --no-full-matrix`; post-analysis command.
- Artifacts generated: rerun command plan, stage status, capability mode, metric readiness, artifact/compatibility checks, report, verdict, recommendation.
- Verdict: `Partially validated`
- Remaining blockers: Stage 1/Stage 2 entrypoints remain protocol-compatible deterministic; labels remain unavailable for performance.
- Next action: `dualscope-first-slice-real-run-artifact-validation`

## 2026-04-25T01:32:11+08:00

- Phase: `dualscope-first-slice-real-run-artifact-validation`
- Commands run: `.venv/bin/python scripts/build_dualscope_first_slice_real_run_artifact_validation.py --output-dir outputs/dualscope_first_slice_real_run_artifact_validation/default`; post-analysis command.
- Artifacts generated: artifact checklist, compatibility report, capability validation, metric/label validation, report, verdict, recommendation.
- Verdict: `Partially validated`
- Remaining blockers: artifacts are present, but full model-integrated entrypoints and performance labels are still missing.
- Next action: `dualscope-first-slice-result-package`

## 2026-04-25T01:32:11+08:00

- Phase: `dualscope-first-slice-result-package`
- Commands run: `.venv/bin/python scripts/build_dualscope_first_slice_result_package.py --output-dir outputs/dualscope_first_slice_result_package/default`; post-analysis command.
- Artifacts generated: result summary, final setting, reportable items, limitations, report, verdict, recommendation.
- Verdict: `First-slice result package validated`
- Remaining blockers: cannot report AUROC/F1/ASR/clean utility yet.
- Next action: `dualscope-next-experiment-readiness-package`

## 2026-04-25T01:32:11+08:00

- Phase: `dualscope-next-experiment-readiness-package`
- Commands run: `.venv/bin/python scripts/build_dualscope_next_experiment_readiness_package.py --output-dir outputs/dualscope_next_experiment_readiness_package/default`; post-analysis command.
- Artifacts generated: readiness summary, options, command plan, required future artifacts, report, verdict, recommendation.
- Verdict: `Next experiment readiness package validated`
- Remaining blockers: next step requires creating one legitimate clean/poisoned labeled slice; not executed in this stage.
- Next action: `dualscope-first-slice-clean-poisoned-labeled-slice-plan`
