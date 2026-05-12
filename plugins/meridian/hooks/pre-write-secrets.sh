#!/usr/bin/env bash
# Trigger:  PreToolUse — matcher: Write|Edit
# Behavior: BLOCKS writes that contain secrets or private keys.
# Disable:  chmod -x .claude/hooks/pre-write-secrets.sh

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/utils.sh"

INPUT=$(cat)
TOOL=$(json_get "$INPUT" "tool_name")
FILE=$(json_get "$INPUT" "tool_input.file_path")

# Extract the content being written
if [[ "$TOOL" == "Write" ]]; then
    CONTENT=$(json_get "$INPUT" "tool_input.content")
else
    CONTENT=$(json_get "$INPUT" "tool_input.new_string")
fi

[[ -z "$CONTENT" ]] && exit 0

# Test fixtures and example env files may contain placeholder secrets — allow them.
if is_exempt_path "$FILE"; then
    exit 0
fi

# Secret patterns to block. Each entry is a grep -E regex.
PATTERNS=(
    'sk-[a-zA-Z0-9]{32,}'                          # OpenAI / Anthropic API key
    'ghp_[a-zA-Z0-9]{36}'                           # GitHub personal access token
    'gho_[a-zA-Z0-9]{36}'                           # GitHub OAuth token
    'github_pat_[a-zA-Z0-9_]{40,}'                  # GitHub fine-grained PAT
    'AKIA[A-Z0-9]{16}'                              # AWS access key ID
    'xoxb-[0-9]+-[a-zA-Z0-9-]+'                     # Slack bot token
    'xoxp-[0-9]+-[a-zA-Z0-9-]+'                     # Slack user token
    'AIza[0-9A-Za-z_-]{35}'                         # Google API key
    '-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'  # Private key block
)

for PATTERN in "${PATTERNS[@]}"; do
    if printf '%s' "$CONTENT" | grep -qE -e "$PATTERN"; then
        log_block "Potential secret detected matching /${PATTERN:0:30}/ in ${FILE:-<content>}. Store credentials in environment variables or a secret manager — never in source code."
        exit 2
    fi
done

exit 0
