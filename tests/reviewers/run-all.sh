#!/usr/bin/env bash
# Run all planted-bug reviewer scenarios across reviewer prompts. Real LLM
# (opus + sonnet) — costs tokens, non-deterministic. Manual; NOT in CI.
#
# Each scenario plants a bug WITHIN the reviewer's remit:
#   - code-quality (opus): security bugs (SQL injection / plaintext pw / secret)
#   - spec        (sonnet): implementation deviates from the task spec
#   - python      (sonnet): Python anti-patterns (mutable default, no typing)
#   - typescript  (sonnet): TS/React anti-patterns (any, missing deps)
# Language reviewers skip security (code-quality's job), so a SQL-injection bug
# against them would wrongly "pass" — bugs must match each reviewer's checklist.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIX="$SCRIPT_DIR/fixtures"
FAILED=0

review() {
  local fixture="$1" bug="$2"
  echo "========================================"
  echo "  $(basename "$fixture")  [$PROMPT]"
  echo "========================================"
  if bash "$SCRIPT_DIR/run-reviewer-test.sh" "$fixture" "$bug"; then
    :
  else
    FAILED=1
  fi
  echo ""
}

# ── code-quality (opus) — security bugs ──────────────────────────────────────
export PROMPT=code-quality-reviewer-prompt.md MODEL=claude-opus-4-8
export TASK_TEXT="Implement a user lookup by email and a user count endpoint."
review "$FIX/sql-injection.diff" \
  "sql injection|injection|注入|parameteriz|参数化|concat|拼接|unsanitiz"
export TASK_TEXT="Implement a login function that verifies a user's password."
review "$FIX/plaintext-password.diff" \
  "password|密码|plaintext|明文|bcrypt|compare|哈希|hash"
export TASK_TEXT="Implement an API client that calls an external service."
review "$FIX/hardcoded-secret.diff" \
  "secret|hardcod|硬编码|api key|api_key|暴露|环境变量|env var|凭证|credential"

# ── spec (sonnet) — spec deviation ───────────────────────────────────────────
# spec reviewer writes 偏离类型 (not CRITICAL/HIGH) and concludes 合规/不合规.
export PROMPT=spec-reviewer-prompt.md MODEL=claude-sonnet-4-6
export TASK_TEXT="实现 UserCard 组件：props 必须包含 name(必填 string)、email(必填 string)、onCancel(回调函数)；loading 为 true 时显示 spinner；点击卡片触发 onSelect 回调。"
export IMPLEMENTER_REPORT="Implementer reports UserCard is complete: renders name with a click handler."
export RATIFIED_DECISIONS=""
export SEVERITY_REGEX="critical|high|严重|偏离|缺失|遗漏|超范围|不合规|不符合|契约|未实现|漏"
review "$FIX/spec-missing-requirement.diff" \
  "偏离|缺失|遗漏|超范围|不合规|契约|未实现|漏|email|onCancel|onSelect|loading|props"
unset IMPLEMENTER_REPORT RATIFIED_DECISIONS SEVERITY_REGEX

# ── python (sonnet) — Python anti-patterns ───────────────────────────────────
export PROMPT=python-reviewer-prompt.md MODEL=claude-sonnet-4-6
unset TASK_TEXT
review "$FIX/python-mutable-default.diff" \
  "可变默认|mutable|默认参数|类型标注|标注|None|is None|推导|join|N+1|查询"

# ── typescript (sonnet) — TS/React anti-patterns ─────────────────────────────
export PROMPT=typescript-reviewer-prompt.md MODEL=claude-sonnet-4-6
review "$FIX/ts-any.diff" \
  "any|非空|断言|React.FC|deps|依赖|cleanup|清理|key|下标|悬浮|promise"

# ── summary ──────────────────────────────────────────────────────────────────
if [ "$FAILED" -eq 0 ]; then
  echo "========================================"
  echo " ALL REVIEWER SCENARIOS PASSED"
  echo "========================================"
  exit 0
else
  echo "========================================"
  echo " SOME SCENARIOS FAILED"
  echo "========================================"
  exit 1
fi
