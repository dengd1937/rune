#!/usr/bin/env bash
# Run all planted-bug reviewer scenarios across reviewer prompts. Real LLM
# (opus + sonnet) — costs tokens, non-deterministic. Manual; NOT in CI.
#
# Each scenario plants a bug WITHIN the reviewer's remit:
#   code-quality (opus)  security bugs in a diff
#   spec        (sonnet) spec deviation in a diff
#   python/ts   (sonnet) language anti-patterns in a diff
#   global      (opus)   cross-task integration conflict in a multi-task diff
#   plan        (sonnet) defects in a plan document (placeholders / vague / TODO)
#   tech-risk   (sonnet) technical risks in a plan (no tests / N+1 / no pagination)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIX="$SCRIPT_DIR/fixtures"
FAILED=0

review() {
  local fixture="$1" bug="$2"
  echo "========================================"
  echo "  $(basename "$fixture")  [$PROMPT_SUBDIR/$PROMPT]"
  echo "========================================"
  if bash "$SCRIPT_DIR/run-reviewer-test.sh" "$fixture" "$bug"; then
    :
  else
    FAILED=1
  fi
  echo ""
}

export PROMPT_SUBDIR=code-review

# ── code-quality (opus) — security ───────────────────────────────────────────
export PROMPT=code-quality-reviewer-prompt.md MODEL=claude-opus-4-8
export TASK_TEXT="Implement a user lookup by email and a user count endpoint."
review "$FIX/sql-injection.diff" "sql injection|injection|注入|parameteriz|参数化|concat|拼接|unsanitiz"
export TASK_TEXT="Implement a login function that verifies a user's password."
review "$FIX/plaintext-password.diff" "password|密码|plaintext|明文|bcrypt|compare|哈希|hash"
export TASK_TEXT="Implement an API client that calls an external service."
review "$FIX/hardcoded-secret.diff" "secret|hardcod|硬编码|api key|api_key|暴露|环境变量|env var|凭证|credential"
unset TASK_TEXT

# ── spec (sonnet) — spec deviation ───────────────────────────────────────────
export PROMPT=spec-reviewer-prompt.md MODEL=claude-sonnet-4-6
export TASK_TEXT="实现 UserCard 组件：props 必须包含 name(必填)、email(必填)、onCancel(回调)；loading 为 true 时显示 spinner；点击卡片触发 onSelect。"
export IMPLEMENTER_REPORT="Implementer reports UserCard complete with name + click handler."
export RATIFIED_DECISIONS=""
export SEVERITY_REGEX="critical|high|严重|偏离|缺失|遗漏|超范围|不合规|契约|未实现"
review "$FIX/spec-missing-requirement.diff" "偏离|缺失|遗漏|超范围|不合规|契约|email|onCancel|onSelect|loading|props"
unset IMPLEMENTER_REPORT RATIFIED_DECISIONS SEVERITY_REGEX TASK_TEXT

# ── python (sonnet) — anti-patterns ──────────────────────────────────────────
export PROMPT=python-reviewer-prompt.md MODEL=claude-sonnet-4-6
review "$FIX/python-mutable-default.diff" "可变默认|mutable|默认参数|类型标注|标注|None|is None|推导|join|N+1"

# ── typescript (sonnet) — anti-patterns ──────────────────────────────────────
export PROMPT=typescript-reviewer-prompt.md MODEL=claude-sonnet-4-6
review "$FIX/ts-any.diff" "any|非空|断言|React.FC|deps|依赖|cleanup|清理|key|下标|悬浮|promise"

# ── global (opus) — cross-task integration conflict ──────────────────────────
export PROMPT=global-reviewer-prompt.md MODEL=claude-opus-4-8
export PLAN_TEXT="Plan: build a user service (Task 1) and an order service (Task 2) as separate modules that reference each other."
export TASK_SUMMARIES="Task 1: user service exposing a User type. Task 2: order service referencing users."
review "$FIX/global-cross-task-conflict.diff" "不一致|inconsistent|接口|契约|类型|冲突|integration|集成|userId|string|number"
unset PLAN_TEXT TASK_SUMMARIES

# ── plan-reviewer (sonnet) — plan document defects ───────────────────────────
export PROMPT_SUBDIR=writing-plans PROMPT=plan-reviewer-prompt.md MODEL=claude-sonnet-4-6
export FIXTURE_LANG=markdown
export SEVERITY_REGEX="issues found|issue|问题|缺陷|gap|placeholder|todo|tbd|含糊|模糊|incomplete|不完整|无法执行|vague"
export APPROVE_REGEX="approve|approved"
export BLOCK_REGEX="issues found|issue|问题|缺陷|gap|placeholder|todo|tbd|含糊|模糊|vague"
review "$FIX/plan-with-defects.md" "todo|tbd|placeholder|占位|含糊|模糊|similar to|缺|遗漏|incomplete|不完整|无法执行|add appropriate|usual|vague"
unset FIXTURE_LANG APPROVE_REGEX BLOCK_REGEX

# ── technical-risk-reviewer (sonnet) — plan technical risks ──────────────────
export PROMPT=technical-risk-reviewer-prompt.md MODEL=claude-sonnet-4-6
export FIXTURE_LANG=markdown
export SEVERITY_REGEX="critical|high|风险|risk|needs-attention|needs attention|block"
export APPROVE_REGEX="approve|approved"
export BLOCK_REGEX="needs-attention|needs attention|block|风险|risk|严重"
review "$FIX/plan-with-risks.md" "风险|risk|happy path|测试|test|并发|N+1|race|edge case|边界|pagination|分页|性能|performance"
unset FIXTURE_LANG SEVERITY_REGEX APPROVE_REGEX BLOCK_REGEX

# ── summary ──────────────────────────────────────────────────────────────────
export PROMPT_SUBDIR=code-review
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
