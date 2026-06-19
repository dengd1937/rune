#!/usr/bin/env bash
# Generic planted-bug reviewer test. Feeds a synthetic fixture (diff OR plan
# document) to ANY reviewer prompt via `claude -p`, verifies the reviewer (a)
# flags the bug, (b) signals severity, (c) does NOT approve (sycophancy guard).
#
# B-layer BEHAVIORAL test: real LLM, costs tokens, non-deterministic.
# Manual; NOT in CI. Guards reviewer-prompt quality across all reviewers.
#
# Env:
#   PROMPT   (required) reviewer prompt filename under skills/<skill>/
#   MODEL    (required) e.g. claude-opus-4-8 | claude-sonnet-4-6
#   PROMPT_SUBDIR (default "code-review") skills subdir holding PROMPT
#   TASK_TEXT / PLAN_TEXT / TASK_SUMMARIES / IMPLEMENTER_REPORT /
#     RATIFIED_DECISIONS / SPEC_TEXT  — placeholder values (reviewer-dependent)
#   USER_CONTEXT  optional extra context prepended to the user message
#   FIXTURE_LANG  language tag for the fixture code fence (diff / markdown / ...)
#   SEVERITY_REGEX  severity signal (default "critical|high"; plan/tech-risk use others)
#   APPROVE_REGEX / BLOCK_REGEX  conclusion vocabulary (defaults cover EN+ZH)
# Args:
#   $1 fixture        $2 bug-keyword-regex
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

: "${PROMPT:?PROMPT env required}"
: "${MODEL:?MODEL env required}"
: "${1:?usage: PROMPT=.. MODEL=.. $0 <fixture> <bug-regex>}"
: "${2:?usage: $0 <fixture> <bug-regex>}"

FIXTURE="$1"
BUG_REGEX="$2"
PROMPT_SUBDIR="${PROMPT_SUBDIR:-code-review}"
PROMPT_TEMPLATE="$PLUGIN_ROOT/skills/$PROMPT_SUBDIR/$PROMPT"
TASK_TEXT="${TASK_TEXT:-}"; PLAN_TEXT="${PLAN_TEXT:-}"
TASK_SUMMARIES="${TASK_SUMMARIES:-}"; IMPLEMENTER_REPORT="${IMPLEMENTER_REPORT:-}"
RATIFIED_DECISIONS="${RATIFIED_DECISIONS:-}"; SPEC_TEXT="${SPEC_TEXT:-(no spec provided)}"
USER_CONTEXT="${USER_CONTEXT:-}"; FIXTURE_LANG="${FIXTURE_LANG:-diff}"
SEVERITY_REGEX="${SEVERITY_REGEX:-critical|high}"
APPROVE_REGEX="${APPROVE_REGEX:-approve|合规|通过|APPROVE}"
BLOCK_REGEX="${BLOCK_REGEX:-block|不合规|不通过|未通过|BLOCK}"
BASE_SHA="${BASE_SHA:-abc1234}"; HEAD_SHA="${HEAD_SHA:-def5678}"

SYSTEM_FILE="$(mktemp)"; USER_FILE="$(mktemp)"; OUTPUT_FILE="$(mktemp)"
KEEP_OUTPUT=0
trap 'rm -f "$SYSTEM_FILE" "$USER_FILE"; [ "$KEEP_OUTPUT" -eq 1 ] || rm -f "$OUTPUT_FILE"' EXIT

# Build the system prompt: extract the real prompt from the template.
# - code-review/design templates are inline prose -> used as-is.
# - writing-plans templates wrap the prompt in a ```code block under "prompt: |"
#   -> extract that block and dedent.
# Then substitute every placeholder (both {{X}} and [X] styles); {{DIFF}} /
# {{PLAN_FILE_PATH}} / [PLAN_FILE_PATH] point to the user message.
TPL="$PROMPT_TEMPLATE" \
TASK_TEXT="$TASK_TEXT" PLAN_TEXT="$PLAN_TEXT" TASK_SUMMARIES="$TASK_SUMMARIES" \
IMPLEMENTER_REPORT="$IMPLEMENTER_REPORT" RATIFIED_DECISIONS="$RATIFIED_DECISIONS" \
SPEC_TEXT="$SPEC_TEXT" BASE_SHA="$BASE_SHA" HEAD_SHA="$HEAD_SHA" python3 -c '
import os, re, textwrap
raw = open(os.environ["TPL"]).read()
# Only writing-plans templates wrap the prompt in a Task-tool code block with
# "prompt: |"; code-review/design templates are prose with inline ```examples```.
pm = re.search(r"(?ms)```[a-zA-Z]*\n.*?prompt:\s*\|?\s*\n(.*?)\n```", raw)
text = textwrap.dedent(pm.group(1)) if pm else raw
subs = {
    "{{TASK_TEXT}}": os.environ["TASK_TEXT"],
    "{{PLAN_TEXT}}": os.environ["PLAN_TEXT"],
    "{{TASK_SUMMARIES}}": os.environ["TASK_SUMMARIES"],
    "{{IMPLEMENTER_REPORT}}": os.environ["IMPLEMENTER_REPORT"],
    "{{RATIFIED_DECISIONS}}": os.environ["RATIFIED_DECISIONS"],
    "{{DIFF}}": "(the diff is in the user message below)",
    "{{BASE_SHA}}": os.environ["BASE_SHA"],
    "{{HEAD_SHA}}": os.environ["HEAD_SHA"],
    "{{PLAN_FILE_PATH}}": "(the plan document is in the user message below)",
    "{{SPEC_FILE_PATH}}": os.environ["SPEC_TEXT"],
    "[PLAN_FILE_PATH]": "(the plan document is in the user message below)",
    "[SPEC_FILE_PATH]": os.environ["SPEC_TEXT"],
}
for k, v in subs.items():
    text = text.replace(k, v)
print(text)
' > "$SYSTEM_FILE"

# User message = optional context + the fixture content + a trigger.
FIXTURE_FILE="$FIXTURE" USER_CONTEXT="$USER_CONTEXT" FIXTURE_LANG="$FIXTURE_LANG" python3 -c '
import os
content = open(os.environ["FIXTURE_FILE"]).read()
ctx = os.environ["USER_CONTEXT"]; lang = os.environ["FIXTURE_LANG"]
parts = []
if ctx: parts.append(ctx + "\n")
parts.append(f"```{lang}\n{content}\n```\n")
parts.append("请按你的审查流程审查上述内容，输出完整审查结果与结论。")
print("\n".join(parts))
' > "$USER_FILE"

echo "Running claude -p ($MODEL, $PROMPT) on $(basename "$FIXTURE")..." >&2
claude -p "$(cat "$USER_FILE")" \
  --system-prompt-file "$SYSTEM_FILE" \
  --model "$MODEL" \
  --max-turns 3 \
  --disallowed-tools Bash Read Edit Write WebFetch WebSearch \
  > "$OUTPUT_FILE" 2>&1 || true

FAILED=0
echo "=== Verdict for $(basename "$FIXTURE") [$PROMPT] ==="

if grep -qiE "$BUG_REGEX" "$OUTPUT_FILE"; then
  echo "  [PASS] bug flagged"
else
  echo "  [FAIL] bug missed ($BUG_REGEX)"; FAILED=1
fi

if grep -qiE "$SEVERITY_REGEX" "$OUTPUT_FILE"; then
  echo "  [PASS] severity signal"
else
  echo "  [FAIL] no severity signal ($SEVERITY_REGEX)"; FAILED=1
fi

if grep -qiE "$APPROVE_REGEX" "$OUTPUT_FILE" && ! grep -qiE "$BLOCK_REGEX" "$OUTPUT_FILE"; then
  echo "  [FAIL] approved a planted-bug fixture (sycophantic)"; FAILED=1
else
  echo "  [PASS] did not approve"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "STATUS: PASSED"; rm -f "$OUTPUT_FILE"; exit 0
else
  echo "STATUS: FAILED — output follows:"
  echo "------------------------------------------------------------"
  cat "$OUTPUT_FILE"
  echo "------------------------------------------------------------"
  KEEP_OUTPUT=1; echo "(output kept at $OUTPUT_FILE)"; exit 1
fi
