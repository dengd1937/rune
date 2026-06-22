#!/usr/bin/env bash
# Generic planted-bug reviewer test. Feeds a synthetic fixture (diff OR plan
# document) to ANY reviewer prompt via `claude -p`, then decides a verdict.
#
# The DETERMINISTIC harness logic (build system prompt, build user message,
# extract conclusion, decide verdict) lives in reviewers_lib.py and is unit-
# tested by test_verdict_logic.py ($0, in CI). This script is a thin orchestrator
# over that module's CLI — it owns only the env plumbing and the one real-LLM
# call. Keeping the logic out of bash (no embedded python -c / awk) removes the
# single-quote-escaping fragility that broke the script twice before.
#
# B-layer BEHAVIORAL test: real LLM, costs tokens, non-deterministic. Manual; NOT in CI.
#
# Env:
#   PROMPT   (required) reviewer prompt filename under skills/<PROMPT_SUBDIR>/
#   MODEL    (required) e.g. claude-opus-4-8 | claude-sonnet-4-6
#   PROMPT_SUBDIR (default code-review)
#   TASK_TEXT / PLAN_TEXT / TASK_SUMMARIES / IMPLEMENTER_REPORT /
#     RATIFIED_DECISIONS / SPEC_TEXT  — placeholder values (reviewer-dependent)
#   USER_CONTEXT  optional extra context prepended to the user message
#   FIXTURE_LANG  code-fence tag for the fixture (diff / markdown / ...)
#   EXPECT  block (default) | approve
#   SEVERITY_REGEX / APPROVE_REGEX / BLOCK_REGEX  — override the python defaults
#     (empty/unset -> use the single-source defaults in reviewers_lib.py)
#   TIMEOUT  seconds before killing claude -p (default 120)
# Args:
#   $1 fixture        $2 bug-keyword-regex (optional when EXPECT=approve)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LIB="$SCRIPT_DIR/reviewers_lib.py"

_timeout() {
  local secs="$1"; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$secs" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then gtimeout "$secs" "$@"
  else "$@"
  fi
}

: "${PROMPT:?PROMPT env required}"
: "${MODEL:?MODEL env required}"
: "${1:?usage: PROMPT=.. MODEL=.. $0 <fixture> [bug-regex]}"

FIXTURE="$1"
EXPECT="${EXPECT:-block}"
if [ "$EXPECT" = "approve" ]; then
  BUG_REGEX="${2:-__no_bug_expected__}"
else
  : "${2:?bug-regex required for block direction}"
  BUG_REGEX="$2"
fi
PROMPT_SUBDIR="${PROMPT_SUBDIR:-code-review}"
PROMPT_TEMPLATE="$PLUGIN_ROOT/skills/$PROMPT_SUBDIR/$PROMPT"
TASK_TEXT="${TASK_TEXT:-}"; PLAN_TEXT="${PLAN_TEXT:-}"
TASK_SUMMARIES="${TASK_SUMMARIES:-}"; IMPLEMENTER_REPORT="${IMPLEMENTER_REPORT:-}"
RATIFIED_DECISIONS="${RATIFIED_DECISIONS:-}"; SPEC_TEXT="${SPEC_TEXT:-(no spec provided)}"
USER_CONTEXT="${USER_CONTEXT:-}"; FIXTURE_LANG="${FIXTURE_LANG:-diff}"
SEVERITY_REGEX="${SEVERITY_REGEX:-}"; APPROVE_REGEX="${APPROVE_REGEX:-}"; BLOCK_REGEX="${BLOCK_REGEX:-}"
BASE_SHA="${BASE_SHA:-abc1234}"; HEAD_SHA="${HEAD_SHA:-def5678}"
TIMEOUT="${TIMEOUT:-120}"

SYSTEM_FILE="$(mktemp)"; USER_FILE="$(mktemp)"; OUTPUT_FILE="$(mktemp)"; STDERR_FILE="$(mktemp)"
KEEP_OUTPUT=0
trap 'rm -f "$SYSTEM_FILE" "$USER_FILE" "$STDERR_FILE"; [ "$KEEP_OUTPUT" -eq 1 ] || rm -f "$OUTPUT_FILE"' EXIT

# Stage ②: build the reviewer system prompt (deterministic).
python3 "$LIB" build-system-prompt --template "$PROMPT_TEMPLATE" --out "$SYSTEM_FILE" \
  --task-text "$TASK_TEXT" --plan-text "$PLAN_TEXT" --task-summaries "$TASK_SUMMARIES" \
  --implementer-report "$IMPLEMENTER_REPORT" --ratified-decisions "$RATIFIED_DECISIONS" \
  --spec-text "$SPEC_TEXT" --base-sha "$BASE_SHA" --head-sha "$HEAD_SHA"

# Stage ③: build the user message (deterministic).
UM_ARGS=(--fixture "$FIXTURE" --out "$USER_FILE" --lang "$FIXTURE_LANG")
if [ -n "$USER_CONTEXT" ]; then UM_ARGS+=(--context "$USER_CONTEXT"); fi
python3 "$LIB" build-user-message "${UM_ARGS[@]}"

# Stage ④: run the reviewer (the only non-deterministic stage).
echo "Running claude -p ($MODEL, $PROMPT) on $(basename "$FIXTURE") [timeout=${TIMEOUT}s]..." >&2
if ! _timeout "$TIMEOUT" claude -p "$(cat "$USER_FILE")" \
  --system-prompt-file "$SYSTEM_FILE" \
  --model "$MODEL" \
  --max-turns 3 \
  --disallowed-tools Bash Read Edit Write WebFetch WebSearch \
  > "$OUTPUT_FILE" 2>"$STDERR_FILE"; then
  EXIT_CODE=$?
  if [ "$EXIT_CODE" -eq 124 ]; then
    echo "  [FAIL] claude -p timed out after ${TIMEOUT}s" >&2
    echo "TIMEOUT" > "$OUTPUT_FILE"
  fi
fi

# Stage ⑤: verdict (deterministic). decide prints the [PASS]/[FAIL] lines and
# exits 0 (all pass) / 1 (any fail); run-all.sh maps that to FAILED vs ADVISORY.
echo "=== Verdict for $(basename "$FIXTURE") [$PROMPT] (expect: $EXPECT) ==="
DECIDE_ARGS=(--output-file "$OUTPUT_FILE" --expect "$EXPECT" --bug-re "$BUG_REGEX")
if [ -n "$SEVERITY_REGEX" ]; then DECIDE_ARGS+=(--severity-re "$SEVERITY_REGEX"); fi
if [ -n "$APPROVE_REGEX" ];  then DECIDE_ARGS+=(--approve-re "$APPROVE_REGEX"); fi
if [ -n "$BLOCK_REGEX" ];   then DECIDE_ARGS+=(--block-re "$BLOCK_REGEX"); fi
if python3 "$LIB" decide "${DECIDE_ARGS[@]}"; then
  echo ""
  echo "STATUS: PASSED"
  rm -f "$OUTPUT_FILE"
  exit 0
else
  rc=$?
  echo ""
  echo "STATUS: FAILED — output follows:"
  echo "------------------------------------------------------------"
  cat "$OUTPUT_FILE"
  if [ -s "$STDERR_FILE" ]; then
    echo "--- stderr ---"
    cat "$STDERR_FILE"
  fi
  echo "------------------------------------------------------------"
  KEEP_OUTPUT=1
  echo "(output kept at $OUTPUT_FILE)"
  exit "$rc"
fi
