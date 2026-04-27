#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage:
  scripts/codex_smart_exec.sh <task_type> "<prompt>"

Examples:
  scripts/codex_smart_exec.sh autorun "从 clean main 运行 DualScope autorun，最多 20 轮。"
  scripts/codex_smart_exec.sh root-cause "诊断为什么 task orchestrator 反复选择同一个 repair task。"
  scripts/codex_smart_exec.sh paper-method "基于 DualScope 当前方案撰写方法章节。"
USAGE
}

die() {
  printf 'codex_smart_exec: error: %s\n' "$*" >&2
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

default_effort_for_task_type() {
  case "$1" in
    default|status|progress|docs|prompt|queue-docs|report|small-edit)
      printf 'medium'
      ;;
    autorun|pr-workflow|code-fix|cli-fix|artifact-fix|metric-computation|response-generation|dataset-materialization|blocker-repair|safe-merge-check)
      printf 'high'
      ;;
    root-cause|architecture|gate-design|execution-gate|safe-merge-gate|worktree-runner|task-orchestrator|blocker-loop|experiment-design|paper-method|paper-writing|complex-debug)
      printf 'xhigh'
      ;;
    *)
      return 1
      ;;
  esac
}

effort_from_config() {
  local config_file="$1"
  local task_type="$2"
  if [[ -f "$config_file" ]] && command -v jq >/dev/null 2>&1; then
    jq -r --arg task_type "$task_type" '.task_types[$task_type] // empty' "$config_file"
  fi
}

model_from_config() {
  local config_file="$1"
  if [[ -f "$config_file" ]] && command -v jq >/dev/null 2>&1; then
    jq -r '.selected_model // empty' "$config_file"
  fi
}

append_required_safety_constraints() {
  local task_type="$1"
  local prompt="$2"
  case "$task_type" in
    autorun|response-generation|metric-computation)
      cat <<EOF
$prompt

Mandatory DualScope safety constraints for this task:
- 不处理 PR #14
- 不 force push
- 不删除分支
- 不 reset --hard
- 不改 benchmark truth
- 不改 gate
- 不伪造 response / logprobs / metrics
EOF
      ;;
    *)
      printf '%s\n' "$prompt"
      ;;
  esac
}

write_log_header() {
  {
    printf 'task_type=%s\n' "$TASK_TYPE"
    printf 'selected_effort=%s\n' "$EFFORT"
    printf 'selected_model=%s\n' "$MODEL"
    printf 'repo_path=%s\n' "$REPO"
    printf 'codex_home=%s\n' "$CODEX_STATE_DIR"
    printf 'codex_tmpdir=%s\n' "$CODEX_TMPDIR"
    printf 'start_time=%s\n' "$START_TIME"
    printf 'codex_exec_help_available=%s\n' "$HELP_AVAILABLE"
    printf 'reasoning_effort_flag_supported=%s\n' "$FLAG_SUPPORTED"
    printf 'config_override_supported=%s\n' "$CONFIG_SUPPORTED"
    printf 'reasoning_effort_config_key=%s\n' "$CONFIG_KEY"
    printf 'reasoning_effort_not_supported_by_current_cli=%s\n' "$EFFORT_NOT_SUPPORTED"
    printf 'full_command_preview=%s\n' "$COMMAND_PREVIEW"
    printf '\n--- codex stdout/stderr ---\n'
  } >"$LOG_FILE"
}

run_and_capture() {
  local -n command_ref="$1"
  set +e
  HOME="$CODEX_BASE_HOME" CODEX_HOME="$CODEX_STATE_DIR" TMPDIR="$CODEX_TMPDIR" TMP="$CODEX_TMPDIR" TEMP="$CODEX_TMPDIR" \
    "${command_ref[@]}" >>"$LOG_FILE" 2>&1
  local status=$?
  set -e
  printf 'exit_code=%s\n' "$status" >>"$LOG_FILE"
  return "$status"
}

prepare_codex_state_dir() {
  mkdir -p "$CODEX_STATE_DIR" "$CODEX_TMPDIR"
  local name
  for name in auth.json config.toml version.json installation_id; do
    if [[ -f "$SOURCE_CODEX_HOME/$name" ]]; then
      cp -p "$SOURCE_CODEX_HOME/$name" "$CODEX_STATE_DIR/$name"
    fi
  done
  for name in rules skills; do
    if [[ -d "$SOURCE_CODEX_HOME/$name" && ! -e "$CODEX_STATE_DIR/$name" ]]; then
      cp -a "$SOURCE_CODEX_HOME/$name" "$CODEX_STATE_DIR/$name"
    fi
  done
}

if [[ $# -lt 2 ]]; then
  usage
  exit 2
fi

TASK_TYPE="$1"
shift
USER_PROMPT="$*"

command -v codex >/dev/null 2>&1 || die "missing required command: codex"
command -v git >/dev/null 2>&1 || die "missing required command: git"

REPO="$(repo_root)"
CONFIG_FILE="${CODEX_SMART_EFFORT_MAP:-$REPO/configs/codex_smart_effort_map.json}"
MODEL="$(model_from_config "$CONFIG_FILE")"
MODEL="${CODEX_SMART_MODEL:-${MODEL:-gpt-5.5}}"
CODEX_BASE_HOME="${CODEX_SMART_BASE_HOME:-$HOME}"
SOURCE_CODEX_HOME="${CODEX_SMART_SOURCE_CODEX_HOME:-$HOME/.codex}"
CODEX_STATE_DIR="${CODEX_SMART_CODEX_HOME:-$REPO/.tmp/codex_home}"
CODEX_TMPDIR="${CODEX_SMART_TMPDIR:-$REPO/.tmp/codex}"
prepare_codex_state_dir

EFFORT="$(effort_from_config "$CONFIG_FILE" "$TASK_TYPE")"
if [[ -z "$EFFORT" ]]; then
  if ! EFFORT="$(default_effort_for_task_type "$TASK_TYPE")"; then
    die "unsupported task_type '$TASK_TYPE'"
  fi
fi

PROMPT="$(append_required_safety_constraints "$TASK_TYPE" "$USER_PROMPT")"

mkdir -p "$REPO/logs"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
START_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LOG_FILE="$REPO/logs/codex_smart_exec_${TIMESTAMP}.log"

HELP_TEXT=""
HELP_AVAILABLE=false
if HELP_TEXT="$(codex exec --help 2>&1)"; then
  HELP_AVAILABLE=true
fi

FLAG_SUPPORTED=false
CONFIG_SUPPORTED=true
EFFORT_NOT_SUPPORTED=false
CONFIG_KEY="model_reasoning_effort"

BASE_CMD=(codex exec --cd "$REPO" --full-auto --model "$MODEL")
COMMAND=("${BASE_CMD[@]}" -c "${CONFIG_KEY}=\"$EFFORT\"" "$PROMPT")
COMMAND_PREVIEW="$(shell_quote_command "${COMMAND[@]}")"

write_log_header

if run_and_capture COMMAND; then
  exit 0
else
  FIRST_EXIT=$?
fi

exit "$FIRST_EXIT"
