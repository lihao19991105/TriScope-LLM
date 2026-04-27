#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage:
  scripts/codex_dualscope_skill.sh [--dry-run] <profile> "<task prompt>"

Examples:
  scripts/codex_dualscope_skill.sh long-autorun "继续推进 DualScope SCI3 实验，最多 6 小时。"
  scripts/codex_dualscope_skill.sh safe-merge-gate "修复 PR #107 的 AdvBench small-slice allowlist blocker。"
  scripts/codex_dualscope_skill.sh root-cause "诊断为什么 orchestrator 仍选择 download-repair。"
  scripts/codex_dualscope_skill.sh paper-method "更新 DualScope 论文方法章节。"
  scripts/codex_dualscope_skill.sh --dry-run status "只回复 DUALSCOPE_SKILL_STATUS_OK"
USAGE
}

die() {
  printf 'codex_dualscope_skill: error: %s\n' "$*" >&2
  exit 2
}

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || pwd
}

shell_quote_command() {
  local item
  for item in "$@"; do
    printf '%q ' "$item"
  done
  printf '\n'
}

decode_b64() {
  python3 - "$1" <<'PY'
import base64
import sys
print(base64.b64decode(sys.argv[1]).decode("utf-8"))
PY
}

load_profile() {
  local config_file="$1"
  local profile="$2"
  python3 - "$config_file" "$profile" <<'PY'
import base64
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
profile_name = sys.argv[2]
payload = json.loads(config_path.read_text(encoding="utf-8"))
profiles = payload.get("profiles", {})
if profile_name not in profiles:
    known = ", ".join(sorted(profiles))
    raise SystemExit(f"unknown profile {profile_name!r}; known profiles: {known}")
profile = profiles[profile_name]
effort = profile.get("effort") or payload.get("task_types", {}).get(profile_name)
valid_efforts = set(payload.get("valid_efforts", []))
if effort not in valid_efforts:
    raise SystemExit(f"profile {profile_name!r} has invalid effort {effort!r}")
print(effort)
print(base64.b64encode(str(profile.get("purpose", "")).encode("utf-8")).decode("ascii"))
print(base64.b64encode(str(profile.get("prompt_template", "")).encode("utf-8")).decode("ascii"))
print(base64.b64encode(str(profile.get("command_template", "")).encode("utf-8")).decode("ascii"))
print(payload.get("selected_model") or "gpt-5.5")
PY
}

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  shift
fi

if [[ $# -lt 2 ]]; then
  usage
  exit 2
fi

PROFILE="$1"
shift
USER_PROMPT="$*"

REPO="${DUALSCOPE_REPO:-$(repo_root)}"
CONFIG_FILE="${DUALSCOPE_CODEX_PROFILE_CONFIG:-$REPO/configs/dualscope_codex_task_profiles.json}"
[[ -f "$CONFIG_FILE" ]] || die "missing profile config: $CONFIG_FILE"
command -v python3 >/dev/null 2>&1 || die "missing required command: python3"

mapfile -t PROFILE_VALUES < <(load_profile "$CONFIG_FILE" "$PROFILE")
if [[ "${#PROFILE_VALUES[@]}" -ne 5 ]]; then
  die "failed to read profile $PROFILE"
fi
EFFORT="${PROFILE_VALUES[0]}"
PURPOSE="$(decode_b64 "${PROFILE_VALUES[1]}")"
PROFILE_PROMPT="$(decode_b64 "${PROFILE_VALUES[2]}")"
COMMAND_TEMPLATE="$(decode_b64 "${PROFILE_VALUES[3]}")"
MODEL="${CODEX_DUALSCOPE_MODEL:-${PROFILE_VALUES[4]}}"

mkdir -p "$REPO/logs"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$REPO/logs/codex_dualscope_skill_${PROFILE}_${TIMESTAMP}.log"

COMPOSED_PROMPT="$(cat <<EOF
请先完整阅读并严格遵守：
- AGENTS.md
- PLANS.md
- DUALSCOPE_MASTER_PLAN.md
- DUALSCOPE_TASK_QUEUE.md
- docs/codex_smart_exec_usage.md
- .codex/skills/dualscope-high-intensity/SKILL.md

Skill: dualscope-high-intensity
Profile: ${PROFILE}
Selected reasoning effort: ${EFFORT}
Profile purpose: ${PURPOSE}

Reasoning effort rule:
Use exactly: -c model_reasoning_effort="${EFFORT}"
Do not use: --reasoning-effort
Do not use: -c reasoning_effort="high"

Profile guidance:
${PROFILE_PROMPT}

Project safety boundaries:
- Do not handle PR #14.
- Do not merge unrelated historical PRs.
- Do not force push.
- Do not delete branches.
- Do not run git reset --hard.
- Do not switch remotes to SSH.
- Do not modify benchmark truth.
- Do not change gate semantics except narrow allowlist or diagnostics false-positive fixes.
- Do not continue old route_c.
- Do not generate 199+.
- Do not fabricate Qwen2.5-7B responses.
- Do not treat blocked rows as real model_response values.
- Do not fabricate logprobs.
- Do not fabricate AUROC, F1, ASR, or clean utility.
- Do not present projected or placeholder metrics as real performance.
- Do not present 1.5B as the SCI3 main model.
- Do not touch /mnt/sda3/CoCoNut-Artifact.
- Do not download 7B models under /home/lh.
- Do not run a full matrix directly.
- Do not full finetune.
- Do not run LoRA or QLoRA unless a later task explicitly authorizes it.
- Do not bypass GPU/CUDA blockers.
- Do not bypass gated dataset permissions.
- Do not fabricate AdvBench or JBB data.

Stop and report for requested changes, failing checks, benchmark truth risk, gate semantic risk, secrets or credentials, or non-auto-fixable GPU/OOM/gated model/persistent network/data permission blockers.

$(if [[ -n "$COMMAND_TEMPLATE" ]]; then printf 'Profile command template:\n%s\n' "$COMMAND_TEMPLATE"; fi)

User task:
${USER_PROMPT}
EOF
)"

DIRECT_CMD=(codex exec --cd "$REPO" --full-auto --model "$MODEL" -c "model_reasoning_effort=\"$EFFORT\"" "$COMPOSED_PROMPT")
DIRECT_PREVIEW="$(shell_quote_command "${DIRECT_CMD[@]}")"

SMART_SCRIPT="$REPO/scripts/codex_smart_exec.sh"
if [[ -x "$SMART_SCRIPT" ]]; then
  COMMAND=(env "CODEX_SMART_EFFORT_MAP=$CONFIG_FILE" "$SMART_SCRIPT" "$PROFILE" "$COMPOSED_PROMPT")
  COMMAND_KIND="codex_smart_exec"
else
  COMMAND=("${DIRECT_CMD[@]}")
  COMMAND_KIND="codex_exec_direct"
fi
COMMAND_PREVIEW="$(shell_quote_command "${COMMAND[@]}")"

{
  printf 'profile=%s\n' "$PROFILE"
  printf 'selected_effort=%s\n' "$EFFORT"
  printf 'selected_model=%s\n' "$MODEL"
  printf 'repo=%s\n' "$REPO"
  printf 'config=%s\n' "$CONFIG_FILE"
  printf 'command_kind=%s\n' "$COMMAND_KIND"
  printf 'full_command_preview=%s\n' "$COMMAND_PREVIEW"
  printf 'direct_codex_equivalent=%s\n' "$DIRECT_PREVIEW"
  printf 'composed_prompt_preview<<PROMPT\n%s\nPROMPT\n' "$(printf '%s\n' "$COMPOSED_PROMPT" | sed -n '1,120p')"
} >"$LOG_FILE"

if [[ "$DRY_RUN" == true ]]; then
  cat <<EOF
profile=${PROFILE}
selected_effort=${EFFORT}
command_kind=${COMMAND_KIND}
log_path=${LOG_FILE}
full_command_preview=${COMMAND_PREVIEW}
direct_codex_equivalent=${DIRECT_PREVIEW}
composed_prompt_preview:
$(printf '%s\n' "$COMPOSED_PROMPT" | sed -n '1,80p')
EOF
  printf 'exit_code=0\n' >>"$LOG_FILE"
  exit 0
fi

set +e
"${COMMAND[@]}" >>"$LOG_FILE" 2>&1
STATUS=$?
set -e
printf 'exit_code=%s\n' "$STATUS" >>"$LOG_FILE"
printf 'codex_dualscope_skill: profile=%s effort=%s exit_code=%s log=%s\n' "$PROFILE" "$EFFORT" "$STATUS" "$LOG_FILE"
exit "$STATUS"
