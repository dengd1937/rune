#!/usr/bin/env bash
# Shared utilities for Claude Code hooks.
# Source this file from each hook script: source "$(dirname "${BASH_SOURCE[0]}")/lib/utils.sh"

# Log a blocking message to stderr — Claude sees this before the tool call is cancelled.
log_block() {
    echo "[hook] BLOCKED: $*" >&2
}

# Log a warning to stderr — Claude sees this as feedback after the tool call.
log_warn() {
    echo "[hook] WARNING: $*" >&2
}

# Return 0 if the given file path is in an exempt location (tests, scripts, fixtures).
# These paths are allowed to contain debug statements and example secrets.
is_exempt_path() {
    local path="$1"
    echo "$path" | grep -qE '(tests?/|__tests__/|test_fixtures?/|spec/|scripts?/|\.env\.example)'
}

# Return 0 if the current project appears to be a Python project.
# Checks for pyproject.toml, setup.py, or requirements.txt at the project root.
is_python_project() {
    local root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
    [[ -f "${root}/pyproject.toml" ]] || \
    [[ -f "${root}/setup.py" ]]      || \
    [[ -f "${root}/requirements.txt" ]]
}

# Extract a dot-separated field from a JSON string via python3.
# Usage: json_get <json_string> <dot.path>
# Returns empty string on any error (python3 unavailable, key missing, etc.).
json_get() {
    local json="$1"
    local path="$2"
    printf '%s' "$json" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for p in sys.argv[1].split('.'):
        d = d.get(p, '') if isinstance(d, dict) else ''
    print(d or '', end='')
except Exception:
    print('', end='')
" "$path" 2>/dev/null || echo ""
}
