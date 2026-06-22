"""Tests for hooks/commit-msg-strip-coauthor — strips Co-authored-by lines from commit messages.

Unlike other A-layer tests, this is a git commit-msg hook (not a Claude Code
PreToolUse/PostToolUse hook). It receives a file path as $1 and modifies it
in-place. No stdin JSON, no exit-code convention — just file mutation.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from conftest import HOOKS_DIR

HOOK = HOOKS_DIR / "commit-msg-strip-coauthor"


def _run(msg_file: Path) -> str:
    """Run the hook on a commit message file and return the resulting content."""
    subprocess.run(
        ["bash", str(HOOK), str(msg_file)],
        check=True,
    )
    return msg_file.read_text(encoding="utf-8")


def test_strips_coauthored_by(tmp_path):
    f = tmp_path / "COMMIT_EDITMSG"
    f.write_text("feat: add feature\n\nCo-authored-by: Bot <bot@example.com>\n")
    result = _run(f)
    assert "Co-authored-by" not in result
    assert "feat: add feature" in result


def test_strips_mixed_case_variants(tmp_path):
    f = tmp_path / "COMMIT_EDITMSG"
    f.write_text(
        "fix: bug\n\n"
        "Co-authored-by: A <a@x.com>\n"
        "Co-Authored-By: B <b@x.com>\n"
        "Co-Authored-by: C <c@x.com>\n"
        "Co-authored-By: D <d@x.com>\n"
    )
    result = _run(f)
    assert "Co-authored-by" not in result
    assert "Co-Authored-By" not in result
    assert "Co-Authored-by" not in result
    assert "Co-authored-By" not in result
    assert "fix: bug" in result


def test_strips_multiple_coauthor_lines(tmp_path):
    f = tmp_path / "COMMIT_EDITMSG"
    f.write_text(
        "feat: x\n\n"
        "Co-authored-by: Alice <a@x.com>\n"
        "Co-authored-by: Bob <b@x.com>\n"
        "Co-authored-by: Charlie <c@x.com>\n"
    )
    result = _run(f)
    assert result.count("Co-authored-by") == 0


def test_preserves_message_without_coauthor(tmp_path):
    f = tmp_path / "COMMIT_EDITMSG"
    original = "refactor: clean up imports\n\nRemoved unused imports from utils.\n"
    f.write_text(original)
    result = _run(f)
    assert result == original


def test_empty_message_no_crash(tmp_path):
    f = tmp_path / "COMMIT_EDITMSG"
    f.write_text("")
    result = _run(f)
    assert result == ""


def test_missing_file_no_crash(tmp_path):
    missing = tmp_path / "nonexistent"
    proc = subprocess.run(
        ["bash", str(HOOK), str(missing)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0


def test_preserves_body_content(tmp_path):
    f = tmp_path / "COMMIT_EDITMSG"
    f.write_text(
        "feat: new feature\n\n"
        "This is a detailed description.\n"
        "It spans multiple lines.\n\n"
        "Co-authored-by: Bot <noreply@anthropic.com>\n"
    )
    result = _run(f)
    assert "This is a detailed description." in result
    assert "It spans multiple lines." in result
    assert "Co-authored-by" not in result


def test_coauthor_mid_body_stripped(tmp_path):
    f = tmp_path / "COMMIT_EDITMSG"
    f.write_text(
        "feat: x\n\n"
        "Some context.\n"
        "Co-authored-by: Bot <bot@x.com>\n"
        "More context.\n"
    )
    result = _run(f)
    assert "Co-authored-by" not in result
    assert "Some context." in result
    assert "More context." in result
