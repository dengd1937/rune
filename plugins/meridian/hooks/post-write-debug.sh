#!/usr/bin/env bash
# Trigger:  PostToolUse — matcher: Write|Edit
# Behavior: WARNS (never blocks) when debug statements are added to source files.
#           Claude sees the warning and removes them before committing.
# Disable:  chmod -x .claude/hooks/post-write-debug.sh

source "$(dirname "${BASH_SOURCE[0]}")/lib/utils.sh"

INPUT=$(cat)
TOOL=$(json_get "$INPUT" "tool_name")
FILE=$(json_get "$INPUT" "tool_input.file_path")

if [[ "$TOOL" == "Write" ]]; then
    CONTENT=$(json_get "$INPUT" "tool_input.content")
else
    CONTENT=$(json_get "$INPUT" "tool_input.new_string")
fi

[[ -z "$CONTENT" ]] && exit 0

# Debug statements in test / script paths are legitimate — skip.
if is_exempt_path "$FILE"; then
    exit 0
fi

DEBUG_PATTERNS=(
    'console\.(log|debug|trace)\('  # JS/TS debug logging
    '\bdebugger\b'                  # JS/TS debugger statement
    'pdb\.set_trace\(\)'            # Python pdb
    'import pdb'                    # Python pdb import
    '\bbreakpoint\(\)'              # Python 3.7+ breakpoint
)

FOUND=()
for PATTERN in "${DEBUG_PATTERNS[@]}"; do
    if printf '%s' "$CONTENT" | grep -qE "$PATTERN"; then
        FOUND+=("$PATTERN")
    fi
done

if [[ ${#FOUND[@]} -gt 0 ]]; then
    log_warn "Debug statement(s) added to ${FILE:-<file>}: ${FOUND[*]}. Remove before committing."
fi

exit 0  # Soft warning — never block
