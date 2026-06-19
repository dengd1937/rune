"""README skill table <-> skills/ directory must stay in sync.

The skill tables in README.md and README.zh-CN.md are hand-maintained catalogs.
A renamed/deleted skill, or a new skill not yet listed, drifts *silently* — the
docs and the actual auto-discovered set disagree with no signal. These tests
lock the currently-clean state (0 phantom, 0 orphan in both languages) so the
next drift is loud.

Doc-drift is Rune's recurring failure mode (there's a whole advisory hook for
spec drift); this is the same guard applied to the skill catalog.
"""
from __future__ import annotations

import re
from pathlib import Path

from skills_lib import PLUGIN_ROOT, SKILLS

_READMES = [PLUGIN_ROOT / "README.md", PLUGIN_ROOT / "README.zh-CN.md"]
_LINK_RE = re.compile(r"skills/([a-z0-9-]+)/SKILL\.md")


def _names_in_readme(readme: Path) -> set[str]:
    return set(_LINK_RE.findall(readme.read_text(encoding="utf-8")))


def _names_on_disk() -> set[str]:
    return {p.parent.name for p in SKILLS}


def test_no_phantom_skills_in_readme():
    """Every README skill link must resolve to a SKILL.md that exists on disk."""
    on_disk = _names_on_disk()
    for readme in _READMES:
        phantom = _names_in_readme(readme) - on_disk
        assert not phantom, f"{readme.name}: references missing skills: {sorted(phantom)}"


def test_no_orphan_skills_missing_from_readme():
    """Every skill on disk must appear in BOTH README tables."""
    for readme in _READMES:
        missing = _names_on_disk() - _names_in_readme(readme)
        assert not missing, f"{readme.name}: skill(s) absent from table: {sorted(missing)}"
