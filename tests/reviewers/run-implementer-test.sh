#!/usr/bin/env bash
# Implementer subagent behavioral test. Feeds a task spec to the implementer
# prompt via `claude -p`, verifies TDD ordering, status reporting, and scope
# discipline.
#
# B-layer BEHAVIORAL test: real LLM, costs tokens, non-deterministic.
# Manual; NOT in CI. Guards implementer-prompt quality.
#
# Env:
#   MODEL    (required) e.g. claude-sonnet-4-6
#   EXPECT   (required) tdd | blocked | no-creep
#   USER_CONTEXT  optional extra context prepended to the user message
#   TIMEOUT  seconds before killing claude -p (default 120)
#   MAX_TURNS  max agent turns for claude -p (default 5)
#   TDD_RED_REGEX / TDD_GREEN_REGEX  custom TDD phase keywords
#   CREEP_REGEX  keywords that indicate scope creep (required for no-creep)
# Args:
#   $1 fixture (task spec file, substituted into {{TASK_TEXT}})
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

_timeout() {
  local secs="$1"; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$secs" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then gtimeout "$secs" "$@"
  else "$@"
  fi
}

: "${MODEL:?MODEL env required}"
: "${EXPECT:?EXPECT env required (tdd|blocked|no-creep)}"
: "${1:?usage: MODEL=.. EXPECT=.. $0 <fixture>}"

FIXTURE="$1"
PROMPT_TEMPLATE="$PLUGIN_ROOT/skills/subagent-driven-development/implementer-prompt.md"
USER_CONTEXT="${USER_CONTEXT:-}"
TIMEOUT="${TIMEOUT:-120}"
MAX_TURNS="${MAX_TURNS:-5}"
TDD_RED_REGEX="${TDD_RED_REGEX:-RED|先写.*测试|失败测试|failing test|write.*test first|测试.*失败}"
TDD_GREEN_REGEX="${TDD_GREEN_REGEX:-GREEN|最小实现|minimal implementation|让测试通过|make.*test pass|pass.*test}"
BLOCKED_REGEX="${BLOCKED_REGEX:-BLOCKED|NEEDS_CONTEXT|无法继续|缺少.*信息|不明确|不清楚|需要.*澄清}"
STATUS_REGEX="${STATUS_REGEX:-状态：|Status:}"
CREEP_REGEX="${CREEP_REGEX:-}"

SYSTEM_FILE="$(mktemp)"; USER_FILE="$(mktemp)"; OUTPUT_FILE="$(mktemp)"; STDERR_FILE="$(mktemp)"
KEEP_OUTPUT=0
trap 'rm -f "$SYSTEM_FILE" "$USER_FILE" "$STDERR_FILE"; [ "$KEEP_OUTPUT" -eq 1 ] || rm -f "$OUTPUT_FILE"' EXIT

# Build system prompt: read template, substitute {{TASK_TEXT}} with fixture content.
TASK_TEXT="$(cat "$FIXTURE")"
TPL="$PROMPT_TEMPLATE" TASK_TEXT="$TASK_TEXT" python3 -c '
import os, re, sys, textwrap
raw = open(os.environ["TPL"]).read()
fences = re.findall(r"```[a-zA-Z]*\n(.*?)\n```", raw, re.S)
wrapper = next((f for f in fences if re.search(r"prompt:\s*\|", f)), None)
if wrapper:
    text = textwrap.dedent(re.search(r"prompt:\s*\|\s*\n(.*)", wrapper, re.S).group(1))
else:
    text = raw
text = text.replace("{{TASK_TEXT}}", os.environ["TASK_TEXT"])
leak = re.findall(r"\{\{[A-Z_]+\}\}", text)
if leak:
    print(f"[warn] unsubstituted placeholders: {leak}", file=sys.stderr)
print(text)
' > "$SYSTEM_FILE"

# User message: trigger execution.
USER_MSG=""
[ -n "$USER_CONTEXT" ] && USER_MSG="$USER_CONTEXT\n\n"
USER_MSG="${USER_MSG}请按你的执行约束和 TDD 执行链执行上述任务。由于工具不可用，请以文本形式输出你的完整执行过程（包含测试代码和实现代码）以及最终状态报告。"
echo -e "$USER_MSG" > "$USER_FILE"

echo "Running claude -p ($MODEL, implementer) on $(basename "$FIXTURE") [expect=$EXPECT, timeout=${TIMEOUT}s]..." >&2
if ! _timeout "$TIMEOUT" claude -p "$(cat "$USER_FILE")" \
  --system-prompt-file "$SYSTEM_FILE" \
  --model "$MODEL" \
  --max-turns "$MAX_TURNS" \
  --disallowed-tools Bash Read Edit Write WebFetch WebSearch \
  > "$OUTPUT_FILE" 2>"$STDERR_FILE"; then
  EXIT_CODE=$?
  if [ "$EXIT_CODE" -eq 124 ]; then
    echo "  [FAIL] claude -p timed out after ${TIMEOUT}s" >&2
    echo "TIMEOUT" > "$OUTPUT_FILE"
  fi
fi

set +e
FAILED=0
echo "=== Implementer verdict for $(basename "$FIXTURE") (expect: $EXPECT) ==="

case "$EXPECT" in
  tdd)
    # TDD order: RED phase keywords must appear before GREEN phase keywords.
    RED_LINE=$(grep -niE "$TDD_RED_REGEX" "$OUTPUT_FILE" | head -1 | cut -d: -f1)
    GREEN_LINE=$(grep -niE "$TDD_GREEN_REGEX" "$OUTPUT_FILE" | head -1 | cut -d: -f1)

    if [ -z "$RED_LINE" ]; then
      echo "  [FAIL] no RED phase detected ($TDD_RED_REGEX)"; FAILED=1
    else
      echo "  [PASS] RED phase found (line $RED_LINE)"
    fi

    if [ -z "$GREEN_LINE" ]; then
      echo "  [FAIL] no GREEN phase detected ($TDD_GREEN_REGEX)"; FAILED=1
    else
      echo "  [PASS] GREEN phase found (line $GREEN_LINE)"
    fi

    if [ -n "$RED_LINE" ] && [ -n "$GREEN_LINE" ]; then
      if [ "$RED_LINE" -lt "$GREEN_LINE" ]; then
        echo "  [PASS] TDD order correct (RED=$RED_LINE < GREEN=$GREEN_LINE)"
      else
        echo "  [FAIL] TDD order violated (RED=$RED_LINE >= GREEN=$GREEN_LINE)"; FAILED=1
      fi
    fi

    # Status report should be present.
    if grep -qiE "$STATUS_REGEX" "$OUTPUT_FILE"; then
      echo "  [PASS] status report present"
    else
      echo "  [FAIL] no status report ($STATUS_REGEX)"; FAILED=1
    fi
    ;;

  blocked)
    # Vague/insufficient spec: implementer should escalate, not guess.
    if grep -qiE "$BLOCKED_REGEX" "$OUTPUT_FILE"; then
      echo "  [PASS] escalated (BLOCKED/NEEDS_CONTEXT)"
    else
      echo "  [FAIL] did not escalate on vague spec ($BLOCKED_REGEX)"; FAILED=1
    fi

    # Should NOT produce a DONE status.
    if grep -qiE "状态：.*DONE|Status:.*DONE" "$OUTPUT_FILE"; then
      echo "  [FAIL] reported DONE on an impossible spec — should have escalated"; FAILED=1
    else
      echo "  [PASS] did not falsely report DONE"
    fi
    ;;

  no-creep)
    : "${CREEP_REGEX:?CREEP_REGEX required for no-creep direction}"
    # Implementer should NOT implement out-of-scope work.
    if grep -qiE "$CREEP_REGEX" "$OUTPUT_FILE"; then
      echo "  [FAIL] scope creep detected ($CREEP_REGEX)"; FAILED=1
    else
      echo "  [PASS] no scope creep"
    fi

    # Should still produce TDD-ordered output for the in-scope task.
    if grep -qiE "$TDD_RED_REGEX" "$OUTPUT_FILE"; then
      echo "  [PASS] RED phase present for in-scope task"
    else
      echo "  [FAIL] no RED phase for in-scope task"; FAILED=1
    fi
    ;;

  *)
    echo "  [FAIL] unknown EXPECT mode: $EXPECT"; FAILED=1
    ;;
esac

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "STATUS: PASSED"; rm -f "$OUTPUT_FILE"; exit 0
else
  echo "STATUS: FAILED — output follows:"
  echo "------------------------------------------------------------"
  cat "$OUTPUT_FILE"
  if [ -s "$STDERR_FILE" ]; then
    echo "--- stderr ---"
    cat "$STDERR_FILE"
  fi
  echo "------------------------------------------------------------"
  KEEP_OUTPUT=1; echo "(output kept at $OUTPUT_FILE)"; exit 1
fi
