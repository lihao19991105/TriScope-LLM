# Reference Implementation Notes

This note reviews nearby method lines relevant to TriScope-LLM and extracts only the implementation details that are useful for the current project. The goal is to absorb practical ideas without turning TriScope-LLM into a stitched copy of external repositories.

## ICLScan

### Reference Sources

- Local repository scan: no local copy or embedded snippet was found under `/home/lh/TriScope-LLM` or nearby user directories.
- Paper: ICLScan: Detecting Backdoors in Black-Box Large Language Models via Targeted In-context Illumination.
- Public materials:
  - OpenReview paper page: <https://openreview.net/forum?id=MtyF5hCI7Y>
  - Public code repository mentioned by the paper: <https://github.com/Harack1126/ICLScan>

### Core Borrowable Ideas

- Method logic:
  - Use black-box probing instead of parameter access.
  - Detect backdoors through susceptibility amplification under targeted in-context examples.
  - Measure a success-rate style statistic over multiple prompts, rather than trusting a single query.
- Prompt / template design:
  - Separate clean examples from deliberately backdoor-like in-context examples.
  - Treat trigger choice, target response, and prompt composition ratio as explicit configuration dimensions.
- CLI / config design:
  - Keep attack type, task type, trigger value, target behavior, and evaluation mode explicit in config files.
  - Distinguish training-time configs from evaluation-time configs.
- Intermediate outputs:
  - Save per-run results to named directories rather than only printing summary metrics.
  - Preserve experiment metadata that explains which trigger/profile/generated prompt family was used.
- Evaluation framing:
  - Work with success-rate thresholds under a query budget.
  - Use adaptive thresholds tied to the ratio of adversarial examples in the ICL prompt.

### What We Should Not Copy

- The repository structure is tightly coupled to that project’s SFT/eval pipeline and LLaMA-Factory modifications; TriScope-LLM should not inherit that whole stack.
- Their task split is centered on individual method evaluation, while TriScope-LLM must preserve a unified evidence-chain view across illumination, reasoning, and confidence.
- Their config tree is useful as a signal, but too task- and model-specific to mirror directly in this repository.

### Absorption Advice for TriScope-LLM

- Absorb into poison pipeline:
  - Keep trigger type, trigger text, target type, and target text explicit in structured configs.
  - Preserve run-level metadata and per-sample attack annotations for later analysis.
- Absorb into illumination module:
  - Use multi-query success-rate statistics, configurable query budget, and threshold logic.
  - Treat prompt composition as a first-class experimental variable.
- Keep as baseline reference only:
  - Their training/eval shell structure and project-specific directory hierarchy.

## Chain-of-Scrutiny (CoS)

### Reference Sources

- Local repository scan: no local code, notes, or cloned implementation was found.
- Paper:
  - ACL Anthology: <https://aclanthology.org/2025.findings-acl.401/>
  - arXiv/DBLP entry: <https://dblp.org/rec/journals/corr/abs-2406-05948>
- Code availability:
  - No complete public implementation was locally available to verify in this workspace.
  - This review therefore relies on the paper’s methodology description rather than a verified codebase.

### Core Borrowable Ideas

- Method logic:
  - Model backdoor behavior as a reasoning shortcut that bypasses legitimate intermediate steps.
  - Separate detection into two stages: reasoning generation and scrutiny/consistency checking.
  - Detect both response mismatch and reasoning-output contradiction.
- Prompt / template design:
  - Use structured demonstrations with task instructions, intermediate results, and final output.
  - Make the demonstration reusable across tasks when possible, rather than writing one bespoke prompt per sample.
- Logging / outputs:
  - Keep both the original answer and the reasoning-conditioned answer for side-by-side comparison.
  - Preserve the reasoning trace itself as an artifact, not just the final label.
- Evaluation framing:
  - Reasoning inconsistency is a structured signal, not only a binary decision.
  - Defense logic should stay interpretable to end users and auditors.

### What We Should Not Copy

- TriScope-LLM should not become a pure CoS-style inference-time defense wrapper; reasoning is only one evidence channel here.
- CoS is prompt-heavy and task-oriented around reasoning demonstrations; reusing that pattern everywhere would overfit the project to one method line.
- Their end goal includes mitigation/correction during inference; TriScope-LLM should first prioritize unified detection evidence.

### Absorption Advice for TriScope-LLM

- Absorb into reasoning module:
  - Explicitly store reasoning trace, answer under scrutiny, and inconsistency annotations.
  - Design reasoning prompts as named templates, not ad hoc strings embedded in scripts.
- Absorb into fusion:
  - Represent reasoning inconsistency as a structured feature family instead of a single yes/no flag.
- Keep as baseline reference only:
  - CoS-style prompt-only defense framing as a standalone method.

## ConfGuard

### Reference Sources

- Local repository scan: no local code or cloned implementation was found.
- Paper / public materials:
  - arXiv abstract page: <https://arxiv.org/abs/2508.01365>
  - DBLP entry: <https://dblp.org/rec/journals/corr/abs-2508-01365>
- Code availability:
  - No complete public implementation was locally available to verify in this workspace.
  - This review therefore marks ConfGuard as “no verified complete code locally; absorbed from the paper description”.

### Core Borrowable Ideas

- Method logic:
  - Detect backdoors through output-space behavior rather than only prompt-space or reasoning-space anomalies.
  - Focus on sequence lock: unusually high and stable confidence along the generated target sequence.
- Statistic design:
  - Monitor a sliding window over token confidence instead of relying on one token or a full-sequence average alone.
  - Keep detection lightweight and streamable for real-time use.
- Output / logging design:
  - Preserve per-token or window-level confidence summaries as structured artifacts.
  - Separate raw confidence traces from aggregated detection scores.
- API assumption:
  - Design to degrade gracefully when full logits are unavailable; top-1 token confidence may still be enough.

### What We Should Not Copy

- TriScope-LLM should not depend on confidence-only detection or assume confidence access everywhere.
- ConfGuard’s strength comes from near-real-time confidence monitoring; copying that structure into earlier data stages like poison building would be artificial.
- The method is centered on a single behavioral discrepancy, whereas TriScope-LLM must ultimately fuse multiple evidence streams.

### Absorption Advice for TriScope-LLM

- Absorb into confidence module:
  - Use window-based statistics and preserve raw confidence traces for later analysis.
  - Model confidence collapse as a structured signal family, not just a thresholded label.
- Absorb into fusion:
  - Treat confidence features as complementary evidence alongside illumination and reasoning.
- Keep as baseline reference only:
  - Confidence-only decision rules as a standalone final detector.

## Cross-Method Synthesis for TriScope-LLM

- Adopt:
  - explicit configs for triggers/targets/templates
  - query-budget-aware probing
  - structured intermediate artifacts
  - reusable prompt template naming
  - window/statistic-based behavior summaries
- Reject:
  - copying any single paper’s directory hierarchy
  - turning TriScope-LLM into three isolated baselines
  - over-coupling the project to one model family or one inference stack
- Current implementation implication:
  - the poison pipeline should continue to prioritize structured metadata, deterministic selection, and reusable artifacts that later support illumination, reasoning, and confidence modules.
