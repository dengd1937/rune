"""C1 manifest invariants for every auto-discovered skill.

Anchored to the spec in skills/writing-skills/SKILL.md (the meta-skill that
defines what a valid Rune skill looks like): `name` is lowercase-hyphen and
matches its directory; `description` is a non-empty, <500-char trigger phrase
starting "Use when". A skill that drifts from this fails to load or route
*silently* (Claude Code auto-discovers skills and emits no error on a malformed
one) — these tests make that drift loud.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from skills_lib import SKILLS, SKILLS_DIR, load_frontmatter

NAME_RE = re.compile(r"^[a-z0-9-]+$")


def test_every_skill_dir_has_a_skill_md():
    """Each skills/<name>/ must contain SKILL.md — the auto-discovery contract."""
    dirs_with_skill = {p.parent for p in SKILLS}
    all_skill_dirs = {p for p in SKILLS_DIR.iterdir() if p.is_dir()}
    assert dirs_with_skill == all_skill_dirs, (
        "skill dir(s) missing SKILL.md, or a SKILL.md outside a dir"
    )


@pytest.mark.parametrize("skill_md", SKILLS, ids=lambda p: p.parent.name)
def test_frontmatter_parses(skill_md: Path):
    fm = load_frontmatter(skill_md)
    assert isinstance(fm, dict), f"frontmatter did not parse to a mapping: {skill_md}"


@pytest.mark.parametrize("skill_md", SKILLS, ids=lambda p: p.parent.name)
def test_name_present_and_valid(skill_md: Path):
    fm = load_frontmatter(skill_md)
    name = fm.get("name")
    assert isinstance(name, str) and NAME_RE.match(name), (
        f"{skill_md.parent.name}: invalid name (need ^[a-z0-9-]+$): {name!r}"
    )


@pytest.mark.parametrize("skill_md", SKILLS, ids=lambda p: p.parent.name)
def test_name_matches_directory(skill_md: Path):
    fm = load_frontmatter(skill_md)
    assert fm.get("name") == skill_md.parent.name, (
        f"name {fm.get('name')!r} != directory {skill_md.parent.name!r}"
    )


@pytest.mark.parametrize("skill_md", SKILLS, ids=lambda p: p.parent.name)
def test_description_present(skill_md: Path):
    fm = load_frontmatter(skill_md)
    desc = fm.get("description")
    assert isinstance(desc, str) and desc.strip(), (
        f"{skill_md.parent.name}: empty or missing description"
    )


@pytest.mark.parametrize("skill_md", SKILLS, ids=lambda p: p.parent.name)
def test_description_under_500_chars(skill_md: Path):
    """writing-skills 铁律: description < 500 chars (CSO entry-point discipline)."""
    desc = load_frontmatter(skill_md)["description"]
    assert len(desc) <= 500, (
        f"{skill_md.parent.name}: description is {len(desc)} chars (max 500)"
    )


@pytest.mark.parametrize("skill_md", SKILLS, ids=lambda p: p.parent.name)
def test_description_starts_use_when(skill_md: Path):
    """writing-skills 铁律: description starts 'Use when' (trigger, not flow summary)."""
    desc = load_frontmatter(skill_md)["description"]
    assert desc.lower().startswith("use when"), (
        f"{skill_md.parent.name}: description must start 'Use when': {desc[:50]!r}"
    )


def test_names_are_unique():
    """No two skills may share a name — that shadows one at auto-discovery time."""
    names = [load_frontmatter(p).get("name") for p in SKILLS]
    seen: dict[str, int] = {}
    dups = set()
    for n in names:
        if n in seen:
            dups.add(n)
        seen[n] = seen.get(n, 0) + 1
    assert not dups, f"duplicate skill names: {sorted(dups)}"
