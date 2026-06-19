"""Shared helpers for Rune skill manifest tests (C1-layer).

Validates the auto-discovered skill layer that neither A (hook code) nor B
(reviewer-prompt behavior) covers: frontmatter integrity, naming, README<->skills
sync, and the iron-law spine that session-start injects. Zero LLM, runs in CI.

Frontmatter is parsed with PyYAML rather than a hand-rolled regex scanner —
multi-line / quoted description values are fiddly to capture correctly, and a
real parser is the whole point (malformed YAML = the failure we want to catch).
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

# tests/skills/skills_lib.py -> parents[2] = repo root.
# Named skills_lib.py (not conftest.py) so it stays a uniquely-importable
# module: two files named conftest.py across tests/hooks and tests/skills
# collide under pytest's prepend import mode when both layers are collected in
# one run (both resolve to the same top-level `conftest` module). A-layer keeps
# its conftest.py; this layer uses a distinctly-named helper module instead.
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PLUGIN_ROOT / "skills"

# Frontmatter block at the very start of the file: opening --- on line 1,
# closing --- on its own line. Tolerates CRLF for CI portability.
_FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)


def load_frontmatter(skill_md: Path) -> dict:
    """Parse the YAML frontmatter block of a SKILL.md into a dict.

    Fails loudly (assertion) when the ---delimited block is missing, so a
    malformed skill surfaces instead of returning a silent empty dict.
    """
    text = skill_md.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.search(text)
    assert m, f"{skill_md}: missing '---' frontmatter delimiters"
    return yaml.safe_load(m.group(1)) or {}


def all_skills() -> list[Path]:
    """Every SKILL.md under skills/, sorted — the parametrize source."""
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


# Materialized once so parametrize ids and the duplicate-name test share one scan.
SKILLS = all_skills()
