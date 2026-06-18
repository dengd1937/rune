#!/usr/bin/env bash
# Trigger:  PreToolUse — matcher: Bash
# Behavior: ADVISORY — warns (non-blocking, exit 0) when a commit touches code
#           in a module that has a capability spec (per docs/CODEMAP.md
#           「Capability Spec」列) but neither that spec nor a
#           docs/changes/*/specs.md delta covering the capability is touched.
#           Catches the most common spec-drift omission mechanically, without
#           depending on Claude remembering to check.
# Bypass:   non-behavior commit types (refactor|docs|test|chore|ci|perf) and
#           the [no-spec-change] token in the commit message.
# No-op:    no docs/CODEMAP.md (e.g. Rune's own repo), or no specced modules.
# Disable:  chmod -x hooks/pre-spec-drift-check.sh
#
# NOTE: advisory by design — spec/delta is updated at finishing, not per-commit,
# so blocking would break SDD's per-task commits. The definitive gate is
# finishing's fresh-eyes spec verify. Escalate to exit 2 only after observing
# a low false-positive rate.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/utils.sh"

INPUT=$(cat)
CMD=$(json_get "$INPUT" "tool_input.command")
[[ -z "$CMD" ]] && exit 0

# Only inspect the first line for the git invocation.
FIRST_LINE=$(printf '%s' "$CMD" | head -1)
echo "$FIRST_LINE" | grep -qE '(^|[;&|]\s*)\s*git\s+commit\b' || exit 0

# ── Extract commit message (heredoc then -m), mirror pre-bash-guard Rule 6 ──
MSG_FIRST=$(printf '%s' "$CMD" | awk '/<<.*EOF/{f=1;next} f&&NF{print;exit}')
if [[ -z "$MSG_FIRST" ]]; then
    MSG_FIRST=$(printf '%s' "$CMD" | sed -n 's/.*-m[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
fi
[[ -z "$MSG_FIRST" ]] && exit 0   # editor-mode commit, nothing to parse

# ── Bypass: non-behavior commit types ───────────────────────────────────────
echo "$MSG_FIRST" | grep -qE '^(refactor|docs|test|chore|ci|perf)(\([^)]+\))?!?: ' && exit 0
# ── Bypass: explicit token ──────────────────────────────────────────────────
echo "$MSG_FIRST" | grep -qF '[no-spec-change]' && exit 0

# ── Graceful no-op: no CODEMAP ──────────────────────────────────────────────
CODEMAP="docs/CODEMAP.md"
[[ -f "$CODEMAP" ]] || exit 0

modmap=$(mktemp); touched=$(mktemp)
trap 'rm -f "$modmap" "$touched"' EXIT

# ── Build module-dir<TAB>capability list from CODEMAP 「关键模块」table ─────
# Columns: | 模块 | 职责 | 入口文件 | 主要依赖 | Capability Spec |
# awk field-by-|: a[4]=入口文件, a[6]=Capability Spec. Skip header/separator.
awk '
    /^##[[:space:]]*关键模块/ { intable=1; next }
    intable && /^##[[:space:]]/ { intable=0 }
    intable && /^\|[[:space:]]/ && !/^\|[[:space:]]*[-:]+/ {
        n = split($0, a, "|")
        if (n >= 6) {
            entry = a[4]; cap = a[6]
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", entry)
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", cap)
            if (cap == "Capability Spec" || entry == "入口文件") next   # header row
            if (cap != "" && cap != "[待补充]" && cap != "-") print entry "\t" cap
        }
    }
' "$CODEMAP" > "$modmap"

[[ -s "$modmap" ]] || exit 0   # no specced modules

# ── Touched set: staged ∪ branch-base..HEAD (fail-open on base detection) ──
git diff --cached --name-only > "$touched" 2>/dev/null || true
base=""
for ref in origin/main main origin/master master; do
    if b=$(git merge-base HEAD "$ref" 2>/dev/null); then base="$b"; break; fi
done
if [[ -n "$base" ]]; then
    git diff --name-only "$base"..HEAD >> "$touched" 2>/dev/null || true
fi

# ── For each touched source file: find its module's capability, check coverage ─
warned=0
while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    case "$f" in docs/*) continue ;; esac          # doc edits are the spec/delta updates themselves
    is_exempt_path "$f" && continue                 # tests/scripts/fixtures don't signal behavior change
    # find module whose dir is a path prefix of f
    cap=""
    while IFS=$'\t' read -r entry mcap; do
        [[ -z "$entry" ]] && continue
        mdir=$(dirname "$entry")
        case "$f" in
            "$mdir"/*) cap="$mcap"; break ;;
        esac
    done < "$modmap"
    [[ -z "$cap" ]] && continue
    # covered if the capability spec is touched, or a delta covers the capability
    spec_path="docs/specs/${cap}-spec.md"
    if grep -qxF "$spec_path" "$touched"; then continue; fi
    covered=0
    for delta in docs/changes/*/specs.md; do
        [[ -f "$delta" ]] || continue
        if grep -qE "^##[[:space:]]+${cap}([[:space:]]|$)" "$delta"; then covered=1; break; fi
    done
    [[ "$covered" -eq 1 ]] && continue
    log_warn "spec drift: $f → capability '$cap' (expected docs/specs/${cap}-spec.md or a changes/*/specs.md delta). Behavior-preserving? add [no-spec-change] to the message."
    warned=1
done < "$touched"

if [[ "$warned" -eq 1 ]]; then
    log_warn "(advisory — non-blocking; finishing's spec verify is the gate)"
fi

exit 0
