"""using-rune is the content session-start injects as iron-law context.

The A-layer (tests/hooks/test_session_start_inject.py) verifies the *injection
mechanism*: that SKILL.md is read, JSON-escaped, and emitted as
hookSpecificOutput.additionalContext. It does NOT verify the injected *content*
still carries the iron laws. This test guards the injection target —
hooks/session-start line 11 pins `skills/using-rune/SKILL.md` as the source.

If using-rune's spine (铁律 / L1 / L3) is ever gutted, the A-layer injection
test stays green while the laws silently vanish from every session. This test
closes that gap and bridges A <-> C.
"""
from __future__ import annotations

from skills_lib import PLUGIN_ROOT

USING_RUNE = PLUGIN_ROOT / "skills" / "using-rune" / "SKILL.md"

# The markers session-start injects and the whole workflow leans on.
# Keep in sync with skills/using-rune/SKILL.md §1.
_IRON_LAW_SPINE = ["铁律", "**L1**", "**L3**"]


def test_using_rune_has_iron_law_spine():
    text = USING_RUNE.read_text(encoding="utf-8")
    missing = [m for m in _IRON_LAW_SPINE if m not in text]
    assert not missing, f"using-rune lost iron-law markers: {missing}"
