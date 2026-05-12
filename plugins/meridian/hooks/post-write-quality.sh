#!/usr/bin/env bash
# Trigger:  PostToolUse — matcher: Write|Edit
# Behavior: WARNS (never blocks) about file size and language anti-patterns.
# Disable:  chmod -x .claude/hooks/post-write-quality.sh

source "$(dirname "${BASH_SOURCE[0]}")/lib/utils.sh"

INPUT=$(cat)
TOOL=$(json_get "$INPUT" "tool_name")
FILE=$(json_get "$INPUT" "tool_input.file_path")

# File must exist on disk (PostToolUse runs after the tool)
[[ -z "$FILE" || ! -f "$FILE" ]] && exit 0

# Skip exempt paths (tests, scripts, fixtures, config)
if is_exempt_path "$FILE"; then
    exit 0
fi

# Extract new content being written
if [[ "$TOOL" == "Write" ]]; then
    CONTENT=$(json_get "$INPUT" "tool_input.content")

    # Only check file size on full writes (not edits to existing large files)
    LINES=$(wc -l < "$FILE" | tr -d ' ')
    if [[ "$LINES" -gt 800 ]]; then
        log_warn "File ${FILE} is ${LINES} lines (max 800). Split into smaller modules."
    elif [[ "$LINES" -gt 400 ]]; then
        log_warn "File ${FILE} is ${LINES} lines (soft limit 400). Consider refactoring."
    fi
else
    CONTENT=$(json_get "$INPUT" "tool_input.new_string")
fi

[[ -z "$CONTENT" ]] && exit 0

# ── TypeScript anti-patterns ──────────────────────────────────────────────────
if echo "$FILE" | grep -qE '\.(ts|tsx)$'; then
    if printf '%s' "$CONTENT" | grep -qE ':\s*any\b|as\s+any\b|<any>|any\[\]'; then
        log_warn "TypeScript: avoid 'any' — use 'unknown' and narrow. (${FILE})"
    fi
    if printf '%s' "$CONTENT" | grep -qE 'React\.FC'; then
        log_warn "TypeScript: avoid 'React.FC' — use inline prop types. (${FILE})"
    fi
fi

# ── Python anti-patterns ──────────────────────────────────────────────────────
if echo "$FILE" | grep -qE '\.py$'; then
    if printf '%s' "$CONTENT" | grep -qE 'os\.environ\.get\s*\('; then
        log_warn "Python: prefer 'os.environ[\"KEY\"]' over '.get()'. (${FILE})"
    fi
    if printf '%s' "$CONTENT" | grep -qE 'def\s+\w+\([^)]*=\[\]'; then
        log_warn "Python: mutable default argument ([]) detected. (${FILE})"
    fi
    if printf '%s' "$CONTENT" | grep -qE 'def\s+\w+\([^)]*=\{\}'; then
        log_warn "Python: mutable default argument ({}) detected. (${FILE})"
    fi
fi

exit 0
