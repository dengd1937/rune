"""Tests for hooks/session-start injection contract (deterministic, no LLM).

Verifies the stdout JSON contract: valid JSON, hookSpecificOutput.additionalContext
schema, iron-laws content present, and — critically — escape correctness (a
poison SKILL.md must still yield valid JSON). All runs use cwd=tmp_path so the
deploy side-effect is a no-op (non-git dir) and the rune repo is not touched.
"""
import json

from conftest import run_hook


def test_outputs_valid_json_with_rune_context(tmp_path):
    res = run_hook("session-start", "", cwd=tmp_path)
    assert res.exit_code == 0
    data = json.loads(res.stdout)  # must parse
    ctx = data["hookSpecificOutput"]["additionalContext"]
    assert ctx  # non-empty
    assert "Rune" in ctx  # template marker


def test_uses_hook_specific_output_schema(tmp_path):
    res = run_hook("session-start", "", cwd=tmp_path)
    data = json.loads(res.stdout)
    assert data["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "additionalContext" in data["hookSpecificOutput"]


def test_escape_correctness_with_poison_skill(tmp_path):
    # characters that break naive JSON embedding
    skill = tmp_path / "skills/using-rune/SKILL.md"
    skill.parent.mkdir(parents=True)
    poison = 'has "double quotes", \\backslash, tab\there, cr\rcarriage, newline\nhere'
    skill.write_text(poison, encoding="utf-8")
    res = run_hook("session-start", "", cwd=tmp_path, env={"CLAUDE_PLUGIN_ROOT": str(tmp_path)})
    data = json.loads(res.stdout)  # raises if escape broke the JSON
    ctx = data["hookSpecificOutput"]["additionalContext"]
    assert poison in ctx  # round-trips intact after JSON decode


def test_missing_skill_file_still_valid_json(tmp_path):
    res = run_hook("session-start", "", cwd=tmp_path, env={"CLAUDE_PLUGIN_ROOT": str(tmp_path)})
    data = json.loads(res.stdout)  # still valid JSON, no crash
    ctx = data["hookSpecificOutput"]["additionalContext"]
    assert "Error reading" in ctx


def test_exit_zero_always(tmp_path):
    assert run_hook("session-start", "", cwd=tmp_path).exit_code == 0
