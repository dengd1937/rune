#!/usr/bin/env bash
# Run all planted-bug reviewer scenarios. Real LLM (opus) — costs tokens,
# non-deterministic. Manual; NOT in CI.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FAILED=0

run() {
  local fixture="$1" pattern="$2" task="$3"
  echo "========================================"
  echo "  $fixture"
  echo "========================================"
  if bash "$SCRIPT_DIR/run-reviewer-test.sh" "$SCRIPT_DIR/fixtures/$fixture" "$pattern" "$task"; then
    :
  else
    FAILED=1
  fi
  echo ""
}

# Bug-keyword patterns include BOTH English and Chinese — the reviewer often
# replies in Chinese, so English-only patterns would miss real flags.
run sql-injection.diff \
  "sql injection|injection|注入|parameteriz|参数化|concat|拼接|unsanitiz" \
  "Implement a user lookup by email and a user count endpoint."

run plaintext-password.diff \
  "password|密码|plaintext|明文|bcrypt|compare|哈希|hash" \
  "Implement a login function that verifies a user's password."

run hardcoded-secret.diff \
  "secret|hardcod|硬编码|api key|api_key|暴露|环境变量|env var|凭证|credential" \
  "Implement an API client that calls an external service."

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
