# DualScope AdvBench Download Repair Verdict Routing Fix

## Purpose / Big Picture

The bounded AdvBench small-slice has already been materialized and validated on `main`, but the task orchestrator still selects `dualscope-advbench-small-slice-download-repair` because that repair task has no tracked validated verdict registry. This plan records the real validated state and keeps the queue moving into bounded response-generation planning without modifying benchmark truth or fabricating data.

## Scope

### In Scope

- Verify the tracked AdvBench small-slice JSONL exists, has at most 32 rows, has valid JSON per line, includes the required schema/provenance fields, and uses `source_dataset == "walledai/AdvBench"`.
- Add the missing tracked verdict registry for `dualscope-advbench-small-slice-download-repair`.
- Ensure the orchestrator selects `dualscope-advbench-small-slice-response-generation-plan`.
- Add missing bounded AdvBench and JBB execution queue nodes so autorun does not skip response generation, metric computation, result packaging, or expanded synthesis routing.

### Out of Scope

- No benchmark truth, gate semantic, route_c, or 199+ changes.
- No full AdvBench/JBB data, full matrix, training, LoRA/QLoRA, or full finetune.
- No fabricated data, responses, logprobs, AUROC/F1/ASR/clean utility, or projected metrics.
- No PR #14 handling.

## Deliverables

- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-download-repair.json`
- Updated `DUALSCOPE_TASK_QUEUE.md` bounded downstream routing.
- Orchestrator validation artifacts under `outputs/dualscope_task_orchestrator/default`.

## Progress

- [x] Read repository instructions and DualScope queue context.
- [x] Confirm local main is dirty and use a clean temporary clone for edits.
- [x] Verify `data/advbench/small_slice/advbench_small_slice_source.jsonl` has 32 valid rows from `walledai/AdvBench`.
- [x] Add the missing AdvBench download-repair verdict registry.
- [x] Add bounded AdvBench/JBB response, metric, result package, and synthesis queue routing.
- [ ] Run py_compile, orchestrator selection, and diff checks.
- [ ] Open, review, safe-merge, and verify the routing fix PR.
- [ ] Start long-run autorun only after clean `main` selects AdvBench response-generation plan.

## Decision Log

- A tracked verdict registry is appropriate because the bounded data file and materialization registry already prove the repair condition is satisfied.
- The response-generation-plan task must route to bounded response generation, not directly to JBB, otherwise autorun would skip required execution artifacts.
- The queue prompts explicitly require safety-aware controlled generation, real blocker artifacts on failure, and no fabricated results.

## Validation

Run:

```bash
python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py
.venv/bin/python scripts/dualscope_task_orchestrator.py \
  --select-next-task \
  --write-next-prompt \
  --output-dir outputs/dualscope_task_orchestrator/default
git diff --check
```

Acceptance requires `selected_task_id == "dualscope-advbench-small-slice-response-generation-plan"`, `prompt_available == true`, and a non-empty prompt.

## Risks

- The main workspace remains dirty, so PR and autorun operations must use a clean clone or worktree fallback.
- Actual response generation may still hit GPU, model path, safety, or execution-runner blockers. Those blockers must be recorded honestly instead of marked validated.
