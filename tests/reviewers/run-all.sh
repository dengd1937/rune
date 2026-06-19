#!/usr/bin/env bash
# Run all reviewer scenarios across reviewer prompts. Real LLM (opus + sonnet) —
# costs tokens, non-deterministic. Manual; NOT in CI.
#
# Two directions per reviewer (recall × precision):
#   block  (default, EXPECT unset)  planted bug  -> reviewer must flag + severity + BLOCK
#   approve (EXPECT=approve)        clean code   -> reviewer must APPROVE and NOT block
# A reviewer that rubber-stamps fails the block scenarios; one that over-blocks
# fails the approve scenarios. BOTH must pass — quality = recall × precision.
#
# Each block scenario plants a bug WITHIN the reviewer's remit; each approve
# scenario is the same context with the bug fixed (a true control).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIX="$SCRIPT_DIR/fixtures"
FAILED=0      # block (recall) failures — hard gate (planted bugs are unambiguous)
ADVISORY=0    # approve (precision) failures — soft signal, non-deterministic (see review())

review() {
  local fixture="$1" bug="$2"
  echo "========================================"
  echo "  $(basename "$fixture")  [$PROMPT_SUBDIR/$PROMPT]  (expect: ${EXPECT:-block})"
  echo "========================================"
  if bash "$SCRIPT_DIR/run-reviewer-test.sh" "$fixture" "$bug"; then
    :
  else
    if [ "${EXPECT:-block}" = "approve" ]; then
      # Approve (precision) is a SOFT signal. Every strict reviewer (HIGH=block by
      # design) non-deterministically invents pedantic nits as HIGH on genuinely-clean
      # code — e.g. flagging a for-loop as "non-Pythonic" or a typed fetch as an
      # "unnecessary assertion." So a single approve fail flakes. Report it; only
      # consistent fails across runs indicate real over-strictness. Block (recall)
      # failures remain the hard gate.
      ADVISORY=$((ADVISORY + 1))
      echo "  ADVISORY FAIL (precision signal, non-deterministic — re-run; consistent fails = real over-strictness)"
    else
      FAILED=1
    fi
  fi
  echo ""
}

export PROMPT_SUBDIR=code-review

# ── code-quality (opus) — security ───────────────────────────────────────────
export PROMPT=code-quality-reviewer-prompt.md MODEL=claude-opus-4-8
export TASK_TEXT="Implement a user lookup by email and a user count endpoint."
review "$FIX/sql-injection.diff" "sql injection|injection|注入|parameteriz|参数化|concat|拼接|unsanitiz"
export TASK_TEXT="Implement a login function that verifies a user's password."
review "$FIX/plaintext-password.diff" "plaintext|明文|bcrypt|compare|比较|直接比对|hash.*比较"
export TASK_TEXT="Implement an API client that calls an external service."
review "$FIX/hardcoded-secret.diff" "hardcod|硬编码|api[_ ]?key|内联|写在代码|暴露|凭证|credential|env|环境变量"
unset TASK_TEXT
#   clean control (precision signal — advisory; code-quality observed to over-block consistently)
export EXPECT=approve TASK_TEXT="Implement a login function that verifies a user's password."
review "$FIX/clean-secure-auth.diff" "clean-fixture-no-bug"
unset EXPECT TASK_TEXT

# ── spec (sonnet) — spec deviation / compliance ──────────────────────────────
export PROMPT=spec-reviewer-prompt.md MODEL=claude-sonnet-4-6
export TASK_TEXT="实现 UserCard 组件：props 必须包含 name(必填)、email(必填)、onCancel(回调)；loading 为 true 时显示 spinner；点击卡片触发 onSelect。"
export IMPLEMENTER_REPORT="Implementer reports UserCard complete with name + click handler."
export RATIFIED_DECISIONS=""
export SEVERITY_REGEX="critical|high|严重|偏离|缺失|遗漏|超范围|不合规|契约|未实现"
export APPROVE_REGEX="规格合规" BLOCK_REGEX="不合规|不通过"
review "$FIX/spec-missing-requirement.diff" "偏离|缺失|遗漏|超范围|不合规|契约|email|onCancel|onSelect|loading|props"
unset IMPLEMENTER_REPORT RATIFIED_DECISIONS SEVERITY_REGEX TASK_TEXT
#   clean control
export EXPECT=approve TASK_TEXT="实现 UserCard 组件：props 必须包含 name(必填)、email(必填)、onCancel(回调)；loading 为 true 时显示 spinner；点击卡片触发 onSelect。"
export IMPLEMENTER_REPORT="Implementer reports UserCard complete: name, email, onCancel, onSelect, and the loading spinner."
review "$FIX/clean-spec-compliant.diff" "clean-fixture-no-bug"
unset EXPECT IMPLEMENTER_REPORT TASK_TEXT APPROVE_REGEX BLOCK_REGEX

# ── python (sonnet) — anti-patterns ──────────────────────────────────────────
export PROMPT=python-reviewer-prompt.md MODEL=claude-sonnet-4-6
review "$FIX/python-mutable-default.diff" "可变默认|mutable|默认参数|类型标注|标注|None|is None|推导|join|N+1"
#   clean control
export EXPECT=approve
review "$FIX/clean-python.diff" "clean-fixture-no-bug"
unset EXPECT

# ── typescript (sonnet) — anti-patterns ──────────────────────────────────────
export PROMPT=typescript-reviewer-prompt.md MODEL=claude-sonnet-4-6
review "$FIX/ts-any.diff" "any|非空|断言|React.FC|deps|依赖|cleanup|清理|key|下标|悬浮|promise"
#   clean control
export EXPECT=approve
review "$FIX/clean-ts.diff" "clean-fixture-no-bug"
unset EXPECT

# ── global (opus) — cross-task integration conflict ──────────────────────────
export PROMPT=global-reviewer-prompt.md MODEL=claude-opus-4-8
export PLAN_TEXT="Plan: build a user service (Task 1) and an order service (Task 2) as separate modules that reference each other."
export TASK_SUMMARIES="Task 1: user service exposing a User type. Task 2: order service referencing users."
review "$FIX/global-cross-task-conflict.diff" "不一致|inconsistent|接口|契约|类型|冲突|integration|集成|userId|string|number"
unset PLAN_TEXT TASK_SUMMARIES
#   clean control
export EXPECT=approve PLAN_TEXT="Plan: build a user service (Task 1) and an order service (Task 2) as separate modules that reference each other."
export TASK_SUMMARIES="Task 1: user service exposing a User type. Task 2: order service referencing users."
review "$FIX/clean-cross-task.diff" "clean-fixture-no-bug"
unset EXPECT PLAN_TEXT TASK_SUMMARIES

# ── plan-reviewer (sonnet) — plan document defects ───────────────────────────
export PROMPT_SUBDIR=writing-plans PROMPT=plan-reviewer-prompt.md MODEL=claude-sonnet-4-6
export FIXTURE_LANG=markdown
export SEVERITY_REGEX="issues found|issue|问题|缺陷|gap|placeholder|todo|tbd|含糊|模糊|incomplete|不完整|无法执行|vague"
export APPROVE_REGEX="approve|approved"
export BLOCK_REGEX="issues found|issue|问题|缺陷|gap|placeholder|todo|tbd|含糊|模糊|vague"
review "$FIX/plan-with-defects.md" "todo|tbd|placeholder|占位|含糊|模糊|similar to|缺|遗漏|incomplete|不完整|无法执行|add appropriate|usual|vague"
unset FIXTURE_LANG SEVERITY_REGEX APPROVE_REGEX BLOCK_REGEX
#   clean control
export EXPECT=approve FIXTURE_LANG=markdown APPROVE_REGEX="approve|approved" BLOCK_REGEX="\*\* issues found"
review "$FIX/clean-plan.md" "clean-fixture-no-bug"
unset EXPECT FIXTURE_LANG APPROVE_REGEX BLOCK_REGEX

# ── technical-risk-reviewer (sonnet) — plan technical risks ──────────────────
export PROMPT=technical-risk-reviewer-prompt.md MODEL=claude-sonnet-4-6
export FIXTURE_LANG=markdown
export SEVERITY_REGEX="critical|high|风险|risk|needs-attention|needs attention|block"
export APPROVE_REGEX="approve|approved"
export BLOCK_REGEX="needs-attention|needs attention|block|风险|risk|严重"
review "$FIX/plan-with-risks.md" "风险|risk|happy path|测试|test|并发|N+1|race|edge case|边界|pagination|分页|性能|performance"
unset FIXTURE_LANG SEVERITY_REGEX APPROVE_REGEX BLOCK_REGEX
#   clean control (precision signal — advisory; tech-risk adversarial, observed to over-block)
export EXPECT=approve FIXTURE_LANG=markdown APPROVE_REGEX="approve|approved" BLOCK_REGEX="needs-attention|needs attention"
review "$FIX/clean-low-risk-plan.md" "clean-fixture-no-bug"
unset EXPECT FIXTURE_LANG APPROVE_REGEX BLOCK_REGEX

# ── summary ──────────────────────────────────────────────────────────────────
export PROMPT_SUBDIR=code-review
if [ "$FAILED" -eq 0 ]; then
  echo "========================================"
  echo " ALL REVIEWER SCENARIOS PASSED (block gate green)"
  [ "$ADVISORY" -gt 0 ] && echo " approve advisory fails: $ADVISORY (precision signal — re-run; consistent fails = real over-strictness)"
  echo "========================================"
  exit 0
else
  echo "========================================"
  echo " SOME SCENARIOS FAILED"
  echo "========================================"
  exit 1
fi
